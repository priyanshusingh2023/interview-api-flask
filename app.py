from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Your ChatService class definition here

class ChatService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + self.api_key

    def get_interview_questions(self, domain, role, difficulty_level, specific_topic, num_questions=10):
        try:
            headers = {'Content-Type': 'application/json'}

            prompt = f"You are a {role} in the {domain} domain preparing interview questions."

            prompt += f"\n\nGenerate {num_questions} interview questions along with answers for the topic of {specific_topic} with difficulty level {difficulty_level}."
            prompt += f"\nReturn your response in an array of Json Objects. Each Object will have question and answer keys. "
            prompt += f"Below is the example structure that you should return your response: "
            prompt += f'''[
              {{
                "question": "What is @SpringBootApplication annotation used for in Spring Boot?",
                "answer": "The @SpringBootApplication annotation is a convenience annotation that combines @Configuration, @EnableAutoConfiguration, and @ComponentScan annotations. It is used to mark a class as the main Spring Boot application class and is typically placed on the main class of the application."
              }},
              {{
                "question": "Explain the concept of dependency injection in Spring Boot.",
                "answer": "Dependency injection is a technique where an object is given its dependencies by external code rather than creating them itself. In Spring Boot, dependency injection is achieved through annotations like @Autowired which allows the Spring IoC container to automatically wire dependencies into beans."
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
    num_questions = request_data.get('num_questions', 10)  # Default to 10 questions if not specified

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
