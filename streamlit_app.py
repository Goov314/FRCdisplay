import streamlit as st
import requests
import pandas as pd
import datetime

st.title("FRC Display")
year = str(datetime.datetime.now().year)
team = st.text_input("Team Number", placeholder="1234")

if team:
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
  eventstartdates = []
  eventenddates = []
  for event in data["Events"]:
      if event["allianceCount"] == "EightAlliance":
          events.append(event["name"])
          currentevents.append(event["code"])
          eventstartdates.append(event["dateStart"])
          eventenddates.append(event["dateEnd"])
  eventselect = st.selectbox("Select Event:", events)
  currentevent = currentevents[events.index(eventselect)]
  eventstartdate = datetime.datetime.fromisoformat(eventstartdates[events.index(eventselect)]).strftime("%B %d %Y")
  eventenddate = datetime.datetime.fromisoformat(eventenddates[events.index(eventselect)]).strftime("%B %d %Y")

  level = st.selectbox("Level:", ("Qualification", "Playoff"))

  if currentevent and level:
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/schedule/{currentevent}?tournamentLevel={level}&teamNumber={team}"
    payload={}
    headers = {
      'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
      'If-Modified-Since': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    scheduledata = response.json()
    #eventstartdate = datetime.datetime.fromisoformat(scheduledata["Schedule"][0]["startTime"]).strftime("%B %d %Y")

    matchnumber = []
    starttime = []
    red1 = []
    red2 = []
    red3 = []
    blue1 = []
    blue2 = []
    blue3 = []
    score = []
    rp = []
    matchdata = [red1, red2, red3, blue1, blue2, blue3]
    with st.spinner(text="Fetching Data"):
      for match in scheduledata["Schedule"]:
          matchnumber.append(match["description"])
          matchtime = datetime.datetime.fromisoformat(match["startTime"])
          starttime.append(matchtime.strftime("%A, %I:%M%p"))
          currentmatchnumber = match["matchNumber"]
          url = f"https://frc-api.firstinspires.org/v3.0/{year}/scores/{currentevent}/{level}?matchNumber={currentmatchnumber}"
          payload={}
          headers = {
           'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
           'If-Modified-Since': ''
          }
          response = requests.request("GET", url, headers=headers, data=payload)
          matchdatajson = response.json()
          bluealliance = matchdatajson["MatchScores"][0]["alliances"][0]
          redalliance = matchdatajson["MatchScores"][0]["alliances"][1]
          score.append("Red: " + str(redalliance["totalPoints"]) + " Blue: " + str(bluealliance["totalPoints"]))
          rp.append("Red: " + str(redalliance["rp"]) + " Blue: " + str(bluealliance["rp"]))

          for i in range(len(match["teams"])): 
              matchdata[i].append(str(match["teams"][i]["teamNumber"]))
            
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/rankings/{currentevent}?teamNumber={team}"
    payload={}
    headers = {
      'Authorization': 'Basic Z29vdjMxNDo0MWM3NGY2My03ODEzLTQ5OTMtODFjNS1hMTZjMzM4NTk1YWI=',
      'If-Modified-Since': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    rankdata = response.json()

    st.write("Team: " + team)
    st.write("Rank: " + str(rankdata["Rankings"][0]["rank"]))
    st.write("W/T/L: " + str(rankdata["Rankings"][0]["wins"]) + "/" + str(rankdata["Rankings"][0]["ties"]) + "/" + str(rankdata["Rankings"][0]["losses"]))
    st.write("Matches Played: " + str(rankdata["Rankings"][0]["matchesPlayed"]))
    st.write("Qualification Average Points: " + str(rankdata["Rankings"][0]["qualAverage"]))

    # st.write("Rank: " + str(rankdata["Rankings"][0]["rank"]) + " --- " + "W/T/L: " + str(rankdata["Rankings"][0]["wins"]) + "/" + str(rankdata["Rankings"][0]["ties"]) + "/" + str(rankdata["Rankings"][0]["losses"]) + " --- " + "Matches Played: " + str(rankdata["Rankings"][0]["matchesPlayed"]) + " --- " + "Qualification Average Points: " + str(rankdata["Rankings"][0]["qualAverage"]))

    scheduledf = pd.DataFrame({
        'Match Number': matchnumber,
        'Start Time': starttime,
        'Score': score,
        'Ranking Points': rp,
        'Red 1': red1,
        'Red 2': red2,
        'Red 3': red3,
        'Blue 1': blue1,
        'Blue 2': blue2,
        'Blue 3': blue3

    })
    st.subheader("Event Schedule (" + eventstartdate + " - " + eventenddate + ")")

    def highlight_team(s):
        color = '#262730' if s == str(team) else ''
        return f'background-color: {color}'

    st.dataframe(scheduledf.style.applymap(highlight_team))
