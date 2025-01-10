# Import "European attitudes towards energy policies_SP555_VOL_A.xlsx"
import sys
 
def print_to_stdout(*a):
 
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stdout)

import pandas as pd

# Load data
excel = pd.ExcelFile("src/data/data_VOL_A.xlsx")

# Get sheet names
sheet_names = excel.sheet_names
question_sheet_names = [sheet_name for sheet_name in sheet_names if sheet_name.startswith("Q")]

# For every sheet that starts with "Q", get the question title and the table
# The titles of the questions are at the 3rd row and 8th column (merged columns count as one)
# The tables begin from the 8th row

# Initialize a dictionary to store the data
data = pd.DataFrame()


for sheet_name in question_sheet_names:
    question_data = {}
    # Load the sheet

    sheet = excel.parse(sheet_name)
    
    # Get the question title
    # For sheet_names that end with _X, (where X is a number), they have a subtitle on the row below
    question_title = sheet.iloc[1, 7]
    subtitle = sheet.iloc[2, 7]
    
    # Get the table, it starts from the 2nd column and 12th row
    # The column names are found on row 8
    # It's possible to take every 2nd row starting from the 12th row
    table = sheet.iloc[11::2, 1:]    
    table.columns = sheet.iloc[7, 1:]
    # The first row table column can be called "Statement" and second column can be called "EU27"
    table.columns.values[0] = "Statement"
    table.columns.values[1] = "EU27"

    question_data["title"] = question_title
    question_data["subtitle"] = subtitle
    question_data["table"] = table

    # Reset all the indexes, including the title row
    # Serialize the table to JSON format
    table.reset_index(drop=True, inplace=True)
    json_data = table.to_json(orient="records")
    question_data["json_data"] = json_data    

    data[sheet_name] = question_data
    

# Write the data to a JSON format, to standard output
# Make sure all data is serialized to JSON format
import json
print_to_stdout(json.dumps(data.to_json(orient="records"), indent=4))
