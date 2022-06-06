from PyQt5.QtWidgets import QMainWindow, QWidget,QStackedWidget, QApplication, QPushButton, QLabel, QFileDialog, QDialog, QInputDialog, QLineEdit, QErrorMessage
from PyQt5.QtGui import QPalette, QColor
from PyQt5 import uic
from PyQt5.QtCore import Qt
from domainChooserDialog import DomainChooserDialog
import sys, re, json, utils as aux, cgitb , multiprocessing
from PyQt5.QtGui import QIcon

 


from mainWindow import MainWindow

#https://github.com/codefirstio/pyqt5-full-app-tutorial-for-beginners/blob/main/main.py
#falta pedir donde crear archivo de nuevo proyecto


class StartScreen(QDialog):
    def __init__(self, startDimensions, windowDimensions, quickstart = None):
        super().__init__()
        self.setWindowIcon(QIcon('auxFiles/appLogo.png'))        
        self.setWindowTitle('Open or Create Project')
        self.mainWindowWidth, self.mainWindowHeight = windowDimensions
        self.setFixedSize(*startDimensions)

        uic.loadUi(aux.resource_path("auxFiles/startscreen.ui"), self)
        self.openJSONbutton = self.findChild(QPushButton, "openJSONButton")
        self.openPDFSbutton = self.findChild(QPushButton, "openPDFsButton")
        
        self.openJSONbutton.clicked.connect(self.loadJSONui)
        self.openPDFSbutton.clicked.connect(self.loadPDFsui)

        self.show()

        if(quickstart != None):
            self.domain = quickstart.split("/")[-1].split(".")[1]
            print(self.domain)
            self.startMainWindow(quickstart, self.loadProject(quickstart))
        
        self.progressBar.hide()

        

    def loadJSONui(self):
        print("LOADING JSON")
        fileName, _ = QFileDialog.getOpenFileName(self,"Select existing project", "","Project (*.agora)")
        if fileName:
            self.domain = fileName.split("/")[-1].split(".")[1]
            print(self.domain)
            self.startMainWindow(fileName, self.loadProject(fileName))
        else:
            exit()




    def loadPDFsui(self):
        print("LOADING PDFs")
        fileNames, _ = QFileDialog.getOpenFileNames(self, caption = "Select PDFs to start project", filter = "Documents (*.pdf *.PDF)")
        if(len(fileNames) == 0):
            exit()


        self.domain = DomainChooserDialog().getResults()

        projectName = ""
        checkspecialchars = re.compile('[@_!#$%^&*()<>?/\|}{~:\.]')
        while(projectName == ""):
            projectName, _ = QInputDialog.getText(self, "Project name", "NOTE: Don't use special characters (dots are not allowed either)\n\nChoose a name for your new project:", QLineEdit.Normal)
            if(checkspecialchars.search(projectName) != None):
                projectName = ""

        savingdirectory = QFileDialog.getExistingDirectory(self, caption = "Where do you want to save the new project? (agora file)")
        if(savingdirectory == ""):
            exit()

        savingdirectory = savingdirectory + "/" + projectName + f".{self.domain}.agora"
        
        self.savingdirectory = savingdirectory
        self.createProject(fileNames)


    def loadProject(self, projectFileName):
        with open(projectFileName, encoding = "utf-8") as json_file:
            projectLoaded = json.load(json_file)
        return projectLoaded


    ########################
    def finishedAddingDocuments(self, projectLoaded):   
            self.startMainWindow(self.savingdirectory, projectLoaded)


    def updateProgressAddingDocuments(self, val):
            self.progressBar.setValue(val)


    def createProject(self, fileNames):
        self.progressBar.show()
        self.openJSONbutton.hide()
        self.openPDFSbutton.hide()
        
        
        


        
        self.worker = aux.ScanDocumentsThread(fileNames)
        self.worker.worker_complete.connect(self.finishedAddingDocuments)
        self.worker.update_progress.connect(self.updateProgressAddingDocuments)
        self.worker.start()
        
        
        self.progressBar.show()
        self.openJSONbutton.hide()
        self.openPDFSbutton.hide()



    ########################
    def startMainWindow(self, projectFilename, projectLoaded):
        self.close()
        self.hide()
        mainwindow = MainWindow(projectFilename, projectLoaded, domain = self.domain)
        #mainwindow.setFixedHeight(self.mainWindowHeight)
        #mainwindow.setFixedWidth(self.mainWindowWidth)
        mainwindow.show()
    
def setStyle(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)


if __name__ == '__main__':
    cgitb.enable(format = 'text')
    multiprocessing.freeze_support()

    sys._excepthook = sys.excepthook 
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback) 
        sys.exit(1) 
    sys.excepthook = exception_hook 

    app = QApplication(sys.argv)
    setStyle(app)

    

    if len(sys.argv) > 1:
        welcome = StartScreen((451, 60), (1300, 700), quickstart = sys.argv[1])
    else:
        welcome = StartScreen((451, 60), (1300, 700))

    sys.exit(app.exec_())