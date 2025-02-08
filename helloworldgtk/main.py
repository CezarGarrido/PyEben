from .application import Application
from .models.base import Base

def main(argv):
    app = Application()
    app.run(argv)
