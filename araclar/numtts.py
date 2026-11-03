"""Coqui Glow-TTS (tr/common-voice) + HiFiGAN (tr/common-voice) çıkarımının saf NumPy uygulaması.
PyTorch gerektirmez. Ağırlıklar pthload ile güvenli biçimde okunur.

Kaynak mimari: coqui-ai/TTS (MPL-2.0) — glow_tts.py, glow_tts/{encoder,decoder,glow,transformer,
duration_predictor}.py, generic/{normalization,wavenet}.py, vocoder/models/hifigan_generator.py.
Modeller: tts_models/tr/common-voice/glow-tts ve vocoder_models/tr/common-voice/hifigan (MIT).
"""
import json
import math
import os

import numpy as np

from pthload import load

F32 = np.float32


# ---------------------------------------------------------------- temel katmanlar
def wn(sd, p):
    """weight_norm: w = g * v / ||v|| (0. eksen dışında norm)."""
    if p + ".weight" in sd:
        return sd[p + ".weight"].astype(F32)
    v, g = sd[p + ".weight_v"].astype(F32), sd[p + ".weight_g"].astype(F32)
    n = np.sqrt((v.reshape(v.shape[0], -1) ** 2).sum(1)).reshape((-1,) + (1,) * (v.ndim - 1))
    return g * v / n


def conv1d(x, w, b=None, dil=1, pad=None):
    """x: (Cin,T)  w: (Cout,Cin,K)"""
    K = w.shape[2]
    if pad is None:
        pad = dil * (K - 1) // 2
    xp = np.pad(x, ((0, 0), (pad, pad))) if pad else x
    T = xp.shape[1] - dil * (K - 1)
    y = np.zeros((w.shape[0], T), F32)
    for k in range(K):
        y += w[:, :, k] @ xp[:, k * dil:k * dil + T]
    if b is not None:
        y += b[:, None]
    return y


def conv_t1d(x, w, b, stride, pad):
    """ConvTranspose1d. x: (Cin,T)  w: (Cin,Cout,K)"""
    Cin, Cout, K = w.shape
    T = x.shape[1]
    L = (T - 1) * stride + K
    y = np.zeros((Cout, L), F32)
    for k in range(K):
        y[:, k:k + (T - 1) * stride + 1:stride] += w[:, :, k].T @ x
    y = y[:, pad:L - pad]
    return y + b[:, None]


def layer_norm(x, g, b, eps=1e-4):
    m = x.mean(0, keepdims=True)
    v = ((x - m) ** 2).mean(0, keepdims=True)
    return (x - m) / np.sqrt(v + eps) * g.reshape(-1, 1) + b.reshape(-1, 1)


def lrelu(x, s=0.1):
    return np.where(x > 0, x, x * s)


# ---------------------------------------------------------------- metin
class Tokenizer:
    def __init__(self, cfg):
        c = cfg["characters"]
        self.vocab = [c["pad"], c["eos"], c["bos"]] + list(c["characters"]) + list(c["punctuations"])
        self.ids = {ch: i for i, ch in enumerate(self.vocab)}

    def __call__(self, text):
        t = text.replace("İ", "i").replace("I", "ı").lower()
        t = t.replace("’", "'").replace("‘", "'").replace("“", "").replace("”", "").replace('"', "")
        t = t.replace("â", "a").replace("î", "i").replace("û", "u")
        t = " ".join(t.split())
        dropped = sorted({ch for ch in t if ch not in self.ids})
        if dropped:
            raise ValueError(f"sözlükte olmayan karakter(ler): {dropped} -> metni yeniden yazın")
        return np.array([self.ids[ch] for ch in t], np.int64)


