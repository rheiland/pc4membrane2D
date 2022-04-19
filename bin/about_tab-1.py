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
from PyQt5.QtWidgets import QFrame,QApplication,QWidget,QTabWidget,QFormLayout,QLineEdit, QHBoxLayout,QVBoxLayout,QRadioButton,QLabel,QCheckBox,QComboBox,QScrollArea, QTextEdit,QTextBrowser
from PyQt5.QtWebEngineWidgets import *

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class MyPage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.in_window = False

    def createWindow(self, type):
        self.in_window = True
        return self

    def acceptNavigationRequest(self, QUrl, type, isMainFrame):
        url_string = QUrl.toString()
        print(type, isMainFrame, QUrl)
        s = str("""<!DOCTYPE html>
         <html>
        <head></head>
         <div style="text-align: center;">
         <iframe frameborder="0" allowtransparency="true" scrolling="yes" src="https://docs.google.com/document/d/1uebPetZgx1-ofKV_A8EYV3lgXtQvH_o4kPUmM6wpwDk/edit?usp=sharing width="950" height="900"></iframe>
         </div>
          <div>
        <a href="https://docs.google.com/document/d/1uebPetZgx1-ofKV_A8EYV3lgXtQvH_o4kPUmM6wpwDk/edit?usp=sharing">TEST LINK</a>
         </div>
         </body>
         </html>""")
        if  self.in_window and type==2:
            webbrowser.open(url_string)
            self.in_window = False
            self.setHtml(s)
        return True

class About(QWidget):
    def __init__(self, doc_absolute_path):
        super().__init__()
        # global self.config_params

        self.doc_absolute_path = doc_absolute_path

        # self.tab = QWidget()
        # self.tabs.resize(200,5)
        
        #-------------------------------------------
        label_width = 110
        domain_value_width = 100
        value_width = 60
        label_height = 20
        units_width = 70

        self.scroll = QScrollArea()  # might contain centralWidget

        self.view = QWebEngineView(self)

        self.text = QTextBrowser()
        self.text.setHtml("&nbsp;")
        self.text.setOpenExternalLinks(True)
        self.text.setOpenLinks(True)

        fname = os.path.join(self.doc_absolute_path,"about.html")
        f = QtCore.QFile(fname)
        f.open(QtCore.QFile.ReadOnly|QtCore.QFile.Text)
        istream = QtCore.QTextStream(f)
        self.text.setHtml(istream.readAll())
        f.close()

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(0)
        self.vbox.addStretch()

        #==================================================================
        self.text.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)

        self.scroll.setWidget(self.text) 
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.scroll)
