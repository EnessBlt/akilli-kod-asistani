import json
import time
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
        margin-bottom: 14px;
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
    .api-link-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        background-color: rgba(14, 27, 43, 0.85);
        border: 1px solid #1E4E68;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 18px;
        font-size: 13px;
        color: #CBD5E1;
    }
    .api-link-box a {
        color: #38BDF8;
        font-weight: 700;
        text-decoration: none;
    }
    .api-link-box a:hover {
        text-decoration: underline;
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
    <div class="api-link-box">
        <span>🔑 API anahtarınız yok mu? Google hesabınızla ücretsiz oluşturabilirsiniz:</span>
        <a href="https://aistudio.google.com/apikey" target="_blank">Ücretsiz API Anahtarı Al (Google AI Studio) ↗</a>
    </div>
    """,
    unsafe_allow_html=True,
)

MODELS = {
    "Otomatik (En Uygun Aktif Modeli Seç - Önerilen)": "auto",
    "Gemini 3.8 Flash (Hızlı & Güncel)": "gemini-3.8-flash",
    "Gemini 3.8 Flash Lite (Düşük Yoğunluk)": "gemini-3.8-flash-lite",
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

EXCLUDED_KEYWORDS = ("tts", "image", "audio", "robotics", "computer-use", "embedding", "aqa", "banana")


def get_available_models(api_key: str) -> list[str]:
    """API anahtarının erişebildiği metin/kod tabanlı Gemini modellerini Google'dan çeker."""
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models",
        headers={"x-goog-api-key": api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            valid = []
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                name = m.get("name", "").replace("models/", "")
                if (
                    "generateContent" in methods
                    and "gemini" in name
                    and not any(bad in name.lower() for bad in EXCLUDED_KEYWORDS)
                ):
                    valid.append(name)
            valid.sort(key=lambda x: (0 if "flash" in x else 1, x))
            if valid:
                return valid
    except Exception:
        pass
    return ["gemini-3.8-flash", "gemini-3.8-flash-lite"]


def call_gemini(api_key: str, primary_model: str, system_prompt: str, user_text: str, status_box) -> tuple[str, str]:
    available = get_available_models(api_key)
    if primary_model == "auto" or not primary_model:
        models_to_try = available
    else:
        models_to_try = [primary_model] + [m for m in available if m != primary_model]

    if not models_to_try:
        models_to_try = ["gemini-3.8-flash"]

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {"temperature": 0.35},
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    last_error = "Sunucudan yanıt alınamadı."

    for index, model_name in enumerate(models_to_try):
        if index > 0:
            status_box.info(f"Seçili model yoğun veya uyumsuz, alternatif model deneniyor: **{model_name}**...")
            time.sleep(1.0)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        req = urllib.request.Request(
            url,
            data=encoded_payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
                answer = "\n\n".join(part.get("text", "") for part in parts if part.get("text"))
                if not answer:
                    raise RuntimeError("Model yanıtı boş döndü.")
                return answer, model_name
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            last_error = f"API Hatası ({e.code}): {msg}"
            if e.code in (401, 403):
                raise RuntimeError(last_error)
        except Exception as e:
            last_error = f"Bağlantı hatası: {e}"

    raise RuntimeError(last_error)


# Ayarlar Bölümü
col1, col2 = st.columns([3, 2])
with col1:
    api_key = st.text_input(
        "Gemini API Anahtarı",
        type="password",
        placeholder="AQ.Ab8... veya AIzaSy...",
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
        st.warning("Lütfen AQ.Ab8... veya AIzaSy... ile başlayan Gemini API anahtarınızı girin.")
    elif not user_input.strip():
        st.warning("Lütfen özetlenecek metni veya analiz edilecek kodu yapıştırın.")
    else:
        model_id = MODELS[selected_model_label]
        status_placeholder = st.empty()
        with st.spinner("Uygun model belirleniyor ve yanıt hazırlanıyor..."):
            try:
                result, used_model = call_gemini(
                    api_key.strip(),
                    model_id,
                    MODES[selected_mode],
                    user_input.strip(),
                    status_placeholder,
                )
                status_placeholder.empty()
                st.success(f"Tamamlandı · Kullanılan Model: {used_model}")
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as ex:
                status_placeholder.empty()
                st.error(str(ex))
