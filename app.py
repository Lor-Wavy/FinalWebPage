import re
import random
import time
import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS  # Required for browser compatibility
from typing import Dict, List, Any

# --- FLASK SETUP ---
app = Flask(__name__)

CORS(app)

@app.route("/", methods=["GET"])
def hello_world():
    """Simple health check to confirm the service is running and not crashing."""
    return "Marcus Bot Service is running and public."

# --- 1. RESUME DATA STRUCTURES ---

RESUME_DATA = {
    "name": "Technical Professional Marcus Jackson",
    "status": "Currently reviewing for entry-level technical roles.",
    "summary": (
        "Results-oriented and highly motivated technical professional seeking an entry-level position where "
        "Marcus can apply his hands-on experience in building and troubleshooting personal computers and leveraging "
        "the skills acquired from his Bachelor of Science in Computer Technology. Marcus is eager to learn new "
        "technologies and contribute to a team environment."
    ),
    "skills": (
        "Key skills include Customer Service, Troubleshooting, Communication, "
        "Custom PC Building (Closed Case / Open Air), Operating Systems (Windows / MacOS / Linux), "
        "and Network Troubleshooting."
    ),
    "experience": (
        "Marcus has experience as a Cashier/Customer Service at Cinemark and Jackson Bakery Curbside Cupcakes. "
        "He also served as a Summer Camp Mentor and an Enrichment Coordinator (Student Mentor) at the "
        "Latin American Youth Center, teaching computer components and basic network technology."
    ),
    "education": (
        "Marcus is completing a Bachelor of Science in Computer Technology from Bowie State University (2025). "
        "He also hold Cisco Credentials in Exploring IoT and Exploring Networking with Cisco Packet Tracer."
    ),
    "tech_stack": (
        "Proficient in these: "
        "Operating Systems: Windows 10 & 11, MacOS, Red Hat Linux 9.x, Ubuntu, Alma, Rocky, iPhoneOS, iPadOS. "
        "Software: MS Office 365, FTP, TELNET, HTML, Borne Shell, Python, PowerShell, Java, and SQL. "
        "Hardware: Intel and AMD compatible PCs, Apple Computers, Crypto Mining Builds and ASICs."
    ),
    "contact_information": (
        "Email: Marcusjr1727@outlook.com, "
        "Phone Number: 410-299-4083, "
        "The Best Way to Reach Marcus: Email"
    ),
    "fallback": "I'm sorry, I can only answer questions about Marcus's summary, skills, experience, education, or status. Please try rephrasing your question or type 'start guided qa' for a tour."
}

# Intent mapping using more detailed regex (Simulating Intent Recognition)
INTENT_MAPPING = {
    'greeting': r'\b(hello|hi|hey|greetings)\b',
    'goodbye': r'\b(bye|thanks|thank you|goodbye|cya|exit|quit)\b',
    'query_summary': r'\b(summary|objective|seeking|tell me about marcus|what job marcus looking for|what is marcus looking for)\b',
    'query_skills': r'\b(skills|expertise|proficient|what skills does marcus have| what expertise does marcus have)\b',
    'query_experience': r'\b(experience|job|role|worked|what experiences does marcus have)\b',
    'query_education': r'\b(education|degree|school|credentials|university|what is the highest level of education that marcus has|what school did/does marcus attend)\b',
    'query_tech_stack': r'\b(what software does marcus know how to use|what hardware does marcus know how to use|what os/operating systems does marcus know|what languages does marcus know how to use|software|os|hardware|tech stack)\b',
    'query_contact_information': r'\b(what is the best way to reach marcus|what is marcus email| what is marcus phone number|contact information|email|phone|phone number|contact)\b',
    'query_status': r'\b(status|available|next step|hiring)\b',
    'start_guided_qa': r'\b(start|guided|tell me more|start guided qa|start guided|guided qa|guided q&a|next)\b'
}

