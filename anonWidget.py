
from tkinter import Y
from PyQt5.QtCore import QDate, QSize, Qt, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from inspect import getmembers, isfunction
import filters, anonymizers, utils as aux
import aiTools
import cgitb 
cgitb.enable(format = 'text')
from threading import Thread
import multiprocessing, docWriter as tbw

threadGlobal = None
workerGlobal = None


class AnonWidget(QWidget):
    def __init__(self,  mainWindow, 
                        filterList = (
                            getmembers(filters, isfunction), 
                            [(aiTools.filter_flair.__name__, aiTools.filter_flair)] 
                        ),
                        deidentifierList = (
                            getmembers(anonymizers, isfunction), 
                            [(aiTools.remove_flair_calle, aiTools.filter_flair), (aiTools.remove_flair_lugar_general, aiTools.filter_flair), (aiTools.remove_flair_nombre_persona, aiTools.filter_flair)]
                        ),
                ):
        super(AnonWidget, self).__init__()
        uic.loadUi(aux.resource_path("auxFiles/anon.ui"),self)
        self.mainWindow = mainWindow

        [i.hide()  for i in [self.progressBarDocuments, self.labelGeneralFilterIcon, self.labelGeneralAnonIcon]]

        
        #LOAD FILTERS and ANONYMIZIERS TO APPLY
        self.loadLoadingIcons()
        self.loadFilters(*filterList)
        self.loadAnonymizers(*deidentifierList)

        #BUTTON ASIGNATION
        self.buttonAssignation()

        self.excelFormats = {"Two Row": tbw.two_row_format, "Format Lara": tbw.format_lara}
        self.outputFormatSelector.clear()
        for format_name in self.excelFormats:
            self.outputFormatSelector.addItem(format_name)


        self.wordFormats = {"Replace with Type": tbw.replace_with_category_word, "Replace with X": tbw.replace_with_x_word, "Remove Completely": tbw.remove_completely_word}
        self.anonymizationFormatSelector.clear()
        for format_name in self.wordFormats:
            self.anonymizationFormatSelector.addItem(format_name)



    def buttonAssignation(self):
        #DOCUMENTS
        self.addDocumentsButton.clicked.connect(self.addDocumentProject)

        #FILTER
        self.excelDirectoryButton.clicked.connect(self.chooseDirectoryExcel)
        self.applyFiltersButton.clicked.connect(self.applyExcelFilters)
        self.exportFiltersButton.clicked.connect(self.exportExcelFilters)

        #ANON
        self.anonDirectoryButton.clicked.connect(self.chooseDirectoryAnon)
        self.exportAnonDocumentsButton.clicked.connect(self.exportAnonDocs)
        self.generateAnonButton.clicked.connect(self.generateAnon)


    def loadLoadingIcons(self):
        self.loadingIconFilter = QMovie(aux.resource_path("auxFiles/filterLoading.gif"))
        self.labelGeneralFilterIcon.setMovie(self.loadingIconFilter)
        self.loadingIconFilter.setScaledSize(self.labelGeneralFilterIcon.size())


        self.loadingIconAnon = QMovie(aux.resource_path("auxFiles/anonLoading.gif"))
        self.labelGeneralAnonIcon.setMovie(self.loadingIconAnon)
        self.loadingIconAnon.setScaledSize(self.labelGeneralAnonIcon.size())



    #DOCUMENTS
    def isFocused(self):
        if self.mainWindow.freezeFlag == True:
            return
    
        print("ANON IS FOCUSED")
        self.listaDocsWidget.clear()
        for key in self.mainWindow.projectLoaded:
            item = QListWidgetItem(key, self.listaDocsWidget)

    def finishedAddingDocuments(self, projectLoaded):   
        self.mainWindow.projectLoaded.update(projectLoaded)
        self.progressBarDocuments.hide()
        self.addDocumentsButton.show()
        self.mainWindow.stop_interaction(False)

        #APLICAR FILTROS YA EXISTENTES
        self.filter_functions_selected = [self.availableFilters[filterCheck] for filterCheck in self.filtros_existentes if self.availableFilters.get(filterCheck, None) != None]
        self.slow_filter_functions_selected = [self.slowFilters[filterCheck] for filterCheck in self.filtros_existentes if self.slowFilters.get(filterCheck, None) != None]

        # prepare to start process
        self.mainWindow.stop_interaction(True)
        [i.hide() for i in [self.applyFiltersButton, self.exportFiltersButton]]
        [i.show()  for i in [self.labelGeneralFilterIcon]]
        self.loadingIconFilter.start()

        self.thread = Thread(target = aux.applyAddDocumentFilterFunction, args = (self.mainWindow.projectLoaded, self.newDocumentsAdded, self.filter_functions_selected, self.slow_filter_functions_selected, self.finalThreadFilterFunction) )
        self.thread.start() 

    
    def updateProgressAddingDocuments(self, val):
        self.progressBarDocuments.setValue(val)

    def addDocumentProject(self):
        if self.mainWindow.check_freeze():
            return
        self.filtros_existentes = self.mainWindow.projectLoaded[list(self.mainWindow.projectLoaded.keys())[0]].keys()
        print("AÑADIENDO NUEVOS DOCUMENTOS RECUERDA QUE HAY QUE APLICAR ***AUTOMATICAMENTE!!*** TODOS LOS FILTROS QUE SE HAN APLICADO A LOS ANTERIORES DOCUMENTOS")
        
        fileNames, _ = QFileDialog.getOpenFileNames(self, caption = "Select PDFs to add to project", filter = "Documents (*.pdf *.PDF)")
        if(len(fileNames) == 0):
            return
        self.newDocumentsAdded = [i.split("/")[-1] for i in fileNames]

        self.progressBarDocuments.show()
        self.addDocumentsButton.hide()
        self.mainWindow.stop_interaction(True)
        self.worker = aux.ScanAndFilterDocumentsThread(fileNames)
        self.worker.worker_complete.connect(self.finishedAddingDocuments)
        self.worker.update_progress.connect(self.updateProgressAddingDocuments)
        self.worker.start()

        
        


    

    #FILTERS
    def loadFilters(self, listfilters, specialcolorfilters):
        self.filtersChecks = []
        self.availableFilters = {}
        self.slowFilters = {}

        for functionName, realFunction in listfilters:
            self.availableFilters[functionName] = realFunction
            self.filtersChecks.append(QListWidgetItem(functionName, self.listaFiltersWidget))

        for functionName, realFunction in specialcolorfilters:
            self.slowFilters[functionName] = realFunction
            self.filtersChecks.append(QListWidgetItem(functionName, self.listaFiltersWidget))
            self.filtersChecks[-1].setBackground(Qt.darkCyan)
            


        for item in self.filtersChecks:
            item.setCheckState(0)

    def chooseDirectoryExcel(self):
        excelDirectory = QFileDialog.getExistingDirectory(self, caption = "Where do you want to export the filters? (Excel file)")
        if(excelDirectory == ""):
            return
        excelFilename = self.mainWindow.projectNameWidget.text().split(".")[0] + ".xlsx"
        self.directoryExcelLineEdit.setText(excelDirectory + "/" +  excelFilename)

    def finalThreadFilterFunction(self):           
        self.mainWindow.stop_interaction(False)
        [i.show() for i in [self.applyFiltersButton, self.exportFiltersButton]]
        [i.hide()  for i in [ self.labelGeneralFilterIcon]]
        print("STOPPING NOW")

    def applyExcelFilters(self):
        if self.mainWindow.check_freeze():
            return
        #print(self.mainWindow.projectLoaded.keys())
        self.filter_functions_selected = [self.availableFilters[filterCheck.text()] for filterCheck in self.filtersChecks if filterCheck.checkState() == 2 and self.availableFilters.get(filterCheck.text(), None) != None]
        self.slow_filter_functions_selected = [self.slowFilters[filterCheck.text()] for filterCheck in self.filtersChecks if filterCheck.checkState() == 2 and self.slowFilters.get(filterCheck.text(), None) != None]



        # prepare to start process
        self.mainWindow.stop_interaction(True)
        [i.hide() for i in [self.applyFiltersButton, self.exportFiltersButton]]
        [i.show()  for i in [ self.labelGeneralFilterIcon]]
        self.loadingIconFilter.start()

        self.thread = Thread(target = aux.applyFilterFunction, args = (self.mainWindow.projectLoaded, self.filter_functions_selected, self.slow_filter_functions_selected, self.finalThreadFilterFunction) )
        self.thread.start() 




    def exportExcelFilters(self):
        if self.directoryExcelLineEdit.text() == "":
            QMessageBox.about(self, "Directory Error", "Please specify a directory to save the Excel...")
            return
        if self.mainWindow.check_freeze():
            return
        


        self.mainWindow.stop_interaction(True)
        [i.hide() for i in [self.applyFiltersButton, self.exportFiltersButton]]
        [i.show()  for i in [ self.labelGeneralFilterIcon]]
        self.loadingIconFilter.start()

        
        self.thread = Thread(target = tbw.excelWriterFunction, args = (self.excelFormats[self.outputFormatSelector.currentText()], self.mainWindow.projectLoaded, self.directoryExcelLineEdit.text(), self.finalThreadFilterFunction) )
        self.thread.start()

        



    #ANONS
    def loadAnonymizers(self, listanon, depends_filters):
        self.anonChecks = []
        self.availableAnons = {}

        for functionName, realFunction in listanon:
            item = QListWidgetItem(functionName, self.listaAnonWidget)
            self.anonChecks.append(item)
            item.setCheckState(2)
            self.availableAnons[functionName] = realFunction

        self.anon_dependency = {}
        for deidentifier_function, filter_function in depends_filters:
            self.anon_dependency[deidentifier_function.__name__] = (deidentifier_function, filter_function)
            item = QListWidgetItem(deidentifier_function.__name__, self.listaAnonWidget)
            self.anonChecks.append(item)
            item.setCheckState(2)
            item.setBackground(Qt.darkCyan)
        
    def chooseDirectoryAnon(self):
        anonDirectory = QFileDialog.getExistingDirectory(self, caption = "Where do you want to save the new project? (JSON file)")
        if(anonDirectory == ""):
            return

        self.directoryAnonLineEdit.setText(anonDirectory + "/ANON_DOCS_" + self.mainWindow.projectNameWidget.text().split(".json")[0]) 

    def finalThreadAnonFunction(self):           
        self.mainWindow.stop_interaction(False)
        [i.show() for i in [self.generateAnonButton, self.exportAnonDocumentsButton]]
        [i.hide()  for i in [self.labelGeneralAnonIcon]]

    def generateAnon(self):
        if self.mainWindow.check_freeze():
            return
        self.anon_functions_selected = [self.availableAnons[anonCheck.text()] for anonCheck in self.anonChecks if anonCheck.checkState() == 2 and self.availableAnons.get(anonCheck.text())]

        for functionName in self.anonChecks:
            if functionName.checkState() != 2:
                continue

            functionName = functionName.text()
            if self.anon_dependency.get(functionName, None) != None:
                anon_function, filter_necessary = self.anon_dependency[functionName][:2]
                filter_necessary = filter_necessary.__name__
                sample_to_check = list(self.mainWindow.projectLoaded.keys())[0]
                if self.mainWindow.projectLoaded[sample_to_check].get(filter_necessary, None) == None:
                    QMessageBox.about(self, "Please apply filter", f"You need to apply {filter_necessary} on the filters panel before trying to use {functionName}!\nNot doing any anonimization")
                    return
                else:
                    self.anon_functions_selected.append(anon_function)

        # prepare to start process
        self.mainWindow.stop_interaction(True)
        [i.hide() for i in [self.generateAnonButton, self.exportAnonDocumentsButton]]
        [i.show()  for i in [self.labelGeneralAnonIcon]]
        self.loadingIconAnon.start()

        self.thread = Thread(target = aux.applyAnonFunction, args = (self.mainWindow.projectLoaded, self.anon_functions_selected, self.finalThreadAnonFunction) )
        self.thread.start() 

    def exportAnonDocs(self):
        if self.mainWindow.check_freeze():
            return
        if self.directoryAnonLineEdit.text() == "":
            QMessageBox.about(self, "Directory Error", "Please specify a directory to save the anonymized documents...")
            return
        if self.mainWindow.projectLoaded[list(self.mainWindow.projectLoaded.keys())[0]].get("deidentified", None) == None:
            QMessageBox.about(self, "Not yet anonymized", "Please select the anonymizers and press the button 'Generate Anonymization' then you will be able to export the anonymized documents")
            return

        self.mainWindow.stop_interaction(True)
        [i.hide() for i in [self.generateAnonButton, self.exportAnonDocumentsButton]]
        [i.show()  for i in [self.labelGeneralAnonIcon]]
        self.loadingIconAnon.start()
        
        self.thread = Thread(target = tbw.wordWriterFunction, args = (self.wordFormats[self.anonymizationFormatSelector.currentText()], self.mainWindow.projectLoaded, self.directoryAnonLineEdit.text(), self.finalThreadAnonFunction) )
        self.thread.start()