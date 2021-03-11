from oauth2client.service_account import ServiceAccountCredentials
import dotenv
import gspread

import os
import csv

# Load the .env file into memory to retrieve important variables
dotenv.load_dotenv()
DATABASE = os.getenv('DATABASE_PATH')

# Get the correct scope that we are working in 
SCOPE = ['https://www.googleapis.com/auth/drive']

# Create and log into Google Spreadsheets and open the 'College Quotes' Worksheet
CREDS = ServiceAccountCredentials.from_json_keyfile_name(os.getenv('SECRET'), SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open('College Quotes').sheet1

# Open up the college_quotes.csv file and parse it line by line into the correct form
with open(DATABASE, 'r') as database:
	CELLS = [[f'{string}' for string in line] for line in csv.reader(database)]

# Finally batch update the spreadsheet with all of the values
SHEET.update(CELLS)
