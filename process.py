import streamlit as st
import uuid
import qrcode
from PIL import Image
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Google Drive Auth
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Opens a browser to authenticate
drive = GoogleDrive(gauth)

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

    # Save locally first (optional)
    cert.save(filename)

    # Upload to Google Drive
    gfile = drive.CreateFile({'title': filename})
    gfile.SetContentFile(filename)
    gfile.Upload()

    # Make file public
    gfile.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    # Get public URL
    cert_url = f"https://drive.google.com/uc?id={gfile['id']}"

    # Generate QR
    qr = qrcode.make(cert_url).convert("RGBA")
    qr_size = int(w * 0.15)
    qr = qr.resize((qr_size, qr_size))

    margin = 30
    position = (w - qr_size - margin, h - qr_size - margin)
    cert.paste(qr, position, qr)

    # Save final certificate locally
    final_path = f"certificate_with_qr_{cert_id}.png"
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
