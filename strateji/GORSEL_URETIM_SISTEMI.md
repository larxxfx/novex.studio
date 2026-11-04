# NØVEX görsel üretim sistemi (Emir, 4 Kasım 2026 10:16 — kalıcı)

**Kural:** Yalnızca yazıya dayalı video yasak. `soru` kapanış kartı dışındaki **her sahnede somut bir görsel varlık** bulunur.
Denetim: `araclar/teslim_dogrula.py` (kural 8) — yalnız yazı/sayaç/harita/grafik sahnesi **hata** verir; video teslim edilemez.

## 1. Görsel varlık türleri (motor: `motor/sahne_v1/sahne.py`)
| Tür | Sahne | Ne zaman | Köken etiketi |
|---|---|---|---|
| Işın izlemeli Dünya / gezegen / Ay | `gezegen` (`doku: dunya|dunya_kuru|venus|mars|ay|buz|gaz`) | Coğrafya, uzay, What If senaryoları; dalış (`hedef_bas → hedef`, `dalis`), işaret, parlayan hat | `prosedurel` (kod) |
| Mekanizma / nesne | `gezegen` + `doku: yok` + `disliler` | Makineler, teknoloji | `prosedurel` |
| Fotoğraf / arşiv / AI görseli | `foto` | Tarih (eser, mekân, insan), doğa (manzara, hayvan, volkan), bilim (laboratuvar, mikroskop) | `fotograf`, `arsiv`, `ai` — **zorunlu** |
| Dünya küresi (referans motor) | `motor/kure_v1` | Ülke/kıta taşıma, parlayan sınırlar | `prosedurel` |

`foto` sahnesi: görsel ekranı doldurur, iki katmanlı **2.5D parallax** (yakın/uzak farklı kayar), Ken Burns zum/kaydırma, uzak katmanda sis, vinyet; üstüne gezegen sahnesiyle aynı yazılar (ust, ana, sayi, karsi). Test: `testler/test_foto_sahne.py`.

## 2. Gerçek, arşiv ve AI görsellerini ayırma (zorunlu)
- Her `foto` sahnesinde `koken`, `kaynak`, `lisans` alanları zorunlu (teslim_dogrula).
- `koken: ai` → ekranda kapatılamaz **"AI-GENERATED ILLUSTRATION"** etiketi; açıklama/SOURCES'ta "AI-generated illustration (not a real photograph)".
- `koken: arsiv` → ekranda "ARCHIVE IMAGE" + `kredi`. AI görseli asla gerçek tarihî fotoğraf/belge gibi sunulmaz; gerçek bir olayın "fotoğrafı" AI ile üretilmez.
- Paket aşaması `teslim/SOURCES.txt` sonuna sahne sahne **VISUALS** listesi yazar (köken, kaynak, lisans).
- Görsel dosyalar `videolar/<v>/gorseller/` altında; 5 MB üstü dosya depoya değil `varliklar` dalına (SHA-256 ile).

## 3. Gerçekten erişilebilen araçlar (4 Kas 2026 ölçümü)
| Araç | Durum | Not |
|---|---|---|
| `sahne_v1` gezegen/dişli/foto, `kure_v1` | ✅ çalışıyor, ücretsiz | Bu oturumda üretilen 4 Short'un tüm görselleri |
| Wikimedia Commons, NASA Images, Library of Congress, Openverse | ❌ bu ortamdan erişilemiyor | curl → 000 (ağ izin listesi). Emir bu kaynaklardan kamu malı görsel indirip sohbete ekleyebilir |
| Emir'in eklediği görseller | ✅ | Sohbete eklenen dosya → `gorseller/` + kaynak/lisans kaydı |
| ElevenLabs görsel/video, vidIQ b-roll/thumbnail, Descript stok | ⚠️ bağlı ama **kredi harcar** | Varsayılan bütçe sıfır → Emir onayı olmadan kullanılmaz |
| Kling AI, Higgsfield | ❌ bağlayıcı yok | Ücretli; yalnız Emir onayıyla, Emir'in hesabından |

## 4. ChatGPT prompt iş akışı
1. ChatGPT, video klasörüne `gorsel_promptlari.md` yazar (şablon aşağıda): sahne no, amaç, prompt, negatif prompt, en-boy 9:16, kamera hareketi, köken önerisi (fotoğraf mı AI mı).
2. Claude promptları sahne planıyla eşler. Görsel **gerçek** bir şey göstermeli ise (ör. Antikythera parçaları) önce kamu malı fotoğraf istenir (Emir ekler); yoksa prosedürel 3D.
3. AI üretimi yalnız Emir onaylarsa (araç + tahmini maliyet yazılı): Emir üretir ya da onay verir → dosya `gorseller/` → `foto` sahnesi `koken: ai`.
4. QC: kare incelemesinde AI görselinde etiket görünüyor mu, gerçek gibi sunuluyor mu kontrol edilir.

```markdown
### Sahne <n> — <amaç>
- Köken: fotograf | arsiv | ai | prosedurel
- Prompt (EN): <ayrıntılı, fiziksel olarak tutarlı, 9:16, sinematik ışık>
- Negatif: text, watermark, logo, distorted hands, fake historical documents
- Kamera: itme | cekme | sol | sag | yukari · derinlik 0–1
- Gerçek olay/kişi mi? evet → AI kullanılmaz, kamu malı fotoğraf aranır
```

## 5. Her Short için en az 2–3 unutulmaz görsel an
Sahne planı yazılırken `GORSEL_YON.md`'ye "unutulmaz anlar" listesi yazılır (ör. Gibraltar: tuz çölüne dönüşen Akdeniz, Atlantik'ten akan sel hattı; Antikythera: Ege'ye dalış, dönen bronz dişliler, tutulmadaki Ay).
