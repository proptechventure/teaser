from parsers.pptx_parser import extract_pptx_text
from parsers.excel_parser import extract_financials
from jinja2 import Environment, FileSystemLoader
import pdfkit
import uuid

def generate_teaser(pptx_path, excel_path, logo_path):
    summary = extract_pptx_text(pptx_path)
    financials = extract_financials(excel_path)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("teaser_template.html")

    html = template.render(summary=summary, financials=financials, logo_path=logo_path)

    output_path = f"output/teaser_{uuid.uuid4()}.pdf"
    pdfkit.from_string(html, output_path)
    return output_path
