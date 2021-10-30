from waitress import serve
from cefpython3 import cefpython as cef
import threading
import sys
from app import *

port = 8052

sys.excepthook = cef.ExceptHook

def thread_cef():
    """This function opens a CEF browser pointing to the
    localhost Dash app."""
    sys.excepthook = cef.ExceptHook
    cef.Initialize(switches={'disable-gpu-compositing': None})
    cef.CreateBrowserSync(url=f"http://localhost:{port}",
                                  window_title="Ledgerdemain")
    cef.MessageLoop()


cef_thread = threading.Thread(target=thread_cef)
cef_thread.start()
serve(app.server, host="localhost", port=port)
cef.Shutdown()
