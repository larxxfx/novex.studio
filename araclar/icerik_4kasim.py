"""4 Kasım 2026 — dört Short'un üretim girdilerini yazar (tek seferlik içerik betiği; içerik JSON'larda yaşar, bu betik yalnız oluşturucu).
Kaynaklar 3 Kasım gecesi web aramasıyla doğrulandı (her klasörde 02_sources.md)."""
import json, os

DEPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LISANS = ("motor: piper en_US-ljspeech-high (rhasspy/piper-voices, MIT; Piper motoru MIT)\n"
          "veri: LJ Speech (keithito.com) — kamu malı; model kartı: 'trained from scratch' (lessac türevi değil)\n"
          "lisans_dogrulandi: evet (3 Kasım 2026; kaynak: HF rhasspy/piper-voices lisans etiketi + MODEL_CARD)\n"
          "emir_ses_onayi: bekliyor\n"
          "yayin_uygun: hayir\n"
          "not: lisans zinciri doğrulandı; Emir sesi dinleyip onaylayınca yayin_uygun alanı değiştirilir.\n")


def p(metin, **k): return dict(metin=metin, **k)
def c(duygu, parcalar, sonra=0.42, altyazi=None):
    d = dict(duygu=duygu, sonra=sonra, parcalar=parcalar)
    if altyazi: d["altyazi"] = altyazi
    return d


