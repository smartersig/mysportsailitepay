import requests
import csv

import streamlit as st
from st_paywall import add_auth

import pandas as pd
import pickle

from image_loader import render_image

import stripe
from stripe import StripeClient

from sklearn.ensemble import GradientBoostingClassifier

def createCols ():

  cols = []
  if cl:
    cols.append("classMove")
  if da:
    cols.append("daysLto")
  if tr:
    cols.append("TRinrace")
  if jo:
    cols.append("Jockinrace")
  if si:
    cols.append("Sireinrace")
  if pa:
    cols.append("paceFig")

  return cols

############################################

def predModel():

    global cols,decs,horses,trackTimes

    try:

      fileName = "models/"
      for col in decs.columns:
        fileName = fileName + col[0:2]
      fileName = fileName + '.sav'

      with open(fileName, "rb") as f:
        m = pickle.load(f)
        for col in cols:
          decs[col] = pd.to_numeric(decs[col], errors='coerce') # convert from string to numeric or NaN
          decs[col] = decs[col].fillna(m.repNaNs[col])

      preds = m.predict_proba(decs)
      preds = preds[:,1:]
      #preds = np.around(preds,decimals=3)
      ratings = pd.DataFrame()
      ratings['trackTime'] = trackTimes
      ratings['Horse'] = horses
      ratings['Rating'] = preds * 100
      ratings = ratings.sort_values(['trackTime','Rating'], ascending=[True,False])
      with inputs:
        with rescol:
          prevtime = ""
          for index,row in ratings.iterrows():
            if prevtime != row['trackTime']:
              st.markdown('###### ' + '-- ' + row['trackTime'] + ' --')
            line = str(row['Horse']) + "  " + str(round(row['Rating'],3))
            st.write(line)
            prevtime = row['trackTime']
    except Exception as e:
      with inputs:
        with rescol:
          st.write ('Error No Predictors ? ', e)

#########################################

st.set_page_config(layout="wide")

header = st.container()
inputs = st.container(height=None)

with header:
  render_image("MLImage5.png")
  st.title('MySportsAILite (Subscription)')

if not st.experimental_user.is_logged_in:
    st.write("Create your own ratings using MySportsAI Machine Learning models pre trained on 10 years of data")
    st.write("Please log in to access this app")
    if st.button("Log in"):
        st.login("google")
else:
  add_auth(required=True) 

  #decs = pd.read_csv('http://www.smartersig.com/mysportsaisamplepay.csv')

  response = requests.get('http://www.smartersig.com/utils/mysportsaisamplepay.csv', auth=(st.secrets['siguser'], st.secrets['sigpassw']), verify=False)
  decoded_content = response.content.decode('utf-8')
  cr = csv.reader(decoded_content.splitlines(), delimiter=',')
  my_list = list(cr)

  #response = requests.get('http://www.smartersig.com/utils/mysportsaisamplepay.csv', auth=(st.secrets['siguser'], st.secrets['sigpassw']), verify=False)
  #decoded_content = response.content.decode('utf-8')
  #cr = csv.reader(decoded_content.splitlines(), delimiter=',')
  #my_list = list(cr)
  #decs = pd.DataFrame(my_list) #, index=None)

  trackTimes = []
  try:

    header = my_list[0]
    decs = pd.DataFrame(my_list[1:], columns=header)

    for index,row in decs.iterrows():
      tt = row['trackTimeDate'].split('_')
      trackTime = tt[0][0:4] + ' ' + tt[1]
      trackTimes.append(trackTime)
  except:
    pass

  if len(trackTimes) == 0:
    st.write('No grade 1 to 4 Handicaps today')
  else:
    #header = my_list[0]
    #decs = pd.DataFrame(my_list[1:], columns=header)
    trackTime = decs.iloc[0]['trackTimeDate']
    tt = trackTime.split('_')
    trackTime = tt[0][0:4] + ' ' + tt[1]
    horses = decs['horse']

    with inputs:
      inputcol, rescol = st.columns([1, 1])
      with inputcol:
        st.subheader('Choose Inputs')
        cl = st.checkbox('Class Move')
        da = st.checkbox('Days Since Last Run')
        tr = st.checkbox('Trainer Strike Rate')
        jo = st.checkbox('Jockey Strike Rate')
        si = st.checkbox('Sire Strike Rate')
        pa = st.checkbox('Pace Figure')
    
        cols = createCols()

    try:
      decs = decs[cols]
    except Exception as e:
      print ('error ',e)

    with inputs:
      with inputcol:
        if st.button("Predict"):
          predModel()
        st.write('MySportsAI has over 90 predictors to choose from www.smartersig.com/mysportsai.php')

