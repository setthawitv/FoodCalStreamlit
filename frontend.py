import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import urllib

class AzureSQL():
    def __init__(self):
        self.SERVER = 'foodcal.database.windows.net'
        self.DATABASE = 'FoodCal'
        self.USERNAME = 'mos'
        self.PASSWORD = 'Setthawit1'
        self.DRIVER = '{ODBC Driver 17 for SQL Server}'
        self.connection_string = f'DRIVER={self.DRIVER};SERVER=tcp:{self.SERVER};PORT=1433;DATABASE={self.DATABASE};UID={self.USERNAME};PWD={self.PASSWORD}'
        self.sqlalchemy_connection_string = f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(self.connection_string)}'

    def get_user_calories(self, user_id, days):
        """Retrieve calorie data for the past N days using UID instead of phone number."""
        engine = create_engine(self.sqlalchemy_connection_string)
        query = text("""
            SELECT CONVERT(DATE, Timestamp) as Date, SUM(Calories) as TotalCalories, STRING_AGG(ImageURL, ',') as Images
            FROM FoodCalories
            WHERE UserID = :user_id AND Timestamp >= DATEADD(DAY, -:days, GETDATE())
            GROUP BY CONVERT(DATE, Timestamp)
            ORDER BY Date DESC
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {'user_id': user_id, 'days': days}).fetchall()
            return result

azure_sql = AzureSQL()

def get_user_calories(self, user_id, days):
    """Retrieve calorie data for the past N days using UID instead of phone number."""
    engine = create_engine(self.sqlalchemy_connection_string)
    query = text("""
        SELECT CONVERT(DATE, Timestamp) as Date, SUM(Calories) as TotalCalories, STRING_AGG(ImageURL, ',') as Images
        FROM FoodCalories
        WHERE UserID = :user_id AND Timestamp >= DATEADD(DAY, -:days, GETDATE())
        GROUP BY CONVERT(DATE, Timestamp)
        ORDER BY Date DESC
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {'user_id': user_id, 'days': days}).fetchall()
        return result

def show_calories_dashboard():
    st.title("📊 Your Calorie Intake Dashboard")

    # ✅ Extract UID from URL parameters (if available)
    query_params = st.query_params
    default_uid = query_params.get("uid", "")

    # ✅ Allow user to manually enter UID (pre-filled if available)
    user_id = st.text_input("🔑 Enter Your UID", value=default_uid)

    if not user_id:
        st.warning("⚠️ Please enter your UID (or tap Rich Menu to autofill).")
        return

    st.subheader("📅 Past 7 Days Summary")
    past_7_days = azure_sql.get_user_calories(user_id, 7)

    if not past_7_days:
        st.info("No records found. Start logging your meals now! 📸")
        return

    for entry in past_7_days:
        st.write(f"**📆 Date:** {entry.Date} - **🔥 Total Calories:** {entry.TotalCalories} kcal")
        for img_url in entry.Images.split(','):
            st.image(img_url, width=200)

    st.subheader("📈 Past 30 Days Trend")
    past_30_days = azure_sql.get_user_calories(user_id, 30)
    df = pd.DataFrame(past_30_days, columns=['Date', 'TotalCalories', 'Images'])

    if not df.empty:
        st.line_chart(df.set_index('Date')['TotalCalories'])
    else:
        st.info("📊 No calorie data available for the last 30 days.")

if __name__ == "__main__":
    show_calories_dashboard()
