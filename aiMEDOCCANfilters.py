import time, os, utils

storage_models = "auxFiles/NERmodels"
entities_model = ["TERRITORIO", "FECHAS", "EDAD_SUJETO_ASISTENCIA", "NOMBRE_SUJETO_ASISTENCIA", "NOMBRE_PERSONAL_SANITARIO", "SEXO_SUJETO_ASISTENCIA", "CALLE", "PAIS", "ID_SUJETO_ASISTENCIA", "CORREO_ELECTRONICO", "ID_TITULACION_PERSONAL_SANITARIO", "ID_ASEGURAMIENTO", "HOSPITAL", "FAMILIARES_SUJETO_ASISTENCIA", "INSTITUCION", "ID_CONTACTO_ASISTENCIAL", "NUMERO_TELEFONO",       "PROFESION", "NUMERO_FAX", "CENTRO_SALUD", "OTROS_SUJETO_ASISTENCIA"]

def filter_flair(contentdict):
    from flair.models import SequenceTagger
    from flair.data import Sentence
    import flair, torch
    flair.device = torch.device('cpu') 

    flairTagger = SequenceTagger.load(utils.resource_path(storage_models + "/meddocanmodel.pt"))
    
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




def remove_ai_tag(contentDict, tag, replacement):
    text = contentDict["deidentified"]
    print("!!!!!!!!!!!!!!REMOVING:", tag, contentDict[tag])
    for startidx, (endidx, entityText) in contentDict[tag].items():
        print("\t\tremoving:", entityText)
        startidx = int(startidx)
        endidx = int(endidx)

        text = text[:int(startidx)] + replacement + "<" * (endidx-startidx-3) + text[int(endidx):]
        

    return text



removers = [(lambda contentDict, entity=entity: remove_ai_tag(contentDict, entity, entity[:3]), f"remove_{entity}") for entity in entities_model]


for i, j in removers:
    i.__name__ = j