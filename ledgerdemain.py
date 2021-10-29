from waitress import serve
from cefpython3 import cefpython as cef
import threading
import sys
from app import *

def thread_cef():
    """This function opens a CEF browser pointing to the
    localhost Dash app."""
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    cef.CreateBrowserSync(url="http://localhost:8042",
                                  window_title="Ledgerdemain")
    cef.MessageLoop()


cef_thread = threading.Thread(target=thread_cef)
cef_thread.start()
serve(app.server, host="localhost", port=8042)
cef.Shutdown()
