from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_key_slides(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        key_slides = [reader.pages[i] for i in [0, len(reader.pages)//2, -1]]
        return key_slides, len(reader.pages)

def create_summary_pdf(pdf_path, output_path):
    """Создаем PDF с кратким содержанием"""
    try:
        # Открываем PDF для чтения
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_slides = len(reader.pages)
            
            # Выбираем ключевые слайды (первый, средний, последний)
            key_slide_indices = [0]
            if total_slides > 1:
                key_slide_indices.append(total_slides // 2)
                key_slide_indices.append(-1)
            
            # Создаем PDF для записи
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, height-72, "Краткое содержание презентации")
            c.setFont("Helvetica", 12)
            c.drawString(72, height-100, f"Исходный файл: {os.path.basename(pdf_path)}")
            c.drawString(72, height-120, f"Всего слайдов: {total_slides}")
            c.drawString(72, height-140, f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            # Основные пункты
            c.drawString(72, height-180, "Основные пункты:")
            c.setFont("Helvetica", 10)
            text = c.beginText(72, height-200)
            
            # Извлекаем текст с ключевых слайдов
            for i, idx in enumerate(key_slide_indices):
                slide = reader.pages[idx]
                try:
                    slide_text = slide.extract_text()
                    if slide_text:
                        text.textLine(f"{i+1}. {slide_text[:100]}{'...' if len(slide_text) > 100 else ''}")
                    else:
                        text.textLine(f"{i+1}. [Графический слайд]")
                except Exception as e:
                    text.textLine(f"{i+1}. [Ошибка чтения слайда: {str(e)}]")
            
            c.drawText(text)
            c.showPage()
            c.save()
            
            return output_path
            
    except Exception as e:
        print(f"Ошибка при обработке PDF: {str(e)}")
        raise

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"summary_{filename}")
            create_summary_pdf(input_path, output_path)
            return send_file(output_path, as_attachment=True)
        return render_template('index.html', error="Invalid PDF file")
    return render_template('index.html')

if __name__ == '__main__':

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
