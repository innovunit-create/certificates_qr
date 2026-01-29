import streamlit as st
import uuid
import qrcode
from PIL import Image
from github import Github
import os
import base64

# --- CONFIG ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Store your token in .streamlit/secrets.toml
GITHUB_REPO = "innovunit-create/certificates_qr.git"  # your repo name
GITHUB_PATH = "certificates_qr/certificates"  # folder in repo
BASE_PUBLIC_URL = f"https://innovunit-create.github.io/{GITHUB_PATH}/"

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
    cert_url = BASE_PUBLIC_URL + filename

    # Generate QR code
    qr = qrcode.make(cert_url).convert("RGBA")
    qr_size = int(w * 0.15)
    qr = qr.resize((qr_size, qr_size))

    margin = 30
    position = (w - qr_size - margin, h - qr_size - margin)
    cert.paste(qr, position, qr)

    # Save temporarily locally
    local_path = f"temp_{filename}"
    cert.save(local_path)

    # Upload to GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    # Read the file and encode as base64
    with open(local_path, "rb") as f:
        content = f.read()
    encoded_content = base64.b64encode(content).decode()

    try:
        # Check if file exists
        repo_file = repo.get_contents(f"{GITHUB_PATH}/{filename}")
        repo.update_file(f"{GITHUB_PATH}/{filename}", f"Update certificate {filename}", content, repo_file.sha)
    except:
        # File doesn't exist, create it
        repo.create_file(f"{GITHUB_PATH}/{filename}", f"Add certificate {filename}", content)

    st.success("✅ Certificate uploaded to GitHub successfully!")

    st.image(cert, caption="Final Certificate with QR", use_column_width=True)

    st.markdown(f"🔗 **QR Code URL:** {cert_url}")
    st.download_button(
        label="⬇️ Download Certificate",
        data=open(local_path, "rb"),
        file_name="certificate_with_qr.png",
        mime="image/png"
    )

    # Clean up local temp file
    os.remove(local_path)
