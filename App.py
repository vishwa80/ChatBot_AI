from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database (change to MySQL/PostgreSQL if needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define database models
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(500), nullable=False)
    bot_response = db.Column(db.String(500), nullable=False)

class UserEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Chatbot response function
def chatbot_response(user_input):
    responses = {
        "hello": "Hi there! How can I assist you today?",
        "courses": "We offer courses in Engineering, Management, and Computer Science.",
        "admission": "You can apply online through our website.",
        "email": "Thank you! We will use this email for updates."
    }
    return responses.get(user_input.lower(), "Sorry, I didn't understand that.")

# Route to handle chat messages
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Check if the message contains an email
    if "@" in user_message and "." in user_message:
        # Save email in the database
        existing_email = UserEmail.query.filter_by(email=user_message).first()
        if not existing_email:
            new_email = UserEmail(email=user_message)
            db.session.add(new_email)
            db.session.commit()
        return jsonify({"reply": "Thank you! Your email has been saved."})

    # Generate bot response
    response = chatbot_response(user_message)

    # Save chat history
    new_chat = ChatHistory(user_message=user_message, bot_response=response)
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({"reply": response})

# Route to get chat history
@app.route("/history", methods=["GET"])
def get_chat_history():
    chats = ChatHistory.query.all()
    chat_data = [{"user": chat.user_message, "bot": chat.bot_response} for chat in chats]
    return jsonify({"history": chat_data})

if __name__ == "__main__":
    app.run(debug=True)
