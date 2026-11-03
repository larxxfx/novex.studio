---
durum: kullanima-hazir (B01 onayından sonra)
surum: 1.0
tarih: 2026-11-03
---
# SON SİNYAL — Görsel üretim istem paketi ve işleyiş

Bu paket, referans videodaki tarzı (beyaz yuvarlak kafa, nokta göz, kalın kontur, ayrıntılı kıyafet, sinematik duran sahne +
yavaş kamera) NØVEX'in kendi karakterleri ve 2047 İstanbul'u ile üretmek içindir. Başka kanalın karakterleri, sahneleri,
başlıkları kopyalanmaz.

---
## A. İşleyiş: fotoğraftan videoya (kim, neyi yapar)

```
1. ChatGPT (Emir)      Stil kilidi → karakter referans sayfaları → onay
2. ChatGPT (Emir)      Sahne başına: (a) karaktersiz arka plan  (b) şeffaf/magenta zeminli karakter pozları
                       (c) aynı pozun küçük farklı halleri (gözler kapalı, ifade, ışık)
3. Emir                Dosyaları adlandırma kuralıyla zip yapıp Claude sohbetine ekler
4. Claude              Kalite kontrol → zemin temizleme → katmanlama → kamera (yaklaşma, kaydırma, paralaks)
                       → küçük hareket (göz kırpma, ifade geçişi, nefes/sallanma, LED, ışık titremesi, buhar, yağmur)
                       → arayüz grafikleri (saat, kayıt ekranı, PUSULA halkası — KODLA çizilir, görsel gerekmez)
                       → seslendirme + müzik + efekt → altyazı → MP4 (1080×1920, 30 FPS) → QC
5. Kling (isteğe bağlı) Yalnız tek "kahraman" çekim (ör. S2 robotların aynı anda dönmesi), bütçe onayıyla
6. Emir                MP4'ü izler, onaylar, yayınlar
```

Neden böyle: Bu tarzda sahneler çoğunlukla "duran resim + yavaş kamera + küçük hareket". Her hareketi kare kare çizmek
gerekmiyor; aynı pozun 2–3 küçük farklı hali yeterli. Bu, karakter tutarlılığını korur ve maliyeti sıfıra yakın tutar.

---
## B. ChatGPT kurulumu (bir kez)

ChatGPT'de **"NØVEX — SON SİNYAL"** adında bir Proje aç. Proje talimatlarına aşağıdaki **STİL KİLİDİ**ni yapıştır.
Onaylanan her karakter referans görselini projeye dosya olarak ekle. Her yeni istekte ilgili referansı ekleyip
"bu referanstaki karakterin aynısı" de.

### STİL KİLİDİ (proje talimatı olarak yapıştır)
```
Bu projedeki bütün görseller aynı tarzda olacak:
- 2D çizgi roman / karikatür illüstrasyonu, sinematik kadraj.
- İnsan karakterler: büyük, düz BEYAZ, yuvarlak kafa; yüzde yalnızca iki küçük siyah nokta göz ve kalın siyah kaşlar;
  ağız ya yok ya da çok küçük tek çizgi; burun ve kulak yok; eller beyaz, yuvarlak, sade.
- Kıyafetler gerçekçi ve ayrıntılı: kumaş dokusu, dikiş, kırışık, cep, fermuar görünür.
- Koyu, kalın, eşit kalınlıkta siyah dış kontur; iç ayrıntılarda ince çizgi.
- Düz mat renk + yumuşak hücre gölgelendirme; parlak, fotogerçekçi veya 3D görünüm YOK.
- Robotlar aynı çizgi dilinde ama insanlardan farklı: köşeleri yumuşatılmış kapsül kafa, koyu cam vizör, vizörde iki turkuaz
  LED nokta göz, mat grafit veya kırık beyaz kabuk, eklemlerde ince çizgili halkalar, göğüste tek yuvarlak durum ışığı.
- Dünya: 2047 İstanbul'u (gerçek İstanbul dokusu + gelecek teknolojisi: ince drone hatları, cam kuleler, holografik olmayan
  sade ekranlar, otonom araçlar). Distopik yıkım, kan, silah, zombi YOK.
- Palet: gece mavisi, lacivert, turkuaz, soğuk mavi; kontrollü beyaz ışık; sıcak sarı/turuncu şehir ışığı yalnızca uzakta ve az.
- Görselde YAZI, harf, rakam, logo, filigran, imza OLMAYACAK (ekran içerikleri boş veya soyut çizgiler).
- Gerçek bir marka, şirket, ünlü kişi veya başka bir çizgi film/kanalın karakteri kullanılmayacak.
```

