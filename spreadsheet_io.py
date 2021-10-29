"""This module defines functions used for importing and exporting data,
as well as formatting at either end of the process.
"""
import pandas as pd
import numpy as np
import json

settings = None
with open("settings.json","r") as reader:
    settings = json.loads(reader.read())
    #Construct a dictionary containing the settings specified in settings.json.


def map_name(refname:str, map=settings["name-map"])->str:
    """This function maps a backend reference name to a dispay name
    according to a name map dictionary, whose entries are formatted as:
        refname: {"default":displayname, "alt":[list of alternate names]}
    """
    return map[refname]["default"]



def capitalize_title(text:str):
    """Capitalizes the first letter of every word (delimited by spaces) in
    a string."""
    return " ".join([word.capitalize() for word in text.split(" ")])



def disambiguate(name:str, map=settings["name-map"])->str:
    """This function allows tolerance in naming convetions for column headers
    and meta tags by mapping acceptable alternate names to a specified default
    display name according to a name map dictionary, whose entries are formatted as:
        refname: {"default":displayname, "alt":[list of alternate names]}"""
    display = capitalize_title(name)
    #If the reference name isn't in the name map, just return it back since we don't
    #want to lose data.

    for refname in map:
        #Iterate over the reference names.
        if name == map[refname]["default"] or name in map[refname]["alt"]:
            display = map[refname]["default"]
            #If the input name matches a default or is in the list of alternates
            #for that reference, then we're done.
            break
    return display


def process_raw_spreadsheet(df: pd.DataFrame) -> tuple:
    """This function takes takes a DataFrame read from an Excel file,
    separates the header (metadata) from the body (data), and returns
    a tuple of (data, metadata).

    Arguments:
        df -- a DataFrame containing raw spreadsheet data read from an Excel file.
        The formatting of the Excel file should follow these rules:
            - The header contains key, value pairs, where the key is the
            name of the field (e.g. "Tenants", "Address", "Phone Number", etc.)
            and the value is the value (e.g. "John Doe", "1600 Pennsylvania Avenue",
            "555-0143").

            - Each key should be the first cell in a row, with its value in the
            in the next cells. Keys with multiple values should have each value
            in its own cell.

            - At the end of the header, there is a row containing the equation
            '=CHAR(02)' in its first column. This row marks that the data
            begins in the next row.

            - Every column containing data must be named; any unnamed columns
            will be expunged.

    Outputs:
        data -- a DataFrame containing th data, with missing values
            replaced with 0
        metadata -- a dict containing the metadata
    """

    stx_index = -1
    for sequence in settings["name-map"]["_stx_"]["alt"]:
        if any(df[0]==sequence):
            stx_index = df.index[df[0]==sequence][0]
            break
            #The end of the header/start of data can be indicated by
            #any string sequence defined in the settings.
    #In the case that there is no end-of-header sequence present in the DataFrame,
    #assume that there is no metadata.

    if stx_index == -1:
        file_header = df[:0]
    else:
        file_header = df[:stx_index]

    metadata = {}

    for row_series in file_header.iterrows():
        #If there is no header, the loop will be skipped, and metadata will
        #be returned as an empty dict.

        row = list(row_series[1].dropna())
        #Get the list of values ([0] contains the index),
        #drop NaN values, and convert to an array to prevent weirdness.
        if len(row) == 0:
            continue
            #Skip empty rows.

        key = disambiguate(row[0])

        if len(row) == 1:
            #Missing value.
            metadata[key] = None
        elif len(row) == 2:
            #Single-valued tag.
            metadata[key] = row[1]
        else:
            #Multi-valued tag.
            metadata[key] = row[1:]


    column_headers = df.loc[stx_index+1]
    #The row after the STX/End of Header row contains the column names
    #of the data.


    spreadsheet_matrix = np.zeros(len(column_headers))
    #Contingency for empty spreadsheets. Create a row of zeros if the spreadsheet is
    #empty to prevent the subsequent code from breaking and still allow the
    #spreadsheet to be parsed.
    try:
        spreadsheet_matrix = df.loc[(stx_index+2):]
    except ValueError:
        print("Empty spreadsheet.")

    data = pd.DataFrame(
        np.array(spreadsheet_matrix),
        columns = np.array(column_headers)
    )
    #Create a DataFrame containing the actual spreadsheet data.

    #If any of the metadata tags contain lists longer than the number
    #of columns in the spreadsheet data, then all the data rows will fill
    #with NaN to match the length.

    data.columns = data.columns.fillna('NaN')
    if "NaN" in data.columns:
        data = data.drop("NaN",axis=1)
        #Drop every column whose header is NaN.
        #The conditional prevents an error from occuring when
        #there are no NaN-valued columns (i.e. metadata lists
        #do not exceed data columns in length).

    for column in data.columns:
        if "datetime" in str(data[column].dtype):
            data[column] = pd.to_datetime(data[column]).dt.date
            #Remove time component from datetime columns
            data[column] = pd.DatetimeIndex(data[column]).strftime(settings["date-format"])
            data[column] = data[column].fillna(method='ffill')
            #Forward-fill missing dates (i.e. assume rows with unspecified dates
            #are from the last specified date.)

    data = data.fillna(0)
    #Fill any remaining NaN entry with 0 - because this is legal stuff,
    #we want to keep every row, regardless of if it has a missing value.
    #Replacing NaN with 0 will cause minimal errors when computing balances.

    data.rename(columns={col:disambiguate(col) for col in data.columns},inplace=True)
    #Disambiguate column headers.

    return (data, metadata)



def load_spreadsheets() -> dict:
    """This function loads data from all specified sources, processes it,
    and stores it in the appropriate data structures."""
    
    loaded_spreadsheets = {}
    for path in settings["spreadsheet_paths"]:
        try:
            raw_data = pd.read_excel(path,header=None)
        except FileNotFoundError:
            print(f"No file found at {path}")
            continue
        except:
            print(f"Invalid file: '{path}'")
            continue
            #If the file is problematic, just skip it.


        try:
            data, metadata = process_raw_spreadsheet(raw_data)
            #Try to process the spreadsheet.

            metadata[map_name("_filepath_")] = path
            metadata[map_name("_filepath_")] = path.split("/")[-1].replace(".xlsx","")
            if not map_name("_name_") in metadata:
                metadata[map_name("_name_")] = metadata[map_name("_filename_")]
                #If the spreadsheet doesn't have a name tag, then set it to
                #the file name.

            meta_name = metadata[map_name("_name_")]

            loaded_spreadsheets[meta_name] = (data, metadata)
        except:
            print(f"Error converting file: '{path}'")
            continue

    return loaded_spreadsheets
