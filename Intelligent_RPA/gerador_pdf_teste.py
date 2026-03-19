import os
import subprocess
import sys

# Auto-instala pacote temporário para gerar o PDF se não houver
try:
    from reportlab.pdfgen import canvas
except ImportError:
    print("⏳ Instalando 'reportlab' para gerar o PDF de teste...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.pdfgen import canvas

def create_dummy_invoice(filepath):
    c = canvas.Canvas(filepath)
    text = c.beginText(50, 800)
    text.setFont("Helvetica-Bold", 16)
    text.textLine("FATURA DE SERVIÇOS - AI AUTOMATION LTDA")
    text.setFont("Helvetica", 12)
    
    linhas = [
        "",
        "============== DADOS DA NOTA ==============",
        "Fatura Nº: 2026-0042",
        "Data de Emissão: 2026-03-18",
        "",
        "============== DADOS DO CLIENTE ==============",
        "Razão Social: Future Corp Inteligência SA",
        "CNPJ: 12.345.678/0001-90",
        "",
        "============== DISCRIMINAÇÃO ==============",
        "1x Desenvolvimento de Arquitetura RPA com Python",
        "1x Integração Local Llama 3.1",
        "",
        "============== FECHAMENTO ==================",
        "Valor Total: R$ 8.450,00",
        "",
        "Fatura com vencimento em 30 dias.",
        "Agradecemos a parceria!"
    ]
    
    text.textLines(linhas)
    c.drawText(text)
    c.save()

if __name__ == "__main__":
    out_dir = "input_invoices"
    os.makedirs(out_dir, exist_ok=True)
    
    pdf_path = os.path.join(out_dir, "fatura_teste_01.pdf")
    create_dummy_invoice(pdf_path)
    print(f"✅ Arquivo PDF fictício gerado com sucesso em: {pdf_path}")
