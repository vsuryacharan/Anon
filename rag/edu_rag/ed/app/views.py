import os
from django.shortcuts import render, redirect,HttpResponse
from .models import PDFDocument
from .forms import PDFUploadForm
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from gtts import gTTS
from django.conf import settings
import os
from gtts import gTTS
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from .models import PDFDocument  # Assuming you have a model named PDF for uploaded PDFs
from PyPDF2 import PdfReader  # Assuming you're using PyPDF2 for PDF reading
from django.core.files.storage import FileSystemStorage
from .new3 import takecommand
import random
# Ensure your OpenAI API key is set
os.environ["OPENAI_API_KEY"] = ""
#takecommand()
def home(request):
    #takecommand()
    return render(request,'intro.html')
def upload_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()
    return render(request, 'upload_pdf.html', {'form': form})

def pdf_list(request):
    pdfs = PDFDocument.objects.all()
    return render(request, 'pdf_list.html', {'pdfs': pdfs})

from django.core.files.storage import FileSystemStorage

def convert_pdf_to_speech(request, pdf_id):
    # Get the PDF object
    pdf = get_object_or_404(PDFDocument, id=pdf_id)
    
    # Extract the PDF text
    pdf_path = pdf.pdf_file.path  # Assuming your PDF model has a file field
    title = pdf.title
    
    # Convert the PDF content to speech and save the audio file
    audio_file_name = convert_pdf_to_speech_function(pdf_path, title)

    # Return the audio file name and make it available in the context
    return redirect('ask_question', pdf_id=pdf_id)

def convert_pdf_to_speech_function(pdf_path, title):
    """
    Convert the entire PDF text to speech and return the audio file path.
    """
    # Load and read PDF using PyPDFLoader or PyPDF2 (assumed PyPDFLoader or similar is used here)
    loader = PdfReader(pdf_path)
    full_text = ""
    for page in loader.pages:
        full_text += page.extract_text()

    # Convert text to speech using gTTS
    tts = gTTS(text=full_text, lang='en')
    
    # Create the file path
    audio_file_name = f"{title.replace(' ', '_')}.mp3"
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
    
    # Ensure the 'audio' folder exists in the media directory
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'audio')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'audio'))

    # Save the audio file
    tts.save(audio_file_path)

    # Return just the file name (relative to MEDIA_URL) for HTML usage
    return audio_file_name

def ask_question(request, pdf_id):
    pdf = PDFDocument.objects.get(id=pdf_id)
    pdf_path = pdf.pdf_file.path
    audio_file = pdf.audio_file.name if pdf.audio_file else None  # Use the stored audio file name

    if request.method == "POST":
        query = request.POST.get('query')

        # Create the RAG application
        rag_app = create_rag_app(pdf_path)

        # Get the answer to the user's query
        try:
            result = rag_app.run(query)
        except Exception as e:
            return render(request, 'ask_question.html', {
                'pdf': pdf,
                'error': f"Error retrieving answer: {str(e)}"
            })

        # Text-to-speech conversion
        if 'convert_to_speech' in request.POST:
            try:
                audio_file_name = convert_pdf_to_speech(pdf_path, pdf.title)  # Call your TTS function
                pdf.audio_file = f'audio/{audio_file_name}'  # Save the audio file path in the model
                pdf.save()  # Save the PDFDocument instance to update the audio file path
                audio_file = pdf.audio_file.name  # Update audio_file variable
            except Exception as e:
                return render(request, 'ask_question.html', {
                    'pdf': pdf,
                    'result': result,
                    'query': query,
                    'error': f"Error converting PDF to speech: {str(e)}"
                })

        return render(request, 'ask_question.html', {
            'pdf': pdf,
            'result': result,
            'query': query,
            'audio_file': audio_file  # Pass audio file path to the template
        })

    return render(request, 'ask_question.html', {'pdf': pdf, 'audio_file': audio_file})

