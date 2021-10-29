"""This module creates the Dash UI for the Ledgerdemain application."""
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output

import plotly.express as px

import pandas as pd
import seaborn as sns

from spreadsheet_io import *
from analytics import *


app = dash.Dash(__name__)
app.title = 'Ledgerdemain'
spreadsheets = load_spreadsheets()
ledgers = {}
for sheet in spreadsheets:
    data, metadata = spreadsheets[sheet]
    if "_type_" in metadata and metadata["_type_"] == 'ledger':
        ledgers[sheet] = (data, metadata)

spreadsheets["Summary of Ledgers"] = ledger_summary(ledgers)
spreadsheets["Daily Journal"] = ledger_journal(ledgers)



header = html.H1(
    children="Ledgerdemain",
    className="header-title",
    )


graph_div = html.Div(
    id="graph-div",
    children = []
    )



def create_dropdown_selector(spreadsheet_dictionary: dict, focused="Summary of Ledgers") -> dcc.Dropdown:
    options = []

    for meta_name in spreadsheet_dictionary:
        data, metadata = spreadsheet_dictionary[meta_name]
        options.append({
            "label": metadata[map_name("_name_")],
            "value": meta_name
        })

    return dcc.Dropdown(id="dropdown-selector",options=options,value=focused)



def metadata_display(metadata: dict):
    header = []

    if map_name("_name_") in metadata:
        header.append(html.H2(metadata[map_name("_name_")]))

    for key in metadata:
        if key in settings["metadata_nodisplay"] or key == map_name("_name_"):
            #Don't print metadata tags specified in this list or the
            #spreadsheet name.
            continue

        value = metadata[key]
        if isinstance(value,(list)):
            value = ", ".join(value)

        header.append(html.Div(
            children=[html.B(key), f": {value}"]
        ))

    header.append(html.Br())
    return html.Div(children=header)


app.layout = html.Div(
    id="main-container",
    children = [header, create_dropdown_selector(spreadsheets)]
    )


@app.callback(
    Output('main-container','children'),
    Input(component_id='dropdown-selector', component_property='value')
)
def display_spreadsheet(selector_value):
    global spreadsheets


    df, meta = spreadsheets[selector_value]

    table = dash_table.DataTable(
        id='spreadsheet-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'whiteSpace': 'pre-line'},
        #Parse \n in a cell value as a line break instead of an em quad (default).
        filter_action="native"
        #Use built-in table filtering feature.
    )


    content = [header,
        create_dropdown_selector(spreadsheets,focused=selector_value),
        metadata_display(meta),
        graph_div,
        table
        ]

    return content
