import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from collections import Counter

def create_hb_plot(df_hb, age):
    f_max = compute_f_max(age)

    zones = compute_zones(f_max)

    hb_series = list(df_hb["HR (bpm)"])
    avg_hb = np.average(hb_series)

    fig = px.line(df_hb, x="Time", y="HR (bpm)", title='Intensità: zone di frequenza')
    fig.update_traces(line_color = '#FF0000')
    fig.update_xaxes(showgrid = False)
    fig.update_yaxes(showgrid = False)
    fig.add_hrect(y0=zones[-1], y1=f_max, line_width=0, fillcolor="red", opacity=0.2)
    fig.add_hrect(y0=zones[-2], y1=zones[-1], line_width=0, fillcolor="yellow", opacity=0.2)
    fig.add_hrect(y0=zones[-3], y1=zones[-2], line_width=0, fillcolor="green", opacity=0.2)
    fig.add_hrect(y0=zones[-4], y1=zones[-3], line_width=0, fillcolor="blue", opacity=0.2)
    fig.add_hrect(y0=zones[-5], y1=zones[-4], line_width=0, fillcolor="grey", opacity=0.2)
    fig.add_hline(y=avg_hb, line_dash="dash", line_color="red")
    return fig, zones, f_max

def create_hb_dist(df_hb, zones, f_max):

    hb_series = list(df_hb["HR (bpm)"])
    counts = Counter(hb_series)

    n_samples = len(hb_series)

    freqs = {"molto leggero": 0, "leggero": 0, "intermedio": 0, "intenso": 0, "massimo": 0}

    for c in counts.keys():
        if c < zones[1] and c >= zones[0]:
            freqs["molto leggero"] += counts[c]
        elif c < zones[2] and c >= zones[1]:
            freqs["leggero"] += counts[c]
        elif c < zones[3] and c >= zones[2]:
            freqs["intermedio"] += counts[c]
        elif c < zones[4] and c >= zones[3]:
            freqs["intenso"] += counts[c]
        elif c < f_max and c >= zones[4]:
            freqs["massimo"] += counts[c]
    
    for k in freqs.keys():
        freqs[k] = (freqs[k]/n_samples)*100

    df = pd.DataFrame.from_dict(freqs, orient="index")
    fig = px.bar(df)
    fig.update_traces(showlegend = False)
    fig.update_layout(xaxis_title="Zone di frequenza", yaxis_title="Percentuale", plot_bgcolor = "white", paper_bgcolor = "white")
    fig.update_yaxes(showgrid = False)

    return fig

def compute_f_max(age):
    return 220 - age

def compute_zones(f_max):
    max_inf = int(np.percentile(np.arange(1,f_max+1), 90))
    hard_inf = int(np.percentile(np.arange(1,f_max+1), 80))
    int_inf = int(np.percentile(np.arange(1,f_max+1), 70))
    light_inf = int(np.percentile(np.arange(1,f_max+1), 60))
    very_light_inf = int(np.percentile(np.arange(1,f_max+1), 50))
    return [very_light_inf, light_inf, int_inf, hard_inf, max_inf]

def search_additional_info(df):
    distance = list(df["Total distance (km)"])[0]
    avg_freq = list(df["Average heart rate (bpm)"])[0]
    avg_speed = list(df["Average speed (km/h)"])[0]
    calories = list(df["Calories"])[0]
    return distance, avg_freq, avg_speed, calories

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

st.set_page_config(layout="wide")

if check_password():

    st.write("# Analisi seduta allenamento")

    cont_file = st.empty()
    file = cont_file.file_uploader("Carica un file csv relativo ad una sessione di allenamento", type={"csv"})

    cont_name = st.empty()
    name = cont_name.text_input(label="Nome dell'atleta")

    cont_age = st.empty()
    age = cont_age.text_input(label="Età dell'atleta")

    if file != None and age != "":
        cont_file.empty()
        cont_name.empty()
        cont_age.empty()
        # prev_df = file
        # prev_age = age
        df = pd.read_csv(file, skiprows=[0,1])
        df_useful  = df[["Time", "HR (bpm)"]]
        file.seek(0)
        # st.write(df_useful.head())
        try:
            df_add = pd.read_csv(file, nrows=1)
            dist, av_freq, av_speed, kal = search_additional_info(df_add)
        except:
            pass

        st.write(f"**Nome atleta**: {name}")
        st.write(f"**Età dell'atleta**:  {age} anni")

        try:
            c1, c2, c3, c4 = st.columns((1, 1, 1, 1))
            c1.markdown(f":round_pushpin:**Distanza totale percorsa**: {dist} km")
            c2.markdown(f":heart:**Frequenza cardiaca media**: {av_freq} bpm")
            c3.markdown(f":man-running:**Andatura media**: {av_speed} km/h")
            c4.write(f":fire:**Calorie consumate**: {kal} calorie")
        except:
            pass

        fig, zones, fmax = create_hb_plot(df_useful, int(age))

        fig2 = create_hb_dist(df_useful, zones, fmax)

        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

        # st.download_button(label="Scarica report", data="")

        # if file != prev_df:
        #     age = ""
        # if age != prev_age:
        #     st.experimental_rerun()

    ##TODO: Aggiungere tasto download report, scrive dati atleta e incolla il grafico su un A4 bianco

