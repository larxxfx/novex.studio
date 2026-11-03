"""PyTorch .pth (zip) ağırlıklarını torch olmadan, GÜVENLİ biçimde numpy'a okur.

Güvenlik: pickle yalnızca aşağıdaki izin listesindeki adları çözebilir (torch'un
weights_only=True moduyla aynı fikir). Listede olmayan herhangi bir sınıf/fonksiyon
istenirse yükleme hata ile durur; hiçbir modül import edilmez, hiçbir kod çalıştırılmaz.
"""
import collections
import pickle
import zipfile

import numpy as np

DTYPES = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64,
          "LongStorage": np.int64, "IntStorage": np.int32, "BoolStorage": np.bool_,
          "ByteStorage": np.uint8}


class UnsafePickle(Exception):
    pass


def _allowed(rebuild_tensor):
    def rebuild_parameter(data, *_):
        return data
    a = {
        ("collections", "OrderedDict"): collections.OrderedDict,
        ("torch._utils", "_rebuild_tensor_v2"): rebuild_tensor,
        ("torch._utils", "_rebuild_parameter"): rebuild_parameter,
    }
    a.update({("torch", n): n for n in DTYPES})
    return a


def _strided(buf, offset, size, stride):
    if len(size) == 0:
        return buf[offset:offset + 1].reshape(()).copy()
    it = buf.itemsize
    return np.lib.stride_tricks.as_strided(buf[offset:], shape=tuple(size),
                                           strides=tuple(s * it for s in stride)).copy()


def load_legacy(path):
    """Eski (zip olmayan) torch formatı: başlık pickle'ları + ana pickle + ham depolar."""
    f = open(path, "rb")
    pending = []  # (tensör yer tutucu listesi) depolar okunduktan sonra doldurulur
    storages = {}

    def rebuild_tensor(storage, offset, size, stride, *_):
        ph = {"storage": storage, "offset": offset, "size": size, "stride": stride}
        pending.append(ph)
        return ph

    allowed = _allowed(rebuild_tensor)

    class Strict(pickle.Unpickler):
        def find_class(self, module, name):
            if (module, name) in allowed:
                return allowed[(module, name)]
            raise UnsafePickle(f"izin verilmeyen pickle nesnesi: {module}.{name}")

        def persistent_load(self, pid):
            if not (isinstance(pid, tuple) and pid[0] == "storage" and pid[1] in DTYPES):
                raise UnsafePickle(f"beklenmeyen persistent id: {pid!r}")
            key = str(pid[2])
            storages.setdefault(key, DTYPES[pid[1]])
            return key

    for _ in range(3):  # magic, protokol, sistem bilgisi: düz veri
        Strict(f).load()
    obj = Strict(f).load()
    keys = Strict(f).load()
    raw = {}
    for k in keys:
        n = int.from_bytes(f.read(8), "little")
        dt = np.dtype(storages[str(k)])
        raw[str(k)] = np.frombuffer(f.read(n * dt.itemsize), dtype=dt)

    def resolve(o):
        if isinstance(o, dict) and set(o) == {"storage", "offset", "size", "stride"}:
            return _strided(raw[o["storage"]], o["offset"], o["size"], o["stride"])
        if isinstance(o, dict):
            return type(o)((k, resolve(v)) for k, v in o.items())
        if isinstance(o, (list, tuple)):
            return type(o)(resolve(v) for v in o)
        return o
    return resolve(obj)


def load(path):
    if not zipfile.is_zipfile(path):
        return load_legacy(path)
    z = zipfile.ZipFile(path)
    root = z.namelist()[0].split("/")[0]
    cache = {}

    def storage_bytes(key, dtype):
        if key not in cache:
            cache[key] = np.frombuffer(z.read(f"{root}/data/{key}"), dtype=dtype)
        return cache[key]

    def rebuild_tensor(storage, offset, size, stride, *_):
        key, dtype = storage
        buf = storage_bytes(key, dtype)
        if len(size) == 0:
            return buf[offset:offset + 1].reshape(()).copy()
        it = buf.itemsize
        return np.lib.stride_tricks.as_strided(buf[offset:], shape=tuple(size),
                                               strides=tuple(s * it for s in stride)).copy()

    def rebuild_parameter(data, *_):
        return data

    allowed = {
        ("collections", "OrderedDict"): collections.OrderedDict,
        ("torch._utils", "_rebuild_tensor_v2"): rebuild_tensor,
        ("torch._utils", "_rebuild_parameter"): rebuild_parameter,
    }
    allowed.update({("torch", n): n for n in DTYPES})

    class StrictUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if (module, name) in allowed:
                return allowed[(module, name)]
            raise UnsafePickle(f"izin verilmeyen pickle nesnesi: {module}.{name}")

        def persistent_load(self, pid):
            if not (isinstance(pid, tuple) and pid[0] == "storage" and pid[1] in DTYPES):
                raise UnsafePickle(f"beklenmeyen persistent id: {pid!r}")
            return (str(pid[2]), DTYPES[pid[1]])

    with z.open(f"{root}/data.pkl") as f:
        return StrictUnpickler(f).load()
