import json
from openai import AzureOpenAI
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


client = AzureOpenAI(
    api_key=settings.OPENAI_API_KEY,
    api_version="",
    azure_endpoint=""
)

DEPLOYMENT_NAME = "gpt-4.1"

def generate_questions(content, num_multiple_choice, num_true_false, num_essay):
    """Generates questions using Azure OpenAI GPT-4"""
    try:
        if not content.strip():
            logger.warning("The document is empty for question generation.")
            return generate_fallback_questions(num_multiple_choice, num_true_false, num_essay)


        content = content.encode('utf-8', errors='replace').decode('utf-8')

        prompt = f"""
        Based on the following educational material in English, generate:
        - {num_multiple_choice} multiple-choice questions with 4 options (only one correct)
        - {num_true_false} true/false questions
        - {num_essay} essay questions

        Format the answer as a JSON object with a 'questions' key that contains a list:
        {{
            "questions": [
                {{
                    "type": "multiple_choice",
                    "question": "Question text?",
                    "choices": [
                        {{"text": "Option 1", "is_correct": false}},
                        {{"text": "Option 2", "is_correct": true}},
                        {{"text": "Option 3", "is_correct": false}},
                        {{"text": "Option 4", "is_correct": false}}
                    ]
                }},
                {{
                    "type": "true_false",
                    "question": "A statement that is either true or false.",
                    "choices": [
                        {{"text": "True", "is_correct": true}},
                        {{"text": "False", "is_correct": false}}
                    ]
                }},
                {{
                    "type": "essay",
                    "question": "An open-ended question that requires an essay answer."
                }}
            ]
        }}

        Educational material:
        {content[:3500]}
        """

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert at creating quiz questions in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content


        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                json_start = max(result.find('{'), result.find('['))
                json_end = max(result.rfind('}'), result.rfind(']')) + 1
                if json_start != -1 and json_end != -1:
                    result = json.loads(result[json_start:json_end])


        if isinstance(result, dict) and 'questions' in result:
            return result['questions']
        elif isinstance(result, list):
            return result
        else:
            raise ValueError("Unexpected response format")

    except Exception as e:
        logger.error(f"Error while generating questions: {str(e)}")
        return generate_fallback_questions(num_multiple_choice, num_true_false, num_essay)

def generate_fallback_questions(num_multiple_choice, num_true_false, num_essay):
    """Generates fallback questions in case the API fails"""
    questions = []

    for i in range(num_multiple_choice):
        questions.append({
            "type": "multiple_choice",
            "question": f"Sample multiple-choice question {i + 1} (edit this)",
            "choices": [
                {"text": "Option 1", "is_correct": True},
                {"text": "Option 2", "is_correct": False},
                {"text": "Option 3", "is_correct": False},
                {"text": "Option 4", "is_correct": False}
            ]
        })

    for i in range(num_true_false):
        questions.append({
            "type": "true_false",
            "question": f"Sample true/false statement {i + 1} (edit this)",
            "choices": [
                {"text": "True", "is_correct": True},
                {"text": "False", "is_correct": False}
            ]
        })

    for i in range(num_essay):
        questions.append({
            "type": "essay",
            "question": f"Sample essay question {i + 1} (edit this)"
        })

    return questions


