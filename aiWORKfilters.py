import time, os, utils, re

storage_models = "auxFiles/NERmodels"
entities_model = ["LUGAR_GENERAL", "ID", "PERSON", "FECHAS", "NOMBRE_CALLE", "TELEFONO"]

weird_regex = r"(,|'|-|\*|:|\.|\)|\º|\(|}|{|;|\/|«|\?|!|¡| +|\||\")"
weird_chars =  [",", "'", "-", "*", ":", ".", ")", "º", "(", "}", "{", ";", "/", "«", "?", "!", "¡"]
weird_regex_function = lambda input_string: [i for i in re.split(weird_regex, input_string) if i not in [" ", ""] + weird_chars and not i.isspace()]



def filter_modelo_generico(contentdict, model_name):
    from flair.models import SequenceTagger
    from flair.data import Sentence
    import flair, torch
    from flair.tokenization import Tokenizer
    class CustomTokenizer(Tokenizer):
        def tokenize(self, text):
            tokens = weird_regex_function(text)
            return tokens

    flair.device = torch.device('cpu') 
    print("LOADING MODEL")
    flairTagger = SequenceTagger.load(utils.resource_path(storage_models + model_name))
    print("LOADED MODEL")
    for documentName in contentdict.keys():
        print("FILTERING:", documentName)
        sentence = Sentence(contentdict[documentName]["raw"], use_tokenizer = CustomTokenizer())
        

        
        flairTagger.predict(sentence)
        
             
        for entity in entities_model:
            contentdict[documentName][entity] = {}
        
        for entity in sentence.get_spans("ner"):
            contentdict[documentName][entity.get_label("ner").value][entity.start_position] = (entity.end_position, entity.text)
        
        contentdict[documentName]["filter_flair"] = {-1: [-1 , "performed flair filter"]}
    
    return contentdict


pn_work = lambda x: filter_modelo_generico(x, "/pn_work.pt")
pn_work.__name__ = "filter_flair"
gc_work = lambda x: filter_modelo_generico(x, "/gc_work.pt")
gc_work.__name__ = "filter_flair"
gc_pn_combined_work = lambda x: filter_modelo_generico(x, "/gc_pn_combined_work.pt")
gc_pn_combined_work.__name__ = "filter_flair"

#entities_model = ["LUGAR_GENERAL", "ID", "PERSON", "FECHAS", "NOMBRE_CALLE", "TELEFONO", "ORGANIZACION"]


def remove_flair_lugar_general(contentDict):
    text = contentDict["deidentified"]
    entities_model = "LUGAR_GENERAL"
    for startidx, (endidx, entityText) in contentDict[entities_model].items():
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "LOC" + "<" * (endidx-startidx-3) + text[int(endidx):]
    return text



def remove_flair_calle( contentDict):
    text = contentDict["deidentified"]
    entities_model = "NOMBRE_CALLE"
    for startidx, (endidx, entityText) in contentDict[entities_model].items():
        startidx = int(startidx)
        endidx = int(endidx)
        text = text[:int(startidx)] + "LOC"+ "<" * (endidx-startidx-3) + text[int(endidx):]
    return text



def remove_flair_nombre_persona(contentDict):
    text = contentDict["deidentified"]
    entities_model = "PERSON"
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "PER" + "<" * (endidx-startidx-3) + text[int(endidx):]

    return text


def remove_flair_id(contentDict):
    text = contentDict["deidentified"]
    entities_model = "ID"
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "PER" + "<" * (endidx-startidx-3) + text[int(endidx):]

    return text

def remove_flair_fechas(contentDict):
    text = contentDict["deidentified"]
    entities_model = "FECHAS"
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "PER" + "<" * (endidx-startidx-3) + text[int(endidx):]

    return text

def remove_flair_telefono(contentDict):
    text = contentDict["deidentified"]
    entities_model = "TELEFONO"
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "PER" + "<" * (endidx-startidx-3) + text[int(endidx):]

    return text

def remove_flair_organizacion(contentDict):
    text = contentDict["deidentified"]
    entities_model = "ORGANIZACION"
    if contentDict.get(entities_model) is None:
        return text
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "ORG" + "<" * (endidx-startidx-3) + text[int(endidx):]

    return text
