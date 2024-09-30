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




st.set_page_config(page_title="Absence Management Dashboard", layout="wide")



tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)

st.markdown("""
    <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700 md:-mb-12">          
    <h1 class="text-3xl  text-center font-extrabold mt-10 
                cursor-pointer md:text-7xl md:font-extrabold
                mb-10 hover:text-blue-400 duration-1000
                ">
                 Absence Management 
                <span class="bg-blue-100 text-blue-800 md:text-5xl mt-2 text-xl font-semibold me-2 px-2.5 py-0.5 rounded dark:bg-blue-200 dark:text-blue-800 ms-2
                hover:scale-125">
                    Dashboard
                </span>
    </h1>
    <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700 md:-mt-7">

    
""", unsafe_allow_html=True)





# data
df_users = load_users()
df_presence = load_presence()


# Sidebar
st.sidebar.markdown("""
      
    <h1 class="text-center text-md md:mb-12 font-extrabold cursor-pointer capitalize hover:text-blue-400 duration-1000
                ">
                 Filter Options
    </h1>


    
""", unsafe_allow_html=True)
student_list = df_users['firstname'] + " " + df_users['lastname']
st.sidebar.markdown("""
      
    <h1 class="text-center text-xs md:-mb-10 font-semibold cursor-pointer capitalize hover:text-blue-400 duration-1000
                ">
                 Select a student
    </h1> 
""", unsafe_allow_html=True)

selected_student = st.sidebar.selectbox("", options=["All"] + student_list.tolist())


# Filtestudent
if selected_student != "All":
    first_name, last_name = selected_student.split()
    df_presence = df_presence[(df_presence['firstname'] == first_name) & (df_presence['lastname'] == last_name)]
    


 
    
# Metrics
col1, col2 ,col3,col4,col5 = st.columns(5)

# Total Users
col2.markdown("""
    <h3 class="text-2xl font-bold mt-5 hover:text-blue-400 duration-500 cursor-pointer hover:underline md:-mb-12">
        Total Users 
    </h3>
    
""", unsafe_allow_html=True)
col3.metric(" ", df_users.shape[0])

# Total Attendance Sessions
col4.markdown("""
    <h4 class="text-xl font-bold mt-5 hover:text-blue-400 duration-500 cursor-pointer md:-ml-20 hover:underline md:-mb-12">
        Total Attendance Sessions 
    </h4>
""", unsafe_allow_html=True)
col5.metric("", df_presence.shape[0])


st.markdown("""
            
    <h6 class="text-3xl   text-center font-bold mt-10 
                  md:hover:text-blue-400   duration-1000
                 cursor-pointer md:text-5xl md:font-extrabold
                mb-10 md:mt-20 md:-mb-8 underline
                ">
                Data Overview
    </h6>
    
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
            
    <h6 class="text-xl   text-center font-bold mt-10 
                  md:hover:text-blue-400 hover:underline  duration-1000
                 cursor-pointer md:text-2xl md:font-semibold md:-mb-6
                mb-10 
                ">
                Users Data
    </h6>
    
    """, unsafe_allow_html=True)

    selected_columns_users = st.multiselect(
        "", 
        options=df_users.columns.tolist(), 
        default=df_users.columns.tolist()
    )

    st.dataframe(df_users[selected_columns_users], use_container_width=True)

    
    
with col2:
    st.markdown("""
            
    <h6 class="text-xl   text-center font-bold mt-10 
                  md:hover:text-blue-400 hover:underline  duration-1000
                 cursor-pointer md:text-2xl md:font-semibold md:-mb-6
                mb-10 
                ">
                Attendance Records
    </h6>
    
    """, unsafe_allow_html=True)

    selected_columns_presence = st.multiselect(
        "", 
        options=df_presence.columns.tolist(), 
        default=df_presence.columns.tolist()
    )

    st.dataframe(df_presence[selected_columns_presence], use_container_width=True)

    
    
    
st.markdown("""
            
    <h6 class="text-xl   text-center font-bold mt-10 
                  md:hover:text-blue-400 hover:underline  duration-1000
                 cursor-pointer md:text-5xl md:font-extrabold
                mb-10 underline
                ">
                Statistical Analysis
    </h6>
    
""", unsafe_allow_html=True)



