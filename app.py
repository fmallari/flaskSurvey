from flask import Flask, session, request, render_template, redirect, make_response, flash 
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys 

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECT'] = False 

debug = DebugToolbarExtension(app)

@app.route("/")
def title_page():
    """title of the survey, the instructions and button to start survey"""

    return render_template("pick_survey.html", surveys=surveys)

@app.route("/", methods=["POST"])
def pick_survey():
    # Select survey

    survey_id = request.form['survey_code']

    # Do not allow survey to be retaken until cookies time out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

        survey = surveys[survey_id]
        session[CURRENT_SURVEY_KEY] = survey_id
        
        return render_template("survey_start.html", survey=survey)

@app.route("/begin", methods=["POST"])
def start_survey():
        # Clear the session of responses

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
        # Save responses and redirect to next question 

    choice = request.form['answer']
    text = request.form.get("text", "")

        # add this response to list in session

    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})

        # add this response to the session

    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        # then they have answered all questions 
        return redirect("/complete")

    else: 
        return redirect(f"/questions/{len(responses)}")

@app.route("/questions/<int:qid>")
def show_question(qid): 
    """Display current question"""

    responses = session.get(RESPONSES_KEY)
    survey_code = session(CURRENT_SURVEY_KEY)
    survey = surveys[survey_code]

    if (responses is None): 
        # Attempting to access question page too soon
        return redirect("/")

    if(len(responses) != qid):
        # Attemping to access questions our of order 
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    questions = survey.questions[qid]

    return render_template("questions.html", question_num=qid, question=question)

@app.route("/complete")
def say_thanks():
    """Thank user and list responses"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("complete.html", survey=survey, responses=responses)

    #Set cookie noting this survey is done so they can't redo it

    response = make_response(html)
    responses.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response 



