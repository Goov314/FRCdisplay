import streamlit as st
import requests
import pandas as pd
import datetime
from getdata import getteamdata, getcompetitions, getschedule, getteamrank, displayteamdata, displayschedule, gettopteams, displayrankings

token = st.secrets['TOKEN']
st.title("FRC Display")
year = str(datetime.datetime.now().year)

team = st.text_input("Team Number", 
          value=(st.query_params.team if "team" in st.query_params else None), 
          placeholder="1234")


if team:
  st.query_params.team = team

  teamdata = getteamdata(team, year)
  st.write("Team " + team + ", " + teamdata["nameShort"] + ", from " + teamdata["schoolName"] + " in " + teamdata["city"] + ", " + teamdata["stateProv"] + ", " + teamdata["country"] + ". Rookie Year: " + str(teamdata["rookieYear"]))
  
  currentevent, eventstartdate, eventenddate = getcompetitions(team, year)
  
  level_list = ["Qualification", "Playoff"]
  levelindex = level_list.index(st.query_params.level) if "level" in st.query_params else 0
  level = st.selectbox("Level:", level_list, index=levelindex)
  if level:
      st.query_params.level = level

  if currentevent and level:
    
    rankdata = getteamrank(team, year, currentevent, level)
    scheduledf, teamrp = getschedule(team, year, currentevent, level)

    displayteamdata(rankdata, teamrp)

    displayschedule(team, eventstartdate, eventenddate, scheduledf)
    
    rankingdf = gettopteams(team, year, currentevent, level)
    
    displayrankings(team, rankingdf)
