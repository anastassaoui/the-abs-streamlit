import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Database connection function
def connect_db():
    conn = psycopg2.connect('postgresql://abs_project_user:XvQmpauXnUqdhlwcG9zPa4R5oPTLNJsR@dpg-creo43rv2p9s73d13u2g-a.frankfurt-postgres.render.com/abs_project', cursor_factory=DictCursor)
    return conn

# Load users data
def load_users():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(""" SELECT id, firstname, lastname, email, admin
                    FROM users;""")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

# Load presence data
def load_presence():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(""" SELECT p.id, u.firstname, u.lastname, p.date, p.scannedat
                    FROM presence p JOIN users u ON p.userid = u.id;""")
    presence = cur.fetchall()
    cur.close()
    conn.close()
    return presence

# Main Streamlit App
def main():
    st.set_page_config(page_title="Absence Management Dashboard", layout="wide")
    
    st.title("📊 Absence Management Dashboard")

    # Load the data
    users = load_users()
    presence = load_presence()

    # Convert to DataFrames for easier manipulation
    df_users = pd.DataFrame(users, columns=["ID", "First Name", "Last Name", "Email", "Admin"])
    df_presence = pd.DataFrame(presence, columns=["ID", "First Name", "Last Name", "Date", "Scanned At"])

    # Sidebar filters
    st.sidebar.header("Filter Options")
    student_list = df_users['First Name'] + " " + df_users['Last Name']
    selected_student = st.sidebar.selectbox("Select a student", options=["All"] + student_list.tolist())
    date_range = st.sidebar.date_input("Filter by date range", [])
    
    # Filter based on student selection
    if selected_student != "All":
        first_name, last_name = selected_student.split()
        df_presence = df_presence[(df_presence['First Name'] == first_name) & (df_presence['Last Name'] == last_name)]
    
    # Filter by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_presence = df_presence[(df_presence['Date'] >= pd.to_datetime(start_date)) & (df_presence['Date'] <= pd.to_datetime(end_date))]

    # KPIs and Metrics section
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", df_users.shape[0])
    col2.metric("Total Attendance Sessions", df_presence.shape[0])
    attendance_rate = (df_presence.shape[0] / (df_users.shape[0] * 30)) * 100  # Assuming 30 classes per month
    col3.metric("Attendance Rate", f"{attendance_rate:.2f}%")

    # Layout for Users and Attendance Data
    st.subheader("Data Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Users Data")
        st.dataframe(df_users)

    with col2:
        st.write("### Attendance Records")
        st.dataframe(df_presence)

    # Attendance statistics section
    st.subheader("Attendance Analysis")



    # Number of classes attended by each user (filtered)
    df_stats = df_presence.groupby(['First Name', 'Last Name']).size().reset_index(name='Classes Attended')
    
    
    
    
    
    
    # Visualization 1: Attendance per User
    if not df_stats.empty:
        st.write("### Classes Attended by Each User")
        fig = px.bar(df_stats, x='First Name', y='Classes Attended', color='Last Name', 
                     title="Classes Attended by Each User", height=400)
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig)



if __name__ == "__main__":
    main()
