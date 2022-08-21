import filters, anonymizers, utils as aux
import aiTools
from inspect import getmembers, isfunction

domainIndex = {"police"     : { "filterList" :       ( getmembers(filters, isfunction), 
                                                   [(aiTools.filter_flair.__name__, aiTools.filter_flair)] ),
                                "deidentifierList" : ( getmembers(anonymizers, isfunction), 
                                                   [(aiTools.remove_flair_calle, aiTools.filter_flair), (aiTools.remove_flair_lugar_general, aiTools.filter_flair), (aiTools.remove_flair_nombre_persona, aiTools.filter_flair)]) 
                                },
                
                
                "meddocan"  : { "filterList" :       ( getmembers(filters, isfunction), 
                                                   [(aiTools.filter_flair.__name__, aiTools.filter_flair)] ),
                                "deidentifierList" : ( getmembers(anonymizers, isfunction), 
                                                   []) 
                                },
}