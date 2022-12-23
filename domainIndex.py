import PNfilters, PNanonymizers
import aiPNfilters, aiWORKfilters, ocr
from inspect import getmembers, isfunction




domainIndex =  {"[Híbrido] Policia Nacional"     : {     "scanner": ocr.scan_PDF_PN,
                                        "fileType": "PDF",
                                        "encoding": "latin-1",
                                        "filterList" :       ( getmembers(PNfilters, isfunction), 
                                                   [(aiPNfilters.filter_flair.__name__, aiPNfilters.filter_flair)] ),
                                         "deidentifierList" : ( getmembers(PNanonymizers, isfunction), 
                                                   [(aiPNfilters.remove_flair_calle, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_lugar_general, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_nombre_persona, aiPNfilters.filter_flair)]) 
                                },

                "[AI] Guardia Civil": {      "scanner": ocr.scan_PDF_OCR_GC,
                                            "fileType": "PDF",
                                            "encoding": "latin-1",
                                            "filterList" :       ([(PNfilters.filter_mail.__name__, PNfilters.filter_mail)], [(aiWORKfilters.gc_work.__name__, aiWORKfilters.gc_work)] ),
                                            "deidentifierList" : ( [(PNanonymizers.remove_mail.__name__, PNanonymizers.remove_mail)],[(aiWORKfilters.remove_flair_nombre_persona, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_lugar_general, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_calle, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_id, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_fechas, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_telefono, aiWORKfilters.gc_work), (aiWORKfilters.remove_flair_organizacion, aiWORKfilters.gc_work)]) 
                                },        
                
                "[AI] Policia Nacional": {      "scanner": ocr.scan_PDF_COMBINE_OCR_TEXT,
                                            "fileType": "PDF",
                                            "encoding": "latin-1",
                                            "filterList" :       ( [(PNfilters.filter_mail.__name__, PNfilters.filter_mail)],[ (aiWORKfilters.pn_work.__name__, aiWORKfilters.pn_work)] ),
                                            "deidentifierList" : ( [(PNanonymizers.remove_mail.__name__, PNanonymizers.remove_mail)],[(aiWORKfilters.remove_flair_nombre_persona, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_lugar_general, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_calle, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_id, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_fechas, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_telefono, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_organizacion, aiWORKfilters.pn_work)]) 
                                },
                "[AI] Policia Nacional & Guardia Civil combinado": {        "scanner": ocr.scan_PDF_COMBINE_OCR_TEXT,
                                                "fileType": "PDF",
                                                "encoding": "latin-1",
                                                "filterList" :  ( [(PNfilters.filter_mail.__name__, PNfilters.filter_mail)], [(aiWORKfilters.gc_pn_combined_work.__name__, aiWORKfilters.gc_pn_combined_work)] ),
                                                "deidentifierList" : ( [[(PNanonymizers.remove_mail.__name__, PNanonymizers.remove_mail)],(aiWORKfilters.remove_flair_nombre_persona, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_lugar_general, aiWORKfilters.gc_pn_combined_work), (aiWORKfilters.remove_flair_calle, aiWORKfilters.gc_pn_combined_work), (aiWORKfilters.remove_flair_id, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_fechas, aiWORKfilters.pn_work), (aiWORKfilters.remove_flair_telefono, aiWORKfilters.gc_pn_combined_work), (aiWORKfilters.remove_flair_organizacion, aiWORKfilters.gc_pn_combined_work)]) 
                                }
}