# ---------------------------------------------------------------- Glow-TTS
class GlowTTS:
    def __init__(self, model_dir):
        self.cfg = json.load(open(os.path.join(model_dir, "config.json")))
        self.sd = {k: v.astype(F32) for k, v in load(os.path.join(model_dir, "model_file.pth"))["model"].items()}
        self.tok = Tokenizer(self.cfg)
        c = self.cfg
        self.H = c["hidden_channels_enc"]
        self.heads = c["encoder_params"]["num_heads"]
        self.n_layers = c["encoder_params"]["num_layers"]
        self.n_blocks = c["num_flow_blocks_dec"]
        self.wn_layers = c["num_block_layers"]
        self.splits = c["num_splits"]
        self.sqz = c["num_squeeze"]
        assert c["encoder_params"].get("rel_attn_window_size") is None and c["mean_only"]
        # tersine akış için ön hesap
        self.inv = {i: np.linalg.inv(self.sd[f"decoder.flows.{3 * i + 1}.weight"].astype(np.float64)).astype(F32)
                    for i in range(self.n_blocks)}
        self.cw = {}
        for i in range(self.n_blocks):
            p = f"decoder.flows.{3 * i + 2}"
            self.cw[(i, "start")] = wn(self.sd, p + ".start")
            for j in range(self.wn_layers):
                self.cw[(i, "in", j)] = wn(self.sd, f"{p}.wn.in_layers.{j}")
                self.cw[(i, "rs", j)] = wn(self.sd, f"{p}.wn.res_skip_layers.{j}")

    def _c(self, p, x, **kw):
        return conv1d(x, self.sd[p + ".weight"], self.sd[p + ".bias"], **kw)

    def encode(self, ids):
        sd, H = self.sd, self.H
        x = (sd["encoder.emb.weight"][ids] * math.sqrt(H)).T  # (H,T)
        # prenet: ResidualConv1dLayerNormBlock (3 katman, k=5)
        r = x
        for i in range(3):
            x = self._c(f"encoder.prenet.conv_layers.{i}", x)
            x = layer_norm(x, sd[f"encoder.prenet.norm_layers.{i}.gamma"], sd[f"encoder.prenet.norm_layers.{i}.beta"])
            x = np.maximum(x, 0)
        x = r + self._c("encoder.prenet.proj", x)
        # RelativePositionTransformer (göreli pencere yok)
        kc = H // self.heads
        T = x.shape[1]
        for i in range(self.n_layers):
            p = f"encoder.encoder.attn_layers.{i}"
            q = self._c(p + ".conv_q", x).reshape(self.heads, kc, T).transpose(0, 2, 1)
            k = self._c(p + ".conv_k", x).reshape(self.heads, kc, T).transpose(0, 2, 1)
            v = self._c(p + ".conv_v", x).reshape(self.heads, kc, T).transpose(0, 2, 1)
            s = q @ k.transpose(0, 2, 1) / math.sqrt(kc)
            s = np.exp(s - s.max(-1, keepdims=True))
            s /= s.sum(-1, keepdims=True)
            o = (s @ v).transpose(0, 2, 1).reshape(H, T)
            y = self._c(p + ".conv_o", o)
            x = layer_norm(x + y, sd[f"encoder.encoder.norm_layers_1.{i}.gamma"], sd[f"encoder.encoder.norm_layers_1.{i}.beta"])
            f = f"encoder.encoder.ffn_layers.{i}"
            y = np.maximum(self._c(f + ".conv_1", x), 0)
            y = self._c(f + ".conv_2", y)
            x = layer_norm(x + y, sd[f"encoder.encoder.norm_layers_2.{i}.gamma"], sd[f"encoder.encoder.norm_layers_2.{i}.beta"])
        x_m = self._c("encoder.proj_m", x)
        d = "encoder.duration_predictor"
        h = np.maximum(self._c(d + ".conv_1", x), 0)
        h = layer_norm(h, sd[d + ".norm_1.gamma"], sd[d + ".norm_1.beta"])
        h = np.maximum(self._c(d + ".conv_2", h), 0)
        h = layer_norm(h, sd[d + ".norm_2.gamma"], sd[d + ".norm_2.beta"])
        logw = self._c(d + ".proj", h)[0]
        return x_m, logw

    def decode(self, z):
        """Ters akış: z (80,T) -> normalize mel (80,T)."""
        C, T = z.shape
        T2 = (T // self.sqz) * self.sqz
        z = z[:, :T2]
        x = z.reshape(C, T2 // 2, 2).transpose(2, 0, 1).reshape(C * 2, T2 // 2)  # squeeze
        CC, t = x.shape
        ns = self.splits
        for i in reversed(range(self.n_blocks)):
            # CouplingBlock ters
            p = f"decoder.flows.{3 * i + 2}"
            x0, x1 = x[:CC // 2], x[CC // 2:]
            h = conv1d(x0, self.cw[(i, "start")], self.sd[p + ".start.bias"])
            out = np.zeros_like(h)
            for j in range(self.wn_layers):
                xin = conv1d(h, self.cw[(i, "in", j)], self.sd[f"{p}.wn.in_layers.{j}.bias"])
                hc = xin.shape[0] // 2
                acts = np.tanh(xin[:hc]) * (1 / (1 + np.exp(-xin[hc:])))
                rs = conv1d(acts, self.cw[(i, "rs", j)], self.sd[f"{p}.wn.res_skip_layers.{j}.bias"])
                if j < self.wn_layers - 1:
                    h = h + rs[:hc]
                    out = out + rs[hc:]
                else:
                    out = out + rs
            o = self._c(p + ".end", out)
            tt, s = o[:CC // 2], o[CC // 2:]
            x = np.concatenate([x0, (x1 - tt) * np.exp(-s)], 0)
            # InvConvNear ters
            W = self.inv[i]
            xv = x.reshape(2, CC // ns, ns // 2, t).transpose(0, 2, 1, 3).reshape(ns, CC // ns, t)
            zz = np.einsum("ij,jct->ict", W, xv)
            x = zz.reshape(2, ns // 2, CC // ns, t).transpose(0, 2, 1, 3).reshape(CC, t)
            # ActNorm ters
            a = f"decoder.flows.{3 * i}"
            x = (x - self.sd[a + ".bias"].reshape(-1, 1)) * np.exp(-self.sd[a + ".logs"].reshape(-1, 1))
        return x.reshape(2, CC // 2, t).transpose(1, 2, 0).reshape(CC // 2, t * 2)  # unsqueeze

    def durations(self, text, length_scale=1.0):
        ids = self.tok(text)
        x_m, logw = self.encode(ids)
        w = (np.exp(logw) - 1) * length_scale
        return ids, x_m, np.maximum(np.ceil(w), 1).astype(int)

    def mel(self, text, length_scale=1.0):
        ids, x_m, wc = self.durations(text, length_scale)
        z = np.repeat(x_m, wc, axis=1)
        return self.decode(z), wc


# ---------------------------------------------------------------- HiFiGAN
class HiFiGAN:
    def __init__(self, model_dir):
        self.cfg = json.load(open(os.path.join(model_dir, "config.json")))
        sd = load(os.path.join(model_dir, "model_file.pth"))["model"]
        sd = {k[len("model_g."):]: v.astype(F32) for k, v in sd.items() if k.startswith("model_g.")}
        g = self.cfg["generator_model_params"]
        self.up = g["upsample_factors"]
        self.upk = g["upsample_kernel_sizes"]
        self.rk = g["resblock_kernel_sizes"]
        self.rd = g["resblock_dilation_sizes"]
        assert g["resblock_type"] == "1"
        self.W = {k[:-len(".weight_v")]: wn(sd, k[:-len(".weight_v")]) for k in sd if k.endswith(".weight_v")}
        self.B = {k[:-len(".bias")]: v for k, v in sd.items() if k.endswith(".bias")}

    def __call__(self, mel, pad=5):
        x = np.pad(mel, ((0, 0), (pad, pad)), mode="edge")
        o = conv1d(x, self.W["conv_pre"], self.B["conv_pre"])
        nk = len(self.rk)
        for i, (u, k) in enumerate(zip(self.up, self.upk)):
            o = lrelu(o)
            o = conv_t1d(o, self.W[f"ups.{i}"], self.B[f"ups.{i}"], u, (k - u) // 2)
            zs = None
            for j in range(nk):
                r = f"resblocks.{i * nk + j}"
                h = o
                for m, d in enumerate(self.rd[j]):
                    xt = conv1d(lrelu(h), self.W[f"{r}.convs1.{m}"], self.B[f"{r}.convs1.{m}"], dil=d)
                    xt = conv1d(lrelu(xt), self.W[f"{r}.convs2.{m}"], self.B[f"{r}.convs2.{m}"], dil=1)
                    h = xt + h
                zs = h if zs is None else zs + h
            o = zs / nk
        o = lrelu(o, 0.01)
        o = np.tanh(conv1d(o, self.W["conv_post"], self.B["conv_post"]))[0]
        hop = int(np.prod(self.up))
        return o[pad * hop: len(o) - pad * hop]
