import re




##############################################
# Eliminar referencias email y páginas web
#############################################
# {correo: [inicio, final]}
def filter_mail(contentdict, keyname = "filter_mail"):
    rules = [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b','(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])']
    contentdict[keyname] = {}
    for rule in rules:
        #print(contentdict["raw"])
        for email in re.finditer(rule, contentdict["raw"]):
            start_pos, end_pos = email.span()
            email = contentdict["raw"][start_pos:end_pos]
            contentdict[keyname][start_pos] = (end_pos, email)


    return contentdict



#######################################
# Eliminar referencias telefónicas
######################################
def filter_phone(contentdict, keyname = "filter_phone"):
    #regexs = ["(?:\+34|0034|34)?[ ]*(?:8|9)[ .]*(?:[0-9][ -]*){8}", "(?:\+34|0034|34)?[ ]*(?:6|7)[ .](?:[0-9][ -]*){8}", "(6|7|9)\d{8}", "MOVIL_reemplazo"]
    #regexs = ["[\+34|0034|34][ ]*[8|9][ .]*[[0-9][ -]*]{8}", "[\+34|0034|34][ ]*[6|7][ .]*[?:[0-9][ -]*]{8}","[6|7|9]\d{8}","MOVIL_reemplazo"]
    regexs = ["(:?(\+[0-9]{2,2}|00[0-9]{2-2}|[0-9]{2,2}))?[ ]*(:?(8|9))[ \.]*(:?[0-9][ |\-]*){8}", "(((\+[0-9]{2,2})|(00[0-9]{2,2})|([0,9]{2,2}))){0,1}([ ]*)([6|7])([ \.]*)(([0-9][ |\-]*){8})","[6|7|9]\d{8}","MOVIL_reemplazo"]


    contentdict[keyname] = {}

    for regexrule in regexs:
        for idfound in re.finditer(regexrule, contentdict["raw"]):
            start_pos, end_pos = idfound.span()
            idfound = contentdict["raw"][start_pos:end_pos]
            contentdict[keyname][start_pos] = (end_pos, idfound)

    return contentdict



######################################
# Eliminar referencia identificadores
#####################################
def filter_id(contentdict, keyname = "filter_id"):
    #text = text["raw"][0]
    regexrules = ["\b\d{5}\b", "(?:\d(?:\.|-)*){7,8}[A-Z]", "[0-9]{8,8}[A-Za-z]{0,1}", "[a-z]{3}[0-9]{6}[a-z]?", "[a-zA-Z]{1}\d{7}[a-zA-Z0-9]{1}", "[XxTtYyZz]{1}[0-9]{7}[a-zA-Z]{1}", "\d{11}", "\d{8}[a-zA-Z]{1}"]
    contentdict[keyname] = {}

    for regexrule in regexrules:
        for idfound in re.finditer(regexrule, contentdict["raw"]):
            start_pos, end_pos = idfound.span()
            idfound = contentdict["raw"][start_pos:end_pos]
            contentdict[keyname][start_pos] = (end_pos, idfound)    
    
    return contentdict


#########################################
# Eliminar referencia número de atestado
########################################
def filter_n_atestado(contentdict, keyname = "filter_n_atestado"):
    #text = text["raw"][0]
    contentdict[keyname] = {}
    regexrule = "[Aa][Tt][Ee][Ss][Tt][Aa][Dd][Oo] *[nN]?º? *:? *\d{3,}\/\d{2}"
    for idfound in re.finditer(regexrule, contentdict["raw"]):
        start_pos, end_pos = idfound.span()
        idfound = contentdict["raw"][start_pos:end_pos]
        contentdict[keyname][start_pos] = (end_pos, idfound)
    return contentdict

#########################################
# Eliminar referencia instructor
###########################################
def filter_instructor(contentdict, keyname = "filter_instructor"):
    contentdict[keyname] = {}

    #text = ogdict["raw"][0]
    for idfound in re.finditer("Instructor *: +(.*?) ", contentdict["raw"]):
        start_pos, end_pos = idfound.span()
        idfound = contentdict["raw"][start_pos:end_pos]
        contentdict[keyname][start_pos] = (end_pos, idfound)
    return contentdict



#############################################
# Eliminar referencia dependencias
#############################################
def filter_dependencia(contentdict, keyname = "filter_dependencia"):
    contentdict[keyname] = {}


    for idfound in re.finditer("Dependencia: +.+? {2,}", contentdict["raw"]):
        if idfound == "":
            continue
        start_pos, end_pos = idfound.span()
        idfound = contentdict["raw"][start_pos:end_pos]
        contentdict[keyname][start_pos] = (end_pos, idfound)

    return contentdict


#####################################
# Eliminar referencias temporales
#####################################
def filter_tiempo(contentdict, keyname = "filter_tiempo"):
    #returntext = ogdict["raw"][0]
    contentdict[keyname] = {}

    rules = ["(?:(?:[0-9]{1,2})(?:(?:\/)|(?:-))(?:[0-9]{1,2})(?:(?:\/)|(?:-))([0-9]{4}))",
    "(?:[0-9]{2}?) +de +(?:\w*?) +del*(?: +año)* +(([0-9]{4}?)|[0-9].[0-9]{3})",
    "(?:[0-9]{2}?) +de +(?:\w*?) +de +([0-9]{4}?).",
    "(?:[0-9]{2}?) +de +(?:\w*?) +del*(?: año)* +(([0-9]{4}?)|[0-9].[0-9]{3})",
    "(?:[0-9]{2}?) +de +(?:\w*?) +de +([0-9]{4}?).",
    "(las *)?([0-9]+(:[0-9]+)?)( *y *)(las *)?([0-9]+(:[0-9]+)?)?( horas)?",
    "([0-9]+(:[0-9]+)?) *(horas|HORAS|Horas)",
    "[0-9]{1,2} *(minutos|MINUTOS|Minutos)",
    "[0-9]{1,2} *(segundos|Segundos|SEGUNDOS)",
    "(día|Día|DÍA) *[0-9]{1,2}","TEMP<* *al *[0-9]{1,2}","día *TEMP<*","[0-9]{1,2}:[0-9]{2,2}"]

    for rule in rules:
        for finding in re.finditer(rule, contentdict["raw"]):
            start_pos, end_pos = finding.span()
            idfound = contentdict["raw"][start_pos:end_pos]
            contentdict[keyname][start_pos] = (end_pos, idfound)
             
    return contentdict