@echo off
echo Создание виртуального окружения...
python -m venv venv

echo Активация окружения...
call venv\Scripts\activate

echo Установка зависимостей...
pip install fastapi uvicorn jinja2 pdfkit python-pptx pandas openpyxl

echo Установка завершена.
echo Для запуска приложения используй:
echo uvicorn main:app --reload
pause
