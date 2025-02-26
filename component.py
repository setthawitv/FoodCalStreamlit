import logging
import os
import urllib
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

# Azure SQL Configuration
class AzureSQL():
    def __init__(self):
        self.SERVER = 'foodcal.database.windows.net'
        self.DATABASE = 'FoodCal'
        self.USERNAME = 'mos'
        self.PASSWORD = 'Setthawit1'
        self.DRIVER = '{ODBC Driver 18 for SQL Server}'
        self.connection_string = f'DRIVER={self.DRIVER};SERVER=tcp:{self.SERVER};PORT=1433;DATABASE={self.DATABASE};UID={self.USERNAME};PWD={self.PASSWORD}'
        self.sqlalchemy_connection_string = f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(self.connection_string)}'

    def insert_row_to_messages(self, user_id, image_url, food_name, calories):
        """Insert a new food record for the user using UID instead of phone number."""
        engine = create_engine(self.sqlalchemy_connection_string)
        data = {
            'Timestamp': [datetime.now()],
            'UserID': [user_id],
            'ImageURL': [image_url],
            'FoodName': [food_name],
            'Calories': [calories]
        }
        df = pd.DataFrame(data)
        df.to_sql('FoodCalories', engine, index=False, if_exists="append", schema="dbo")
        logging.info(f"✅ Inserted food record: {food_name} ({calories} kcal) for user {user_id}")

    def get_daily_calories(self, user_id):
        """Get total calorie intake for today using UID."""
        engine = create_engine(self.sqlalchemy_connection_string)
        query = text("""
        SELECT SUM(Calories) FROM FoodCalories 
        WHERE UserID = :user_id AND CONVERT(DATE, Timestamp) = CONVERT(DATE, GETDATE())
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {'user_id': user_id}).scalar()
            return result if result else 0

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
