import dash
from dash import html, dcc, dash_table
import pandas as pd
#openpyxl
import seaborn as sns
from cefpython3 import cefpython as cef
import threading
import sys
from app import *






def parallel_cef():
    """This function opens a CEF browser pointing to the
    localhost Dash app."""
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    cef.CreateBrowserSync(url="http://localhost:8050",
                                  window_title="Hello World!")
    cef.MessageLoop()


if __name__ == "__main__":
    cef_thread = threading.Thread(target=parallel_cef)
    #cef_thread.start()
    app.run_server(debug=True,port="8042")
    cef.Shutdown()
