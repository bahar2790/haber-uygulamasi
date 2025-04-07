import streamlit as st
import feedparser
import datetime

# ----------------- VERİ -----------------

rss_sources = {
    "Gündem": {
        "Hürriyet": "https://www.hurriyet.com.tr/rss/anasayfa",
        "Milliyet": "https://www.milliyet.com.tr/rss/rssNew/anasayfa.xml",
        "TRT Haber": "https://www.trthaber.com/anasayfa.rss",
        "NTV": "https://www.ntv.com.tr/rss",
        "Sözcü": "https://www.sozcu.com.tr/rss/son-dakika.xml"
    },
    "Ekonomi": {
        "Hürriyet Ekonomi": "https://www.hurriyet.com.tr/rss/ekonomi",
        "Dünya Gazetesi": "https://www.dunya.com/rss/rss.xml",
        "TRT Ekonomi": "https://www.trthaber.com/ekonomi.rss"
    },
    "Spor": {
        "TRT Spor": "https://www.trtspor.com.tr/rss/anasayfa.xml",
        "Fanatik": "https://www.fanatik.com.tr/rss/anasayfa",
        "HaberTürk Spor": "https://www.haberturk.com/rss/spor.xml"
    },
    "Teknoloji": {
        "DonanımHaber": "https://www.donanimhaber.com/rss/tumhaberler.xml",
        "Webtekno": "https://www.webtekno.com/rss.xml",
        "Webrazzi": "https://www.webrazzi.com/feed",
        "ShiftDelete": "https://www.shiftdelete.net/feed"
    },
    "Magazin": {
        "Milliyet Magazin": "https://www.milliyet.com.tr/rss/rssNew/magazin.xml",
        "Sözcü Magazin": "https://www.sozcu.com.tr/rss/magazin.xml",
        "Onedio Magazin": "https://onedio.com/rss/magazin.xml"
    }
}

# ----------------- UI -----------------

st.set_page_config(page_title="Haber Uygulaması", layout="centered")
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp {
            background-image: linear-gradient(to right top, #e3f2fd, #fce4ec);
            background-size: cover;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5em 1em;
            border-radius: 10px;
            border: none;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 1px solid #ccc;
        }
        .css-1cpxqw2 {
            background-color: rgba(255,255,255,0.7) !important;
            padding: 1em;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)


st.title("📰 Kişisel Haber Uygulaması")

# Tema seçimi
tema = st.radio("🎨 Tema seçin:", ["Açık", "Koyu"])
if tema == "Koyu":
    st.markdown("<style>body { background-color: #121212; color: white; }</style>", unsafe_allow_html=True)

# Kategori ve kaynak seçimi
secilen_kategoriler = st.multiselect("📂 Kategorileri seçin:", list(rss_sources.keys()),
                                     default=st.session_state.get("kategoriler", []))

secilen_kaynaklar = []
for kategori in secilen_kategoriler:
    kaynaklar = list(rss_sources[kategori].keys())
    secilen = st.multiselect(f"🔹 {kategori} kaynakları:", kaynaklar,
                             default=st.session_state.get(f"{kategori}_kaynaklar", kaynaklar))
    secilen_kaynaklar.extend([(kategori, kaynak) for kaynak in secilen])

# Arama kutusu
arama = st.text_input("🔍 Belirli bir kelimeyle arama yapabilirsiniz (isteğe bağlı):")

# Tarih filtresi
tarih_filtre = st.selectbox("⏳ Tarih filtresi:", ["Hepsi", "Bugün", "Son 3 Gün", "Bu Hafta"])

# ----------------- HABER ÇEKME -----------------

favoriler = st.session_state.get("favoriler", [])

def get_news(secilen_kaynaklar):
    haberler = []
    for kategori, kaynak in secilen_kaynaklar:
        url = rss_sources[kategori][kaynak]
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            tarih = entry.get("published_parsed")
            if tarih:
                yayin_tarihi = datetime.datetime(*tarih[:6])
            else:
                yayin_tarihi = None

            haber = {
                "kategori": kategori,
                "kaynak": kaynak,
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
                "date": yayin_tarihi
            }
            haberler.append(haber)
    return haberler

def tarih_filtrele(haberler, secilen_filtre):
    if secilen_filtre == "Hepsi":
        return haberler
    bugun = datetime.datetime.now()
    if secilen_filtre == "Bugün":
        return [h for h in haberler if h["date"] and h["date"].date() == bugun.date()]
    elif secilen_filtre == "Son 3 Gün":
        ucgun = bugun - datetime.timedelta(days=3)
        return [h for h in haberler if h["date"] and h["date"] >= ucgun]
    elif secilen_filtre == "Bu Hafta":
        baslangic = bugun - datetime.timedelta(days=bugun.weekday())
        return [h for h in haberler if h["date"] and h["date"] >= baslangic]
    return haberler

# ----------------- GÖSTER -----------------

if secilen_kaynaklar:
    st.session_state["kategoriler"] = secilen_kategoriler
    for k in secilen_kategoriler:
        st.session_state[f"{k}_kaynaklar"] = [i[1] for i in secilen_kaynaklar if i[0] == k]

    haberler = get_news(secilen_kaynaklar)

    if arama:
        haberler = [h for h in haberler if arama.lower() in h["title"].lower() or arama.lower() in h["summary"].lower()]

    haberler = tarih_filtrele(haberler, tarih_filtre)

    if haberler:
        st.subheader("🗞️ Haberler")
        for haber in haberler:
            st.markdown(f"### {haber['title']}")
            st.caption(f"📍 {haber['kategori']} | 📰 {haber['kaynak']}")
            st.write(haber["summary"][:200] + "...")
            st.markdown(f"[🔗 Haberi Oku]({haber['link']})")

            if st.button(f"⭐ Beğen - {haber['title']}", key=haber['title']):
                favoriler.append(haber)
                st.session_state["favoriler"] = favoriler

            st.markdown("---")
    else:
        st.warning("Hiç haber bulunamadı.")
else:
    st.info("Lütfen kategori ve kaynak seçin.")

# ----------------- FAVORİLER -----------------

if favoriler:
    st.sidebar.header("⭐ Favori Haberler")
    for f in favoriler:
        st.sidebar.write(f"📌 {f['title']}")
        st.sidebar.markdown(f"[🔗 Oku]({f['link']})")
