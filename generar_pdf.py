import os
from fpdf import FPDF
import unicodedata

docs_dir = os.path.join(os.path.dirname(__file__), 'public', 'docs')
os.makedirs(docs_dir, exist_ok=True)
pdf_path = os.path.join(docs_dir, 'Manual_Ut_Emplea.pdf')
txt_path = os.path.join(os.path.dirname(__file__), 'manual_ut_emplea.txt')

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 18)
        self.set_text_color(14, 49, 45) # Verde
        self.cell(0, 10, "BOLSA DE TRABAJO - UT ORIENTAL", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "I", 12)
        self.set_text_color(194, 145, 79) # Dorado
        self.cell(0, 8, "Manual de Usuario Tecnico y Operativo", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

def sanitizar_texto(texto):
    # Reemplazar comillas raras, emojis y otros que no entren en cp1252
    texto_normal = unicodedata.normalize('NFKC', texto)
    return texto_normal.encode('cp1252', 'replace').decode('cp1252')

def crear_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page("P") 
    pdf.set_auto_page_break(auto=True, margin=15)
    
    with open(txt_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith("===") or line.startswith("---"):
            continue
            
        line_safe = sanitizar_texto(line)
        
        if line.isupper() and len(line) > 5 and not "UT ORIENTAL" in line:
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(14, 49, 45)
            pdf.cell(0, 10, line_safe, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif line.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.set_x(20)
            pdf.multi_cell(0, 7, line_safe)
        else:
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 7, line_safe)

    pdf.output(pdf_path)
    print(f"PDF generado exitosamente en: {pdf_path}")

if __name__ == "__main__":
    crear_pdf()
