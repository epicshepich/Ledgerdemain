"""This module creates the Dash UI for the Ledgerdemain application."""
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import seaborn as sns

from ledger_io import *


app = dash.Dash(__name__)
app.title = 'Ledgerdemain'
ledgers = load_ledgers()



header = html.H1(
    children="Ledgerdemain",
    className="header-title",
    )


def create_ledger_selector(ledger_list: list, focused=0):
    options = []

    for index, ledger in enumerate(ledger_list):
        data, metadata = ledger
        options.append({
            "label": metadata[settings["ledger-name-tag"]],
            "value": index
        })

    return dcc.Dropdown(id="ledger-selector",options=options,value=focused)



def metadata_display(metadata: dict):
    header = []

    if settings["ledger-name-tag"] in metadata:
        header.append(html.H2(metadata[settings["ledger-name-tag"]]))

    for key in metadata:
        if key in settings["metadata_nodisplay"] or key == settings["ledger-name-tag"]:
            #Don't print metadata tags specified in this list or the
            #ledger name.
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
    children = [header, create_ledger_selector(ledgers)]
    )


@app.callback(
    Output('main-container','children'),
    Input(component_id='ledger-selector', component_property='value')
)
def display_ledger(selector_value):
    global ledgers


    df, meta = ledgers[selector_value]

    table = dash_table.DataTable(
        id='ledger-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
    )


    content = [header,
        create_ledger_selector(ledgers,focused=selector_value),
        metadata_display(meta),
        table
        ]

    return content
