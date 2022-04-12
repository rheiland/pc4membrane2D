"""
Authors:
Randy Heiland (heiland@iu.edu)
Adam Morrow, Grant Waldrow, Drew Willis, Kim Crevecoeur
Dr. Paul Macklin (macklinp@iu.edu)

--- Versions ---
0.1 - initial version
"""

import os
# import sys
from pathlib import Path
# import xml.etree.ElementTree as ET  # https://docs.python.org/2/library/xml.etree.elementtree.html
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame,QApplication,QWidget,QTabWidget,QFormLayout,QLineEdit, QHBoxLayout,QVBoxLayout,QRadioButton,QLabel,QCheckBox,QComboBox,QScrollArea, QTextEdit

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class About(QWidget):
    def __init__(self, nanohub_flag):
        super().__init__()
        # global self.config_params

        self.nanohub_flag = nanohub_flag

        # self.tab = QWidget()
        # self.tabs.resize(200,5)
        
        #-------------------------------------------
        label_width = 110
        domain_value_width = 100
        value_width = 60
        label_height = 20
        units_width = 70

        self.scroll = QScrollArea()  # might contain centralWidget

        self.text = QTextEdit()
        # self.text.setPlainText("Hello, world")
        # doc_dir = os.path.abspath('doc')
        # # html_file = Path(doc_dir,"about.html")
        # html_file = Path("doc","about.html")
        # print(html_file)
        f = QtCore.QFile("doc/about.html")
        # f = QtCore.QFile("html_file")
        f.open(QtCore.QFile.ReadOnly|QtCore.QFile.Text)
        print("\n\n------------------- about_tab.py:  f.isOpen() = ",f.isOpen())
        print("------------------- \n\n")
        istream = QtCore.QTextStream(f)
        self.text.setHtml(istream.readAll())
        f.close()

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(0)


        # self.vbox.addWidget(self.cells_csv)

        #--------------------------
        # Dummy widget for filler??
        # label = QLabel("")
        # label.setFixedHeight(1000)
        # # label.setStyleSheet("background-color: orange")
        # label.setAlignment(QtCore.Qt.AlignCenter)
        # self.vbox.addWidget(label)

        self.vbox.addStretch()


        #==================================================================
        self.text.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)

        # self.scroll.setWidget(self.config_params) # self.config_params = QWidget()
        self.scroll.setWidget(self.text) 

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.scroll)
