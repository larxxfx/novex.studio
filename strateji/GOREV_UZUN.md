# NØVEX — haftalık uzun belgesel görevi (Cumartesi 10:13 başlar, teslim Pazar 19:00)

8–12 dk, tamamen İngilizce, 16:9 (1920×1080), sinematik belgesel; Shorts'un uzatılmış hâli değil. **Shorts hattından ayrı hat.**
1. Dal `claude/kalite-standardi`; önce CLAUDE.md, strateji/URETIM_TESLIM_STANDARDI.md, strateji/GORSEL_REFERANS.md, NEXT_ACTIONS.md (N-06). `bash araclar/kurulum_ortam.sh`.
2. Hat durumu: uzun video hattı henüz YOK (sahne_v1 1080×1920 sabit, qc.py ≤60 sn). Önce kur: W/H plandan, 16:9 güvenli alan, bölüm sahnesi, çok parçalı devam ettirilebilir render, uzun QC modu. Short üretimini bozma: 2026-11-04 Short karelerini eski kodla piksel piksel karşılaştır (fark 0) + `python3 -m unittest discover -s testler`.
3. Konu: ChatGPT'nin haftalık senaryosu (CHATGPT_REPORT.md/TASK_QUEUE.md) yoksa plan/en/longform_* veya bu haftanın Short'larıyla çakışmayan araştırması güçlü konu; her iddia kaynaklı; REALITY/SPECULATION/FICTION.
4. 5–7 bölüm, her bölümde farklı 3D sahne dizisi (Dünya dalışı, `bolge` sınır/taşıma, gezegen, dişli, `foto`); somut görsel kuralı; düz slayt yok.
5. Ses: **resmî ses `kokoro:5` (Adam), hiz_carpani 1.0** — başka ses yasak (`marka/SES_RESMI_ADAM.md`). Miks: konuşma fonun ≥ 12 dB üstünde, −14 LUFS.
6. Kapanış zorunlu: konuya özel, tekrarsız "next" sorusu (anlatım + ekran + sabit yorum) + yorum rozeti + NØVEX kartı.
7. Paket: başlık + 2 alternatif, açıklama, bölümler (00:00, ≥3, her biri ≥10 sn), etiketler, hashtag, SRT, NARRATION, sabit yorum, kaynaklar + görsel lisanslar, 16:9 kapak, QC + REFERANS_QC; IG/TikTok tanıtım metni.
8. En az 20 kare referansla yan yana; teknik QC. "NØVEX videon hazır!" yalnız gerçek MP4 + QC geçtiyse; yoksa biten/kalan işi dürüstçe bildir, yarım işi commit et.
9. Kayıtlar güncellenir; `claude/kalite-standardi`'ye push (önce pull --rebase; force-push yok).
SINIRLAR: yayın/yükleme/zamanlama yok · ücretli servis/kredi yok · gizli bilgi yok (depo PUBLIC) · main'e dokunma · dosya silme yok · yapılmayanı yapılmış gibi raporlama.