def create_rag_app(pdf_path):
    """
    Creates a RAG application using LangChain, OpenAI, and ChromaDB.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    db = Chroma.from_documents(texts, embeddings)

    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)

    return qa

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import PDFDocument
from gtts import gTTS
import os
from django.conf import settings

from django.shortcuts import render, get_object_or_404
from .models import PDFDocument  # Assuming your PDFDocument model is imported

def text_to_speech_view(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)

    audio_file = pdf.audio_file.name if pdf.audio_file else None  # Use the stored audio file name

    if request.method == "POST":
        # Call your conversion function here
        audio_file_name = convert_pdf_to_speech_function(pdf.pdf_file.path, pdf.title)  # Convert to speech
        pdf.audio_file = f'audio/{audio_file_name}'  # Save the audio file path in the model
        pdf.save()  # Save the PDFDocument instance to update the audio file path
        audio_file = pdf.audio_file.name  # Update audio_file variable

    # Fetch all PDF documents for listing
    all_pdfs = PDFDocument.objects.all()

    return render(request, 'text_to_speech.html', {
        'pdf': pdf,
        'audio_file': audio_file,
        'pdfs': all_pdfs  # Pass all PDFs to the template
    })


def convert_pdf_to_speech_function(pdf_path, title):
    """
    Convert the entire PDF text to speech and return the audio file path.
    """
    # Load and read PDF using PyPDF2 or similar
    loader = PdfReader(pdf_path)
    full_text = ""
    for page in loader.pages:
        full_text += page.extract_text()

    # Convert text to speech using gTTS
    tts = gTTS(text=full_text, lang='en')
    
    # Create the file path
    audio_file_name = f"{title.replace(' ', '_')}.mp3"
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
    
    # Ensure the 'audio' folder exists in the media directory
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'audio')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'audio'))

    # Save the audio file
    tts.save(audio_file_path)

    return audio_file_name
import os
from django.conf import settings
from django.shortcuts import render, HttpResponse
import google.generativeai as genai

# Configure Google Gemini API key
genai.configure(api_key='AIzaSyC5Dq6Pb_YJGlMsa5WR0pufFjTtmhhNc7M')

def prep_image(image_path):
    """Uploads the image file and returns the sample file object."""
    sample_file = genai.upload_file(path=image_path, display_name="Diagram")
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    return sample_file

def extract_text_from_image(sample_file, prompt):
    """Generates content based on the uploaded image and the given prompt."""
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content([sample_file, prompt])
    return response.text

# from .gemini import text,prep_image,extract_text_from_image
def upload_screenshot_view(request):
    if request.method == 'POST':
        sample_file=prep_image('sketch_screenshot.png')
        text = extract_text_from_image(sample_file, "Extract a mathematical equations and solve all of it or physics equations and values or chemistry problems, its an handwritten equation just give step and answers dont mention anything about prompts")
        text_list=text.split(",")
        return render(request, "photo_ans.html", {'text_list': text_list}) 



from django.shortcuts import render, redirect
from django.http import HttpResponse
import subprocess
import os
def open_sketchbook(request):
    """View to open the Sketchbook application."""
    if request.method == "POST":
        # Path to your sketch.py file
        sketchbook_path = os.path.join(os.path.dirname(__file__), 'sketch.py')
        
        # Run the sketch.py file using subprocess
        subprocess.Popen(["python", sketchbook_path])
        
        return redirect('sketch_opened')  # Redirect to a confirmation page or any other page

    return HttpResponse("Sketchbook can only be opened via POST request.", status=405)


def sketch_opened(request):
    """A confirmation page to show that the Sketchbook has been opened."""
    return render(request, 'sketch_opened.html')

# views.py
from django.shortcuts import render
from django.http import JsonResponse
import os
from .frames import capture_frame
from .pdf import create_pdf_from_images

folder_path = os.path.join(os.path.dirname(__file__), 'Folder_with_Frames')

def capture_frame_view(request):
    """View to capture a frame when the user clicks a button."""
    if request.method == 'POST':
        # Capture frame and save it
        frame_index = request.POST.get('frame_index', 0)
        capture_frame(frame_index)
        return JsonResponse({'status': 'Frame captured!', 'frame_index': frame_index})
    
    return JsonResponse({'status': 'Invalid request'}, status=400)

def create_pdf_view(request):
    """View to create a PDF from captured frames."""
    if request.method == 'POST':
        create_pdf_from_images(folder_path)
        return JsonResponse({'status': 'PDF created!'})
    
    return JsonResponse({'status': 'Invalid request'}, status=400)
def photos(request):
    return render(request,'photos.html')

# views.py


# views.py

# def generate_quiz_questions(qa, num_questions=10):
#     """
#     Generate a list of quiz questions and answers from the document content.
#     """
#     question_prompt = "Generate ten quiz questions based on the document."
    
