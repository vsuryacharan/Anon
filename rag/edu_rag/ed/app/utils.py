# utils.py

def process_mcq_questions(response):
    """
    Process the response from the RAG application to match each question with options and the correct answer.
    """
    questions = []
    
    for item in response:
        question_text = item.get('question', '').strip()
        options = item.get('options', [])
        correct_answer = item.get('correct_answer', '').strip().upper()

        question_data = {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        }
        
        questions.append(question_data)
    
    return questions


def generate_mcq_questions(qa):
    """
    Generates a list of MCQs using the RAG application and formats them for scoring.
    """
    rag_response = qa.run("Generate multiple-choice questions with options and indicate the correct answer.")
    formatted_questions = process_mcq_questions(rag_response)
    return formatted_questions
