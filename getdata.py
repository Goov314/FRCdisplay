import streamlit as st
import requests
import pandas as pd
import datetime
from PIL import Image
from io import BytesIO
import base64

token = st.secrets['TOKEN']

def getteamdata(team, year):
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/teams?teamNumber={team}"
    payload={}
    headers = {
      'Authorization': token,
      'If-Modified-Since': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response:
      teamdata = response.json()["teams"][0]
      
      districtcode = teamdata["districtCode"]
      rookieyear = teamdata["rookieYear"]

      url = f"https://frc-api.firstinspires.org/v3.0/{year}/avatars?teamNumber={team}"
      payload={}
      headers = {
        'Authorization': token,
        'If-Modified-Since': ''
      }
      response = requests.request("GET", url, headers=headers, data=payload)
      teamavatardata = response.json()["teams"]

      if teamavatardata:

        base64image = teamavatardata[0]["encodedAvatar"]
        bytesimage = base64.b64decode(base64image)
        teamavatar = Image.open(BytesIO(bytesimage))
      else:
        teamavatar = Image.open("FRCdisplayicon.png")

      with st.expander("Team Data"):
        st.write("Team " + team + ", " + teamdata["nameShort"])
        st.write("From " + teamdata["schoolName"] + " in " + teamdata["city"] + ", " + teamdata["stateProv"] + ", " + teamdata["country"])
        st.write("Rookie Year: " + str(teamdata["rookieYear"]))
        st.write("Sponsors: " + str(teamdata["nameFull"].replace("/", ", ")).replace("&", " and "))

      return(districtcode, rookieyear, teamavatar)
    else:
      return("","", Image.open("FRCdisplayicon.png"))

def getcompetitions(team, year):
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/events?eventCode=&teamNumber={team}&districtCode=&excludeDistrict=&weekNumber&tournamentType"
    payload={}
    headers = {
      'Authorization': token,
      'If-Modified-Since': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    events = []
    currentevents = []
    eventinfos = []
    for event in data["Events"]:
      if event["allianceCount"] == "EightAlliance":
        events.append(event["name"])
        currentevents.append(event["code"])
        eventinfos.append("From **" + 
                          datetime.datetime.fromisoformat(event["dateStart"]).strftime("%B %d %Y") + 
                          "** to **" + 
                          datetime.datetime.fromisoformat(event["dateEnd"]).strftime("%B %d %Y") +
                          "** at **" + 
                          event["venue"] + 
                          "** - " + 
                          event["address"] + ", " + 
                          event["city"] + ", " + 
                          event["stateprov"] + ", " + 
                          event["country"])
    
    if "event" in st.query_params and st.query_params.event in events:
        current_index = events.index(st.query_params.event)
    else:
        current_index = 0
        
    eventselect = st.sidebar.selectbox("Select Event:", events, index=current_index)
    if eventselect:
        st.query_params.event = eventselect
    currentevent = currentevents[events.index(eventselect)]
    eventinfo = "**" + eventselect + "** " + (eventinfos[events.index(eventselect)])
    return(currentevent, eventinfo, events, currentevents)

def getschedule(team, year, event, level):
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
      teamrp = 0
      matchdata = [red1, red2, red3, blue1, blue2, blue3]
      url = f"https://frc-api.firstinspires.org/v3.0/{year}/schedule/{event}?tournamentLevel={level}&teamNumber={team}"
      payload={}
      headers = {
        'Authorization': token,
        'If-Modified-Since': ''
      }
      response = requests.request("GET", url, headers=headers, data=payload)
      scheduledata = response.json()

      with st.spinner(text="Fetching Data..."):
        for match in scheduledata["Schedule"]:
          matchnumber.append(match["description"])
          matchtime = datetime.datetime.fromisoformat(match["startTime"])
          starttime.append(matchtime.strftime("%A, %I:%M%p"))
          currentmatchnumber = match["matchNumber"]
          url = f"https://frc-api.firstinspires.org/v3.0/{year}/scores/{event}/{level}?matchNumber={currentmatchnumber}"
          payload={}
          headers = {
            'Authorization': token,
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
            if i <= 2 and str(match["teams"][i]["teamNumber"]) == team:
              teamrp += redalliance["rp"]
            elif i >= 2 and str(match["teams"][i]["teamNumber"]) == team:
              teamrp += bluealliance["rp"]
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
      return(scheduledf, teamrp)

def getteamrank(team, year, event, level):
      url = f"https://frc-api.firstinspires.org/v3.0/{year}/rankings/{event}?teamNumber={team}"
      payload={}
      headers = {
        'Authorization': token,
        'If-Modified-Since': ''
      }
      response = requests.request("GET", url, headers=headers, data=payload)
      rankdata = response.json()
      return(rankdata)

def displayteamdata(rankdata, teamrp):
  if rankdata["Rankings"]:
    with st.expander("Team Event Data"):
      st.write("Rank: " + str(rankdata["Rankings"][0]["rank"]))
      st.write("W/T/L: " + str(rankdata["Rankings"][0]["wins"]) + "/" + str(rankdata["Rankings"][0]["ties"]) + "/" + str(rankdata["Rankings"][0]["losses"]))
      st.write("Matches Played: " + str(rankdata["Rankings"][0]["matchesPlayed"]))
      st.write("Qualification Average Points: " + str(rankdata["Rankings"][0]["qualAverage"]))
      st.write("Total Ranking Points: " + str(teamrp))

def displayschedule(team, eventinfo, scheduledf):
      with st.expander("Event Schedule"):
        st.write(eventinfo)
        def highlight_team(s):
          color = '#262730' if s == str(team) else ''
          return f'background-color: {color}'
        st.dataframe(scheduledf.style.applymap(highlight_team))

def gettopteams(team, year, event, level):
      teamrank = []
      teamnumber = []
      wtl = []
      matchesplayed = []
      avgpoints = []
      url = f"https://frc-api.firstinspires.org/v3.0/{year}/rankings/{event}?top=10"
      payload={}
      headers = {
        'Authorization': token,
        'If-Modified-Since': ''
      }
      response = requests.request("GET", url, headers=headers, data=payload)
      eventrankingdata = response.json()

      for currentteam in eventrankingdata["Rankings"]:
        teamrank.append(str(currentteam["rank"]))
        teamnumber.append(str(currentteam["teamNumber"]))
        wtl.append(str(currentteam["wins"]) + "/" + str(currentteam["ties"]) + "/" + str(currentteam["losses"]))
        matchesplayed.append(str(currentteam["matchesPlayed"]))
        avgpoints.append(str(currentteam["qualAverage"]))
      rankingdf = pd.DataFrame({
      'Rank': teamrank,
      'Team Number': teamnumber,
      'Wins/Ties/Losses': wtl,
      'Average Points': avgpoints,
      'Matches Played': matchesplayed,
      })
      return(rankingdf)

def displayrankings(team, rankingdf):
      def highlight_team(s):
        color = '#262730' if str(s) == str(team) else ''
        return f'background-color: {color}'
      with st.expander("Event Rankings"):
        st.dataframe(rankingdf.style.applymap(highlight_team))

def getdistrictrank(team, year, districtcode, events, eventcodes):
    url = f"https://frc-api.firstinspires.org/v3.0/{year}/rankings/district?teamNumber={team}"
    payload={}
    headers = {
      'Authorization': token,
      'If-Modified-Since': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    districtrankingdata = response.json()  

    if districtrankingdata["districtRanks"]:
      rank = districtrankingdata["districtRanks"][0]["rank"]
      totalrp = districtrankingdata["districtRanks"][0]["totalPoints"]
      qdistrict = districtrankingdata["districtRanks"][0]["qualifiedDistrictCmp"]
      qworlds = districtrankingdata["districtRanks"][0]["qualifiedFirstCmp"]
      event1code = districtrankingdata["districtRanks"][0]["event1Code"]
      event1pts = districtrankingdata["districtRanks"][0]["event1Points"]
      event2code = districtrankingdata["districtRanks"][0]["event2Code"]
      event2pts = districtrankingdata["districtRanks"][0]["event2Points"]
      districtcompcode = districtrankingdata["districtRanks"][0]["districtCmpCode"]
      districtcomppoints = districtrankingdata["districtRanks"][0]["districtCmpPoints"]

      event1 = events[eventcodes.index(event1code)]
      event2 = events[eventcodes.index(event2code)]
      if districtcompcode in eventcodes:
        districtcomp = events[eventcodes.index(districtcompcode)]
      else:
        districtcomp = "N/A"
      qdist = ""
      qworld = ""
      if qdistrict == True:
          qdist = "Yes"
      else:
          qdist = "No"
      if qworlds == True: 
          qworld = "Yes"
      else:
          qworld = "No"

      with st.expander("District Rankings - " + districtcode):
        st.write("District Rank: " + str(rank) + " - Total Ranking Points: " + str(totalrp))
        st.write("Event 1: " + event1 + " - Ranking Points: " + str(event1pts))
        st.write("Event 2: " + event2 + " - Ranking Points: " + str(event2pts))
        st.write("District Event: " + districtcomp + " - Ranking Points: " + str(districtcomppoints))
        st.write("Qualified for District Event: " + qdist + " - Qualified for World Championships: " + qworld)

def getawards(team, year, rookieyear):
    awardyear = []
    awardname = []
    awardata = ""
    with st.spinner(text="Fetching Data..."):
      for currentyear in range(int(year), int(rookieyear) - 1, -1):
        url = f"https://frc-api.firstinspires.org/v3.0/{currentyear}/awards/team/{team}"
        payload={}
        headers = {
          'Authorization': token,
          'If-Modified-Since': ''
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response:
          awarddata = response.json()
          for award in awarddata["Awards"]:
            if currentyear not in awardyear:
              awardyear.append(currentyear)
            else:
              awardyear.append("")
            awardname.append(award["name"])
      if awardyear:
        awarddf = pd.DataFrame({
            'Year': awardyear,
            'Award': awardname,
        })
      with st.expander("Awards"):
        if awardyear:
          st.dataframe(awarddf)
        else:
          st.write(f"Team {team} has not won any awards.")



