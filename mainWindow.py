#https://www.youtube.com/watch?v=i4rau-6PhNM
key = "AIzaSyAoafYjVCpZ6jH8fP57jY7rfXjxRaBJxEo"

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from domainIndex import domainIndex
from PyQt5.QtGui import QPixmap
from anonWidget import AnonWidget
from geoWidget import GeoWidget
from PyQt5.QtGui import QIcon
import os, json, utils, sys


class MainWindow(QMainWindow):
    def __init__(self, projectDirectory, projectLoaded, domain = "Police"):
        super(MainWindow, self).__init__()
        loadUi(utils.resource_path("auxFiles/mainwindow.ui"),self)
        self.freezeFlag = False
        self.setWindowIcon(QIcon(utils.resource_path('auxFiles/appLogo.png')))        
        self.appLogo.setPixmap(QPixmap(utils.resource_path('auxFiles/appLogo.png')))
        self.appLogo.setScaledContents( True );

        self.setWindowTitle("AGORA")
        self.projectDirectory = projectDirectory
        self.projectNameWidget.setText(os.path.normpath(projectDirectory).split(os.sep)[-1])
        self.projectLoaded = projectLoaded

        
        self.tabWidgetList = {"Anonimizator": AnonWidget(self, domainIndex[domain]["filterList"], domainIndex[domain]["deidentifierList"]), "Geotool": GeoWidget(self), }
        
        
        self.tabsOrder = []     
        for tabName, tabContent in self.tabWidgetList.items():
            self.tabWidget.addTab(tabContent, tabName)
            self.tabsOrder.append(tabContent)
        
        self.tabWidget.currentChanged.connect(self.tabChanged)  
        
        
        self.saveButton.clicked.connect(self.saveButtonAction)
        self.tabChanged()

    def tabChanged(self):
        if self.check_freeze():
            self.tabWidget.setCurrentWidget(self.tabWidgetList["Anonimizator"])

        self.tabsOrder[self.tabWidget.currentIndex()].isFocused()

    def saveButtonAction(self):
        if self.check_freeze():
            return
                       
        with open(utils.resource_path(self.projectDirectory), "w", encoding = "utf-8") as file:
            json.dump(self.projectLoaded, file, indent = 4, ensure_ascii = False)

    def closeEvent(self, event):
        if self.check_freeze():
            return

        if QMessageBox.question(self, 'Save project', "Do you want to save the project changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.saveButtonAction()
        print("CERRANDO APP")
        event.accept()
    


    def stop_interaction(self, dostop = True):
            self.freezeFlag = dostop
            if dostop == False:
                self.tabsOrder[self.tabWidget.currentIndex()].isFocused()

    def check_freeze(self):
        if self.freezeFlag == True:
            QMessageBox.about(self, "Please wait", "Please wait until the current process is done")
        
        return self.freezeFlag
