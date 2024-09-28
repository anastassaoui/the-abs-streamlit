import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import plotly.express as px


def connect_db():
    conn = psycopg2.connect(
        'postgresql://abs_project_user:XvQmpauXnUqdhlwcG9zPa4R5oPTLNJsR@dpg-creo43rv2p9s73d13u2g-a.frankfurt-postgres.render.com/abs_project',
        cursor_factory=DictCursor
    )
    return conn


def load_users():
    with connect_db() as conn:
        return pd.read_sql("""  SELECT id, firstname, lastname, email, admin 
                                FROM users;""",
                            conn)


def load_presence():
    with connect_db() as conn:
        return pd.read_sql("""
            SELECT p.id, u.firstname, u.lastname, p.date, p.scannedat
            FROM presence p JOIN users u ON p.userid = u.id;
        """, conn)


st.set_page_config(page_title="Absence Management Dashboard", layout="wide")

st.title("📊 Absence Management Dashboard 📊 ")

# data
df_users = load_users()
df_presence = load_presence()

#filters
st.sidebar.header("Filter Options")
student_list = df_users['firstname'] + " " + df_users['lastname']
selected_student = st.sidebar.selectbox("Select a student", options=["All"] + student_list.tolist())


# Filter student
if selected_student != "All":
    first_name, last_name = selected_student.split()
    df_presence = df_presence[(df_presence['firstname'] == first_name) & (df_presence['lastname'] == last_name)]
    
    
# Input Classes
st.sidebar.header("Class Settings")
total_classes_input = st.sidebar.number_input("Enter the Total Number of Classes", min_value=1, value=10)




# Metrics
st.subheader("Key Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Users", df_users.shape[0])
col2.metric("Total Attendance Sessions", df_presence.shape[0])




# Layout
st.subheader("Data Overview")
col1, col2 = st.columns(2)
with col1:
    st.write("### Users Data")
    st.dataframe(df_users, use_container_width=True)
with col2:
    st.write("### Attendance Records")
    st.dataframe(df_presence, use_container_width=True)
    
    
    
#  Analysis
st.subheader("Attendance Analysis")
df_stats = df_presence.groupby(['firstname', 'lastname']).size().reset_index(name='Classes Attended')
df_stats['Attendance Rate (%)'] = (df_stats['Classes Attended'] / total_classes_input) * 100



# Visualization 1: Bar chart 
if not df_stats.empty:
    st.write("### Classes Attended by Each User")
    fig_bar = px.bar(df_stats, x='firstname', y='Classes Attended', 
                     hover_data=['lastname', 'Attendance Rate (%)'], 
                     color='Classes Attended', 
                     labels={'firstname': 'First Name', 'Classes Attended': 'Number of Classes Attended'},
                     height=900,
                     color_continuous_scale=px.colors.sequential.Oranges)
    fig_bar.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig_bar)
# Show table with Attendance Rate
st.write("### Detailed Attendance Rates")
st.dataframe(df_stats[['firstname', 'lastname', 'Classes Attended', 'Attendance Rate (%)']], use_container_width=True)





# Visualization 2: Pie chart 
fig_pie = px.pie(df_stats, 
                 values='Attendance Rate (%)', 
                 names=df_stats['firstname'] + " " + df_stats['lastname'],
                 title='Distribution of Attendance Rates',
                 height=1000,
<<<<<<< Updated upstream
                 width=1300,
                 )

fig_pie.update_traces(textfont=dict(size=16, color='black', family='Arial', weight='bold'))
st.plotly_chart(fig_pie)
=======
                 color_continuous_scale=px.colors.sequential.Reds) 
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig)





#dfdkfjsd
>>>>>>> Stashed changes
