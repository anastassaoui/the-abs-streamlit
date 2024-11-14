import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import plotly.express as px
import os
from langchain_groq import ChatGroq
#from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
#from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest
from prophet import Prophet



# Database connection function
def connect_db():
    conn = psycopg2.connect(
        'postgresql://my_abs_data_user:52uhBcZ7nWInFijiPiID1adLpI6yDc43@dpg-cs99ql5svqrc73d92c8g-a.frankfurt-postgres.render.com/my_abs_data',
        cursor_factory=DictCursor
    )
    return conn

@st.cache_data
def load_users():
    with connect_db() as conn:
        return pd.read_sql("SELECT id, firstname, lastname, email, admin FROM users;", conn)

@st.cache_data
def load_presence():
    with connect_db() as conn:
        return pd.read_sql("""
            SELECT p.id, u.firstname, u.lastname, p.userid, p.date, p.scannedat
            FROM presence p JOIN users u ON p.userid = u.id;
        """, conn)



load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("Groq API key not found. Make sure it's defined in the .env file.")

llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key)




st.set_page_config(page_title="Absence Management Dashboard", layout="wide")



tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Center the table header and cell content */
        .css-1q8dd3e.e1ewe7hr3 th, .css-1q8dd3e.e1ewe7hr3 td {
            text-align: center !important;
        }
    </style>
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
    
    df_presence = df_presence[
        (df_presence['firstname']   ==   first_name) &
        (df_presence['lastname']    ==   last_name)
        ]
    #df_presence = df_presence[(df_presence['firstname'] = first_name) & (df_presence['last_name'] == last_name)]
    
 
    
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

    
st.markdown("""  
<h6 class=" text-xl   text-center font-bold mt-10 
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

col1, col2 = st.columns(2)   
    
with col1:
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

with col2:

    df_days_missed = df_presence.groupby(['userid', 'firstname', 'lastname']).size().reset_index(name='days_missed')



    threshold_days = 3  

    def highlight_poor_attendance(days_missed):
        return 'color: red' if days_missed > threshold_days else ''


    st.markdown("""
        <h6 class=" text-xl   text-center font-bold mt-10 
                    md:hover:text-blue-400 hover:underline  duration-1000
                    cursor-pointer md:text-2xl md:font-semibold md:-mb-6
                    mb-10 
                ">Attendance Records Highlighted</h6>
    """, unsafe_allow_html=True)

    selected_columns_users = st.multiselect(
    "", 
    options=df_users.columns.tolist(), 
    default=df_users.columns.tolist(),
    key="user_columns_multiselect"
    
    )
    
    st.dataframe(
        df_days_missed.style.applymap(highlight_poor_attendance, subset=['days_missed']),
        use_container_width=True
    )
    
    
st.markdown("""
            
    <h6 class=" text-xl text-center font-bold mt-10 
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

    # Visualization 1:
    if not df_stats.empty:
        st.markdown("""

        <h6 class=" text-xl font-bold mt-10 text-center
                    md:hover:text-blue-400 hover:underline duration-1000
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



# Ensure the 'date' column is in datetime format
df_presence['date'] = pd.to_datetime(df_presence['date'], errors='coerce')

# Now calculate 'days_between'
df_presence['days_between'] = df_presence.groupby('userid')['date'].diff().dt.days.fillna(0)


# Use 'days_between' instead of 'userid' and 'date'
model = IsolationForest(contamination=0.1)
df_presence['anomaly'] = model.fit_predict(df_presence[['days_between']])


# date datetime format df_attendance_over_time
df_attendance_over_time['date'] = pd.to_datetime(df_attendance_over_time['date'], errors='coerce')

# Rename 'date' to 'ds' for Prophet (this will be the datetime column)
df_attendance_over_time.rename(columns={'date': 'ds', 'attendance_count': 'y'}, inplace=True)

# Ensure you have 'ds' (dates) and 'y' (values for prediction) columns for Prophet
df_attendance_over_time = df_attendance_over_time.set_index('ds').resample('D').sum().reset_index()

# Prophet model fitting
model = Prophet()
model.fit(df_attendance_over_time[['ds', 'y']])  # Only pass the 'ds' and 'y' columns

# Create future dataframe and forecast for 30 days
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Plot the forecast
fig = model.plot(forecast)
st.pyplot(fig)
# Summarize the Prophet forecast (last 30 rows)
forecast_summary = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30).to_csv(index=False)



# Summarize dataframe
df_summary = df_presence.describe().reset_index().to_csv(index=False)

#ask
user_question = st.text_input("Ask a question about the forecast or attendance data:")

if user_question:
    # Create context combining both the dataframe summary and Prophet forecast
    context = f"""
    The following is a summary of the attendance data:
    {df_summary}

    The following is a summary of the attendance forecast based on the Prophet model:
    {forecast_summary}

    Analyze this information and answer the user's question regarding the data and forecast.
    """

    # Create the system message with the dataframe and Prophet forecast data
    system_message = SystemMessage(content=context)

    # Add the user's question
    user_message = HumanMessage(content=user_question)

    # Invoke the Groq AI model
    result = llm.invoke([system_message, user_message])

    # Parse and display the result
    parser = StrOutputParser()
    parsed_result = parser.invoke(result)

    # Show the AI's response in the app
    st.code(parsed_result, language='python')