# Guided Q&A Flow
GUIDED_QA_FLOW = [
    {"intent_key": "summary",
     "question": "Starting the Guided Q&A. Marcus's summary is: {summary}. What key skills support this goal?"},
    {"intent_key": "skills",
     "question": "Key skills are: {skills}. Can you elaborate on the practical experience he has with these skills?"},
    {"intent_key": "experience",
     "question": "His experience includes mentorship and service roles: {experience}. What formal education supports his technical background?"},
    {"intent_key": "education",
     "question": "His education includes: {education}. What specific software or hardware knowledge do they possess beyond his degree?"},
    {"intent_key": "tech_stack",
     "question": "Tech stack details are: {tech_stack}. Finally, how can we best contact Marcus?"},
    {"intent_key": "contact_information",
     "question": "This is Marcus's contact information: {contact_information}. This concludes the guided tour. Feel free to ask any other questions or type 'bye' to exit."}
]

# --- CHATBOT STATE MANAGEMENT (Global variable for guided flow state) ---
current_guided_index = -1


# --- CHATBOT LOGIC FUNCTIONS ---

def get_data_key_from_intent(intent_key: str) -> str:
    """Converts a query intent (e.g., 'query_skills') to a RESUME_DATA key (e.g., 'skills')."""
    return intent_key.replace("query_", "")


def handle_guided_qa(user_input: str) -> str:
    """Handles the stateful, step-by-step Guided Q&A flow."""
    global current_guided_index

    stop_triggers = ["stop", "end", "exit", "no", "bye"]
    if any(trigger in user_input.lower() for trigger in stop_triggers) and current_guided_index != -1:
        current_guided_index = -1
        return "Guided tour ended. Feel free to ask any specific question about Marcus's background."

    # Move to the next step
    if current_guided_index == -1:
        # Start the flow
        current_guided_index = 0
    elif current_guided_index < len(GUIDED_QA_FLOW) - 1:
        # Continue to the next step
        current_guided_index += 1
    else:
        # Flow finished
        current_guided_index = -1
        return "The Guided Q&A is complete. Please ask any final questions or type 'bye' to exit."

    # Get the current step's question and data key
    step = GUIDED_QA_FLOW[current_guided_index]
    data_key = step["intent_key"]
    question_template = step["question"]

    # Retrieve the relevant data and format the question
    data_value = RESUME_DATA.get(data_key, "data not found.")

    # Substitute the data into the question placeholder
    response = question_template.format(**{data_key: data_value})

    return response


def process_user_input(user_input: str) -> str:
    """The main brain of the chatbot, recognizing intent and providing the response."""
    global current_guided_index

    # 1. Check for Guided Q&A state first
    if current_guided_index != -1:
        return handle_guided_qa(user_input)

    # 2. Check for intents
    for intent, pattern in INTENT_MAPPING.items():
        if re.search(pattern, user_input.lower()):

            # --- Specific Actions based on Intent ---

            if intent == 'greeting':
                return f"Hello! I am the {RESUME_DATA['name']} Resume Assistant. I can answer questions about his summary, skills, experience, education, tech stack, or status. You can also type 'start guided qa' for a step-by-step tour."

            elif intent == 'goodbye':
                return "Thank you for reviewing Marcus's qualifications. Have a productive day!"

            elif intent == 'start_guided_qa':
                return handle_guided_qa(user_input)

            # --- Standard Data Queries ---
            data_key = get_data_key_from_intent(intent)

            if data_key in RESUME_DATA:
                return RESUME_DATA[data_key]

    # 3. Fallback/Error Handling
    return RESUME_DATA["fallback"]


# --- FLASK ROUTE ---

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint for the frontend to send user messages."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"response": "Invalid request: 'message' field missing."}), 400

        user_message = data['message']
        bot_response = process_user_input(user_message)

        return jsonify({"response": bot_response})

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return jsonify({"response": "An internal server error occurred."}), 500


# --- RUNNING THE APP ---

if __name__ == '__main__':
    # Running on port 5000 as defined in the frontend JS
    print("Marcus Jackson Resume Chatbot Backend running on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server.")

    app.run(debug=True, port=5000)
