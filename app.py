import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import plotly.express as px

# Database connection function
def connect_db():
    conn = psycopg2.connect(
        'postgresql://abs_project_user:XvQmpauXnUqdhlwcG9zPa4R5oPTLNJsR@dpg-creo43rv2p9s73d13u2g-a.frankfurt-postgres.render.com/abs_project',
        cursor_factory=DictCursor
    )
    return conn

# Load user data
def load_users():
    with connect_db() as conn:
        return pd.read_sql("SELECT id, firstname, lastname, email, admin FROM users;", conn)

# Load presence data
def load_presence():
    with connect_db() as conn:
        return pd.read_sql("""
            SELECT p.id, u.firstname, u.lastname, p.date, p.scannedat
            FROM presence p JOIN users u ON p.userid = u.id;
        """, conn)

# Main Streamlit App
def main():
    st.set_page_config(page_title="Absence Management Dashboard", layout="wide")

    st.title("📊 Absence Management Dashboard")

    # Load the data
    df_users = load_users()
    df_presence = load_presence()

    # Sidebar filters
    st.sidebar.header("Filter Options")
    student_list = df_users['firstname'] + " " + df_users['lastname']
    selected_student = st.sidebar.selectbox("Select a student", options=["All"] + student_list.tolist())

    # Filter based on student selection
    if selected_student != "All":
        first_name, last_name = selected_student.split()
        df_presence = df_presence[(df_presence['firstname'] == first_name) & (df_presence['lastname'] == last_name)]

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

    # Attendance Analysis
    st.subheader("Attendance Analysis")

    # Number of classes attended by each user (filtered)
    df_stats = df_presence.groupby(['firstname', 'lastname']).size().reset_index(name='Classes Attended')

    # Visualization 1: Attendance per User
    if not df_stats.empty:
        st.write("### Classes Attended by Each User")
        fig = px.bar(df_stats, x='firstname', y='Classes Attended', 
                     hover_data=['lastname'], 
                     color='Classes Attended', 
                     labels={'firstname': 'First Name', 'Classes Attended': 'Population'},
                     height=1000,
                     color_continuous_scale=px.colors.sequential.Oranges)  # Change to Reds for gradient
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
