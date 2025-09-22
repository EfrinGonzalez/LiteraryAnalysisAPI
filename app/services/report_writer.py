from fpdf import FPDF
from datetime import datetime

def generate_pdf_report(text: str, top_words, sentiment, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Literary Analysis Report", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resumen de Sentimiento", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Polaridad: {sentiment['polarity']}\nSubjetividad: {sentiment['subjectivity']}")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Palabras más frecuentes", ln=True)
    pdf.set_font("Arial", '', 12)
    for word, count in top_words:
        pdf.cell(0, 10, f"{word}: {count}", ln=True)

    pdf.output(output_path)