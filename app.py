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
        "Sözcü Magazin": "https://www.sozcu.com.tr/rss/magazin.xml"
    }
}

# ----------------- FONKSİYONLAR -----------------

def get_news(secilen_kaynaklar):
    haberler = []
    for kategori, kaynak in secilen_kaynaklar:
        url = rss_sources[kategori][kaynak]
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            tarih = entry.get("published_parsed") or entry.get("updated_parsed")
            yayin_tarihi = datetime.datetime(*tarih[:6]) if tarih else None

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
    if secilen_filtre == "Hepsi" or not haberler:
        return haberler
        
    bugun = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    filtered_haberler = []
    for haber in haberler:
        if not haber["date"]:
            continue
            
        haber_tarihi = haber["date"].replace(hour=0, minute=0, second=0, microsecond=0)
        
        if secilen_filtre == "Bugün":
            if haber_tarihi == bugun:
                filtered_haberler.append(haber)
        elif secilen_filtre == "Son 3 Gün":
            ucgun = bugun - datetime.timedelta(days=3)
            if haber_tarihi >= ucgun:
                filtered_haberler.append(haber)
        elif secilen_filtre == "Bu Hafta":
            baslangic = bugun - datetime.timedelta(days=bugun.weekday())
            if haber_tarihi >= baslangic:
                filtered_haberler.append(haber)
                
    return filtered_haberler

def arama_filtrele(haberler, arama_terimi):
    if not arama_terimi:
        return haberler
        
    arama_terimi = arama_terimi.lower().strip()
    filtered_haberler = []
    
    for haber in haberler:
        baslik = haber["title"].lower()
        ozet = haber["summary"].lower()
        
        # Tam kelime eşleşmesi için
        arama_kelimeleri = arama_terimi.split()
        if all(kelime in baslik or kelime in ozet for kelime in arama_kelimeleri):
            filtered_haberler.append(haber)
            
    return filtered_haberler

# ----------------- TASARIM -----------------

