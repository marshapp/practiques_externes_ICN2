import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from ui.design import Ui_MainWindow
from logic.tab_idvd import Tab1Handler
from logic.tab_idvg import Tab2Handler
from logic.tab_idtime import Tab3Handler


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowIcon(QIcon("assets/icon.png"))
        
        self.tab1 = Tab1Handler(self)
        self.tab2 = Tab2Handler(self)
        self.tab3 = Tab3Handler(self)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
