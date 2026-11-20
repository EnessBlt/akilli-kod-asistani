import json
import urllib.error
import urllib.request
import streamlit as st

st.set_page_config(
    page_title="Akıllı Kod Asistanı & Konu Özetleyici",
    page_icon="✨",
    layout="centered",
)

# Özel Mor - Mavi - Cam Göbeği - Yeşil Koyu Tema Stili
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #12102E 0%, #07111A 55%, #061A17 100%);
        color: #F8FAFC;
    }
    .hero-box {
        background: linear-gradient(135deg, rgba(168,85,247,0.16), rgba(59,130,246,0.16), rgba(6,182,212,0.16), rgba(16,185,129,0.16));
        border: 1px solid #2A3F6E;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #A855F7, #3B82F6, #06B6D4, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #22D3EE;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #A855F7, #3B82F6, #06B6D4, #10B981);
        color: #06111A;
        font-weight: 800;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.5rem;
        width: 100%;
        transition: 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        opacity: 0.92;
        transform: translateY(-1px);
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #0E1B2B !important;
        color: #F8FAFC !important;
        border: 1px solid #1E4E68 !important;
        border-radius: 10px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #06B6D4 !important;
        box-shadow: 0 0 0 1px #10B981 !important;
    }
    label, .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #34D399 !important;
        font-weight: 600 !important;
    }
    .output-card {
        background-color: #0E1B2B;
        border: 1px solid #0D9488;
        border-radius: 14px;
        padding: 18px;
        margin-top: 12px;
    }
    </style>
    <div class="hero-box">
        <p class="hero-title">Akıllı Kod Asistanı & Konu Özetleyici</p>
        <p class="hero-sub">Yapay Zeka Destekli Kod Analizi, Hata Ayıklama ve Metin Özetleme Aracı</p>
    </div>
    """,
    unsafe_allow_html=True,
)

MODELS = {
    "Gemini 3.8 Flash (Hızlı & Güncel - Önerilen)": "gemini-3.8-flash",
    "Gemini 3.8 Pro (Gelişmiş Kodlama & Analiz)": "gemini-3.8-pro",
    "Gemini 2.5 Flash (Klasik Hızlı)": "gemini-2.5-flash",
    "Gemini 2.5 Pro (Klasik Pro)": "gemini-2.5-pro",
}

MODES = {
    "Metin / Konu Özetle": (
        "Sen uzman bir içerik özetleyicisin. Verilen metni veya ders konusunu "
        "ana fikirlerini kaybetmeden, açık, anlaşılır ve Türkçe madde işaretleri halinde özetle."
    ),
    "Kodu Açıkla": (
        "Sen deneyimli bir yazılım eğitmenisin. Verilen programlama kodunu "
        "ne işe yaradığını, adım adım çalışma mantığını ve önemli kısımlarını sade bir Türkçe ile açıkla."
    ),
    "Hataları Bul ve Düzelt": (
        "Sen kıdemli bir yazılım geliştiricisin. Verilen koddaki sözdizimi (syntax) ve mantık hatalarını bul, "
        "hataların neden kaynaklandığını Türkçe açıkla ve ardından düzeltilmiş tam kodu paylaş."
    ),
}


def call_gemini(api_key: str, model: str, system_prompt: str, user_text: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_text}]}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"API Hatası ({e.code}): {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Bağlantı hatası: {e}")


# Ayarlar Bölümü
col1, col2 = st.columns([3, 2])
with col1:
    api_key = st.text_input(
        "Gemini API Anahtarı",
        type="password",
        placeholder="AIzaSy...",
        help="Anahtar yalnızca bu oturumda bellekte tutulur.",
    )
with col2:
    selected_model_label = st.selectbox("Yapay Zeka Modeli", list(MODELS.keys()))

selected_mode = st.selectbox("İşlem Türü", list(MODES.keys()))

user_input = st.text_area(
    "Metninizi veya Kodunuzu Buraya Yapıştırın",
    height=220,
    placeholder="Özetlenecek ders notunu ya da açıklanacak / hatası düzeltilecek kodu girin...",
)

if st.button("✨ Analiz Et / Oluştur"):
    if not api_key.strip():
        st.warning("Lütfen AIzaSy... ile başlayan Gemini API anahtarınızı girin.")
    elif not user_input.strip():
        st.warning("Lütfen özetlenecek metni veya analiz edilecek kodu yapıştırın.")
    else:
        model_id = MODELS[selected_model_label]
        with st.spinner(f"{selected_model_label} yanıt hazırlıyor..."):
            try:
                result = call_gemini(
                    api_key.strip(),
                    model_id,
                    MODES[selected_mode],
                    user_input.strip(),
                )
                st.success(f"Tamamlandı · Kullanılan Model: {model_id}")
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as ex:
                st.error(str(ex))