VIDEOLAR = {
# ------------------------------------------------------------------ 08:00 TARİH
"2026-11-04_0800_antikythera-mechanism": dict(
 uretim=dict(tarih="2026-11-04", slot="08:00", kategori="A History & Ancient Civilizations", mod="REALITY", ses_motoru="kokoro:5", hiz_carpani=1.0, ruh="gizem", ortam="okyanus"),
 performans=dict(bas_sessizlik=0.35, cumleler=[
  c("merak (kanca)", [p("In nineteen-oh-one, sponge divers pulled a lump of corroded bronze", hiz=1.0), p("from a Roman-era shipwreck.", hiz=1.04, once=0.12)], 0.5,
    altyazi="In 1901, sponge divers pulled a lump of corroded bronze from a Roman-era shipwreck."),
  c("şaşkınlık", [p("Inside it were gears.", hiz=1.15, kazanc_db=2.5, perde=-0.5)], 0.55),
  c("hayranlık", [p("At least thirty of them,", hiz=1.04, kazanc_db=1.0), p("cut by hand, more than two thousand years ago.", hiz=1.02, once=0.16)], 0.45,
    altyazi="At least 30 of them, cut by hand, more than 2,000 years ago."),
  c("açılım", [p("This is the Antikythera Mechanism.", soyle="This is the Anti-kythera Mechanism.", hiz=1.06, kazanc_db=2.0)], 0.45),
  c("keşif", [p("Turn a handle, and it showed the Sun, the Moon, and the planets,", hiz=1.0)], 0.2),
  c("hayranlık", [p("predicted eclipses,", hiz=1.02), p("and even tracked the dates of the Olympic Games.", hiz=1.04, kazanc_db=1.5, once=0.1)], 0.5),
  c("gizem", [p("Only about a third of it survived,", hiz=1.04, perde=-0.3), p("in eighty-two fragments.", hiz=1.08, once=0.14)], 0.42,
    altyazi="Only about a third of it survived, in 82 fragments."),
  c("güven / kanıt", [p("In twenty twenty-one, a team at University College London rebuilt its front display from X-ray scans.", hiz=1.0)], 0.45,
    altyazi="In 2021, a team at University College London rebuilt its front display from X-ray scans."),
  c("doruk", [p("Nothing this complex appears again", hiz=1.02), p("for more than a thousand years.", hiz=1.1, kazanc_db=2.5, once=0.22)], 0.6,
    altyazi="Nothing this complex appears again for more than 1,000 years."),
  c("soru / katılım", [p("So was it one of a kind,", hiz=1.02, perde=0.5), p("or the only one that survived?", hiz=1.08, kazanc_db=1.5, once=0.3)], 0.3),
 ]),
 plan=dict(dil="arsiv", doku="kagit", kamera="itme", kapanis_sn=2.2,
  palet=dict(zemin0="#1a120a", zemin1="#3b2814", vurgu="#d9a441", metin="#f2e3c4", ikincil="#a08a64", kara="#6b5436"),
  kapak=dict(ust="2,000 years old", ana="It had gears.", zemin_sahne=1),
  sahneler=[
   dict(cumle=1, tur="baslik", ust="1901 · Antikythera, Greece", ana="A lump of bronze from the sea", alt="Roman-era shipwreck"),
   dict(cumle=2, tur="sayi", bas=0, son=30, birim="BRONZE GEARS", etiket="at least 30 survive, cut by hand", sure=2.4),
   dict(cumle=4, tur="harita", bas_bolge=[-15, 25, 45, 50], bolge=[19, 33, 30, 41], noktalar=[[23.3, 35.87, "Antikythera"]], baslik="Found off Antikythera"),
   dict(cumle=5, tur="liste", baslik="What it calculated", maddeler=["The Sun", "The Moon & its phases", "The planets", "Eclipses", "Olympic Games dates"]),
   dict(cumle=7, tur="sayi", bas=0, son=82, birim="FRAGMENTS", etiket="only about a third survives", sure=1.8),
   dict(cumle=8, tur="alinti", metin="The first model that conforms to all the physical evidence.", kaynak="Prof. Tony Freeth, UCL, 2021"),
   dict(cumle=9, tur="zaman", baslik="The gap", olaylar=[["c. 100 BC", "Antikythera Mechanism"], ["1300s", "Astronomical clocks in Europe"]]),
   dict(cumle=10, tur="soru", metin="One of a kind, or the only survivor?", secenekler=["ONE", "MANY"]),
  ]),
 paket=dict(mod="REALITY", baslik="A 2,000-Year-Old Machine With Gears Inside",
  alternatif=["Divers Found a Computer in a Roman Shipwreck", "The Ancient Machine That Predicted Eclipses"],
  kapak_metni="It had gears.",
  aciklama="In 1901, sponge divers raised a corroded lump of bronze from a Roman-era shipwreck off the Greek island of Antikythera. Inside were gears: at least 30 survive, cut by hand more than 2,000 years ago.\n\nThe Antikythera Mechanism tracked the Sun, the Moon and the planets, predicted eclipses and even counted down to the Olympic Games. Only about a third of it survives, in 82 fragments. In 2021 a UCL team led by Tony Freeth published a reconstruction of its front display, built from X-ray CT data.\n\nWas it one of a kind, or just the only one that survived? Tell us below.\n\nSources: Freeth et al., \"A Model of the Cosmos in the ancient Greek Antikythera Mechanism\", Scientific Reports (2021); UCL News; Antikythera Mechanism Research Project.\nVisuals: original motion graphics (not archival footage). Narration: synthetic voice.",
  etiketler=["Antikythera mechanism", "ancient computer", "ancient Greece", "shipwreck discovery", "lost technology", "archaeology", "ancient astronomy", "Tony Freeth", "history facts", "NØVEX"],
  hashtag=["#history", "#archaeology", "#ancientgreece", "#antikythera", "#shorts"],
  sabit_yorum="Only a third of it survived. What do you think the missing two-thirds could do? 🤔\nAnd do you think the Greeks built more than one?",
  kaynaklar=["Freeth T. et al. (2021). A Model of the Cosmos in the ancient Greek Antikythera Mechanism. Scientific Reports 11, 5821.",
             "UCL News / ScienceDaily (12 Mar 2021): 30 surviving bronze gears, 82 fragments, eclipses, planets, Olympic Games dates.",
             "Sky & Telescope (Nov 2023): discovered 1900–1901 by sponge divers; at least 30 gears.",
             "Natural Earth (public domain) map data."],
  instagram=dict(kapak="Gears. 2,000 years ago.", aciklama="Sponge divers found it in a Roman-era shipwreck in 1901. Inside: at least 30 hand-cut bronze gears that predicted eclipses. 🌑⚙️ One of a kind, or the only survivor?",
                 hashtag=["#antikythera", "#archaeology", "#ancienthistory", "#history", "#reels"]),
  tiktok=dict(kapak="This is 2,000 years old ⚙️", aciklama="It predicted eclipses. One of a kind or the only survivor? 👇", hashtag=["#history", "#archaeology", "#ancientgreece", "#fyp"])),
 kaynak_md="""# Sources — Antikythera Mechanism (REALITY)
| # | Claim (narrated) | Source | Status |
|---|---|---|---|
| 1 | Found 1901 by sponge divers in a Roman-era shipwreck off Antikythera | UCL / ScienceDaily 2021; Sky & Telescope Nov 2023 (1900–1901) | ✅ |
| 2 | At least 30 bronze gears survive, hand-cut | ScienceDaily 2021 ("30 surviving bronze gears"); S&T 2023 | ✅ |
| 3 | More than 2,000 years old | Widely dated 2nd–1st c. BC (Freeth et al. 2021) | ✅ |
| 4 | Showed Sun, Moon, planets; predicted eclipses; Olympic Games dates | ScienceDaily 2021 | ✅ |
| 5 | About a third survives, in 82 fragments | ScienceDaily 2021 | ✅ |
| 6 | 2021 UCL reconstruction of front display from X-ray (CT) data | Freeth et al., Sci. Rep. 2021 | ✅ |
| 7 | Nothing this complex for 1,000+ years (European astronomical clocks, 14th c.) | Common scholarly statement (Freeth/Price); ⚠️ phrased as "appears again", not "existed" | ⚠️ |
| 8 | Quote "first model that conforms to all the physical evidence" | Freeth, UCL press release 2021 (ScienceDaily) | ✅ |
"""),
# ------------------------------------------------------------------ 12:00 DÜNYA / GİZEM
"2026-11-04_1200_lake-nyos": dict(
 uretim=dict(tarih="2026-11-04", slot="12:00", kategori="D Mysteries & Earth", mod="REALITY", ses_motoru="piper-ljspeech", hiz_carpani=1.0, ruh="gerilim", ortam="ruzgar"),
 performans=dict(bas_sessizlik=0.35, cumleler=[
  c("gerilim (kanca)", [p("On the night of August twenty-first, nineteen eighty-six,", hiz=1.02), p("a lake in Cameroon exhaled.", hiz=1.12, kazanc_db=2.5, perde=-0.6, once=0.3)], 0.55,
    altyazi="On the night of 21 August 1986, a lake in Cameroon exhaled."),
  c("gizem", [p("There was no fire.", hiz=1.06), p("No flood.", hiz=1.06, once=0.12), p("No explosion.", hiz=1.08, once=0.12)], 0.45),
  c("gizem / gerilim", [p("Just a silent cloud of carbon dioxide,", hiz=1.04, perde=-0.3), p("rising from the bottom of Lake Nyos.", soyle="rising from the bottom of Lake Nee-ohss.", hiz=1.04, once=0.12)], 0.45),
  c("gerilim", [p("The gas was heavier than air.", hiz=1.04, kazanc_db=1.5)], 0.35),
  c("gerilim", [p("It flowed down the valleys,", hiz=1.02), p("into the villages,", hiz=1.04, once=0.1), p("while people slept.", hiz=1.12, kazanc_db=1.5, perde=-0.4, once=0.18)], 0.6),
  c("doruk / hüzün", [p("By morning, one thousand seven hundred and forty-six people were dead,", hiz=1.04, kazanc_db=2.5), p("and three thousand five hundred animals.", hiz=1.04, once=0.15)], 0.6,
    altyazi="By morning, 1,746 people were dead, and 3,500 animals."),
  c("açıklama", [p("Volcanic gas had been slowly building up deep in the water,", hiz=1.0), p("until the lake could not hold it.", hiz=1.04, once=0.12)], 0.45),
  c("umut", [p("Today, pipes vent that gas safely,", hiz=1.0), p("shooting fountains high above the lake.", hiz=1.02, once=0.1)], 0.45),
  c("gizem", [p("And just two years earlier,", hiz=1.02), p("nearby Lake Monoun had done the same.", hiz=1.04, kazanc_db=2.0, once=0.15)], 0.55),
  c("soru / katılım", [p("Would you live beside a lake that can breathe?", hiz=1.04, perde=0.5)], 0.3),
 ]),
 plan=dict(dil="modern", doku="gren", kamera="kaydirma", kapanis_sn=2.2,
  palet=dict(zemin0="#04080b", zemin1="#0c1c21", vurgu="#5fe3b8", metin="#e6f2ee", ikincil="#7d9a94", kara="#1f3d3c"),
  kapak=dict(ust="1,746 dead", ana="The lake exhaled.", zemin_sahne=2),
  sahneler=[
   dict(cumle=1, tur="baslik", ust="21 August 1986 · Cameroon", ana="The lake that exhaled", alt="Lake Nyos"),
   dict(cumle=2, tur="liste", baslik="What happened", maddeler=["No fire", "No flood", "No explosion"]),
   dict(cumle=3, tur="harita", bas_bolge=[-20, -35, 55, 38], bolge=[5, 2, 16, 11], noktalar=[[10.30, 6.44, "Lake Nyos"]], baslik="North-west Cameroon"),
   dict(cumle=4, tur="karsilastir", baslik="Density vs. air", birim="×", ogeler=[["Air", 1.0], ["Carbon dioxide", 1.5]]),
   dict(cumle=6, tur="sayi", bas=0, son=1746, birim="PEOPLE", etiket="and 3,500 animals, in one night", sure=2.6),
   dict(cumle=8, tur="zaman", baslik="After", olaylar=[["1984", "Lake Monoun gas release"], ["1986", "Lake Nyos disaster"], ["2001", "First degassing pipe"], ["2011", "Two more pipes"]]),
   dict(cumle=10, tur="soru", metin="Would you live beside a lake that can breathe?", secenekler=["YES", "NO"]),
  ]),
 paket=dict(mod="REALITY", baslik="The Lake That Killed 1,746 People in One Night",
  alternatif=["A Lake in Cameroon Exhaled… and a Valley Went Silent", "No Fire, No Flood: The Lake Nyos Disaster"],
  kapak_metni="It exhaled.",
  aciklama="On the night of 21 August 1986, Lake Nyos in north-west Cameroon released a huge cloud of carbon dioxide. Heavier than air, the gas flowed down the valleys into sleeping villages. By morning 1,746 people and about 3,500 livestock were dead.\n\nScientists call it a limnic eruption: volcanic CO2 builds up in deep water until the lake can no longer hold it. Since 2001, degassing pipes have vented the gas safely. Two years earlier, nearby Lake Monoun had released gas too.\n\nWould you live beside a lake that can breathe?\n\nSources: Kling et al., Science (1987); USGS; BBC (21 Aug 1986); Kling et al., PNAS (2005).\nVisuals: original motion graphics. Narration: synthetic voice.",
  etiketler=["Lake Nyos", "limnic eruption", "Cameroon disaster", "carbon dioxide cloud", "natural disasters", "geology", "deadly lake", "1986", "earth facts", "NØVEX"],
  hashtag=["#lakenyos", "#naturaldisaster", "#geology", "#earth", "#shorts"],
  sabit_yorum="Pipes now vent the gas safely, but the cause is still in the ground. 🌋\nHave you ever heard of a lake that can kill without water? Tell us where.",
  kaynaklar=["Kling G. et al. (1987). The 1986 Lake Nyos Gas Disaster in Cameroon, West Africa. Science 236:169–175.",
             "USGS Cascades Volcano Observatory / USGS feature: at least 1,700 deaths, 3,500 livestock; Lake Monoun 1984.",
             "BBC On This Day, 21 Aug 1986.",
             "Kling G. et al. (2005). Degassing Lakes Nyos and Monoun: Defusing certain disaster. PNAS. (first pipe 2001; two more 2011)",
             "Natural Earth (public domain) map data."],
  instagram=dict(kapak="The lake exhaled.", aciklama="21 August 1986, Cameroon. No fire, no flood, no explosion — just an invisible cloud of CO2 rolling into sleeping villages. 1,746 people died. Would you live beside a lake that can breathe?",
                 hashtag=["#lakenyos", "#history", "#geology", "#earth", "#reels"]),
  tiktok=dict(kapak="A lake killed 1,746 people", aciklama="No fire. No flood. Just gas. Would you live near it? 👇", hashtag=["#lakenyos", "#disaster", "#geology", "#fyp"])),
 kaynak_md="""# Sources — Lake Nyos (REALITY)
| # | Claim | Source | Status |
|---|---|---|---|
| 1 | Night of 21 Aug 1986, Lake Nyos, Cameroon | Kling et al., Science 1987; BBC 1986 | ✅ |
| 2 | CO2 cloud; no fire/flood/explosion (asphyxiation) | USGS; Kling 1987 | ✅ |
| 3 | CO2 ~1.5× denser than air, flowed down valleys | Wikipedia (Kling 1987 cited) | ✅ |
| 4 | 1,746 dead, 3,500 livestock | Wikipedia/Kling; USGS ("at least 1,700", 3,500 livestock) | ✅ |
| 5 | Volcanic CO2 accumulated in deep water (limnic eruption) | USGS CVO | ✅ |
| 6 | Degassing pipes: first 2001, two more 2011 | Kling 2005 PNAS; secondary reports | ✅ |
| 7 | Lake Monoun gas release 1984 | USGS CVO | ✅ |
"""),
# ------------------------------------------------------------------ 16:00 UZAY
"2026-11-04_1600_venus-day-longer-than-year": dict(
 uretim=dict(tarih="2026-11-04", slot="16:00", kategori="C Space & Universe", mod="REALITY", ses_motoru="piper-ljspeech", hiz_carpani=1.0, ruh="hayranlik", ortam="uzay"),
 performans=dict(bas_sessizlik=0.35, cumleler=[
  c("şaşkınlık (kanca)", [p("On Venus,", hiz=1.04), p("a single day lasts longer than an entire year.", hiz=1.06, kazanc_db=2.5, once=0.22)], 0.55),
  c("merak", [p("Venus takes two hundred and twenty-five Earth days to orbit the Sun.", hiz=1.0)], 0.4,
    altyazi="Venus takes 225 Earth days to orbit the Sun."),
  c("açılım", [p("But it takes two hundred and forty-three Earth days", hiz=1.0), p("to spin around just once.", hiz=1.1, kazanc_db=2.0, once=0.15)], 0.5,
    altyazi="But it takes 243 Earth days to spin around just once."),
  c("hayranlık", [p("No planet in the solar system spins slower.", hiz=1.04)], 0.4),
  c("şaşkınlık", [p("And it spins backwards.", hiz=1.12, kazanc_db=2.0, perde=-0.4)], 0.45),
  c("merak", [p("So on Venus, the Sun rises in the west,", hiz=1.0), p("and sets in the east.", hiz=1.06, once=0.12)], 0.45),
  c("açıklama", [p("From one sunrise to the next takes about a hundred and seventeen Earth days.", hiz=1.02)], 0.4,
    altyazi="From one sunrise to the next takes about 117 Earth days."),
  c("hayranlık", [p("Just two sunrises", hiz=1.04, kazanc_db=1.5), p("in a whole Venus year.", hiz=1.06, once=0.12)], 0.45),
  c("gerilim", [p("Under clouds of sulfuric acid,", hiz=1.02, perde=-0.3), p("at around four hundred and sixty-five degrees Celsius.", hiz=1.06, kazanc_db=2.0, once=0.15)], 0.55,
    altyazi="Under clouds of sulfuric acid, at around 465 °C."),
  c("soru / katılım", [p("Could you survive a single day on Venus?", hiz=1.04, perde=0.5)], 0.3),
 ]),
 plan=dict(dil="modern", doku="yildiz", kamera="itme", kapanis_sn=2.2,
  palet=dict(zemin0="#070302", zemin1="#2a1206", vurgu="#ffb347", metin="#fff1dc", ikincil="#c08a5a", kara="#5a3418"),
  kapak=dict(ust="Venus", ana="Day > Year", zemin_sahne=2),
  sahneler=[
   dict(cumle=1, tur="baslik", ust="Venus", ana="A day longer than a year", alt="the slowest spin in the solar system"),
   dict(cumle=2, tur="sayi", bas=0, son=225, birim="EARTH DAYS", etiket="one Venus year (one orbit)", sure=2.0),
   dict(cumle=3, tur="karsilastir", baslik="Venus, in Earth days", birim="days", ogeler=[["One year (orbit)", 225], ["One day (spin)", 243]]),
   dict(cumle=5, tur="baslik", ust="Retrograde rotation", ana="It spins backwards", alt="Sun rises in the west"),
   dict(cumle=7, tur="sayi", bas=0, son=117, birim="EARTH DAYS", etiket="sunrise to sunrise", sure=2.0),
   dict(cumle=9, tur="sayi", bas=0, son=465, birim="°C", etiket="surface, under sulfuric acid clouds", sure=2.0),
   dict(cumle=10, tur="soru", metin="Could you survive a single day on Venus?", secenekler=["YES", "NO"]),
  ]),
 paket=dict(mod="REALITY", baslik="On Venus, a Day Is Longer Than a Year",
  alternatif=["The Planet Where the Sun Rises in the West", "Venus Spins Backwards (And Very Slowly)"],
  kapak_metni="Day > Year",
  aciklama="Venus orbits the Sun in about 225 Earth days, but needs about 243 Earth days to spin once on its axis. So a Venus day (one rotation) is longer than its year.\n\nIt also spins backwards (retrograde), so the Sun rises in the west and sets in the east. Combined with its orbit, sunrise to sunrise takes about 117 Earth days: just two sunrises per Venus year, under sulfuric acid clouds at around 465 °C.\n\nCould you survive a single day on Venus?\n\nSources: NASA Science, Venus Facts; NASA Space Place; Universe Today.\nVisuals: original motion graphics. Narration: synthetic voice.",
  etiketler=["Venus", "day longer than year", "retrograde rotation", "solar system facts", "space facts", "planets", "astronomy", "NASA", "science shorts", "NØVEX"],
  hashtag=["#venus", "#space", "#astronomy", "#solarsystem", "#shorts"],
  sabit_yorum="A sunrise every 117 Earth days… 🌅 What would you do with a 'day' that long?",
  kaynaklar=["NASA Science — Venus: Facts (rotation ~243 Earth days, year ~225 Earth days, retrograde, ~465 °C / 900 °F, sulfuric acid clouds).",
             "NASA Space Place — How long is a year on other planets? (Venus 225 days).",
             "Universe Today — Rotation of Venus (243.025 days; slowest of any planet; solar day 116.75 days)."],
  instagram=dict(kapak="Day > Year", aciklama="On Venus a day (243 Earth days) lasts longer than a year (225). It spins backwards, so the Sun rises in the west. ☀️ Could you survive one Venus day?",
                 hashtag=["#venus", "#space", "#astronomy", "#science", "#reels"]),
  tiktok=dict(kapak="A day longer than a year?!", aciklama="Venus breaks the rules. Could you survive one day there? 👇", hashtag=["#space", "#venus", "#science", "#fyp"])),
 kaynak_md="""# Sources — Venus (REALITY)
| # | Claim | Source | Status |
|---|---|---|---|
| 1 | Year ≈ 225 Earth days | NASA Space Place / NASA Science | ✅ |
| 2 | Sidereal rotation ≈ 243 Earth days → day longer than year | NASA Science; Universe Today (243.025) | ✅ |
| 3 | Slowest rotation of any planet | Universe Today | ✅ |
| 4 | Retrograde rotation; Sun rises in the west | NASA Science | ✅ |
| 5 | Solar day ≈ 117 Earth days; two sunrises per Venus year | Universe Today (116.75); Snopes citing NASA | ✅ |
| 6 | Sulfuric acid clouds; surface ≈ 465 °C | NASA Science — Venus Facts | ✅ |
"""),
# ------------------------------------------------------------------ 20:00 WHAT IF
"2026-11-04_2000_what-if-gibraltar-closed": dict(
 uretim=dict(tarih="2026-11-04", slot="20:00", kategori="G What If Scenarios", mod="SPECULATION", ses_motoru="piper-ljspeech", hiz_carpani=1.0, ruh="epik", ortam="okyanus"),
 performans=dict(bas_sessizlik=0.35, cumleler=[
  c("merak (kanca)", [p("What if someone closed the Strait of Gibraltar", hiz=1.0), p("tomorrow?", hiz=1.12, kazanc_db=2.0, perde=0.4, once=0.15)], 0.5),
  c("keşif", [p("It's only about thirteen kilometers wide,", hiz=1.02), p("but it keeps the Mediterranean alive.", hiz=1.04, kazanc_db=1.5, once=0.12)], 0.42,
    altyazi="It's only about 13 kilometers wide, but it keeps the Mediterranean alive."),
  c("açıklama", [p("The sea loses more water to evaporation than its rivers bring in.", hiz=1.0)], 0.42),
  c("gerilim", [p("Cut off from the Atlantic,", hiz=1.02, perde=-0.3), p("its level would fall by up to a meter every year.", hiz=1.04, kazanc_db=1.5, once=0.12)], 0.45,
    altyazi="Cut off from the Atlantic, its level would fall by up to 1 meter every year."),
  c("gerilim", [p("In about a thousand years,", hiz=1.04), p("most of it would be gone.", hiz=1.1, kazanc_db=2.5, perde=-0.5, once=0.2)], 0.5,
    altyazi="In about 1,000 years, most of it would be gone."),
  c("hayranlık", [p("A salt desert,", hiz=1.04), p("kilometers below sea level.", hiz=1.06, once=0.12)], 0.5),
  c("açılım", [p("And this isn't just a thought experiment.", hiz=1.02), p("It happened, about six million years ago.", hiz=1.06, kazanc_db=2.0, once=0.18)], 0.5),
  c("epik", [p("Then the Atlantic broke back through,", hiz=1.02, kazanc_db=1.0), p("in what may have been the biggest flood in Earth's history.", hiz=1.04, once=0.12)], 0.4),
  c("hayranlık", [p("Refilling most of the sea in as little as two years.", hiz=1.04, kazanc_db=1.5)], 0.55),
  c("soru / katılım", [p("Would you walk across the dry Mediterranean?", hiz=1.04, perde=0.5)], 0.3),
 ]),
 plan=dict(dil="daktilo", doku="gren", kamera="kaydirma", kapanis_sn=2.2,
  palet=dict(zemin0="#06141d", zemin1="#1c3a4b", vurgu="#f2c14e", metin="#f4f1ea", ikincil="#8fb3c4", kara="#c9b48a"),
  kapak=dict(ust="What if…", ana="Gibraltar closes?", zemin_sahne=1),
  sahneler=[
   dict(cumle=1, tur="baslik", ust="What if · a thought experiment", ana="Close the Strait of Gibraltar", alt="scenario, not prediction"),
   dict(cumle=2, tur="harita", bas_bolge=[-20, 20, 45, 52], bolge=[-9.5, 33.5, -2.5, 38.5], noktalar=[[-5.6, 35.95, "Strait of Gibraltar"]], baslik="~13 km wide"),
   dict(cumle=3, tur="karsilastir", baslik="Water budget (schematic)", birim="", ogeler=[["Rivers + rain in", 1], ["Evaporation out", 2]]),
   dict(cumle=4, tur="sayi", bas=0, son=1, birim="METER / YEAR", etiket="up to ~1 m fall per year (estimates 0.5–1 m)", sure=1.6),
   dict(cumle=5, tur="sayi", bas=0, son=1000, birim="YEARS", etiket="to lose most of the sea", sure=2.2),
   dict(cumle=6, tur="harita", bas_bolge=[-10, 28, 40, 47], bolge=[-6, 30, 37, 46], baslik="Salt desert, 3–5 km deep", yakinlas=False),
   dict(cumle=7, tur="zaman", baslik="It already happened", olaylar=[["5.96 Ma", "Gateway closes"], ["~5.6 Ma", "Sea nearly dry"], ["5.33 Ma", "Zanclean flood"]]),
   dict(cumle=10, tur="soru", metin="Would you walk across the dry Mediterranean?", secenekler=["YES", "NO"]),
  ]),
 paket=dict(mod="SPECULATION", baslik="What If the Strait of Gibraltar Closed?",
  alternatif=["The Mediterranean Would Disappear in 1,000 Years", "It Already Happened: When the Mediterranean Dried Up"],
  kapak_metni="1,000 years.",
  aciklama="A thought experiment, not a prediction: what if the Strait of Gibraltar closed?\n\nThe Mediterranean loses more water to evaporation than its rivers bring in; the Atlantic makes up the difference through a gap only about 13 km wide. Cut it off and the sea level would drop by roughly half a metre to a metre a year, leaving a salt desert kilometres below sea level within about a thousand years.\n\nIt has happened before: in the Messinian Salinity Crisis (5.96–5.33 million years ago) the Mediterranean largely dried out, until the Zanclean flood refilled most of it in as little as two years.\n\nWould you walk across the dry Mediterranean?\n\nSources: Aloisi et al., Nature Communications (2024); Garcia-Castellanos et al. (2020); Encyclopaedia Britannica — Strait of Gibraltar.\nScenario segments are hypothetical. Visuals: original motion graphics. Narration: synthetic voice.",
  etiketler=["Strait of Gibraltar", "Mediterranean dries up", "Messinian salinity crisis", "Zanclean flood", "what if", "geography", "earth science", "thought experiment", "NØVEX"],
  hashtag=["#whatif", "#mediterranean", "#geography", "#earthscience", "#shorts"],
  sabit_yorum="This really happened ~6 million years ago. 🌊 If it happened again, which coast would you visit first: the old shoreline or the new salt floor?",
  kaynaklar=["Aloisi G. et al. (2024). Nature Communications — two-phase Messinian Salinity Crisis; ~70% water loss; today ~0.5 m/yr drop if isolated (ScienceAlert summary).",
             "Garcia-Castellanos D. et al. (2020). Earth-Science Reviews — Zanclean megaflood; most refilling within ~2 years.",
             "Messinian Salinity Crisis 5.96–5.33 Ma; near-desiccation within ~1,000 years; basin 3–5 km below sea level (Wikipedia, citing Hsü et al.).",
             "Encyclopaedia Britannica — Strait of Gibraltar (~13 km at narrowest)."],
  instagram=dict(kapak="What if Gibraltar closed?", aciklama="Close a 13 km gap and the Mediterranean starts to vanish — about a thousand years to a salt desert. And it already happened 6 million years ago. 🌊 Would you walk across it?",
                 hashtag=["#whatif", "#mediterranean", "#geography", "#science", "#reels"]),
  tiktok=dict(kapak="What if Gibraltar closed? 🌊", aciklama="The Mediterranean would dry up… and it already did once. Would you walk across? 👇", hashtag=["#whatif", "#geography", "#science", "#fyp"])),
 kaynak_md="""# Sources — What if Gibraltar closed? (SPECULATION; historical part REALITY)
| # | Claim | Source | Status |
|---|---|---|---|
| 1 | Strait ≈ 13 km at narrowest | Britannica; Big Think ("about 8 miles") | ✅ |
| 2 | Evaporation exceeds river input; Atlantic inflow replenishes | ScienceABC; Britannica | ✅ |
| 3 | If isolated, level falls ~0.5–1 m/yr | Aloisi et al. 2024 (via ScienceAlert ~0.5 m); ScienceABC (~1 m) — narrated "up to a meter" | ✅ |
| 4 | Mostly gone in ~1,000 years | Wikipedia (Messinian), Big Think | ✅ |
| 5 | Basin 3–5 km below sea level | Wikipedia; Big Think | ✅ (on screen) / "kilometers" narrated |
| 6 | Happened ~6 Ma (5.96–5.33 Ma) | Wikipedia; Nature Comms 2024 | ✅ |
| 7 | Zanclean flood possibly largest flood in Earth history | Big Think ("quite possibly the largest") — narrated "may have been" | ✅ |
| 8 | Refilled most of the sea in as little as two years | Garcia-Castellanos 2020; The National 2024 | ✅ |
| — | Closing the strait "tomorrow" | Hypothetical framing, labelled WHAT IF on screen and in description | SPECULATION |
"""),
}

