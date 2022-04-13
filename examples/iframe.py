#!/usr/bin/python
# -*- coding: utf-8 -*-
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

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


class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.resize(900, 700)
        self.view = QWebEngineView(self)

        mypage = MyPage(self.view)
        self.view.setPage(mypage)
        mypage.setHtml(s)

        grid = QGridLayout()
        grid.addWidget(self.view, 0, 0)
        self.setLayout(grid)
        self.show()

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
        if  self.in_window and type==2:
            webbrowser.open(url_string)
            self.in_window = False
            self.setHtml(s)
        return True

if __name__ == '__main__':
    app = None
    if not QApplication.instance():
        app = QApplication([])
    dlg = MainWindow()
    if app: app.exec_()