#     # Run the prompt and print the response for debugging
#     response = qa.run(question_prompt)
#     print("Response from model:", response)  # Debugging line
    
#     # Split the response into questions
#     questions = [q.strip() for q in response.split("\n") if q.strip()]
    
#     return questions[:num_questions], []  # Return empty answers if you’re only testing questions


def generate_mcq_questions(qa, num_questions=10):
    """
    Generate a list of multiple-choice quiz questions with answer options and correct answers.
    """
    question_prompt = "Generate ten multiple-choice quiz questions based on the document, with four answer options each and an indication of the correct answer. Format as: Q: <question> Options: A) ..., B) ..., C) ..., D) ... Correct: <option>."
    response = qa.run(question_prompt)
    
    questions = []
    for line in response.split("\n"):
        if "Q:" in line:
            question_text = line.split("Q:")[1].strip()
            questions.append({"question": question_text, "options": [], "correct_answer": None})
        elif "Options:" in line and questions:
            options = line.split("Options:")[1].split(", ")
            questions[-1]["options"] = [option.strip() for option in options]
        elif "Correct:" in line and questions:
            correct_option = line.split("Correct:")[1].strip().split(")")[0]  # Extract only the letter part (e.g., "A")
            if correct_option:  # Check if correct_option is not empty
                questions[-1]["correct_answer"] = correct_option

    # Filter out any incomplete questions without a correct answer or options
    questions = [q for q in questions if q["correct_answer"] and q["options"]]
    
    print(questions)
    return questions[:num_questions]


def quiz_view(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)
    pdf_path = pdf.pdf_file.path
    qa = create_rag_app(pdf_path)

    # Generate MCQs with options
    mcqs = generate_mcq_questions(qa)

    if request.method == "POST":
        # Retrieve user's answers and validate them
        user_answers = [request.POST.get(f"answer_{i}", "") for i in range(len(mcqs))]  # Default to empty string if no answer
        score = 0
        feedback = []

        for i, mcq in enumerate(mcqs):
            correct_answer = mcq.get("correct_answer", "").upper() if mcq.get("correct_answer") else ""  # Safely retrieve correct_answer
            user_answer = user_answers[i].strip().upper() if user_answers[i] else ""  # Handle case-insensitivity

            # Debugging print statements
            print(f"Question {i+1}:")
            print(f"Correct Answer: {correct_answer}")
            print(f"User Answer: {user_answer}")

            if user_answer == correct_answer:
                score += 1
                feedback.append("Correct")
            else:
                feedback.append(f"Incorrect (Correct answer: {correct_answer})")

        zipped_data = zip(mcqs, user_answers, feedback)

        return render(request, 'quiz_results.html', {
            'zipped_data': zipped_data,
            'score': score,
            'total': len(mcqs),
            'pdf_id': pdf_id  # Pass pdf_id to the template context
        })

    return render(request, 'quiz.html', {'mcqs': mcqs})


