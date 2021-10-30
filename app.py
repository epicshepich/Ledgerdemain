"""This module creates the Dash UI for the Ledgerdemain application."""
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from functools import partial
from spreadsheet_io import *
from analytics import *


app = dash.Dash(__name__)
app.title = 'Ledgerdemain'
spreadsheets = load_spreadsheets()
ledgers = {}
for sheet in spreadsheets:
    data, metadata = spreadsheets[sheet]
    if "_type_" in metadata and metadata["_type_"] == map_name("_ledgertype_"):
        ledgers[sheet] = (data, metadata)

spreadsheets[map_name("ledger-summary")] = ledger_summary(ledgers)
spreadsheets[map_name("journal-name")] = ledger_journal(ledgers)



app_header = html.H1(
    children="Ledgerdemain",
    className="header-title",
    )


graph_div = html.Div(
    id="graph-div",
    children = []
    )



def create_ledger_dropdown(spreadsheet_dictionary: dict, focused=None) -> dcc.Dropdown:
    options = []

    for meta_name in spreadsheet_dictionary:
        data, metadata = spreadsheet_dictionary[meta_name]
        if metadata[map_name("_type_")] == map_name("_ledgertype_"):
            options.append({
                "label": metadata[map_name("_name_")],
                "value": meta_name
            })

    return dcc.Dropdown(id="ledger-dropdown",options=options,value=focused)


ledger_container = html.Div(
    id="ledger-div",
    children = [
        create_ledger_dropdown(spreadsheets),
        html.Div(id="ledger-display",children=[])
    ]
)



def display_sheet(sheet:tuple) -> html.Div:
    df, meta = sheet
    header = []

    if map_name("_name_") in meta:
        header.append(html.H2(meta[map_name("_name_")]))

    for key in meta:
        if key in settings["metadata_nodisplay"] or key == map_name("_name_"):
            #Don't print metadata tags specified in this list or the
            #spreadsheet name.
            continue

        value = meta[key]
        if isinstance(value,(list)):
            value = ", ".join(value)

        header.append(html.Div(
            children=[html.B(key), f": {value}"]
        ))

    header.append(html.Br())

    clip_id = f'copy-{meta[map_name("_name_")]}'
    table_id = f'spreadsheet-table-{meta[map_name("_name_")]}'

    header.append(dcc.Clipboard(id=clip_id))
    #Add a clipboard icon above the table that allows you to copy its contents.

    copy_table_callback(clip_id,table_id)

    table = dash_table.DataTable(
        id=table_id,
        columns=[{"name": column, "id": column} for column in df.columns],
        data=df.to_dict('records'),
        style_cell={'whiteSpace': 'pre-line'},
        #Parse \n in a cell value as a line break instead of an em quad (default).
        filter_action="native"
        #Use built-in table filtering feature.
    )

    content = html.Div(
        children = [*header,table],
        id = meta[map_name("_name_")]
    )
    return content



@app.callback(
    Output('ledger-display','children'),
    Input(component_id='ledger-dropdown', component_property='value')
)
def display_ledger(selector_value):
    global spreadsheets

    if selector_value is not None:
        content = display_sheet(spreadsheets[selector_value])
    else:
        content = []

    return content


def copy_table_callback(clipboard,table):
    @app.callback(
        Output(clipboard, "content"),
        Input(clipboard, "n_clicks"),
        State(table, "data"),
        )
    def copy_table(_,data):
        df_ = pd.DataFrame(data)
        df_.to_clipboard(index=False,excel=True)
        return None







def tag_editor(key, tags, name=None):
    #https://stackoverflow.com/questions/69678621/input-with-multiple-removable-values-in-dash
    content = html.Div(
        id=f"{key} tag editor",
        children = [
            dcc.Dropdown(
                id=f"{key} tags",
                options=[{'label': tag, 'value': tag} for tag in tags],
                value=[tag for tag in tags],
                multi = True
            )
        ]
    )

    return content





settings_menu = html.Div(
    id="Settings",
    children=[html.H2("Settings"),
    dcc.Markdown(f'Version: {settings["version"]}'),
    tag_editor("test", settings["journal-exclude"])
    ]
)



tabs = dcc.Tabs([
    dcc.Tab(label="Ledgers",children=[ledger_container]),
    dcc.Tab(label=map_name("journal-name"),children=[display_sheet(spreadsheets[map_name("journal-name")])]),
    dcc.Tab(label=map_name("ledger-summary"),children=[display_sheet(spreadsheets[map_name("ledger-summary")])]),
    dcc.Tab(label="Settings",children=[settings_menu]),
])



app.layout = html.Div(
    id="main-container",
    children = [app_header, tabs]
    )
