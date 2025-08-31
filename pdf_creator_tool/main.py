from src.pdf_creator import PDFApp

# Keep main minimal: construct and render the UI.
if __name__ == "__main__":
    app = PDFApp()
    app.render()
