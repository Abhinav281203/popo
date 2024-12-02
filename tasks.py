from celery_config import celery_app
import pypdf
import os
import csv
from mail_send import send_email_with_attachment
import openai
import os

@celery_app.task
def process_file(file_path: str, email: str, num_questions: int):

    try:
        chunks = create_chunks(file_path)

        len_of_chunks = len(chunks)
        
        questions = []
        for chunk in chunks:
            questions.extend(generate_questions(chunk, num_questions / len_of_chunks))

        csv_path = save_csv(questions, file_path)
        send_email_with_attachment(receiver_email=email,
                                   file_path=csv_path,)
    except Exception as e:
        return f"Error processing file {file_path}: {str(e)}"


def create_chunks(file_path):
    pdf = pypdf.PdfReader(file_path)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    chunk_size = 2000
    os.remove(file_path)
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def generate_questions(chunk, num_questions):
    if num_questions <= 0:
        num_questions = 1

    client = openai.Client(api_key="")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates questions from PDF content."},
            {"role": "user", "content": f"Generate {num_questions} unique questions based on this text, seperate them by \
             new line character. and do not give any output besides the questions,\n text: \n{chunk}"}
        ]
    )
    return response.choices[0].message.content.strip().split("\n")


def save_csv(questions, file_path):
    try:
        output_dir = "./outputs/"
        os.makedirs(output_dir, exist_ok=True)

        file_name = os.path.basename(file_path)
        file_name = file_name.replace(".pdf", ".csv")
        file_path = f"./outputs/{file_name}"

        print(file_path)
      
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Question"])
            for question in questions:
                writer.writerow([question])
        return file_path
    except Exception as e:
        print(e)


if __name__ == "__main__":
    process_file(file_path="./uploads/ML Assignment - BYOM.pdf", 
                 email="chhnvngl@gmail.com", 
                 num_questions=5)