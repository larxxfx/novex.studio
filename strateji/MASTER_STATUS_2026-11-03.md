# NØVEX — MASTER STATUS & MISSING TASKS REPORT (3 Kasım 2026, 23:20 TSİ)

Hazırlayan: Claude.
- Her madde bu oturumda **çalıştırılarak** test edildi; test edilemeyenler DOĞRULANAMADI olarak işaretli.
- Dosyanın var olması "tamamlandı" sayılmadı.
- Durum etiketleri: TAMAMLANDI · ÇALIŞIYOR · EKSİK · HATALI · DOĞRULANAMADI.

## Özet sayılar
| | Sayı | Not |
|---|---|---|
| Render edilmiş MP4 (EN) | 3 | Okyanus rotası: v1 Sarah, v2 Sarah, alternatif final (Matcha). Aynı video, üç sürüm. |
| Render edilmiş MP4 (TR) | 1 | Antarktika final (36,8 sn). "Amerika" videosunun dosyası bu ortamda yok. |
| Tüm teknik QC'yi geçen | 3 EN + 1 TR | Ses lisans kontrolü hariç. |
| Tam yayın paketine sahip | 1 | Okyanus rotası alternatif final: 10 dosya + kapak. |
| **YAYINA HAZIR (lisans dahil)** | **0** | Ses modeli lisansı hiçbir EN videoda tam doğrulanmadı. |
| Üretimde | 0 | |
| Kontrolde (Emir onayı bekleyen) | 1 | Okyanus rotası (ses seçimi + lisans). |
| Planlanmış ama üretilmemiş video klasörü | 29 | `videolar/2026-11-04…08`. Çoğu eski Türkçe plan, MP4 yok. |

## A. Tamamlanan işler
| İş | Durum | Kanıt |
|---|---|---|
| Okyanus rotası Short, alternatif final (Matcha, olay tabanlı ses tasarımı) | TAMAMLANDI | `VIDEO.mp4` sha256 `cd87a109…`; QC 10/10 teknik; senkron kayması 2 ms |
| Okyanus rotası v2 (Sarah), v1 | TAMAMLANDI | sha `4600e987…`, `341c5f7a…` |
| Karakter motoru kimlik düzeltmesi, PR #1 | TAMAMLANDI | Emir 20:21'de main'e birleştirdi (`967aca8`). Main'de: JS 15/15, servisler OK, fikir_puanla OK |
| EN ses lisans araştırması | TAMAMLANDI | `marka/SES_LISANS_ARASTIRMASI_EN.md` |
| İfadeli anlatım aracı | TAMAMLANDI | `araclar/anlatim_ifade.py`: parça başına hız, vurgu, perde, duraklama; Matcha/Piper/Kokoro |
| Üretim/teslim standardı, Creative Evolution, görsel kayıt | TAMAMLANDI | `strateji/URETIM_TESLIM_STANDARDI.md`, `GORSEL_KAYIT.md` |

## B. Halen çalışan sistemler (bugün çalıştırıldı)
| Sistem | Durum | Sınır |
|---|---|---|
| Küre render motoru `kure_v1` + rota modu | ÇALIŞIYOR | Yalnız küre/harita formatı. 51 sn video ≈ 20 dk (2 çekirdek, 4 parça). |
| Yerel EN TTS: Matcha/Piper/Kokoro (sherpa-onnx) | ÇALIŞIYOR | Duygu kontrolü yalnız parça tabanlı performansla. Matcha WER %1,8, Piper %5,6–6,4. |
| Whisper doğrulama (telaffuz, WER) | ÇALIŞIYOR | Cümle başına ~20 sn |
| Ses işleme, miks, ducking, konuşma/fon ölçümü (`ses_isle.py`, `miks.py`) | ÇALIŞIYOR | |
| Olay tabanlı ses tasarımı (`rota_ses.py`) | ÇALIŞIYOR | Kodla sentez, lisans temiz. Yalnız bu video tipine bağlı. |
| Teknik QC (`qc.py`) + blackdetect/freezedetect + senkron | ÇALIŞIYOR | İnsan kulağıyla dinleme yapılamıyor |
| Karakter motoru (Canvas/JS → MP4) | ÇALIŞIYOR | Tek test sahnesi; Explorer kiti lisansı doğrulanmadı |
| yt-* betikleri (chapters, deadair, title, retention, hookscore, swipe) | ÇALIŞIYOR | `--help` 6/6; `title.py` gerçek başlıkla çalıştı (66/100) |
| yt-audit, yt-comment, yt-plan, yt-seo, yt-shorts | DOĞRULANAMADI | Betiksiz talimat paketleri; kanal verisi olmadan sınırlı |
| GitHub (dal, push, PR REST) | ÇALIŞIYOR | GraphQL 403 → `gh pr create` çalışmıyor; REST çalışıyor |
| Sohbete dosya teslimi | ÇALIŞIYOR | 200 MB'a kadar gönderildi |
| vidIQ bağlayıcısı | ÇALIŞIYOR (kısmi) | Emir'in vidIQ hesabı; **kanal yetkili değil**; 80 kredi (ücretsiz plan) |

