import time, os

storage_models = "auxFiles"
entities_model = ["CALLE", "LUGAR_GENERAL", "NOMBRE_PERSONA"]

def filter_flair(contentdict):
    from flair.models import SequenceTagger
    from flair.data import Sentence
    import flair, torch
    flair.device = torch.device('cpu') 

    flairTagger = SequenceTagger.load(storage_models + "/nermodel.pt")
    
    for documentName in contentdict.keys():
        print("FILTERING:", documentName)
        sentence = Sentence(contentdict[documentName]["raw"], use_tokenizer = True)
        
        flairTagger.predict(sentence)
                
        for entity in entities_model:
            contentdict[documentName][entity] = {}
        
        for entity in sentence.get_spans("ner"):
            contentdict[documentName][entity.get_label("ner").value][entity.start_position] = (entity.end_position, entity.text)
        
        contentdict[documentName]["filter_flair"] = {-1: [-1 , "performed flair filter"]}
    
    return contentdict




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
    entities_model = "CALLE"
    for startidx, (endidx, entityText) in contentDict[entities_model].items():
        startidx = int(startidx)
        endidx = int(endidx)
        text = text[:int(startidx)] + "LOC"+ "<" * (endidx-startidx-3) + text[int(endidx):]
        

    return text



def remove_flair_nombre_persona(contentDict):
    text = contentDict["deidentified"]
    entities_model = "NOMBRE_PERSONA"
    for startidx, contents in contentDict[entities_model].items():
        endidx, entityText = contents
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + "PER" + "<" * (endidx-startidx-3) + text[int(endidx):]
        

    return text

