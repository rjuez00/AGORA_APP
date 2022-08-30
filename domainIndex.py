import PNfilters, PNanonymizers
import aiPNfilters, aiMEDOCCANfilters, ocr
from inspect import getmembers, isfunction

domainIndex = {"police_PDF"     : {     "scanner": ocr.scan_PDF_PN,
                                        "fileType": "PDF",
                                        "encoding": "latin-1",
                                        "filterList" :       ( getmembers(PNfilters, isfunction), 
                                                   [(aiPNfilters.filter_flair.__name__, aiPNfilters.filter_flair)] ),
                                         "deidentifierList" : ( getmembers(PNanonymizers, isfunction), 
                                                   [(aiPNfilters.remove_flair_calle, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_lugar_general, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_nombre_persona, aiPNfilters.filter_flair)]) 
                                },

                "guardia_civil_PDF": {      "scanner": ocr.scan_PDF_OCR_GC,
                                            "fileType": "PDF",
                                            "encoding": "latin-1",
                                            "filterList" :       ( getmembers(PNfilters, isfunction), 
                                                    [(aiPNfilters.filter_flair.__name__, aiPNfilters.filter_flair)] ),
                                            "deidentifierList" : ( getmembers(PNanonymizers, isfunction), 
                                                    [(aiPNfilters.remove_flair_calle, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_lugar_general, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_nombre_persona, aiPNfilters.filter_flair)]) 
                                },
                
                
                "meddocan_TXT"  : {  "scanner": ocr.scan_TXT_MEDDOCAN,
                                     "fileType": "TXT",
                                     "encoding": "utf-8",
                                     "filterList" :       ([], [(aiMEDOCCANfilters.filter_flair.__name__, aiMEDOCCANfilters.filter_flair)] ),
                                     "deidentifierList" : ([],  [(i,aiMEDOCCANfilters.filter_flair) for i, _ in aiMEDOCCANfilters.removers])},
                
                "policia_nacional_o_guardia_civil_PDF": {      "scanner": ocr.scan_PDF_COMBINE_OCR_TEXT,
                                            "fileType": "PDF",
                                            "encoding": "latin-1",
                                            "filterList" :       ( getmembers(PNfilters, isfunction), 
                                                    [(aiPNfilters.filter_flair.__name__, aiPNfilters.filter_flair)] ),
                                            "deidentifierList" : ( getmembers(PNanonymizers, isfunction), 
                                                    [(aiPNfilters.remove_flair_calle, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_lugar_general, aiPNfilters.filter_flair), (aiPNfilters.remove_flair_nombre_persona, aiPNfilters.filter_flair)]) 
                                }
}