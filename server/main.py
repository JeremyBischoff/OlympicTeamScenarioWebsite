from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, origins='*')

# team scenario python file
import pandas as pd
import itertools
import math
import numpy as np

# import from webscrape.py
from webscrape import scrapeData, createGymnastData
from collections import defaultdict

eventKey = ["FX", "PH", "SR", "V", "PB", "HB"]

champsURL = "https://myusagym.com/meets/past/89744/results/256676/" 
trialsURL = "https://myusagym.com/meets/past/90017/results/256770/"

urls = [champsURL, trialsURL]
gymnastData = []

for url in urls:
    driver = scrapeData(url)
    # champs data - an array of two elements: day 1 scores and day 2 scores
    gymnastCompetitionData = createGymnastData(driver)
    gymnastData.extend(gymnastCompetitionData)
driver.quit()

# do the logic to get top three scores and average them

#def calculateAverageTopThree(data):
    # Initialize a dictionary to store all scores for each gymnast
#    all_scores = defaultdict(lambda: defaultdict(list))

    # Gather all scores for each gymnast on each event
#    for entry in data:
#        for gymnast, scores in entry.items():
#            for event_idx, score in enumerate(scores):
#                all_scores[gymnast][event_idx].append(score)

    # Calculate the average of the top three scores for each event
#    average_top_three_scores = {}
#    for gymnast, events in all_scores.items():
#        average_scores = []
#        for event_idx, scores in events.items():
#            top_three_scores = sorted(scores, reverse=True)[:3]
#            average_top_three = sum(top_three_scores) / len(top_three_scores) if top_three_scores else 0
#            average_scores.append(average_top_three)
#        average_top_three_scores[gymnast] = average_scores

#    return average_top_three_scores

#averagedScores = calculateAverageTopThree(gymnastData)

def calculateAverageFourScores(data):
    # Initialize a dictionary to store all scores for each gymnast
    all_scores = defaultdict(lambda: defaultdict(list))

    # Gather all scores for each gymnast on each event
    for entry in data:
        for gymnast, scores in entry.items():
            for event_idx, score in enumerate(scores):
                all_scores[gymnast][event_idx].append(score)

    # Calculate the average of the scores for each event
    average_event_scores = {}
    for gymnast, events in all_scores.items():
        average_scores = []
        for event_idx, scores in events.items():
            average_score = round((sum(scores) / len(scores)), 3) if scores else 0.0
            average_scores.append(average_score)
        average_event_scores[gymnast] = average_scores

    return average_event_scores

averagedScores = calculateAverageFourScores(gymnastData)

initial_scores = averagedScores

# team scenario class
class TeamScenario:
    def __init__(self, teamScore, fiveManTeam, eventInfo):
        self.teamScore = teamScore
        self.fiveManTeam = fiveManTeam
        self.eventInfo = eventInfo

    def printTeamScore(self):
        print(self.teamScore)

    def printFiveManTeam(self):
        print(self.fiveManTeam)

    def printEventInfo(self):
        print(self.eventInfo)

    def printInfo(self):
        # makes it nicer to print out
        string = ""
        #shouldPrint = False
        for gymnast in self.fiveManTeam:
            #if gymnast == 'Jeremy Bischoff':
            #    shouldPrint = True
            if gymnast != self.fiveManTeam[-1]:
                string += gymnast + ", "
            else:
                string += gymnast
        # prints out all info with clean formatting
        #if shouldPrint:

        print("Team Score:", self.teamScore, "Team:", string)
        print("Event Info:", self.eventInfo)
        print()

def runTeamScenario(scores, numTeamScenarios):

    fiveManTeams = itertools.combinations(scores.keys(), 5)
    # create an array of TeamScenario classes
    teamScenarios = []

    # goes through combinations of five man teams
    for fiveManTeam in fiveManTeams:
        eventInfo = {}
        teamScenario = TeamScenario(0, fiveManTeam, eventInfo)

        # iterates through each event
        for event in range(6):
            threeManLineups = itertools.combinations(fiveManTeam, 3)
            eventCombinedScores3 = {}

            # iterates through all possible three man lineups
            for threeManLineup in threeManLineups:
                eventScore = sum(scores[gymnast][event] for gymnast in threeManLineup)
                eventCombinedScores3[round(eventScore, 2)] = threeManLineup

            # gets max event score and prints it out
            maxEventScore = max(eventCombinedScores3)
            event_key = eventKey[event] + ": " + str(maxEventScore)
            eventInfo[event_key] = eventCombinedScores3[maxEventScore]

        teamScore5 = sum(float(eventScore.split(": ")[1]) for eventScore in eventInfo)
        teamScenario.teamScore = round(teamScore5, 2)
        teamScenarios.append(teamScenario)
    
    sortedTeamScenarios = sorted(teamScenarios, key=lambda x: x.teamScore, reverse=True)

    return sortedTeamScenarios[:numTeamScenarios]
        

# team scenario app route
@app.route("/teamscenario/scores", methods=['GET'])
def returnScores():
    return jsonify(initial_scores)

# get scores from frontend
@app.route("/teamscenario/submit", methods=['POST'])
def updateScoresOnSubmit():
    data = request.json
    inputScores = data.get("inputScores")
    numTeamScenarios = data.get("numTeamScenarios")

    for gymnast in inputScores:
        inputScores[gymnast] = [0 if math.isnan(score) else score for score in inputScores[gymnast]]
    topScenarios = runTeamScenario(inputScores, numTeamScenarios)
    results = [{"teamScore": teamScenario.teamScore, "fiveManTeam": teamScenario.fiveManTeam, "eventInfo": teamScenario.eventInfo} for teamScenario in topScenarios]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=8080)