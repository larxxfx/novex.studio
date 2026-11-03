# NØVEX görsel stil kılavuzu — "çizgi roman sahne" tarzı (3 Kasım 2026)

Emir'in referans ekran kaydına (56 sn, başka bir kanalın Türkçe animasyon dizisi bölümü) göre çıkarıldı. **Amaç tarzı yakalamak, o kanalın karakterlerini,
sahnelerini, dizi adını veya kurgu öğelerini kopyalamak değil.** NØVEX'in kendi karakterleri, mekânları ve hikâyesi kullanılır.

## 1. Tarzın tanımı (referanstan gözlenen)

| Öğe | Özellik |
|---|---|
| Karakter başı | Büyük, bembeyaz, yuvarlak/hafif oval; saç çoğu zaman şapka/başörtüsü/bere altında |
| Yüz | Çok sade: iki küçük siyah göz (nokta veya kısık çizgi), kalın kaşlar; ağız ya yok ya tek çizgi. **Duygu kaş + göz ile** verilir |
| Eller | Beyaz, yuvarlak, eldiven gibi; parmak sayısı az |
| Kıyafet | Gerçekçi ve ayrıntılı: kapitone yelek, kasket, hırka, kamuflaj, puantiyeli etek; dokular (örgü, kadife) görülür |
| Çizgi | Koyu, kalın, eşit kalınlıkta dış çizgi; iç ayrıntıda ince çizgi |
| Boyama | Düz renk + yumuşak gölge (cel-shading); gradyan az |
| Palet | Sıcak toprak tonları + gece laciverti; ampul sarısı ışık noktaları; kırmızı tek vurgu (mendil) |
| Arka plan | Ayrıntılı, el çizimi Anadolu mekânı (taş duvar, ahşap balkon, kiremit çatı); karakterlerden daha az doygun |
| Kadraj | Sinema dili: geniş plan → omuz üstü → yakın plan; ön planda bulanık kafa/omuz (derinlik) |
| Hareket | Çoğunlukla duran sahne + yavaş kamera yaklaşması; karakterde küçük hareket (sallanma, kol, kaş); çizilmiş hareket çizgileri (davul, el) |
| Çekim süresi | ~2–4 sn; 56 sn'de ~20 çekim |
| Efektler | Buhar, ampul titremesi, ateş, ses dalgası çizgileri |
| Format | Referans 16:9 (uzun bölüm). NØVEX Shorts 9:16, film 16:9 — ikisi de desteklenir |

## 2. NØVEX'i ayırt eden kurallar (kopya görünmemek için)
- Kendi karakter kadromuz: her karakterin `KART.md`'si; referanstaki kişiler, kıyafet kombinasyonları ve mekânlar birebir kullanılmaz.
- İmza: gece sahnelerinde NØVEX turkuaz/elektrik mavisi ikincil ışık (telsiz ekranı, sinyal, uzak şehir), sıcak ampul ışığının yanında.
- SON SİNYAL: 2047 İstanbul'unda yapay zekâ ve insansı robotlar (bilim kurgu; zombi/salgın yok) — `seriler/son-sinyal/SERIES_BIBLE.md`.
  Robotlar aynı çizgi dilinde ama insanlardan anında ayrılır: kapsül kafa, koyu vizör, turkuaz LED nokta gözler. "KURGU · BİLİM KURGU" etiketi ekranda.
- Başlık/kapak tipografisi NØVEX kimliğinde; başka kanalın başlık yapısı taklit edilmez.

## 3. Üretim tarifi (çekim başına)

1. **Arka plan plakası** (karakter yok): GPT Images / ChatGPT. 9:16 için 1024×1536 (sonra 1080×1920'ye), 16:9 için 1536×1024.
2. **Karakter kesik görselleri** (şeffaf PNG): gövde pozu + ayrı **baş** (ifade seti: nötr, kızgın, şaşkın, gülen, kapalı göz, endişeli).
   Baş ayrı olunca göz kırpma ve kaş değişimi kod motorunda yapılır → aynı karakter yüzlerce çekimde tutarlı.
3. **Birleştirme (kendi motorumuz, $0):** katmanlı sahne + kamera yaklaşması/kaydırma + paralaks + küçük kukla hareketi
   (gövde sallanma, kafa eğme, kol döndürme, nefes) + efekt döngüleri (buhar, ampul, ateş, hareket çizgileri).
4. **Kling / Higgsfield yalnızca kahraman çekimleri için** (dans, koşma, kalabalık): bitmiş kare → image-to-video, 5 sn. Bütçe onayıyla.
5. Seslendirme + müzik + efekt → mevcut ses hattı → QC.

## 4. İstem şablonları (ChatGPT / GPT Images)

**Ortak stil cümlesi (her isteme eklenir):**
```
2D çizgi roman/karikatür illüstrasyonu. Karakterlerin başları büyük, düz beyaz ve yuvarlak; yüzde yalnızca iki küçük siyah göz
ve kalın kaşlar, ağız çok küçük veya yok; eller beyaz ve yuvarlak. Kıyafetler gerçekçi ve ayrıntılı dokulu. Koyu, kalın, eşit dış
çizgiler; düz renk + yumuşak hücre gölgelendirme. Sıcak toprak tonları, gece laciverti, sarı ampul ışıkları. Yazı, logo, filigran yok.
```
**Arka plan:** `… Mekân: {yer, saat, hava}. Karakter YOK. Kadraj: {geniş/orta}. Dikey 9:16.`
**Karakter gövde:** `… Karakter: {KART özeti}. Tam boy, {poz}. Baş YOK (boyun hizasında kesik). Şeffaf arka plan.`
**Karakter baş seti:** `… Aynı karakterin başı, önden, 6 ifade yan yana eşit aralıklı: nötr, kızgın, şaşkın, gülen, gözler kapalı, endişeli. Şeffaf arka plan, numara/yazı yok.`
Tutarlılık için: onaylı ilk görseli sonraki isteklere **referans olarak ekle** ("bu karakterin aynısı, sadece poz değişsin").
