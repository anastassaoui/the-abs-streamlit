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
            
    <h1 class="text-3xl bg-red-500 text-center font-extrabold mt-10 hover:bg-red-300
                hover:border-red-500 hover:text-black rounded-2xl duration-1000
                border-2 border-red-300 cursor-pointer md:text-7xl md:font-extrabold
                mb-10
                ">
                📊 Absence Management Dashboard📊
    </h1>
    
""", unsafe_allow_html=True)





# data
df_users = load_users()
df_presence = load_presence()


# Sidebar
st.sidebar.header("Filter Options")
student_list = df_users['firstname'] + " " + df_users['lastname']
selected_student = st.sidebar.selectbox("Select a student", options=["All"] + student_list.tolist())


# Filtestudent
if selected_student != "All":
    first_name, last_name = selected_student.split()
    df_presence = df_presence[(df_presence['firstname'] == first_name) & (df_presence['lastname'] == last_name)]
    
    
    
# Metrics
col1, col2 ,col3,col4,col5 = st.columns(5)

# Total Users
col2.markdown("""
    <h3 class="text-3xl font-bold mt-5 hover:text-red-400 duration-500 cursor-pointer hover:underline md:-mb-12">
        Total Users 
    </h3>
""", unsafe_allow_html=True)
col3.metric(" ", df_users.shape[0])

# Total Attendance Sessions
col4.markdown("""
    <h3 class="text-3xl font-bold mt-5 hover:text-red-400 duration-500 cursor-pointer md:-ml-20 hover:underline md:-mb-12">
        Total Attendance Sessions 
    </h3>
""", unsafe_allow_html=True)
col5.metric("", df_presence.shape[0])


st.markdown("""
            
    <h6 class="text-xl text-white  text-center font-bold mt-10 
                 md:text-white md:hover:text-red-400 hover:underline  duration-1000
                 cursor-pointer md:text-5xl md:font-extrabold
                mb-10 md:mt-20
                ">
                Data Overview
    </h6>
    
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns(2)
with col1:
    st.write("### Users Data")
    st.dataframe(df_users, use_container_width=True)
with col2:
    st.write("### Attendance Records")
    st.dataframe(df_presence, use_container_width=True)
    
    
    
st.markdown("""
            
    <h6 class="text-xl text-white  text-center font-bold mt-10 
                 md:text-white md:hover:text-red-400 hover:underline  duration-1000
                 cursor-pointer md:text-5xl md:font-extrabold
                mb-10 md:mt-20
                ">
                Data Overview
    </h6>
    
""", unsafe_allow_html=True)


#each user (filtered)
df_stats = df_presence.groupby(['firstname', 'lastname']).size().reset_index(name='Classes Attended')


# Visualization 1: Attendance per User
if not df_stats.empty:
    st.write("### Classes Attended by Each User")
    fig = px.bar(df_stats, x='firstname', y='Classes Attended', 
                 hover_data=['lastname'], 
                 color='Classes Attended', 
                 labels={'firstname': 'First Name', 'Classes Attended': 'Population'},
                 height=1000,
                 color_continuous_scale=px.colors.sequential.Reds) 
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig)