## C. Eksik işler
| Eksik | Durum |
|---|---|
| Konudan bağımsız görsel üretim hattı (tarih, uzay, gizem, bilim…) | EKSİK. Tek motor küre; Creative Evolution her videoya farklı dil istiyor |
| Uzun video (8–12 dk) hattı | EKSİK. Hiç denenmedi; mevcut hızla ~4–5 saat render |
| Zamanlanmış görevler (08/12/16/20, Pazar 19) | EKSİK. Hesapta 0 zamanlanmış görev |
| Hazır bildirimi | DOĞRULANAMADI. `PushNotification` aracı var, test edilmedi. E-posta yalnız izinle |
| Instagram Reels / TikTok paketleri ve erişimi | EKSİK |
| YouTube analytics, yorumlar | EKSİK. vidIQ'da kanal yetkisi yok |
| Ortak görev kuyruğu (ChatGPT ↔ Claude) | EKSİK. `inceleme/` boş; kuyruk dosyası yok |
| ChatGPT'nin depoya yazabildiği | DOĞRULANAMADI |
| Duygu kontrollü, lisansı tam doğrulanmış EN ses | EKSİK. Matcha ağırlık lisansı yazılı değil; Emir dinleme onayı yok |
| Konu başına özel kapak üretimi | EKSİK. Kapak motor karesinden; title.py tekrar uyarısı verdi |

## D. Hatalar ve riskler
| Risk | Durum |
|---|---|
| Ortam yeniden başlayınca uzun işler ölüyor (bugün 1 kez oldu) | HATALI → parçalı render ile azaltıldı |
| Natural Earth verisi temiz oturumda indirilemiyor (403) | HATALI: otomatik oturum küre motorunu kuramaz |
| Kokoro (Michael/Sarah) eğitim verisinde kapalı ticari TTS çıktısı | Risk: yayında kullanılmamalı |
| Explorer karakter kiti lisansı doğrulanmadan main'de (PR #1 birleşti) | Risk: kit yayında kullanılmamalı |
| vidIQ'da yükleme/güncelleme/üretim araçları açık | Risk: Emir onayı olmadan asla çağrılmaz |
| Görsel tekrar (iki video aynı gece küresi) | Risk |
| Descript AI kredisi bitmiş; ElevenLabs askıda | Bilgi |

## E. Erişim ve izin eksikleri
1. NØVEX YouTube kanalının vidIQ'da yetkilendirilmesi (analytics, yorumlar).
2. Instagram ve TikTok hesap erişimi (bağlayıcı yok).
3. Hugging Face / PyPI bu ortamda kapalı → daha iyi açık modeller (ör. Chatterbox) kurulamıyor.
4. `larxxfx/bilgi-grafigi` deposu oturuma eklenmedi.
5. Emir'in ses dinleme onayı ve lisans kararı.

## F. Otomatik çalışmayı engelleyen noktalar
1. Zamanlanmış görev yok (oluşturmak Emir onayı ister).
2. Temiz oturumda varlıklar yok: NE verisi indirilemiyor; modeller ~400 MB her seferinde indirilmeli.
3. Çeşitli konular için görsel motor yok → günde 4 farklı, özgün Short üretilemez.
4. Bir Short ≈ 30–40 dk toplam iş (ses + doğrulama + render + QC). 4/gün mümkün ama hiç denenmedi.
5. Yayına uygun ses yok (lisans + onay).

## G. Yarın sabah başlamadan önce gerekenler
1. **Emir:** `EN_same_script_MATCHA_videodaki_086.mp3` + alternatif final videoyu dinle → Matcha onayı veya ret.
2. **Claude:** Matcha model ağırlık lisansını k2-fsa/icefall kaynağından kesinleştir.
3. **Emir onayıyla:** varlıkları (NE verisi + build) `novex.studio` deposunda bir GitHub Release'e koymak → otomatik oturum indirebilir.
4. **Emir onayıyla:** zamanlanmış görevleri oluşturmak. Öneri: önce günde 1 Short; 3 gün kararlı çalışırsa 4'e çıkmak.
5. **Emir:** vidIQ'da NØVEX kanalını yetkilendir.

## H. Öncelik sırası
1. Ses onayı + lisans kesinleştirme.
2. Varlık barındırma + temiz oturumda uçtan uca prova (1 Short, insan müdahalesiz).
3. İkinci görsel motor: animasyonlu harita/arşiv-belgesel 2D dil; küreye bağımlılığı kırar.
4. Zamanlanmış 08:00 görevi (1/gün) + bildirim testi.
5. Ortak görev kuyruğu dosyası (`KUYRUK.md`) + ChatGPT yazma testi.
6. Instagram/TikTok paket şablonları.
7. Uzun video hattı (Voyager konsepti) — ayrı sprint.
8. 4/gün'e çıkış.

## I. Otomatik yapılabilenler / insan onayı gerektirenler
| Otomatik (geri alınabilir) | İnsan onayı şart |
|---|---|
| Konu araştırma, senaryo, ifadeli anlatım (onaylı sesle) | Yeni ses modeli seçimi |
| Render, ses tasarımı, QC, paket dosyaları | YouTube/IG/TikTok yükleme ve zamanlama |
| Dal üzerinde commit/push, rapor | main birleştirme, PR merge |
| Sohbete teslim + push bildirimi | Ücretli servis / vidIQ kredisi / e-posta gönderimi |
| Analytics okuma (yetki verilince, 0 kredi olanlar) | Yorum silme, engelleme, kanal ayarı; hassas yorum yanıtı |

## Yarın sabah bağımsız çalışma için gerçekte kalan adımlar
Yarın 08:00'de **otomatik ve insan müdahalesiz** Short üretimi henüz mümkün değil.
- **En kısa gerçekçi yol:** G1–G4 tamamlanırsa 4 Kasım akşamı ilk otomatik prova, 5 Kasım 08:00'de günde 1 Short.
- **Çeşitli konular** (ikinci görsel motor) için ayrıca 1–2 iş günü gerekiyor.