col1, col2 = st.columns(2)


with col1:
    #each user (filtered)
    df_stats = df_presence.groupby(['firstname', 'lastname']).size().reset_index(name='Classes Attended')


    # Visualization 1: Attendance per User
    if not df_stats.empty:
        st.markdown("""

        <h6 class="text-xl    font-bold mt-10 text-center
                      md:hover:text-blue-400 hover:underline  duration-1000
                     cursor-pointer md:text-2xl md:font-semibold
                    -mb-9 
                    ">
                    Classes Attended by Each User
        </h6>

    """, unsafe_allow_html=True)

        fig = px.bar(df_stats, x='firstname', y='Classes Attended', 
                     hover_data=['lastname'], 
                     color='Classes Attended', 
                     labels={'firstname': 'First Name', 'Classes Attended': 'Classes Attended'},
                     height=500,
                     color_continuous_scale=px.colors.sequential.Blues) 
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig)

with col2:
    def load_attendance_over_time():
        with connect_db() as conn:
            return pd.read_sql("""
                SELECT date, COUNT(*) AS attendance_count
                FROM presence
                GROUP BY date
                ORDER BY date;
            """, conn)

    df_attendance_over_time = load_attendance_over_time()


    if not df_stats.empty:
        st.markdown("""
            <h6 class="text-xl  font-bold mt-10 
                         md:hover:text-blue-400 hover:underline duration-1000
                        cursor-pointer md:text-2xl md:font-semibold text-center
                        -mb-9">
                Attendance Rate by User
            </h6>
        """, unsafe_allow_html=True)

        fig1 = px.pie(df_stats, names='firstname', values='Classes Attended',
                       title='', 
                       color='firstname', 
                       color_discrete_sequence=px.colors.qualitative.Plotly)

        st.plotly_chart(fig1)




col1, col2 = st.columns(2)


with col1:
    # Load monthly attendance data
    def load_monthly_attendance():
        with connect_db() as conn:
            return pd.read_sql("""
                SELECT DATE_TRUNC('month', date) AS month, COUNT(*) AS total_attendance
                FROM presence
                GROUP BY month
                ORDER BY month;
            """, conn)

    df_monthly_attendance = load_monthly_attendance()

    # Visualization 2: Monthly Attendance Summary
    if not df_monthly_attendance.empty:
        st.markdown("""
            <h6 class="text-xl  font-bold mt-10 text-center
                        e md:hover:text-blue-400 hover:underline duration-1000
                        cursor-pointer md:text-2xl md:font-semibold
                        -mb-9">
                Monthly Attendance Summary
            </h6>
        """, unsafe_allow_html=True)

        fig2 = px.line(df_monthly_attendance, x='month', y='total_attendance', 
                       title='',
                       labels={'month': 'Month', 'total_attendance': 'Total Attendance'},
                       markers=True,
                       color_discrete_sequence=['#1f77b4'])

        fig2.update_layout(xaxis_title='Month', yaxis_title='Total Attendance', height=500)
        st.plotly_chart(fig2)

with col2:


    # Load daily attendance data
    def load_daily_attendance():
        with connect_db() as conn:
            return pd.read_sql("""
                SELECT date, COUNT(*) AS total_attendance
                FROM presence
                GROUP BY date
                ORDER BY date;
            """, conn)

    df_daily_attendance = load_daily_attendance()

    # Visualization: Total Attendance Per Day
    if not df_daily_attendance.empty:
        st.markdown("""
            <h6 class="text-xl  font-bold mt-10 text-center
                        e md:hover:text-blue-400 hover:underline duration-1000
                        cursor-pointer md:text-2xl md:font-semibold
                        -mb-9">
                Total Attendance Per Day
            </h6>
        """, unsafe_allow_html=True)

        fig3 = px.bar(df_daily_attendance, x='date', y='total_attendance',
                       title='',
                       labels={'date': 'Date', 'total_attendance': 'Total Attendance'},
                       color='total_attendance',
                       color_continuous_scale=px.colors.sequential.Blues)

        fig3.update_layout(xaxis_title='Date', yaxis_title='Total Attendance', height=500)
        st.plotly_chart(fig3)

