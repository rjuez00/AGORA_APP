import pandas as pd, docx, json, re, os
from fileinput import filename
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from docx.shared import RGBColor, Inches, Cm


def create_common_pandas(projectLoaded):   
    default_filters = [key for key, contents in projectLoaded[list(projectLoaded.keys())[0]].items() if type(contents) == dict]
    multiindex = []
    each_entity_in_filter_has = ["entity", "index"]
    for documentName in projectLoaded.keys():
        for miniindex in each_entity_in_filter_has:
            multiindex.append((documentName, miniindex))
    multiindex = pd.MultiIndex.from_tuples(multiindex, names=["documentName", "filterContents"])
    
    filters_length = {filterName : 0 for filterName in default_filters}
    for _, contentDocument in projectLoaded.items():
        for filterName in default_filters:
            filters_length[filterName] = max(filters_length[filterName], len(contentDocument[filterName]))
    
    multicolumn = []
    for filtersName, length in filters_length.items():
        for i in range(length):
            multicolumn.append((filtersName, i+1))
    multicolumn = pd.MultiIndex.from_tuples(multicolumn, names=["filterName", "#"])


    a = pd.DataFrame(index=multiindex, columns = multicolumn)


    for documentName in projectLoaded.keys():
        for filterName in default_filters:
            for idx, (startidx, (endidx, entityText)) in enumerate(projectLoaded[documentName][filterName].items()):
                a.loc[(documentName, "entity")  ,   (filterName, idx+1)] = entityText
                a.loc[(documentName, "index")  ,   (filterName, idx+1)] = f"{startidx} - {endidx}"
    
    return a

def excelWriterFunction(projectLoaded, directorySave, finishingfunction):
    a = create_common_pandas(projectLoaded)
    a.to_excel(directorySave)
    finishingfunction()

def wordWriterFunction(projectLoaded, directorySave, finishingfunction):
    if not os.path.exists(directorySave):
        os.mkdir(directorySave)

    for documentName, documentContents in projectLoaded.items():
        document_to_word(documentName, documentContents["deidentified"], directorySave + "/" + documentName.split(".PDF")[0] + ".docx")
    
    finishingfunction()

def document_to_word(filename, target, directory_save):
    red = RGBColor(0xFF, 0x0, 0x0)

    def valid_xml_char_ordinal(c):
        codepoint = ord(c)
        # conditions ordered by presumed frequency
        return (
            0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF
            )

    decode_string = lambda input_string: ''.join(c for c in input_string if valid_xml_char_ordinal(c))


    document = docx.Document()
    for section in document.sections:
        section.top_margin = Cm(0.5)
        section.bottom_margin = Cm(0.5)
        section.left_margin = Cm(0.5)
        section.right_margin = Cm(0.5)


    document.add_heading("ANONIMIZADO_" + filename, 0)
    target = decode_string(target)
    parrafos = re.split(" - - ", target)

    for paragraphText in parrafos:
        paragraphWord = document.add_paragraph()

        pointerText = 0
        for coloredWord in re.finditer(r"[A-Z]+<+", paragraphText):
            startIdxColored, endIdxColored = coloredWord.span()
            paragraphWord.add_run(paragraphText[pointerText:startIdxColored])
            specialWordRunner = paragraphWord.add_run(paragraphText[startIdxColored:endIdxColored])
            pointerText = endIdxColored

            specialWordRunner = specialWordRunner.font
            specialWordRunner.bold = True
            specialWordRunner.underline = True
            specialWordRunner.color.rgb = red
        paragraphWord.add_run(paragraphText[pointerText:])     
   
    document.save(directory_save)


