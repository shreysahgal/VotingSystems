from flask import Flask, render_template, request, flash, redirect, session
# from RankVoting import PreferenceSchedule, Aggregator
import os, csv
from preference_schedule import PreferenceSchedule, Aggregator

app = Flask(__name__)
app.secret_key = 'verysecret'.encode('utf-8')

def matrix_to_table(arr):
    html  = "<table class='table' style='border:1px solid black;'><thead class='thead-dark'><tr>"
    for i in arr[0]:
        html += "<th>" + str(i) + "</th>"
    html += "</tr></thead><tbody>"

    for i in arr[1:]:
        html += "<tr>"
        for j in i:
            html += "<td>" + str(j) + "</td>"
        html += "</tr>"
    
    html += "</tbody></table>"

    return html

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file found")
            redirect('/')

        f = request.files['file']

        if f.filename == '':
            flash("No file found")
            redirect('/')

        alldata = [i.split(',') for i in f.read().decode('ASCII').split('\n')]
        cands = alldata[0]
        prefarr = alldata[1:]

        if [''] in prefarr:
            prefarr.remove([''])

        prefsched = PreferenceSchedule(cands, prefarr)

        arr = prefsched.prettyarr()
        

        session['candidates'] = prefsched.get_candidates()
        session['prefarr'] = prefsched.get_prefarr()

        table = matrix_to_table(arr)
        
        return render_template("index.html", table=table, file=f)
    else:
        return render_template('fileinput.html')

@app.route('/analyze/<method>', methods=['GET'])
def analyze(method):
    prefsched = PreferenceSchedule(session['candidates'], session['prefarr'])
    aggr = Aggregator(prefsched)
    if method == "plurality":
        (counts, winners) = aggr.plurality()

        tablearr = [[k, counts[k]] for k in counts]
        tablearr.insert(0, ['Candidate', '1st Place Votes'])
        table = matrix_to_table(tablearr)

        return render_template("plurality.html", winner=', '.join(winners), table=table)
    elif method == "bordacount":
        (counts, winners) = aggr.borda_count()

        tablearr = [[k, counts[k]] for k in counts]
        tablearr.insert(0, ['Candidate', 'Borda Count Points'])
        table = matrix_to_table(tablearr)

        return render_template("bordacount.html", table=table, winner=', '.join(winners))
        
    elif method == "instantrunoff":
        (progress, winner) = aggr.instant_runoff()

        html = ""
        for i in progress:
            html += "<h4>Round %d</h4>" % i[0]
            counts = i[1]
            tablearr = [[k, counts[k]] for k in counts]
            tablearr.insert(0, ['Candidate', '1st Place Votes'])
            html += matrix_to_table(tablearr)
            html += "<br>"
        return render_template('instantrunoff.html', table=html, winner=winner)
    
    elif method == "condorcet":
        (counts, winners) = aggr.condorcet_winner()

        tablearr = [[k, counts[k]] for k in counts]
        tablearr.insert(0, ['Candidate', 'Head-to-Head Points'])
        table = matrix_to_table(tablearr)

        return render_template("condorcet.html", table=table, winner=', '.join(winners))
    
    elif method == "approval":
        (counts, winners) = aggr.top2approval()

        tablearr = [[k, counts[k]] for k in counts]
        tablearr.insert(0, ['Candidate', 'Approval Votes'])
        table = matrix_to_table(tablearr)

        return render_template("approval.html", table=table, winner=', '.join(winners))


if __name__ == '__main__':
    app.run(debug=True)