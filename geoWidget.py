
from PyQt5.QtCore import QDate, QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5 import uic
import json
from statMap import Statmap
from threading import Thread
import matplotlib
callesFilter = "CALLE"
import utils
from geocoding import finalAmenityDict


class GeoWidget(QWidget):
    def __init__(self, mainWindow):
        super(GeoWidget, self).__init__()
        uic.loadUi(utils.resource_path("auxFiles/geo.ui"),self)
        self.mainWindow = mainWindow
        self.listaDocsWidget.itemSelectionChanged.connect(self.selectDocument)
        self.loadMapButton.clicked.connect(self.loadMap)
        with open(utils.resource_path("auxFiles/geoPlaceHolder.html")) as f:
            geoPlaceHolder = f.read()
        #self.mapWebWidget.setHtml(geoPlaceHolder)
        self.cacheMaps = dict(zip(self.mainWindow.projectLoaded.keys(), [None] * len(self.mainWindow.projectLoaded)))
        self.mapProgressBar.hide()

        self.amenitiesReferences = []
        for topic, listAmenities in finalAmenityDict.items():
            branch = QTreeWidgetItem([topic])
            self.amenitiesList.addTopLevelItem(branch)
          
            for amenity in listAmenities:
                tempitem = QTreeWidgetItem([amenity])
                branch.addChild(tempitem)
                self.amenitiesReferences.append(tempitem)
                tempitem.setCheckState(0, Qt.Checked)



    def isFocused(self):
        if self.mainWindow.freezeFlag == True:
            return

        self.geoFiltersWarning()

        print("GEO IS FOCUSED CHECK ADDRESSES EXTRACTED IF NOT FOCUS AGAIN IN ANON AND SHOW MESSAGE")
        for key in self.mainWindow.projectLoaded:
            item = QListWidgetItem(key, self.listaDocsWidget)

        self.listaDocsWidget.setSelectionMode(QAbstractItemView.SingleSelection)



    def selectDocument(self):
        self.geoFiltersWarning()
        selectedDocument = self.listaDocsWidget.selectedItems()[0].text()

        self.callesList.clear()
        self.streetChecks = []
        for _, (_, calle) in self.mainWindow.projectLoaded[selectedDocument][callesFilter].items():
            item = QListWidgetItem(calle, self.callesList)
            self.streetChecks.append(item)
            item.setCheckState(2)



    
    def hasGeoFilters(self):
        sampleDoc = self.mainWindow.projectLoaded[list(self.mainWindow.projectLoaded.keys())[0]]
        return sampleDoc.get(callesFilter, None) != None

    def geoFiltersWarning(self):
        if not self.hasGeoFilters():
            QMessageBox.warning(self, "Geographic filters not available", "For the geotool to work you must first apply the filters with a [GEO] tag")
            self.mainWindow.tabWidget.setCurrentWidget(self.mainWindow.tabWidgetList["Anonimizator"])
            return False
        
        return True

    def finishLoadingMap(self, cachedMap = None):
        if cachedMap == None:
            newmap = self.mapGenerator.getHtmlMap()    
            if newmap == None:  
                with open(utils.resource_path("auxFiles/noMapAvailable.html")) as f:
                    newmap = f.read()
        else:
            newmap = cachedMap
        print("TERMINADO\n")
        self.mapWebWidget.setHtml(newmap)
        self.loadMapButton.show()
        self.radiusBox.show()
        self.mapProgressBar.hide()

        self.cacheMaps[self.loadingMapDocumentName] = {'html': newmap, 'streets': self.loadingMapStreetChecks}

    def updateMapProgressBar(self, progress):
        self.mapProgressBar.setValue(progress)

    def loadMap(self):
        canContinue = self.geoFiltersWarning()
        if not canContinue:
            return
        
        with open(utils.resource_path("auxFiles/geoPlaceHolder.html")) as f:
            self.mapWebWidget.setHtml(f.read())

        itemSelected = self.listaDocsWidget.currentItem()
        if itemSelected == None:
            return
            
        self.documentCurrentlySelected = itemSelected.text()
        self.documentDisplayedName.setText(self.documentCurrentlySelected)
        
        self.streetsSelected = [calleCheck.text() for calleCheck in self.streetChecks if calleCheck.checkState() == 2]
        
        if self.cacheMaps[self.documentCurrentlySelected] != None and self.cacheMaps[self.documentCurrentlySelected]["streets"] == self.streetsSelected:
            self.finishLoadingMap(self.cacheMaps[self.documentCurrentlySelected]['html'])
            return
        
        
        self.loadMapButton.hide()
        self.radiusBox.hide()

        self.currentlySelectedAmenities = [filterCheck.text(0) for filterCheck in self.amenitiesReferences if filterCheck.checkState(0) == 2]
        print("AAAAAAAAAAAAAAAAAAAAA"*10 , self.currentlySelectedAmenities)

        self.mapGenerator = Statmap(self.streetsSelected.copy(), self.radiusBox.value(), self.currentlySelectedAmenities)
        
        self.loadingMapDocumentName = self.documentCurrentlySelected
        self.loadingMapStreetChecks = self.streetsSelected
        
        self.mapProgressBar.show()
       
        self.worker = utils.LoadMap(self.mapGenerator, parent = self.mainWindow)
        self.worker.worker_complete.connect(self.finishLoadingMap)
        self.worker.worker_progress.connect(self.updateMapProgressBar)
        self.worker.start()

        self.loadingMapDocumentName = self.documentCurrentlySelected
        self.loadingMapStreetChecks = self.streetsSelected
        
        for i in self.streetChecks:
            if i.text() in self.mapGenerator.get_incorrect_addresses:
                i.setBackground(QBrush(QColor(255,0,0)))
            
            if i.text() in self.mapGenerator.repeated_addresses:
                i.setBackground(Qt.darkYellow)



   

        #self.worker.wait()
