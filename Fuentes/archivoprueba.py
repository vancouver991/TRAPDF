from fpdf import FPDF, XPos, YPos
import os

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    # Ruta absoluta al archivo de fuente
    font_path = os.path.join(os.path.dirname(__file__), 'Brother-1816-ExtraBold.ttf')
    pdf.add_font('Brother1816ExtraBold', '', font_path)
    pdf.set_font('Brother1816ExtraBold', size=12)
    pdf.cell(200, 10, text="Este es un texto de prueba usando Brother 1816 ExtraBold.", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.output("test_brother1816.pdf")
    print("Archivo PDF de prueba generado: test_brother1816.pdf")

if __name__ == "__main__":
    create_test_pdf()
