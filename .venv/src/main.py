import os, sys, asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qasync import QEventLoop
from ui.page.MainPage import MainPage
import atexit
from tel.Client import Client
from backend.db import close_session

script_dir = os.path.dirname(os.path.abspath(__file__))
print(script_dir)
os.chdir(script_dir)

async def cleanup():
    await Client().disconnect()
    close_session()

def on_exit():
    asyncio.run(cleanup())

if __name__ == "__main__":
    atexit.register(on_exit)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    ui = MainPage()
    ui.window.show()
    with loop:
        loop.run_forever()