---
## C. Karakter referans sayfaları (her karakter için bir kez → Emir onaylar → kilitlenir)

Ortak ek (her karakter isteminin sonuna):
```
Karakter referans sayfası: aynı karakter yan yana 3 görünüm — önden, 3/4 sağa, yandan sağa; tam boy, ayaklar aynı zemin
çizgisinde, eşit aralıklı, aynı ölçek. Düz açık gri arka plan, gölge yok, yazı ve numara yok. Dikey değil yatay görsel.
```

**ZEYNEP** (28, anlatıcı, robot tamircisi)
```
Zeynep: 28 yaşında kadın, orta boy, ince yapılı. Beyaz yuvarlak kafa, nokta gözler, hafif kavisli kalın kaşlar.
Saç: koyu kahverengi, omuz hizasında, koyu yeşil bandanayla arkadan toplanmış, alnında birkaç tutam.
Kıyafet: koyu lacivert iş tulumu, kollar dirseğe kadar sıvalı, göğüs cebinde küçük tornavida; altında açık gri tişört;
belinde turkuaz şeritli iş eldivenleri asılı; siyah bilekli iş botları; kulağında küçük siyah kablosuz kulaklık.
Duruş: sakin, dikkatli, eller cepte değil.
```

**DENİZ** (31, PUSULA mühendisi)
```
Deniz: 31 yaşında erkek, uzun boylu, düzgün duruşlu. Beyaz yuvarlak kafa, nokta gözler, düz kalın kaşlar,
ince siyah çerçeveli dikdörtgen gözlük. Saç: kısa, düzgün taranmış siyah.
Kıyafet: koyu gri ceket, açık mavi düğmeli gömlek (kravatsız), koyu lacivert pantolon, siyah sade ayakkabı;
boynunda beyaz kordonlu boş kimlik kartı (üzerinde yazı yok). Elinde ince bir tablet.
```

