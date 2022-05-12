import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re
import streamlit as st

st.set_page_config(page_title = "JFK departures dashboard",
                   page_icon = ":airplane:",
                   layout = "wide"
)

# --- READ CSV AND FORMAT DF ---
@st.cache
def to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub(r'\s+', '', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

@st.cache
def get_JFK_departures_data():
    df = pd.read_csv("./JFK_dep_data.csv")
    df.columns = map(to_snake, df.columns)
    df['dew_point'] = df['dew_point'].astype('int64')
    df.dropna(inplace=True)
    df.drop('tail_num', axis=1, inplace=True)
    df['is_delay'] = np.where(df['dep_delay'] >= 15, 1, 0)
    return df

@st.cache
def get_airports_data():
    df = pd.read_csv("./airports.csv")
    df.rename(columns = {'IATA_CODE':'dest'}, inplace=True)
    return df

df = get_JFK_departures_data()

# ---- SIDEBAR ----
st.sidebar.header("Please filter here:")

# AIRLINES FILTER
airlines_list = list(df["op_unique_carrier"].unique())
airlines_list_all = airlines_list[:]
airlines_list_all.sort()
airlines_list_all.insert(0, "SELECT ALL")

airline = st.sidebar.multiselect(
    "Select airline:",
    options=airlines_list_all,
    default="SELECT ALL"
)
if "SELECT ALL" in airline:
    airline = airlines_list

# DESTINATION FILTER
dest_list = list(df["dest"].unique())
dest_list_all = dest_list[:]
dest_list_all.sort()
dest_list_all.insert(0, "SELECT ALL")

destination = st.sidebar.multiselect(
    "Select destination:",
    options=dest_list_all,
    default="SELECT ALL"
)
if "SELECT ALL" in destination:
    destination = dest_list

df_selection = df.query(
    "op_unique_carrier == @airline & dest == @destination"
)

# ---- MAINPAGE ----
st.title(":airplane: JFK Departures Dashboard")
st.subheader("November 2019 - January 2020")
st.markdown("##")

# TOP KPI's
total_flights = len(df_selection)
delayed_flights_perc = round(100*df_selection["is_delay"].sum()/len(df_selection), 2)
average_delay = round(df_selection["dep_delay"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Flights:")
    st.subheader(total_flights)
with middle_column:
    st.subheader("Delayed Flights (>15 min):")
    st.subheader(f"{delayed_flights_perc} %")
with right_column:
    st.subheader("Average Delay Per Flight:")
    st.subheader(f"{average_delay} min")

st.markdown("""---""")

# DEPARTURE DELAY HISTOGRAM
st.markdown("**Departure delay histogram**")
values = st.slider('Select the range (in minutes)', -25, 400, (-20, 60), step = 1)
fig_hist = px.histogram(
    df_selection, x='dep_delay', range_x=[values[0], values[1]],
    labels = {'dep_delay' : 'Departure delay (min)'}
)

fig_hist.update_layout(
    margin=dict(l=5, r=5, t=0, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

st.plotly_chart(fig_hist, use_container_width=True)
st.markdown('#')
st.markdown('####')

# AIRLINES DELAY CHART
df_del_airlines = (
    (df_selection.groupby('op_unique_carrier')['is_delay'].mean()*100).reset_index(name='delayed_percentage')
)

fig_del_airlines = px.bar(
    df_del_airlines,
    x='op_unique_carrier',
    y='delayed_percentage',
    labels = {'op_unique_carrier' : 'Airline code', 'delayed_percentage' : 'Delayed flights (%)'},
    title = '<b>Percentage of delayed flights for each airline</b>',
    color_discrete_sequence = ["#0083B8"],
    template="plotly_white"
)

fig_del_airlines.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


# SKY CONDITION CHART
df_sky_cond = (
    (df_selection.groupby('condition')['is_delay'].mean()*100).reset_index(name='delayed_percentage')
)

fig_sky_cond = px.bar(
    df_sky_cond, x='delayed_percentage',
    y='condition',
    orientation = 'h',
    labels = {'condition' : 'Sky condition', 'delayed_percentage' : 'Delayed flights (%)'},
    title = '<b>Percentage of delayed flights depending on sky condition</b>',
    height = 600,
    color_discrete_sequence = ["#0083B8"],
    template="plotly_white"
)

fig_sky_cond.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


#DELAY FOR EACH DESTINATION MAP
df_grouped = df_selection \
                .groupby('dest') \
                .agg(np.mean)['dep_delay'] \
                .sort_values(ascending=False) \
                .reset_index()

df_airports = get_airports_data()

df_merge = pd.merge(df_grouped, df_airports, on='dest')
df_merge.columns = df_merge.columns.str.lower()
df_merge.drop(['country'], axis=1, inplace=True)

min_opacity = 0.2
max_opacity = 1
min_color = 0
max_color = 255
min_delay = df_merge['dep_delay'].min()
max_delay = df_merge['dep_delay'].max()

if len(df_merge) != 1:
    df_merge['opacity'] = (df_merge['dep_delay'] - min_delay)*((max_opacity - min_opacity)/(max_delay - min_delay)) + min_opacity
    df_merge['color'] = (df_merge['dep_delay'] - min_delay)*((max_color - min_color)/(max_delay - min_delay)) + min_color
else:
    df_merge['opacity'] = 1
    df_merge['color'] = 0

st.markdown("**Mean flight delay for every destination**")    
min_delay_to_plot = st.slider('Choose the minimum delay to plot:', -2, 23, 0)
st.write('Plotting mean delays bigger than', min_delay_to_plot, 'minutes')

fig = go.Figure()

fig.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = df_merge['longitude'],
    lat = df_merge['latitude'],
    hoverinfo = 'text',
    text = df_merge['city'] +" ("+df_merge['dest']+")",
    mode = 'markers',
    marker = dict(
        size = 2,
        color = 'rgb(0, 0, 0)',
        line = dict(
            width = 3,
            color = 'rgba(68, 68, 68, 0)'
        )
    )))

jfk_lon = -73.77893
jfk_lat = 40.63975

for i in range(len(df_merge)):
    if df_merge['dep_delay'][i] > min_delay_to_plot:
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [jfk_lon, df_merge['longitude'][i]],
                lat = [jfk_lat, df_merge['latitude'][i]],
                mode = 'lines',
                line = dict(width = 1.5,
                            # color = 'rgb('+str(df_merge['color'][i])+',0,'+str(255-df_merge['color'][i])+')'),
                            color = 'rgb('+str(df_merge['color'][i])+',0,0)'),
                            # color = 'rgb(0,0,0)'),
                opacity = df_merge['opacity'][i],
                hoverinfo = 'text',
                text = df_merge['city'][i] +" ("+df_merge['dest'][i]+"), mean_delay = " + str(round(df_merge['dep_delay'][i], 2))
            )
        )

fig.update_layout(
    showlegend = False,
    geo = dict(
        scope = 'north america',
        projection_type = 'azimuthal equal area',
        showland = True,
        landcolor = 'rgb(243, 243, 243)',
        countrycolor = 'rgb(180, 180, 180)'
    ),
    margin=dict(l=5, r=5, t=0, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    height=500
)

st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig_del_airlines, use_container_width=True)
st.plotly_chart(fig_sky_cond, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)