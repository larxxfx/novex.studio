# NØVEX üretim motoru — karakter + hibrit video (dal: `feat/novex-character-engine`)

Mevcut üretim hattına (araclar/: ses_isle, hizala, miks, qc) **dokunmadan** eklenen bağımsız modüller.

## Mimari

```
motor/
├── karakter/                      Canvas/JS karakter motoru (tarayıcıda da, MP4 render'ında da aynı kod)
│   ├── src/characters/            CharacterManifest (şema v2 doğrulama) · CharacterLoader (ön yükleme + önbellek) · CharacterManager
│   ├── src/animation/             AnimationTimeline (deterministik kare seçimi, döngü, next, anahtar kare) · SpriteCharacter
│   ├── src/scene/                 SceneRenderer (katmanlar, z sırası, renderFrame(t)) · CameraController · sahneKur (JSON → sahne)
│   ├── render/sahne.html          MP4 render girişi (başsız Chromium; requestAnimationFrame YOK)
│   ├── onizleme.html              iPad canlı önizleme (aynı renderFrame; zamanı rAF ilerletir)
│   ├── karakterler/<id>/          üretime hazırlanmış kareler + manifest.json + qc/
│   ├── kaynak/<kit>/              gelen kitler, DEĞİŞTİRİLMEDEN saklanır
│   ├── sahneler/*.json            sahne tanımları
│   ├── araclar/kare_hazirla.py    kit → temiz, hizalı kareler + manifest + kontrol sayfası
│   ├── araclar/karakter_render.py sahne → MP4 (1080×1920/30, ses efektleri karelerden, −14 LUFS, qc.py)
│   └── testler/                   motor.test.mjs (14) · render_dogrula.py (7, gerçek MP4 üzerinde)
└── servisler/                     Harici servis adaptörleri (yalnız sunucu/yerel; anahtar ortam değişkeninde)
    ├── temel.py                   ortak arayüz · harcama kilidi · yeniden deneme · anahtar maskeleme
    ├── adaptorler.py              Kling · Higgsfield · GPT Images (birbirinden bağımsız)
    ├── karar.py                   hibrit karar motoru (varsayılan: yerel, $0)
    └── test_servisler.py          11 test
```

## Komutlar

```bash
node motor/karakter/testler/motor.test.mjs                                        # motor birim testleri
python3 -m unittest motor/servisler/test_servisler.py -v                          # adaptör + karar testleri
python3 motor/karakter/araclar/kare_hazirla.py motor/karakter/kaynak/explorer_kit_v1 explorer motor/karakter/karakterler/explorer
python3 motor/karakter/araclar/karakter_render.py motor/karakter/sahneler/ornek_kasif.json /tmp/kasif [--ses anlatim.wav]
python3 motor/karakter/testler/render_dogrula.py /tmp/kasif                        # MP4 + senkron doğrulaması
python3 -m http.server   →   /motor/karakter/onizleme.html                         # canlı önizleme
```

## Harici servisler — gerçek durum (3 Kasım 2026)

| Servis | Gerçek API | Bizdeki durum | Fiyat (doğrulanmadı) |
|---|---|---|---|
| Kling AI | Var (başvuru + onay, ayrı kredi havuzu) | Anahtar yok · `_gonder` yazılmadı | ≈ $0.075–0.11/sn |
| Higgsfield | Var (self-serve, ön ödemeli $ bakiye; web planı API vermez) | Anahtar yok · `_gonder` yazılmadı | ör. $0.115/sn, DoP $0.125/üretim |
| GPT Images (gpt-image-2) | Var (token bazlı; şeffaf arka plan önizlemede) | Anahtar yok · `_gonder` yazılmadı | ≈ $0.006–0.21/görsel |

Ücretli çağrı için üç koşul birlikte gerekir: `<SERVİS>_API_KEY`, `NOVEX_HARCAMA_ONAYI=evet`, tahmini maliyet ≤ `NOVEX_IS_BASINA_MAKS_USD`.
Anahtarlar depoya, tarayıcıya, loglara girmez.
