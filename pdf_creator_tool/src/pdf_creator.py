from typing import List
from PIL import Image
import io
import re
import os


class PDFApp:
    """
    Encapsulated Image→PDF Streamlit app.
    """

    def __init__(self, title: str = "Image → PDF Converter", max_images: int = 50):
        self.title = title
        self.max_images = max_images

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        name = (name or "combined").strip()
        name = re.sub(r"[^\w\-. ]+", "", name)  # remove unsafe chars
        name = name.replace(" ", "_")
        return f"{name or 'combined'}.pdf"

    @staticmethod
    def images_to_pdf(images: List[Image.Image]) -> io.BytesIO:
        """
        Convert a list of PIL Image objects into a single PDF (BytesIO).
        Ensures RGB mode for all images.
        """
        if not images:
            raise ValueError("No images provided for PDF conversion.")

        rgb_images = [(img if img.mode == "RGB" else img.convert("RGB")) for img in images]

        out = io.BytesIO()
        rgb_images[0].save(
            out,
            format="PDF",
            save_all=True,
            append_images=rgb_images[1:],
        )
        out.seek(0)
        return out

    @staticmethod
    def load_images_from_dir(dir_path: str) -> List[Image.Image]:
        """
        Load all JPG/PNG images from a given directory.
        """
        if not os.path.isdir(dir_path):
            raise ValueError(f"Invalid directory: {dir_path}")

        supported_ext = (".jpg", ".jpeg", ".png")
        files = sorted(
            [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith(supported_ext)]
        )

        if not files:
            raise ValueError(f"No supported images found in {dir_path}")

        return [Image.open(f) for f in files]

    def render(self) -> None:
        import streamlit as st

        st.set_page_config(page_title=self.title, page_icon="📄", layout="centered")

        # --- UI Styling ---
        st.markdown(
            """
            <style>
              [data-testid="stAppViewContainer"] {
                  background: linear-gradient(135deg, #1c1c1c 0%, #2a2a2a 100%);
                  color: #e0e0e0;
              }
              [data-testid="stHeader"] { display: none; }
              .app-card {
                  background: #2e2e2e;
                  padding: 2rem 2rem;
                  border-radius: 16px;
                  box-shadow: 0 6px 18px rgba(0,0,0,0.5);
                  max-width: 680px;
                  margin: 3rem auto;
              }
              h1, .subtitle { text-align: center; }
              h1 { color: #ffffff; }
              .subtitle { color: #bbbbbb; margin-bottom: 1.25rem; }
              .stTextInput>div>div>input,
              .stFileUploader>div>div>div>div {
                  background-color: #3a3a3a;
                  color: #ffffff;
              }
              .stButton>button {
                  border-radius: 8px;
                  padding: 0.6rem 1rem;
                  font-weight: 600;
                  background: #4cafef;
                  color: white;
                  border: none;
              }
              .stButton>button:hover {
                  background: #2196f3;
                  color: #fff;
              }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # --- UI ---
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.title("📄 Image → PDF")
        st.markdown('<div class="subtitle">Upload images OR provide a directory path.</div>', unsafe_allow_html=True)

        mode = st.radio("Choose input mode:", ["Upload files", "Directory path"])

        images = []
        error = None

        if mode == "Upload files":
            uploaded_files = st.file_uploader(
                "Upload images (JPG, PNG)", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
            )
            if uploaded_files:
                try:
                    images = [Image.open(f) for f in uploaded_files]
                except Exception as e:
                    error = str(e)

        elif mode == "Directory path":
            dir_path = st.text_input("Enter directory path:")
            if dir_path:
                try:
                    images = self.load_images_from_dir(dir_path)
                except Exception as e:
                    error = str(e)

        pdf_name = st.text_input("PDF name (without extension):", value="combined")

        col1, col2 = st.columns(2)
        with col1:
            convert_clicked = st.button("Convert", use_container_width=True)
        with col2:
            clear_clicked = st.button("Clear", use_container_width=True)

        if clear_clicked:
            st.rerun()

        if convert_clicked:
            if not images:
                st.warning("No images found. Upload files or specify a valid directory.")
            elif error:
                st.error(error)
            else:
                try:
                    pdf_bytes = self.images_to_pdf(images)
                    safe_name = self._sanitize_filename(pdf_name)
                    st.success("✅ PDF generated successfully.")
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=safe_name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error creating PDF: {e}")

        st.markdown("</div>", unsafe_allow_html=True)
