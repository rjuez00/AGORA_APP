from PyQt5.QtCore import pyqtSignal, QThread
import re, cgitb, os, sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pathos.multiprocessing import ProcessingPool as Pool
cgitb.enable(format = 'text')

def reemplazos(text,args=None):
    text = re.sub("''","",text)
    text = re.sub('[^a-zA-Zá-úÁ-Ú0-9_\.,]+'," ",text)
    text = re.sub(" +"," ",text)
    text = re.sub("\.+",".",text)
    text = re.sub("-+","",text)
    text = re.sub("<+","<",text)
    return text





################# SCANNING DOCUMENTS #################



class ScanDocumentsThread(QThread):
    update_progress = pyqtSignal(int)
    worker_complete = pyqtSignal(dict)

    def __init__(self, filenames, scanner_to_use, parent = None):
        super(ScanDocumentsThread, self).__init__(parent)
        self.scanner_to_use = scanner_to_use
        self.filenames = filenames

    def run(self):
        self.update_progress.emit(5)
        docs = {}
        cuantDocs = len(self.filenames)
        for idx, filename in enumerate(self.filenames):
            texto, hasOCR = self.scanner_to_use(filename)
            #print("ESCANEANDO ", filename, "CHECKS:", texto != "", texto.isspace)
            


            if texto != "" and texto.isspace() == False:
                docs[filename.split("/")[-1]] = {"raw": texto, "hasOCR": hasOCR} 
                self.update_progress.emit(100 * ((1+idx)/cuantDocs))

            else:
                print(f"ALERTA: El documento {filename} no ha sido escaneado")

        self.worker_complete.emit(docs)


class ScanAndFilterDocumentsThread(QThread):
    update_progress = pyqtSignal(int)
    worker_complete = pyqtSignal(dict)

    def __init__(self, filenames, scanner_to_use, parent = None):
        super(ScanAndFilterDocumentsThread, self).__init__(parent)
        self.filenames = filenames
        self.scanner_to_use = scanner_to_use

    def run(self):
        self.update_progress.emit(5)
        docs = {}
        cuantDocs = len(self.filenames)
        for idx, filename in enumerate(self.filenames):
            print("ESCANEANDO ", filename)
            scannedText = self.scanner_to_use(filename)
            if scannedText == None:
                scannedText = ""
           
            docs[filename.split("/")[-1]] = {"raw":scannedText} 
            
            self.update_progress.emit(100 * ((1+idx)/cuantDocs))


        self.worker_complete.emit(docs)

import time


class LoadMap(QThread):
    worker_complete = pyqtSignal()
    worker_progress = pyqtSignal(int)

    def __init__(self, mapGenerator, parent = None):
        super(LoadMap, self).__init__(parent)
        self.mapGenerator = mapGenerator

    def run(self):
        newmap = self.mapGenerator.perform_summary_queries(self.worker_progress)   
        self.worker_complete.emit()


################# FILTERS #################
def applyFilterFunction(contentDict, filter_list, slow_filter_list, finalthreadfunction):
    args = {}
    args['filtros'] = filter_list
    args['procesadores'] = [filtrar_texto]
    args['fragmentos'] = 0


    paral = ParalelizadorTarea()
    a = paral.ejectuar_tarea(contentDict ,procesamiento_info_completa,args, threaduse = 8)
    contentDict.update(a)
    
    print("STARTING SLOW FILTERS!!")
    a = procesamiento_slow_filters(contentDict, slow_filter_list)
    
    print("UPDATING!")
    contentDict.update(a)
    print("UPDATED ALREADY AFTER FINISHING FUNCTION")

    finalthreadfunction()


##########################################################################
# Función single thre
#########################################################################
def procesamiento_slow_filters(dicts, slow_filters):       
    for filtro in slow_filters:
        dicts = filtro(dicts)

    return dicts




def applyAddDocumentFilterFunction(contentDict, fileNames_added, filter_list, slow_filter_list, finalthreadfunction):
    tempContentDict = {i:contentDict[i] for i in fileNames_added}
    args = {}
    args['filtros'] = filter_list
    args['procesadores'] = [filtrar_texto]
    args['fragmentos'] = 0


    paral = ParalelizadorTarea()
    a = paral.ejectuar_tarea(tempContentDict ,procesamiento_info_completa,args, threaduse = 8)
    tempContentDict.update(a)
    
    print("STARTING SLOW FILTERS!!")
    a = procesamiento_slow_filters(tempContentDict, slow_filter_list)
    
    print("UPDATING!")
    tempContentDict.update(a)
    print("UPDATED ALREADY AFTER FINISHING FUNCTION")


    contentDict.update(tempContentDict)

    finalthreadfunction()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(application_path, relative_path)