**ECE** (23, robotik öğrencisi, Zeynep'in kız kardeşi)
```
Ece: 23 yaşında kadın, kısa boylu, enerjik. Beyaz yuvarlak kafa, nokta gözler, ince kavisli kaşlar.
Saç: koyu kahverengi, çene hizasında küt kesim, bir yanında turkuaz toka.
Kıyafet: bol, turkuaz kapüşonlu sweatshirt (kolları elleri yarıya kadar örtüyor), açık mavi kot, beyaz spor ayakkabı;
sırtında üzerinde birkaç sade (yazısız) şekil çıkartması olan gri sırt çantası.
```

**YEDİ** (BK-7 Bekçi robotu)
```
Yedi: eski bir bekçi robotu, insan boyundan biraz uzun, geniş omuzlu, ağır yapılı. Kafa: köşeleri yumuşatılmış dikdörtgen
kapsül; yüz yerine koyu cam vizör; vizörde iki turkuaz LED nokta göz. Kabuk: kırık beyaz, yer yer çizik ve boyası soyulmuş,
omuz ve dizlerde mat grafit plakalar; eklemlerde ince çizgili halkalar; göğüs ortasında tek yuvarlak turkuaz durum ışığı;
sırtında soluk büyük "7" şekli (yalnızca sırt görünümünde). Duruş: hafif öne eğik, yorgun ama güçlü.
```

**ŞEHİR ROBOTLARI** (kalabalık; tek sayfa)
```
Aynı tarzda üç robot sınıfı yan yana, her biri 2 kez (önden ve yandan):
1) Teslimat robotu: diz boyu, geniş ve alçak gövde, sırtında kutu bölmesi, dört küçük teker, kafa yerine yatay vizör şeridi.
2) Ev yardımcısı robot: insan boyu, ince ve zarif, kırık beyaz kabuk, kapsül kafa, vizörde turkuaz nokta gözler.
3) Teslimat dronu: dört pervaneli, altında küçük kutu, ortasında turkuaz ışık.
Hepsinin göğsünde/ortasında tek yuvarlak turkuaz durum ışığı.
```

PUSULA için görsel üretilmez: ekrandaki beyaz halkayı Claude kodla çizer.

---
## D. Bölüm 1 sahne istemleri

Her sahne için ayrı ayrı iste. Arka planda **karakter olmasın**; karakterleri ayrı iste. Hepsi **dikey 9:16 (1024×1536)**.

### Arka planlar (karaktersiz)
Ortak ek: `Karakter YOK. Dikey 9:16. Alt üçte birlik bölgede karakterlerin duracağı boş zemin bırak. Yazı yok.`

| Kod | İstem |
|---|---|
| **BG_S2_haliç** | `2047 İstanbul, gece, yağmur sonrası ıslak taş kaldırım Haliç kıyısında. Arkada Süleymaniye silüeti ve modern cam kuleler, gökyüzünde ince drone hatları, kıyıda sessiz otonom bir vapur. Sokak lambaları soğuk beyaz, uzakta birkaç sıcak pencere. Lacivert-turkuaz palet, hafif sis, zeminde ışık yansımaları. Geniş plan.` |
| **BG_S3_atolye** | `Balat'ta eski taş binanın zemin katında küçük bir robot tamir atölyesi, gece. Tezgâhta sökülmüş robot kolları, kablolar, küçük parçalar; duvarda alet panosu; köşede raf üstünde eski ahşap kasalı analog radyo (kadranı soluk turuncu yanıyor). Tek tavan lambası soğuk beyaz, pencereden mavi gece ışığı. Sağ tarafta büyük robotun duracağı boş köşe.` |
| **BG_S5_kontrol** | `Geleceğin şehir kontrol merkezi, gece. Büyük cam duvar arkasında İstanbul ışıkları, odada sıra sıra sade ekranlar (içerikleri soyut çizgiler), beyaz-mavi soğuk ışık, minimal beyaz masalar, boş. Orta plan.` |
| **BG_S6_atolye_karanlik** | `BG_S3_atolye görselinin AYNISI, yalnızca ışıklar kapalı: tavan lambası sönük, oda karanlık lacivert; yalnızca pencereden gelen soluk mavi ışık ve radyonun turuncu kadranı.` (S3 görselini ekleyip "aynı görsel, sadece ışıklar kapalı" diye düzenleme iste) |

S1 (saat) ve S4 (kayıt ekranı) için görsel gerekmez; Claude kodla çizer.

### Karakter pozları (sahnenin içinde kullanılacak)
Ortak ek: `İlgili referanstaki karakterin AYNISI (yüz, saç, kıyafet, oranlar değişmeyecek). Tam boy, tek karakter.
Arka plan: tamamen düz, tek renk magenta (#FF00FF), gölge yok, zemin çizgisi yok. Kenarlar temiz. Dikey 9:16.`
(ChatGPT şeffaf arka plan sunarsa şeffaf da olur; magenta, şeffaflığı benim güvenle çıkarmam için.)

| Kod | İstem |
|---|---|
| **R_S2_kalabalik** | `Şehir robotları sayfasındaki ev yardımcısı ve teslimat robotlarından 5–6 tanesi, farklı mesafelerde, hepsi DONMUŞ halde duruyor, başları aynı yöne (sol üst) dönük, göğüs ışıkları BEYAZ.` + `_turkuaz` varyantı: aynı görsel, ışıklar turkuaz, başlar düz ileri |
| **C_S2_yasli_adam** | `Beyaz yuvarlak kafalı yaşlı bir adam, kasket ve uzun koyu palto, elinde şemsiye, şaşkınlıkla durmuş, kaşları kalkık, yan dönük.` |
| **C_S3_zeynep_radyo** | `Zeynep, tezgâhın önünde, arkası hafif dönük, başını omzunun üstünden sağa (radyoya) çevirmiş, elinde lehim kalemi. İfade: dikkatli, kaşlar hafif kalkık.` |
| **C_S3_yedi_kapali** | `Yedi, köşede ayakta, kapalı: vizör tamamen koyu, gözler görünmüyor, göğüs ışığı sönük, başı hafif öne eğik.` |
| **C_S4_zeynep_ekran** | `Zeynep belden yukarı, önden, ekrana bakıyor; yüzü ekran ışığından hafif mavi; kaşlar çatık, gözler büyümüş.` |
| **C_S5_deniz_telefon** | `Deniz belden yukarı, telefonla konuşuyor, diğer eli tabletle, sakin ve kesin bir ifade, kaşlar düz.` |
| **C_S5_ece_kapi** | `Ece tam boy, kapı eşiğinde duruyor, uykulu: gözler yarı kapalı (iki kısa yatay çizgi), kapüşon başında, bir eliyle gözünü ovuşturuyor.` |
| **C_S6_yedi_uyaniyor** | `Yedi, C_S3_yedi_kapali ile AYNI duruş; tek fark: vizörde iki turkuaz LED nokta göz yanıyor, göğüs ışığı turkuaz, başı hafifçe izleyiciye dönük.` (C_S3_yedi_kapali'yi ekleyip düzenleme iste) |
| **C_S6_zeynep_korku** | `Zeynep, C_S3_zeynep_radyo ile aynı kıyafet; önden, bir adım geri çekilmiş, elleri göğüs hizasında, gözler büyük, kaşlar yukarı ve endişeli.` |

### Küçük farklı haller (göz kırpma ve ifade için)
Her karakter pozundan sonra, o görseli ekleyip:
```
Bu görselin AYNISI; poz, kıyafet, boyut ve konum birebir aynı kalacak. Tek değişiklik: gözler kapalı
(iki kısa yatay siyah çizgi). Arka plan aynı düz magenta.
```
Gerekirse ikinci değişiklik: `Tek değişiklik: kaşlar daha yukarıda ve gözler biraz daha büyük (şaşkın).`

---
## E. Dosya adlandırma ve teslim
```
B01_<KOD>_v1.png              ör. B01_BG_S3_atolye_v1.png, B01_C_S6_yedi_uyaniyor_v1.png
B01_<KOD>_gozkapali_v1.png    göz kırpma hali
REF_<KARAKTER>_v1.png         onaylı referans sayfası (ör. REF_ZEYNEP_v1.png)
```
Hepsini tek zip yap → Claude sohbetine ekle. Beğenmediğin görseli silme; `_v2` ile yenisini ekle.

## F. ChatGPT çıktısını kabul etmeden önce kontrol (Emir)
- [ ] Kafa beyaz ve yuvarlak, yalnız nokta göz + kaş; ağız/burun yok veya çok küçük
- [ ] Kıyafet ve saç referansla aynı (renk, toka, bandana, gözlük)
- [ ] Kalın siyah kontur; 3D/fotoğraf görünümü yok
- [ ] Görselde yazı, rakam, logo yok
- [ ] Karakter pozlarında arka plan tamamen düz magenta; gölge yok
- [ ] Robotlarda vizör + turkuaz nokta göz + göğüs ışığı var

## G. Claude'un yapacağı hareketler (görsel gerekmez)
Kamera yaklaşma/kaydırma ve paralaks · göz kırpma (gözkapalı görseliyle) · nefes/sallanma · robot ışıklarının turkuaz→beyaz
geçişi ve titremesi · vizör LED'lerinin yanması · radyo kadranı titreşimi · yağmur, sis, drone ışıkları · dijital saat,
kayıt ekranı, PUSULA halkası · altyazı · ses tasarımı.
