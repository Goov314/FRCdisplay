import streamlit as st
import requests
import pandas as pd
import datetime

st.title("FRC Display")
year = str(datetime.datetime.now().year)
team = st.text_input("Team Number", placeholder="1234")

url = f"https://frc-api.firstinspires.org/v3.0/{year}/events?eventCode=&teamNumber={team}&districtCode=&excludeDistrict=&weekNumber&tournamentType"
payload={}
headers = {
  'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
  'If-Modified-Since': ''
}
response = requests.request("GET", url, headers=headers, data=payload)
data = response.json()
events = []
currentevents = []
for event in data["Events"]:
    if event["allianceCount"] == "EightAlliance":
        events.append(event["name"])
        currentevents.append(event["code"])
currentevent = currentevents[events.index(st.selectbox("Select Event:", events))]
level = st.selectbox("Level:", ("Qualification", "Playoff"))

url = f"https://frc-api.firstinspires.org/v3.0/{year}/schedule/{currentevent}?tournamentLevel={level}&teamNumber={team}"
payload={}
headers = {
  'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
  'If-Modified-Since': ''
}
response = requests.request("GET", url, headers=headers, data=payload)
scheduledata = response.json()

matchnumber = []
starttime = []
red1 = []
red2 = []
red3 = []
blue1 = []
blue2 = []
blue3 = []
matchdata = [red1, red2, red3, blue1, blue2, blue3]
for match in scheduledata["Schedule"]:
    matchnumber.append(match["description"])
    starttime.append(str(match["startTime"].split("T")[0]) + " @ " + str(match["startTime"].split("T")[1]))
    for i in range(len(match["teams"])): 
        if str(match["teams"][i]["teamNumber"]) == team:
            matchdata[i].append("**"+str(match["teams"][i]["teamNumber"])+"**")
        else:
            matchdata[i].append(str(match["teams"][i]["teamNumber"]))
        
url = f"https://frc-api.firstinspires.org/v3.0/{year}/rankings/{currentevent}?teamNumber={team}"
payload={}
headers = {
  'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
  'If-Modified-Since': ''
}
response = requests.request("GET", url, headers=headers, data=payload)
rankdata = response.json()

st.write("Rank: " + str(rankdata["Rankings"][0]["rank"]))
st.write("W/T/L: " + str(rankdata["Rankings"][0]["wins"]) + "/" + str(rankdata["Rankings"][0]["ties"]) + "/" + str(rankdata["Rankings"][0]["losses"]))
st.write("Matches Played: " + str(rankdata["Rankings"][0]["matchesPlayed"]))
st.write("Qualification Average Points: " + str(rankdata["Rankings"][0]["qualAverage"]))

# st.write("Rank: " + str(rankdata["Rankings"][0]["rank"]) + " --- " + "W/T/L: " + str(rankdata["Rankings"][0]["wins"]) + "/" + str(rankdata["Rankings"][0]["ties"]) + "/" + str(rankdata["Rankings"][0]["losses"]) + " --- " + "Matches Played: " + str(rankdata["Rankings"][0]["matchesPlayed"]) + " --- " + "Qualification Average Points: " + str(rankdata["Rankings"][0]["qualAverage"]))

scheduledf = pd.DataFrame({
    'Match Number': matchnumber,
    'Start Time': starttime,
    'Red 1': red1,
    'Red 2': red2,
    'Red 3': red3,
    'Blue 1': blue1,
    'Blue 2': blue2,
    'Blue 3': blue3
})
st.markdown("**Event Schedule**")
st.write(scheduledf)
