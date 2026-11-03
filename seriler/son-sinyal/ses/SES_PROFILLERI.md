# SON SİNYAL — ses tutarlılığı

Her karakterin sesi **tek bir kaynaktan** gelir ve her bölümde aynı kayıt koşulu + aynı işleme ön ayarıyla üretilir.
Ön ayarlar `ses_profilleri.json`'da; `araclar/ses_isle.py` sonrası `araclar/karakter_ses.py <kod>` uygulanır (efekt).

| Kod | Karakter | Seslendiren | Kayıt koşulu | Efekt ön ayarı | Referans klip (SHA-256) |
|---|---|---|---|---|---|
| K1 | (bible'da) | Karar bekliyor | 20 cm, aynı oda | kuru | — |
| K2 | (bible'da) | Karar bekliyor | 20 cm | kuru | — |
| K3 | (bible'da) | Karar bekliyor | 20 cm | kuru | — |
| K4 | (bible'da) | Karar bekliyor | 20 cm | kuru | — |
| S | Sinyaldeki ses | Karar bekliyor | 20 cm | `telsiz` (300–3000 Hz bant, hafif bozulma, cızırtı yatağı) | — |
| A | Anlatıcı (bölüm girişi/özet) | Emir | 15–20 cm | kuru | — |

**Kurallar**
1. Seslendiren kişi bölüm ortasında değişmez. Değişirse bible'da gerekçe yazılır.
2. Lisans: yalnızca seslendirenin yazılı izni olan kayıtlar (`ses/izinler/` altında imzalı not; depoya kişisel veri yazılmaz, yalnızca "izin var: evet/tarih").
3. TTS yalnızca taslak/animatik içindir (`marka/SESLENDIRME.md`).
4. Her bölümün QC'sinde karakter replikleri referans klipleriyle aynı perde aralığında mı diye `araclar/ses_isle.py` raporu karşılaştırılır.
