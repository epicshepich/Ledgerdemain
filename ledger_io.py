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



def process_raw_ledger(df: pd.DataFrame) -> tuple:
    """This function takes takes a DataFrame read from an Excel file,
    separates the header (metadata) from the body (ledger data), and returns
    a tuple of (data, metadata).

    Arguments:
        df -- a DataFrame containing raw ledger data read from an Excel file.
        The formatting of the Excel file should follow these rules:
            - The header contains key, value pairs, where the key is the
            name of the field (e.g. "Tenants", "Address", "Phone Number", etc.)
            and the value is the value (e.g. "John Doe", "1600 Pennsylvania Avenue",
            "555-0143").

            - Each key should be the first cell in a row, with its value in the
            in the next cells. Keys with multiple values should have each value
            in its own cell.

            - At the end of the header, there is a row containing the equation
            '=CHAR(02)' in its first column. This row marks that the ledger
            data begins in the next row.

            - Every column containing data must be named; any unnamed columns
            will be expunged.

    Outputs:
        data -- a DataFrame containing the ledger data, with missing values
            replaced with 0
        metadata -- a dict containing the metadata
    """

    stx_index = -1
    for sequence in settings["end_header_seq"]:
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

        key = row[0]

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


    ledger_matrix = np.zeros(len(column_headers))
    #Contingency for empty ledgers. Create a row of zeros if the ledger is
    #empty to prevent the subsequent code from breaking and still allow the
    #ledger to be parsed.
    try:
        ledger_matrix = df.loc[(stx_index+2):]
    except ValueError:
        print("Empty ledger.")

    data = pd.DataFrame(
        np.array(ledger_matrix),
        columns = np.array(column_headers)
    )
    #Create a DataFrame containing the actual ledger data.

    #If any of the metadata tags contain lists longer than the number
    #of columns in the ledger data, then all the data rows will fill
    #with NaN to match the length.

    data.columns = data.columns.fillna('NaN')
    if "NaN" in data.columns:
        data = data.drop("NaN",axis=1)
        #Drop every column whose header is NaN.
        #The conditional prevents an error from occuring when
        #there are no NaN-valued columns (i.e. metadata lists
        #do not exceed data columns in length).

    data = data.fillna(0)
    #Fill any remaining NaN entry with 0 - because this is legal stuff,
    #we want to keep every row, regardless of if it has a missing value.
    #Replacing NaN with 0 will cause minimal errors when computing balances.

    return (data, metadata)



def load_ledgers() -> list:
    loaded_ledgers = []
    for path in settings["ledger_paths"]:
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
            data, metadata = process_raw_ledger(raw_data)
            #Try to process the ledger.

            metadata["__filepath__"] = path
            metadata["__filename__"] = path.split("/")[-1].replace(".xlsx","")
            if not settings["ledger-name-tag"] in metadata:
                metadata[settings["ledger-name-tag"]] = metadata["__filename__"]
                #If the spreadsheet doesn't have a name tag, then set it to
                #the file name.

            loaded_ledgers.append((data,metadata))
        except:
            print(f"Error converting file: '{path}'")
            continue

    return loaded_ledgers
