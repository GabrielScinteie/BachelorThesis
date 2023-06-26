import sys
import os

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./Agent'))
sys.path.append(os.path.abspath('./GraphicalUserInterface'))
sys.path.append(os.path.abspath('..'))

import MainMenu
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
if __name__ == "__main__":
    window_size = 600
    mainMenu = MainMenu.MainMenu(window_size)
    mainMenu.show()
    sys.exit(app.exec_())
