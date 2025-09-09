from flask import Flask, render_template, request, redirect, url_for, session
from flask import g
import os

app = Flask(__name__)
# Prefer environment variable for sessions in production (Vercel dashboard -> Settings -> Environment Variables)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me')

# Privacy quiz questions
quiz_questions = {
    "1": {
        "quiz_id": "1",
        "question": "What kind of organization are you?",
        "options": [
            {"label": "Healthcare or Related"},
            {"label": "Education Institution"},
            {"label": "Business with Customers"},
            {"label": "Nonprofit or Research"}
        ],
        "next_question": "2"
    },
    "2": {
        "quiz_id": "2",
        "question": "Where will your data be stored or used?",
        "options": [
            {"label": "On many user devices like phones or laptops"},
            {"label": "In one place like a server or computer"}
        ],
        "next_question": "3"
    },
    "3": {
        "quiz_id": "3",
        "question": "Will the data be transferred across international borders?",
        "options": [
            {"label": "U.S. - No transfers"},
            {"label": "U.S. - Yes transfers"},
            {"label": "EU - No transfers"},
            {"label": "EU - Yes transfers"},
            {"label": "Other Countries - No transfers"},
            {"label": "Multiple Countries - Yes transfers"}
        ],
        "next_question": "4"
    },
    "4": {
        "quiz_id": "4",
        "question": "Do you need to do calculations or run models on data while it's still encrypted?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": "5"
    },
    "5": {
        "quiz_id": "5",
        "question": "Is there a trusted person or organization managing the data safely?",
        "options": [{"label": "Yes, I trust someone"}, {"label": "No, I don’t trust anyone"}],
        "next_question": "6"
    },
    "6": {
        "quiz_id": "6",
        "question": "How sensitive is the data you're working with?",
        "options": [
            {"label": "Very sensitive (health, finances, identity)"},
            {"label": "Somewhat sensitive (emails, surveys)"},
            {"label": "Not sensitive at all"}
        ],
        "next_question": "7"
    },
    "7": {
        "quiz_id": "7",
        "question": "Who should be able to see the real, unprotected data?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": "8"
    },
    "8": {
        "quiz_id": "8",
        "question": "Are you working with other organizations that don’t want to share their raw data?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": "9"
    },
    "9": {
        "quiz_id": "9",
        "question": "Do you need to control access to the data based on roles (like “only nurses” or “only HR”)?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": "10"
    },
    "10": {
        "quiz_id": "10",
        "question": "What matters more for your data analysis?",
        "options": [
            {"label": "Protecting people’s info while showing trends"},
            {"label": "Keeping full accuracy"}
        ],
        "next_question": "11"
    },
    "11": {
        "quiz_id": "11",
        "question": "Will this data be combined with other data from different sources?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": "12"
    },
    "12": {
        "quiz_id": "12",
        "question": "Do you need your system to run fast and use very little computing power?",
        "options": [{"label": "Yes"}, {"label": "No"}],
        "next_question": None
    }
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/quiz_start', methods=['GET', 'POST'])
def quiz_start():
    if request.method == 'POST':
        session['responses'] = {}
        return redirect(url_for('quiz', quiz_id="1"))
    return render_template('quiz_start.html')

@app.route('/quiz/<quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):
    question = quiz_questions.get(quiz_id)
    if not question:
        return redirect(url_for('quiz_start'))

    if request.method == 'POST':
        answer = request.form.get('answer')
        if not answer:
            return render_template('quiz.html', question=question, question_number=int(quiz_id), total_questions=len(quiz_questions), errors={"answer": "Please select an answer."})
        
        responses = session.get('responses', {})
        responses[quiz_id] = answer
        session['responses'] = responses

        next_id = question.get('next_question')
        if next_id:
            return redirect(url_for('quiz', quiz_id=next_id))
        else:
            return redirect(url_for('quiz_results'))

    return render_template('quiz.html', question=question, question_number=int(quiz_id), total_questions=len(quiz_questions), errors={})

@app.route('/quiz_results')
def quiz_results():
    responses = session.get('responses', {})
    results = []

    for quiz_id, answer in responses.items():
        q = quiz_questions[quiz_id]
        results.append({
            "question": q["question"],
            "user_answer": answer
        })

    return render_template("quiz_results.html", results=results)

@app.route('/recommend')
def recommend():
    responses = session.get('responses', {})

    recommended_method = "anon"  

    if (
        "4" in responses and responses["4"] == "Yes" and
        "5" in responses and responses["5"] == "No, I don’t trust anyone" and
        "6" in responses and responses["6"] == "Very sensitive (health, finances, identity)"
    ):
        recommended_method = "he"
    elif "10" in responses and responses["10"] == "Protecting people’s info while showing trends":
        recommended_method = "dp"
    elif "1" in responses and responses["1"] == "Nonprofit or Research":
        recommended_method = "fl"
    elif "3" in responses and responses["3"] == "Multiple Countries - Yes transfers":
        recommended_method = "crypto"


    return redirect(url_for('privacy_method', method=recommended_method))


@app.route('/recommend/<method>')
def privacy_method(method):
    template_map = {
        "he": "recommend_he.html",
        "dp": "recommend_dp.html",
        "crypto": "recommend_crypto.html",
        "anon": "recommend_anon.html",
        "fl": "recommend_fl.html"
    }
    return render_template(template_map.get(method, "recommend_anon.html"))


@app.route('/legal_recommendation')
def legal_recommendation():
    responses = session.get('responses', {})
    applicable_laws = []

    # Identify legal frameworks based on quiz answers
    location_answer = responses.get("3", "").lower()
    org_type = responses.get("1", "").lower()

    # GDPR: EU data, international transfers, or strict compliance scenarios
    if "eu" in location_answer or "multiple" in location_answer:
        applicable_laws.append("GDPR")

    # HIPAA: Healthcare orgs
    if "healthcare" in org_type:
        applicable_laws.append("HIPAA")

    # CCPA/CPRA: California or U.S. business
    if "u.s." in location_answer:
        applicable_laws.append("CCPA/CPRA")

    # LGPD: Brazil mentioned or implied by cross-border + multiple countries
    if "brazil" in location_answer or "multiple" in location_answer:
        applicable_laws.append("LGPD")

    # If no strong match, just say: you may need to consult legal guidance
    if not applicable_laws:
        applicable_laws.append("General Guidance")

    return render_template("recommend_law.html", laws=applicable_laws)



if __name__ == '__main__':
    app.run(debug=True)
