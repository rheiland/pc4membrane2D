import os
import sys
import getopt
import shutil
import glob
from pathlib import Path

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QProcess

from about_tab import About


class ExternalBrowser(QWidget):
    def __init__(self, parent = None):
        super(ExternalBrowser, self).__init__(parent)

        self.setWindowTitle("External Browser")

        # Menus
        vlayout = QVBoxLayout(self)
        vlayout.setContentsMargins(-1, 10, -1, -1)
        self.setLayout(vlayout)

        self.resize(800, 600)

        docDirectory = os.path.join(os.getcwd(),"doc")
        self.absolute_doc_dir = os.path.abspath(docDirectory)

        self.about_tab = About(self.absolute_doc_dir)

        self.tabWidget = QTabWidget()

        stylesheet = """
            QTabBar::tab:selected {background: orange;}   #  dodgerblue
            """
        self.tabWidget.setStyleSheet(stylesheet)
        self.tabWidget.addTab(self.about_tab,"About")

        vlayout.addWidget(self.tabWidget)

        self.tabWidget.setCurrentIndex(0)  # Config (default)


def main():
    app = QApplication(sys.argv)
    ex = ExternalBrowser()
    ex.show()
    sys.exit(app.exec_())
	
if __name__ == '__main__':
    main()
