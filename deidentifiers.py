import re
from tracemalloc import start

##############################################
# Eliminar referencias email y páginas web
#############################################
def remove_mail(contentDict):
    text = contentDict["deidentified"]
    rules = [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b','(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])']
    for rule in rules:
        for email in re.finditer(rule, text):
            start_pos, end_pos = email.span()
            text =  text[:start_pos] + 'MAIL' + "<"*(-4 + end_pos-start_pos) + text[end_pos:]
    return text


#######################################
# Eliminar referencias telefónicas
######################################
def remove_phone(contentDict):
    #regexs = ["(?:\+34|0034|34)?[ ]*(?:8|9)[ .]*(?:[0-9][ -]*){8}", "(?:\+34|0034|34)?[ ]*(?:6|7)[ .](?:[0-9][ -]*){8}", "(6|7|9)\d{8}", "MOVIL_reemplazo"]
    #regexs = ["[\+34|0034|34][ ]*[8|9][ .]*[[0-9][ -]*]{8}", "[\+34|0034|34][ ]*[6|7][ .]*[?:[0-9][ -]*]{8}","[6|7|9]\d{8}","MOVIL_reemplazo"]
    regexs = ["(:?(\+[0-9]{2,2}|00[0-9]{2-2}|[0-9]{2,2}))?[ ]*(:?(8|9))[ \.]*(:?[0-9][ |\-]*){8}", "(((\+[0-9]{2,2})|(00[0-9]{2,2})|([0,9]{2,2}))){0,1}([ ]*)([6|7])([ \.]*)(([0-9][ |\-]*){8})","[6|7|9]\d{8}","MOVIL_reemplazo"]
    text = contentDict["deidentified"]
    for regexrule in regexs:
        for idfound in re.finditer(regexrule, text):
            startdx, endidx = idfound.span()
            #idfound = re.sub("\+","\+",idfound)
            #idfound = re.sub("\(","\(",idfound)
            #idfound = re.sub("\)","\)",idfound)
            #idfound = re.sub("\]","\]",idfound)
            #idfound = re.sub("\[","\[",idfound)
            #idfound = re.sub("\*","\*",idfound)
            
            text = text[:startdx] + "NUM" + "<"*(-3 + endidx-startdx) + text[endidx:]

    
    for match in re.finditer('[0-9]?NUM<+[0-9]?',text):
        startidx, endidx = match.span()

        text = text[:startidx] + "NUM" + "<"*(-3 + endidx-startidx) + text[endidx:]

    return text

######################################
# Eliminar referencia identificadores
#####################################
def remove_id(contentDict):
    text = contentDict["deidentified"]
    regexrules = ["\b\d{5}\b", "(?:\d(?:\.|-)*){7,8}[A-Z]", "[0-9]{8,8}[A-Za-z]{0,1}", "[a-z]{3}[0-9]{6}[a-z]?", "[a-zA-Z]{1}\d{7}[a-zA-Z0-9]{1}", "[XxTtYyZz]{1}[0-9]{7}[a-zA-Z]{1}", "\d{11}", "\d{8}[a-zA-Z]{1}"]

    for regexrule in regexrules:
        for match in re.finditer(regexrule, text):
            startidx, endidx = match.span()
            text = text[:startidx] + "NUM" + "<"*(-3 + endidx-startidx) + text[endidx:]
    
    for match in re.finditer('[A-Za-z0-9]?NUM<+[A-Za-z0-9]?',text):
        startidx, endidx = match.span()
        text = text[:startidx] + "NUM" + "<"*(-3 + endidx-startidx) + text[endidx:]

    return text
#########################################
# Eliminar referencia número de atestado
########################################
def remove_n_atestado(contentDict):
    text = contentDict["deidentified"]
    regexrule = "[Aa][Tt][Ee][Ss][Tt][Aa][Dd][Oo] *[nN]?º? *:? *\d{3,}\/\d{2}"
    for match in re.finditer(regexrule, text):
        startidx, endidx = match.span()
        text = text[:startidx] + "AT" + "<"*(-2 + endidx-startidx) + text[endidx:]
    return text

#########################################
# Eliminar referencia instructor
###########################################
def remove_instructor(contentDict):
    text = contentDict["deidentified"]
    for match in re.finditer("Instructor *: +(.*?) ", text):
        startidx, endidx = match.span()
        text = text[:startidx] + "INS" + "<"*(-3 + endidx-startidx) + text[endidx:]

    return text
#############################################
# Eliminar referencia dependencias
#############################################
def remove_dependencia(contentDict):
    text = contentDict["deidentified"]
    #for idfound in re.findall("Dependencia: +.*? {2,}", text):
    for match in re.finditer("Dependencia: +.+? {2,}", text):
        startidx, endidx = match.span()
        if startidx -endidx < 1:
            continue
        text = text[:startidx] + "DEP" + "<"*(-3 + endidx-startidx) + text[endidx:]
    
    return text


#####################################
# Eliminar referencias temporales
#####################################
def remove_tiempo(contentDict):
    returntext = contentDict["deidentified"]
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
        for finding in re.finditer(rule, returntext):
            starte, ende = finding.span()
            lene = ende - starte - 4
            returntext = returntext[:starte] + 'TIEM' + lene*"<" + returntext[ende:]    
    return returntext

#########################################
# Eliminar carnet profesional del texto
#########################################
def remove_carnet_profesional(contentDict):
    text = contentDict["deidentified"]
    regexrules =  ["número +de +soporte +(.*?)(,| |\n|\.)"]
    for regexrule in regexrules:
        print(regexrule)
        for finding in re.finditer(regexrule, text):
            print("entra")
            start_pos, end_pos = finding.span()
            text =  text[:start_pos] + 'CAR' + "<"*(-3 + end_pos-start_pos) + text[end_pos:]
    return text