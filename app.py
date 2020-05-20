from flask import Flask, render_template, request, flash, redirect, session
from RankVoting import PreferenceSchedule, Aggregator

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        if 'file' not in request.files:
            flash("No file found")
            redirect('/')
        file = request.files['file']

        if file.filename == '':
            flash("No file found")
            redirect('/')

        try:
            session.prefsched = PreferenceSchedule(file)
        except:
            flash("Error with file.")
            redirect('/')
        


if __name__ == '__main__':
    app.run(debug=True)