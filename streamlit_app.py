import streamlit as st
import requests
import pandas as pd
import datetime
from PIL import Image
from streamlit_autorefresh import st_autorefresh as autoref

from getdata import getteamdata, getcompetitions, getschedule, getteamrank, displayteamdata, displayschedule, gettopteams, displayrankings, getdistrictrank

st.set_page_config(page_title="FRC Display", page_icon=Image.open("FRCdisplayicon.png"), layout="centered", initial_sidebar_state="expanded", menu_items=None)
st.logo(Image.open("FRCexpandedicon.png"), size="large", icon_image=Image.open("FRCdisplayicon.png"))

token = st.secrets['TOKEN']
st.title("FRC Display")
year = str(datetime.datetime.now().year)

team = st.sidebar.text_input("Team Number", 
          value=(st.query_params.team if "team" in st.query_params else None), 
          placeholder="1234")

if team:
  st.query_params.team = team

  teamdata = getteamdata(team, year)
  st.write("Team **" + team + "**, **" + teamdata["nameShort"] + "**, from **" + teamdata["schoolName"] + "** in **" + teamdata["city"] + "**, " + teamdata["stateProv"] + ", " + teamdata["country"] + ". Rookie Year: " + str(teamdata["rookieYear"]))
  districtcode = teamdata["districtCode"]

  currentevents = []
  events = []
  currentevent, eventinfo, events, currentevents = getcompetitions(team, year)
  
  level_list = ["Qualification", "Playoff"]
  levelindex = level_list.index(st.query_params.level) if "level" in st.query_params else 0
  level = st.sidebar.selectbox("Level:", level_list, index=levelindex)
  if level:
      st.query_params.level = level

  if currentevent and level:
    
    rankdata = getteamrank(team, year, currentevent, level)
    scheduledf, teamrp = getschedule(team, year, currentevent, level)

    displayteamdata(rankdata, teamrp)

    displayschedule(team, eventinfo, scheduledf)
    
    rankingdf = gettopteams(team, year, currentevent, level)
    
    displayrankings(team, rankingdf)

    getdistrictrank(team, year, districtcode, events, currentevents)



checkbox = st.sidebar.checkbox("Auto Refresh?", value=st.query_params.refresh if "refresh" in st.query_params else 0)
if checkbox:
  autoref(interval=60000)
  st.query_params.refresh = checkbox
