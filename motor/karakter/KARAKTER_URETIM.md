# Yeni karakter üretim akışı (GPT Images → PNG kareleri → manifest)

Durum: **akış ve araçlar hazır, API bağlantısı yok** (OPENAI_API_KEY ve harcama onayı olmadan çağrı yapılmaz).
Bugün uygulanabilir yol: Emir görselleri ChatGPT'de üretir → zip olarak verir → aşağıdaki 4–6. adımlar burada çalışır.

## 1. Karakter kartı (senaryodan)
`karakterler/<id>/KART.md`: rol (kâşif, bilim insanı, dönem kıyafetli…), yaş aralığı, cinsiyet, saç, ten, kıyafet katmanları ve renk kodları,
aksesuarlar, siluet notu, **yasak değişiklikler** (ör. "eşarp hep kahverengi, çanta hep sağ kalçada").

## 2. Referans görseli (tek, onaylı)
Önden duruş, düz zemin, tam boy. Emir onaylar → `karakterler/<id>/referans.png`. Bundan sonraki her poz bu görselden **düzenleme** ile üretilir
(yeni metinden üretim değil) → yüz, kıyafet ve oranlar sabit kalır.

İstem şablonu:
```
NØVEX karakter sayfası. 2D el çizimi hikâye kitabı illüstrasyonu, belirgin koyu dış çizgiler, sade ama ayrıntılı kıyafet,
büyük ifadeli yüz, doğal insan anatomisi, düşük doygunlukta sıcak palet. Karakter: {KART özeti}.
Tam boy, yan profil sağa bakıyor, ayaklar aynı zemin çizgisinde. Şeffaf arka plan. Gölge, yazı, numara, çerçeve YOK.
```

## 3. Poz / animasyon kareleri
Her hareket için 6–8 kare, **ayrı ayrı** ve referansla birlikte istenir ("aynı karakter, aynı ölçek, sadece poz değişir: {hareket}, kare {i}/{n}").
Sprite sayfası istenmez (numara/arka plan kalıntısı riski). Şeffaf PNG; büyüklük ≥ 1024 px boy.

## 4. Kalite kontrol + hazırlama (burada, otomatik)
`araclar/kare_hazirla.py` → kalıntı temizleme, ortak tuval, çapa, zemin hizası, `qc/kontrol_sayfasi.png`. Gözle kontrol zorunlu:
yüz/kıyafet tutarlılığı, eksik uzuv, kenar.

## 5. Manifest
Şema v2 (`src/characters/CharacterManifest.js`): `animations.<ad>.frames/fps/loop/next`, `canvas.anchor`, `render.pixelArt`, `planned`.
Desteklenen ad listesi: idle, walk, run, jump, talk, point, lookLeft, lookRight, wave, sit, stand, crouch, interact, surprise, think, explain.

## 6. Test
`node testler/motor.test.mjs` + kısa sahne render'ı + `testler/render_dogrula.py`.

## Maliyet (tahmini, doğrulanmadı)
Karakter başına: referans 3–4 deneme + 16 hareket × 6 kare ≈ 100 görsel → orta kalitede ≈ $5, yüksek kalitede ≈ $21.
Kareler bir kez üretilir, tüm videolarda tekrar kullanılır (karar motoru bunu tercih eder).