##########################################################################
# Función que permite procesar un conjuto de textos
# se pasa dentro del diccionario el conjunto de procesadores (funciones)
# que se deben de aplicar secuencialmente a los textos
#########################################################################
def procesamiento_info_completa(conjunto_inicial,args):   
    procesadores = args['procesadores']
    
    claves = list(conjunto_inicial.keys())
    procesados = 0
    for key in claves:
        text = conjunto_inicial[key]
        for proc in procesadores:
            # si detro de un texto se quiere procesar independientemente
            # cada fragmento separado por ~SEP~
            if(args['fragmentos']==1):
                text = procesar_por_fragmentos(text,proc,args)
            else:
                text = proc(text,args)
            if(text == {}):
                conjunto_inicial.pop(key, None)
                break
            
          
    

        if(text != {}):
            conjunto_inicial[key] = text

        procesados +=1
        
    
    return conjunto_inicial


################# EXECUTION #################
class ParalelizadorTarea():
    def __init__(self):
        self.conjunto_final = {}
    
    
    def ejectuar_tarea(self,dicts,funcion,args=None,threaduse=8):
        if(threaduse > len(dicts)):
            threadcount = len(dicts)
            jumpdelta=1
        else:
            threadcount = threaduse 
            jumpdelta = int(len(dicts)/threadcount)
        
        currentrange = 0
        
        print(jumpdelta,threadcount)
        
        claves = list(dicts.keys())
        

        if threadcount == 1:
            a = [funcion(dicts, args)]
        
        else:
            # iniciar threads
            try:
                pool = Pool(threadcount)
            except:
                return dicts

            splittedProject = []
            for i in range(0, threadcount-1):
                splittedProject.append(    {key: dicts[key] for key in claves[currentrange:(currentrange+jumpdelta)]}   )
                currentrange += jumpdelta
            
            splittedProject.append(  {key: dicts[key] for key in claves[currentrange:]}   )
            
            a = pool.map(funcion, splittedProject, [args]*len(splittedProject))
    
        
            # comentar las siguientes dos lineas si se va a hacer el pyinstaller, si no descomentar
            """pool.close()
            pool.join()"""

        newDict = {}
        for i in a:
            newDict.update(i)
        
        
         
        print("ENDING PARALELIZADOR HANDLER AND RETURNING FINAL RESULT")
        return newDict







################# ANONS #################
def applyAnonFunction(contentDict, anon_list, finalthreadfunction):
    args = {}
    args['anonimizadores'] = anon_list
    args['procesadores'] = [anonimizar_texto]
    args['fragmentos'] = 0


    paral = ParalelizadorTarea()
    a = paral.ejectuar_tarea(contentDict ,procesamiento_info_completa,args, threaduse = 8)
    contentDict.update(a)
    finalthreadfunction()



#########################################################
#  Funcion para anonimizar textos
#  se pasa dentro del diccionario args
#  el conjunto de anonimizadores
########################################################## 
def anonimizar_texto(contentDict, args):
    anonimizers = args['anonimizadores']
    if contentDict.get("deidentified", None) == None:
        contentDict["deidentified"] = contentDict["raw"]
    
    for anonimizier in anonimizers:
        print("ANONINIMIZANDO DE VERDAD")
        print(anonimizier.__name__)
        contentDict["deidentified"] = anonimizier(contentDict)
    
    return contentDict


#########################################################
#  Funcion para anonimizar textos
#  se pasa dentro del diccionario args
#  el conjunto de anonimizadores
########################################################## 
def filtrar_texto(docDict,args):
    filters = args['filtros']
    for filter in filters:
        docDict = filter(docDict)
    return docDict





#########################################################
# Función para procesar textos por fragmentos separados
# por ~SEP~
########################################################
def procesar_por_fragmentos(text,funcion,args=None):
    fragmentos = re.split("~*SEP~",text)
    procesados =[]
    for frag in fragmentos:
        procesados += [funcion(frag,args)]
    return "~SEP~".join(procesados)
