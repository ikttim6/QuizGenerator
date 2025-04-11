import os
import openai
import json
from django.conf import settings

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY


def generate_questions(content, num_multiple_choice, num_true_false, num_essay):
    """Generate questions using OpenAI GPT-4"""

    # Prepare the prompt for OpenAI
    prompt = f"""
    Based on the following educational content, generate:
    - {num_multiple_choice} multiple-choice questions with 4 options each (only one correct)
    - {num_true_false} true/false questions
    - {num_essay} open-ended essay questions

    Format the response as a JSON array with the following structure:
    [
        {{
            "type": "multiple_choice",
            "question": "Question text here?",
            "choices": [
                {{"text": "Option 1", "is_correct": false}},
                {{"text": "Option 2", "is_correct": true}},
                {{"text": "Option 3", "is_correct": false}},
                {{"text": "Option 4", "is_correct": false}}
            ]
        }},
        {{
            "type": "true_false",
            "question": "Statement that is true or false.",
            "choices": [
                {{"text": "True", "is_correct": true}},
                {{"text": "False", "is_correct": false}}
            ]
        }},
        {{
            "type": "essay",
            "question": "Open-ended question requiring an essay response."
        }}
    ]

    Educational content:
    {content[:4000]}  # Limit content to avoid token limits
    """

    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an educational expert who creates high-quality quiz questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # Parse the response
        result = response.choices[0].message.content.strip()

        # Extract the JSON part
        json_start = result.find('[')
        json_end = result.rfind(']') + 1

        if json_start >= 0 and json_end > json_start:
            json_str = result[json_start:json_end]
            questions = json.loads(json_str)
            return questions
        else:
            # Fallback if JSON parsing fails
            return generate_fallback_questions(num_multiple_choice, num_true_false, num_essay)

    except Exception as e:
        print(f"Error generating questions: {e}")
        return generate_fallback_questions(num_multiple_choice, num_true_false, num_essay)


def generate_fallback_questions(num_multiple_choice, num_true_false, num_essay):
    """Generate fallback questions if OpenAI API fails"""
    questions = []

    # Generate multiple choice questions
    for i in range(num_multiple_choice):
        questions.append({
            "type": "multiple_choice",
            "question": f"Sample multiple choice question {i + 1}. Please edit this.",
            "choices": [
                {"text": "Option 1", "is_correct": True},
                {"text": "Option 2", "is_correct": False},
                {"text": "Option 3", "is_correct": False},
                {"text": "Option 4", "is_correct": False}
            ]
        })

    # Generate true/false questions
    for i in range(num_true_false):
        questions.append({
            "type": "true_false",
            "question": f"Sample true/false statement {i + 1}. Please edit this.",
            "choices": [
                {"text": "True", "is_correct": True},
                {"text": "False", "is_correct": False}
            ]
        })

    # Generate essay questions
    for i in range(num_essay):
        questions.append({
            "type": "essay",
            "question": f"Sample essay question {i + 1}. Please edit this."
        })

    return questions
