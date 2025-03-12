import os
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text(file_path):
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == 'docx':
        return extract_text_from_docx(file_path)
    elif file_extension in ['png', 'jpg', 'jpeg']:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def get_answer(question, context):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided document context. "
                    "Provide accurate, concise answers based only on the information available in the context."
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\n\nQuestion: {question}"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Failed to get answer from OpenAI: {str(e)}")
