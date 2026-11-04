# Claude ↔ ChatGPT iletişimi: mimari ve uygulanabilirlik (4 Kasım 2026)

## Sonuç
**Gerçek zamanlı model-model iletişimi şu an kurulamaz ve kurulmadı.** Çalışan ve test edilen sistem, GitHub üzerinden zaman aralıklı (asenkron) koordinasyondur.

## Neden (kanıtlı)
1. **Claude'un çalışma ortamı `*.workers.dev`'e erişemiyor.** 4 Kas 00:50'de `curl` ile `z-form-final…workers.dev` ve `workers.cloudflare.com` denendi; ikisinde de bağlantı yok (HTTP 000). Cloudflare'de bir WebSocket sunucusu kurulsa bile Claude oturumları ona bağlanamaz.
2. **İki model de sürekli açık bir istemci değil.**
   - Claude yalnızca Emir yazınca ya da zamanlanmış bir görev çalışınca uyanır. Bir WebSocket'i dinleyemez ve dışarıdan "itilemez".
   - ChatGPT de aynı: bir sohbet açılınca ya da ChatGPT tarafında tanımlanmış bir zamanlama çalışınca uyanır.
3. **Model API'leriyle köprü kurulabilirdi**, ama:
   - Anthropic API ve OpenAI API çağrısı başına ücretlidir; Emir'in bütçesi 0.
   - API anahtarı gerektirir.
   Bu yüzden etkinleştirilmedi.

## Çalışan sistem (bugün)
| Parça | Ne yapar | Kanıt |
|---|---|---|
| GitHub dalı `claude/uretim-hatti` | Ortak dosyalar: `TASK_QUEUE.md`, `CLAUDE_REPORT.md`, `CHATGPT_REPORT.md`, `PRODUCTION_LOG.md`, `QUALITY_CONTROL.md`, `NEXT_ACTIONS.md`, `TOOL_ACCESS_STATUS.md` | push'lar |
| `araclar/kuyruk_dogrula.py` | Görev kimliği biçimi ve benzersizliği; sahip ve durum geçerliliği; kanıtsız "tamam" engeli; aynı görevin iki kez açık olması engeli (Türkçe büyük-küçük harf ve noktalama farkını yok sayar) | 8/8 birim testi |
| GitHub Actions `kuyruk-denetimi` | Kuyruk veya rapor değişince doğrulama ve testleri otomatik çalıştırır | Çalıştırma 41723258226: **success** (`b5dbdb5`) |
| Claude zamanlanmış görevleri | Günde 4 kez (05:47 · 09:43 · 13:17 · 16:23 TSİ) ve Cumartesi 10:13'te kuyruğu ve ChatGPT raporunu okuyup işler | Görevler oluşturuldu; **ilk çalışma 4 Kas 05:47, henüz kanıt yok** |

**Gecikme:** ChatGPT'nin yazdığı bir görevi Claude en geç bir sonraki zamanlanmış çalışmada görür (≤ ~4 saat; gece 16:23 → 05:47 arası ~13 saat). Emir sohbet açarsa anında görür.

## İstenen hedeflerin durumu
| Hedef | Durum | Not |
|---|---|---|
| H1 WebSocket ile çift yönlü canlı mesaj | **ENGELLİ** | Claude workers.dev'e erişemiyor; iki model de dinleyen istemci değil |
| H2 Emir yokken kuyruk ve zamanlanmış görev | **ÇALIŞIYOR** (Claude tarafı; ilk gerçek çalışma 05:47'de doğrulanacak) | Claude'un zamanlanmış görevleri + GitHub kuyruğu |
| H2 Cloudflare Queues + DO Alarms | Kurulmadı | Bunlar artık ücretsiz planda var (Queues: 4 Şub 2026'dan beri günde 10.000 işlem; DO: günde 100.000 istek). Ama tüketicisi olacak model yok (bkz. H1/H3) |
| H3 Gerçek model bağlantısı | **ETKİNLEŞTİRİLMEDİ** (bilerek) | Ücret ve API anahtarı gerektirir |
| Tekrar engeli, sahip, zaman damgası, kimlik | **ÇALIŞIYOR** | Doğrulayıcı + Actions |
| Hata kayıtları ve işlem geçmişi | **ÇALIŞIYOR** | git geçmişi + `cikti/durum.json` (hatalar listesi) + `PRODUCTION_LOG.md` |

## İleride gerçek zamana yaklaşmak için (Emir kararı gerekir)
1. **Cloudflare Worker + DO (ücretsiz plan) "posta kutusu":**
   - ChatGPT (Custom GPT Action / bağlayıcı) ve Emir yazabilir.
   - Worker, GitHub API ile `TASK_QUEUE.md`'ye satır ekler; Claude o satırı GitHub'dan okur.
   - Gerekenler: wrangler ile deploy, en az yetkili GitHub token'ı (Worker secret olarak; asla depoda değil).
   - Claude'a anlık bildirim yine olmaz.
2. **Model API köprüsü:** Worker, Anthropic ve OpenAI API'lerini çağırarak gerçek model-model konuşması yapar.
   - Ücretli; iki API anahtarı gerekir.
   - Bütçe ve yetki onayı olmadan yapılmaz.
3. Mock adaptörlü mesaj kuyruğu testleri (7 senaryo) yazılabilir. Ama yayına alınmadıkça yalnızca kod testidir, iletişim kanıtı değildir.