for ad, v in VIDEOLAR.items():
    k = os.path.join(DEPO, "videolar", ad); os.makedirs(os.path.join(k, "ses"), exist_ok=True)
    for f, d in (("uretim.json", v["uretim"]), ("anlatim_performans.json", v["performans"]), ("sahne_plani.json", v["plan"]), ("paket.json", v["paket"])):
        json.dump(d, open(os.path.join(k, f), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(os.path.join(k, "02_sources.md"), "w", encoding="utf-8").write(v["kaynak_md"])
    open(os.path.join(k, "ses", "LISANS.txt"), "w", encoding="utf-8").write(LISANS)
    pl = v["plan"]
    open(os.path.join(k, "GORSEL_YON.md"), "w", encoding="utf-8").write(
        f"# Görsel yön — {v['paket']['baslik']}\n- Dil/tipografi: **{pl['dil']}** · doku: {pl['doku']} · kamera: {pl['kamera']}\n"
        f"- Palet: {', '.join(f'{a} {b}' for a, b in pl['palet'].items())}\n- Sahneler: {', '.join(s['tur'] for s in pl['sahneler'])}\n"
        f"- Ses: ruh={v['uretim']['ruh']}, ortam={v['uretim']['ortam']}\n- Tekrar kontrolü: `strateji/GORSEL_KAYIT.md` (küre estetiği kullanılmadı).\n")
    print("✓", ad)
