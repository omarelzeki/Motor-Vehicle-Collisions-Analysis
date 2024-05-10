import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


st.title("Motor Vehicle Collisions in New York City")
st.markdown("This is a dashboard whose purpose is to monitor motor vehicles collisions in NYC")

# Data loading:

@st.cache_data(persist=True)
def load_data(nrows): 
    data = pd.read_csv("Motor_Vehicle_Collisions_-_Crashes.csv", nrows= nrows, parse_dates= [['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data.rename(columns={'CRASH_DATE_CRASH_TIME':'DATE/TIME', 'CONTRIBUTING_FACTOR_VEHICLE_1':'CONTRIBUTING_FACTOR'}, inplace=True)
    return data

data = load_data(100000)

# data cleaning:

# I have noticed the existence of some data points clearly outside of New York or even america which are clearly errors in data entry
data = data[(data['LONGITUDE']<=-72) & (data['LONGITUDE']>=-75)]

st.sidebar.header('Filters')
injuries= (data['INJURED_PERSONS']+data['INJURED_PEDESTRIANS']+data['INJURED_CYCLISTS'])

max_injuries=injuries.max()
injured_people = 0

if st.sidebar.checkbox("Filter by Injuries per Accident", False):
    injured_people = st.sidebar.slider("", 0, int(max_injuries))
    data = data[injuries >=injured_people]

if st.sidebar.checkbox("Filter by Time", False):
    hour = st.sidebar.slider("Hour to look at", 0,23)
    data = data[data['DATE/TIME'].dt.hour ==hour]


#Data viz
    
## maps:

# st.header('Where are the most people inured in New York City')
# data = data[injuries>=injured_people]
# st.map(data[['LATITUDE', 'LONGITUDE']])


st.header("Frequency of collisions")

midpoint = np.average(data[['LATITUDE', 'LONGITUDE']],axis=1)

st.write(pdk.Deck(
    map_style="mapbox://style/mapbox/light-v9",
    initial_view_state={
        "latitude": 40.63,
        "longitude": -74,
        "zoom": 11,
        "pitch": 50,
        },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['DATE/TIME', 'LATITUDE', 'LONGITUDE']],
            get_position=['LONGITUDE', 'LATITUDE'],
            radius = 100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
            ),
        ],    
    ))

st.subheader('Reasons of accidents')
reasons = data[data['CONTRIBUTING_FACTOR'] != "Unspecified"]['CONTRIBUTING_FACTOR'].value_counts().reset_index()
reasons.columns = ['CONTRIBUTING_FACTOR', 'COUNT']
total = reasons['COUNT'].sum()

top_99 = reasons[reasons['COUNT'] >= total * 0.0095]

if reasons['COUNT'].min() < total * 0.0095:
    other = pd.DataFrame(data = {
        'CONTRIBUTING_FACTOR' : ['Other'],
        'COUNT' : [reasons[reasons['COUNT'] < total * 0.0095]['COUNT'].sum()]
    })
    final = pd.concat([top_99, other])
else:
    final = top_99

st.write(px.pie(final, names='CONTRIBUTING_FACTOR', values='COUNT'))

raw_data=data[[ 'DATE/TIME','BOROUGH', 'ON_STREET_NAME', 'CROSS_STREET_NAME']]
raw_data['INJURIES']=injuries

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(raw_data)
