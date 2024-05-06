from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
import json

import logging

# Configure the logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
CORS(app)

# Your ChatService class definition here

class ChatService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + self.api_key

    def get_interview_questions(self, domain, role, difficulty_level, specific_topic, num_questions=15):
        try:
            headers = {'Content-Type': 'application/json'}
            logging.info(f"Generate {num_questions} interview questions on {specific_topic} with level {difficulty_level}.")
            prompt = f"You are a {role} in the {domain} domain preparing interview questions."

            prompt += f"\n\nGenerate {num_questions} interview questions along with answers for the topic of {specific_topic} with difficulty level {difficulty_level}."
            prompt += f"\nOut of these, include 3-5 scenario-based questions."
            prompt += f"\nProvide direct answers without suggestions or advice. Give the answer in first person."
            prompt += f"\nReturn your response in an array of JSON objects. Each object will have 'question' and 'answer' keys."
            prompt += f"\nBelow is the example structure that you should return your response:"
            prompt += f'''[
              {{
                "question": "What is @SpringBootApplication annotation used for in Spring Boot?",
                "answer": "The @SpringBootApplication annotation is used to mark a class as the main Spring Boot application class and is typically placed on the main class of the application."
              }},
              {{
                "question": "Explain the concept of dependency injection in Spring Boot.",
                "answer": "Dependency injection is a technique where an object is given its dependencies by external code rather than creating them itself."
              }},
              {{
                "question": "You encounter a circular dependency issue in a Spring Boot project. How would you resolve it?",
                "answer": "One way to resolve a circular dependency issue in Spring Boot is by using constructor injection instead of field injection. This allows dependencies to be injected via constructor parameters, avoiding the circular reference problem."
              }},
              {{
                "question": "You are tasked with optimizing the performance of a Spring Boot application. What steps would you take?",
                "answer": "To optimize the performance of a Spring Boot application, I will analyze and optimize database queries, implement caching mechanisms, and utilize asynchronous processing where applicable."
              }},
              {{
            "question": "In a Spring Boot application, how do you handle data validation using the Bean Validation API?",
            "answer": "To utilize the Bean Validation API for data validation, I will add the 'hibernate-validator' dependency and annotate data fields with constraints defined in the javax.validation package. Spring Boot will automatically perform validation during object creation, providing detailed error messages for invalid data.",
            
        }},
        {{
        "question": "You are working on a Spring Boot application that uses an in-memory database. What steps would you take to ensure data persistence across application restarts?",
            "answer": "To ensure data persistence in Spring Boot applications using an in-memory database, I will consider implementing a data persistence mechanism such as using a persistent database (e.g., MySQL, PostgreSQL) or incorporating a caching solution (e.g., Redis, Memcached) to store data.",
            
        }}
            ]'''

            generation_config = {
                'temperature': 0.9,
                'topK': 1,
                'topP': 1,
                'maxOutputTokens': 2048,
                'stopSequences': []
            }

            request_body = {
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': generation_config
            }

            response = requests.post(self.base_url, json=request_body, headers=headers)
            response.raise_for_status()  # Raise an error if the request was unsuccessful

            response_data = response.json()

            generated_questions = []

            for candidate in response_data['candidates']:
                question_answer_pairs = json.loads(candidate['content']['parts'][0]['text'])
                for pair in question_answer_pairs:
                    generated_questions.append({'question': pair['question'], 'answer': pair['answer']})

            return generated_questions[:num_questions]  # Return only the first num_questions

        except Exception as e:
            logging.error(f"Error in generating interview question: {str(e)}")
            print("Service Exception:", str(e))
            raise Exception("Error in getting response from Gemini API")

# Define your Flask route for generating interview questions
@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    # Get data from the request body
    request_data = request.json
    domain = request_data.get('domain')
    role = request_data.get('role')
    difficulty_level = request_data.get('difficulty_level')
    specific_topic = request_data.get('specific_topic')
    num_questions = request_data.get('num_questions', 15)  # Default to 15 questions if not specified

    logging.info(f"Called for generating questions")
    # Generate interview questions using ChatService
    api_key = "AIzaSyCYutjs2BzQThKnA2q1hDNbZro4Al7N0Dw"  # Replace 'YOUR_API_KEY' with your actual API key
    chat_service = ChatService(api_key)
    interview_questions = chat_service.get_interview_questions(domain, role, difficulty_level, specific_topic, num_questions)

    for i, question in enumerate(interview_questions, start=1):
        print(f"Question {i}: {question['question']}")
        print(f"Answer : {question['answer']}")

    # Return the generated questions as JSON response
    return jsonify({'questions': interview_questions})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
