import re
import random
import time
import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS # Required for browser compatibility


# --- 1. Resume Knowledge Base (Data from Resume Copy.docx) ---
# Data is hardcoded here to simulate a successful API or database lookup.
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
    "fallback": "I can only answer questions about the Marcus's summary, skills, experience, education, or status. Please try rephrasing your question."
}

# Intent mapping using more detailed regex (Simulating Intent Recognition)
INTENT_MAPPING = {
    'greeting': r'\b(hello|hi|hey|greetings)\b',
    'goodbye': r'\b(bye|thanks|thank you|goodbye|cya)\b',
    'query_summary': r'\b(summary|objective|seeking|tell me about marcus|what job marcus looking for|what is marcus looking for)\b',
    'query_skills': r'\b(skills|expertise|proficient|what skills does marcus have| what expertise does marcus have)\b',
    'query_experience': r'\b(experience|job|role|worked|what experiences does marcus have)\b',
    'query_education': r'\b(education|degree|school|credentials|university|what is the highest level of education that marcus has|what school did/does marcus attend)\b',
    'query_tech_stack': r'\b(what software does marcus know how to use|what hardware does marcus know how to use|what os/operating systems does marcus know|what languages does marcus know how to use|software|os|hardware)\b',
    'query_contact_information': r'\b(what is the best way to reach marcus|what is marcus email| what is marcus phone number|contact information|email|phone|phone number)\b',
    'query_status': r'\b(status|available|next step|hiring)\b',
    'start_guided_qa': r'\b(start|guided|tell me more|start guided qa|start guided|guided qa|guided q&a)\b'  # Feature B
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
     "question": "Tech stack details are: {tech_stack}. This concludes the guided tour. What else can I retrieve?"},
    {"intent_key": "contact_information",
     "question": "This is marcus's contact information: {contact_information}. This concludes the guided tour. What else can I retrieve?"}
]


# --- 2. Chatbot Core Logic ---

class ResumeQABot:
    def __init__(self, resume_data):
        self.data = resume_data
        self.state = {"in_guided_qa": False, "qa_step": 0}
        self.intent_map = INTENT_MAPPING

    def _recognize_intent(self, text):
        """Simulates NLP Intent Recognition using regex."""
        text_lower = text.lower()
        for intent, pattern in self.intent_map.items():
            if re.search(pattern, text_lower):
                return intent
        return 'unknown'

    def _handle_single_query(self, intent):
        """Feature A & C: Single-turn information retrieval."""
        if intent == 'query_status':
            return f"Marcus's current status is: {self.data['status']}"

        # Maps query_summary -> summary, query_skills -> skills, etc.
        key = intent.replace('query_', '')

        if key in self.data:
            return self.data[key]

        return self.data['fallback']

    def _start_guided_qa(self):
        """Feature B: Starts the multi-turn session."""
        self.state["in_guided_qa"] = True
        self.state["qa_step"] = 0

        # Start with the first question, injecting the first piece of data
        first_step = GUIDED_QA_FLOW[0]
        self.state["qa_step"] += 1

        # Use string formatting to inject data into the question text
        initial_answer = self.data[first_step['intent_key']]
        return first_step['question'].format(**{first_step['intent_key']: initial_answer})

    def _continue_guided_qa(self, user_input):
        """Feature B: Advances the multi-turn session."""
        current_step_index = self.state["qa_step"]

        # Check for user requesting to stop the guided flow
        if re.search(r'\b(stop|end|exit)\b', user_input.lower()):
            self.state["in_guided_qa"] = False
            self.state["qa_step"] = 0
            return "Guided Q&A session terminated. Ask me any specific question now, or say 'start' to resume the flow."

        # Check if the flow is complete
        if current_step_index >= len(GUIDED_QA_FLOW):
            self.state["in_guided_qa"] = False
            self.state["qa_step"] = 0
            return "The guided Q&A is complete. I've covered all major resume sections. How else can I assist?"

        # Advance to the next question
        next_step = GUIDED_QA_FLOW[current_step_index]
        self.state["qa_step"] += 1

        # Retrieve the relevant data and format the question/answer pair
        answer_key = next_step['intent_key']
        answer = self.data[answer_key]

        # Use the answer to populate the next question prompt
        return next_step['question'].format(**{answer_key: answer})

    def process_input(self, user_input):
        """Main processing method for all user input."""

        if self.state["in_guided_qa"]:
            # Prioritize handling the guided flow continuation
            return self._continue_guided_qa(user_input)

        intent = self._recognize_intent(user_input)

        if intent == 'greeting':
            return random.choice([
                f"Hello! I am the Q&A bot for the {self.data['name']}. What would you like to know about his background?",
                "Hi there! Ask me about Marcus's skills, experience, or education. Or say 'start guided Q&A'."
            ])
        elif intent == 'goodbye':
            return random.choice([
                "Thank you for your interest! Goodbye.",
                "I hope the information was helpful. Farewell!"
            ])
        elif intent == 'start_guided_qa':
            return self._start_guided_qa()
        elif intent.startswith(('query_', 'query_status')):
            return self._handle_single_query(intent)
        elif intent == 'unknown':
            # Graceful error handling
            return self.data['fallback']

        return "System error: Failed to process request."


# --- 3. Execution in PyCharm Console ---

def run_chatbot_cli():
    """Runs the main command-line interface suitable for PyCharm."""

    bot = ResumeQABot(RESUME_DATA)
    name = bot.data['name']

    print("---------------------------------------------------------")
    print(f"🤖 Welcome! I am the {name} Q&A Bot.")
    print("Running in PyCharm CLI environment.")
    print("I can instantly retrieve information from the Marcus's resume.")
    print("Try asking about: skills, status, or say 'start guided Q&A'.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("---------------------------------------------------------")

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print(f"Bot: {bot.process_input('bye')}")
                break

            # Simulate processing time for better user experience
            time.sleep(0.3)

            response = bot.process_input(user_input)
            print(f"Bot: {response}")

        except EOFError:
            # Handles console closing in some environments
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"Bot: An unexpected error occurred. State reset. ({e})")
            bot.state = {"in_guided_qa": False, "qa_step": 0}  # Reset state


if __name__ == "__main__":
    run_chatbot_cli()