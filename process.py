import streamlit as st
import uuid
import qrcode
import os
from PIL import Image

# Config
BASE_PUBLIC_URL = "https://your-public-app-url.streamlit.app/certificates/"
PUBLIC_FOLDER = "certificates_public"
FINAL_FOLDER = "certificates_final"

os.makedirs(PUBLIC_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)

st.set_page_config(page_title="Certificate QR Generator", layout="centered")

st.title("🎓 Certificate QR Generator")
st.write("Upload a certificate image. A QR code will be embedded that links to its softcopy.")

uploaded_file = st.file_uploader(
    "Upload Certificate (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    # Load image
    cert = Image.open(uploaded_file).convert("RGBA")
    w, h = cert.size

    # Unique ID
    cert_id = str(uuid.uuid4())
    filename = f"{cert_id}.png"

    # Save public softcopy
    public_path = os.path.join(PUBLIC_FOLDER, filename)
    cert.save(public_path)

    # Generate QR
    cert_url = BASE_PUBLIC_URL + filename
    qr = qrcode.make(cert_url).convert("RGBA")

    qr_size = int(w * 0.15)
    qr = qr.resize((qr_size, qr_size))

    margin = 30
    position = (w - qr_size - margin, h - qr_size - margin)

    cert.paste(qr, position, qr)

    # Save final certificate
    final_path = os.path.join(FINAL_FOLDER, filename)
    cert.save(final_path)

    st.success("Certificate processed successfully!")

    st.image(cert, caption="Final Certificate with QR", use_column_width=True)

    with open(final_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Certificate",
            data=f,
            file_name="certificate_with_qr.png",
            mime="image/png"
        )

    st.markdown(f"🔗 **QR Code URL:** {cert_url}")