st.set_page_config(page_title="Haber Uygulaması", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* Ana tema renkleri */
        :root {
            --primary-color: #1E88E5;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #2c3e50;
        }

        /* Genel stil */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        /* Başlık stili */
        h1 {
            color: var(--primary-color);
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            padding: 1rem 0;
            text-align: center;
            border-bottom: 2px solid #eee;
            margin-bottom: 2rem;
            font-size: clamp(1.5rem, 4vw, 2.5rem);
        }

        /* Responsive container */
        @media (max-width: 768px) {
            .main-container {
                padding: 0.5rem;
            }
            
            .news-card {
                margin: 0.5rem 0;
                padding: 1rem;
            }
            
            .stButton > button {
                width: 100%;
                margin: 0.25rem 0;
            }
        }

        /* Multiselect ve selectbox stilleri */
        .stMultiSelect, .stSelectbox {
            background-color: var(--card-background);
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            max-width: 100%;
        }

        /* Buton stilleri */
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .stButton > button:hover {
            background-color: #1976D2;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transform: translateY(-1px);
        }

        /* Haber kartı stili */
        .news-card {
            background-color: var(--card-background);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            border: 1px solid #eee;
            transition: transform 0.2s ease;
        }

        .news-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .news-card h3 {
            font-size: clamp(1rem, 3vw, 1.25rem);
            margin-bottom: 0.5rem;
            color: var(--text-color);
        }

        .news-card p {
            font-size: clamp(0.875rem, 2vw, 1rem);
            line-height: 1.5;
        }

        .news-card small {
            font-size: clamp(0.75rem, 1.5vw, 0.875rem);
            color: #666;
        }

        /* Arama kutusu stili */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #eee;
            padding: 0.5rem 1rem;
            font-size: clamp(0.875rem, 2vw, 1rem);
            width: 100%;
        }

        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
        }

        /* Sidebar stili */
        .css-1d391kg {
            background-color: var(--card-background);
            padding: 1rem;
            border-right: 1px solid #eee;
        }

        /* Favori haberlerin stili */
        .favorite-news {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            border-left: 4px solid var(--primary-color);
        }

        .favorite-news h4 {
            font-size: clamp(0.875rem, 2vw, 1rem);
            margin-bottom: 0.5rem;
        }

        /* Kategori başlıkları */
        .category-title {
            font-size: clamp(1rem, 2.5vw, 1.25rem);
            color: var(--primary-color);
            margin: 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #eee;
        }

        /* Link stilleri */
        a {
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.2s ease;
        }

        a:hover {
            color: #1976D2;
            text-decoration: underline;
        }

        /* Bilgi mesajları */
        .stAlert {
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown("<h1>📰 Kişisel Haber Akışınız</h1>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;'>
        <h4>⚠️ Portfolio Project Disclaimer</h4>
        <p>This is a portfolio project created for demonstration purposes only. 
        It showcases full-stack development capabilities using Streamlit and Python.</p>
        <p>All news content is sourced from publicly available RSS feeds and belongs to their respective owners. 
        This application is not intended for commercial use.</p>
        <p>For more information about this portfolio project, please visit the GitHub repository.</p>
    </div>
""", unsafe_allow_html=True)

# Favori haberleri session state'den al
favoriler = st.session_state.get("favoriler", [])

# Mobil uyumlu layout
if st.session_state.get("mobile_view", True):
    # Tek sütun layout - mobil için
    st.markdown("### 🔍 Filtreleme ve Arama")
    secilen_kategoriler = st.multiselect("📂 Kategorileri seçin:", list(rss_sources.keys()),
                                        default=st.session_state.get("kategoriler", []))
    
    tarih_filtre = st.selectbox("⏳ Tarih filtresi:", ["Hepsi", "Bugün", "Son 3 Gün", "Bu Hafta"])
    arama = st.text_input("🔍 Arama yapın...")
else:
    # İki sütunlu layout - masaüstü için
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🔍 Filtreleme ve Arama")
        secilen_kategoriler = st.multiselect("📂 Kategorileri seçin:", list(rss_sources.keys()),
                                            default=st.session_state.get("kategoriler", []))
    with col2:
        st.markdown("### ⚙️ Ayarlar")
        tarih_filtre = st.selectbox("⏳ Tarih filtresi:", ["Hepsi", "Bugün", "Son 3 Gün", "Bu Hafta"])
        arama = st.text_input("🔍 Arama yapın...")

# Görünüm değiştirme butonu
if st.button("🔄 Görünümü Değiştir"):
    st.session_state["mobile_view"] = not st.session_state.get("mobile_view", True)
    st.rerun()

# Kaynak seçimi
if secilen_kategoriler:
    st.markdown('<div class="category-title">📰 Haber Kaynakları</div>', unsafe_allow_html=True)
    
    # Mobil görünümde tek sütun, masaüstünde çoklu sütun
    if st.session_state.get("mobile_view", True):
        cols = [st.container()]
    else:
        cols = st.columns(min(len(secilen_kategoriler), 3))  # En fazla 3 sütun
    
    secilen_kaynaklar = []
    for idx, kategori in enumerate(secilen_kategoriler):
        with cols[idx % len(cols)]:
            st.markdown(f"**{kategori}**")
            kaynaklar = list(rss_sources[kategori].keys())
            secilen = st.multiselect(f"🔹 Kaynaklar", kaynaklar,
                                   default=st.session_state.get(f"{kategori}_kaynaklar", kaynaklar),
                                   key=f"kaynak_{kategori}")
            secilen_kaynaklar.extend([(kategori, kaynak) for kaynak in secilen])

    # Session state güncelleme
    st.session_state["kategoriler"] = secilen_kategoriler
    for kategori in secilen_kategoriler:
        st.session_state[f"{kategori}_kaynaklar"] = [k[1] for k in secilen_kaynaklar if k[0] == kategori]

    # Haberleri çek ve göster
    with st.spinner("📡 Haberler yükleniyor..."):
        haberler = get_news(secilen_kaynaklar)

    # Önce tarih filtreleme
    haberler = [h for h in haberler if h["date"]]  # Tarihi olmayan haberleri filtrele
    haberler = tarih_filtrele(haberler, tarih_filtre)
    
    # Sonra arama filtreleme
    if arama:
        haberler = arama_filtrele(haberler, arama)

    if haberler:
        st.markdown("### 📄 Haberler")
        for haber in haberler:
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <h3>{haber['title']}</h3>
                    <p><small>📍 {haber['kategori']} | 📰 {haber['kaynak']} | 🕒 {haber['date'].strftime('%d.%m.%Y %H:%M')}</small></p>
                    <p>{haber['summary'][:200]}...</p>
                    <a href="{haber['link']}" target="_blank">🔗 Haberin Devamı için {haber['kaynak']} sitesini ziyaret edin</a>
                    <p><small>© {haber['kaynak']} - Tüm hakları saklıdır.</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                if not any(f["link"] == haber["link"] for f in favoriler):
                    if st.button(f"⭐ Beğen", key=haber['link']):
                        favoriler.append(haber)
                        st.session_state["favoriler"] = favoriler
                else:
                    st.success("✅ Favorilere eklendi")
    else:
        st.info("📌 Hiç haber bulunamadı.")
else:
    st.info("📌 Lütfen yukarıdan bir kategori ve kaynak seçin.")

# Favoriler sidebar'ı
if favoriler:
    with st.sidebar:
        st.markdown("### ⭐ Favori Haberleriniz")
        for f in favoriler:
            st.markdown(f"""
            <div class="favorite-news">
                <h4>{f['title']}</h4>
                <a href="{f['link']}" target="_blank">🔗 Habere Git</a>
            </div>
            """, unsafe_allow_html=True)
