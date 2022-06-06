from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.Qt import QButtonGroup, QRadioButton, QPushButton
from PyQt5 import uic, QtCore, QtWidgets
from domainIndex import domainIndex
from PyQt5.QtGui import QIcon
from utils import resource_path

Ui_Dialog, _ = uic.loadUiType(resource_path("auxFiles/domainPicker.ui"))

class DomainChooserDialog(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super(DomainChooserDialog, self).__init__()
        self.setupUi(self)
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)
        self.setWindowIcon(QIcon(resource_path('auxFiles/appLogo.png')))        
        self.options = []
        firstFlag = True
        for idx, key in enumerate(domainIndex.keys()):
            radiobutton = QRadioButton(key)
            #radiobutton.setAlignment(QtCore.Qt.AlignLeft)
            if firstFlag == True:
                radiobutton.setChecked(True)
                firstFlag = False
            layout.addWidget(radiobutton, idx, alignment=QtCore.Qt.AlignLeft)
            self.options.append(radiobutton)

            

        confirm = QPushButton("CONFIRMAR\nSELECCCIÓN")
        layout.addWidget(confirm, idx+1)
        confirm.clicked.connect(self.accept)
        self.setFixedSize(self.minimumSizeHint())



    def getResults(self):
        if self.exec_() == QDialog.Accepted:
            for option in self.options:
                if option.isChecked():
                    return option.text()
        else:
            return None