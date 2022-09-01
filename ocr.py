# Useful libraries
from pdf2image import convert_from_path 
from pytesseract import image_to_string
import tqdm, fitz, codecs, pytesseract, utils

pytesseract.pytesseract.tesseract_cmd = utils.resource_path("auxFiles/tesseract/tesseract.exe")

def convert_pdf_to_img(pdf_file):
    """
    @desc: this function converts a PDF into Image
    
    @params:
        - pdf_file: the file to be converted
    pu
    @returns:
        - an interable containing image format of all the pages of the PDF
    """
    return convert_from_path(pdf_file, poppler_path = r"auxFiles\poppler-22.04.0\Library\bin")


def convert_image_to_text(file):
    """
    @desc: this function extracts text from image
    
    @params:
        - file: the image file to extract the content
    
    @returns:
        - the textual content of single image
    """
    
    text = image_to_string(file)
    return text


def get_text_from_any_pdf(pdf_file):
    """
    @desc: this function is our final system combining the previous functions
    
    @params:
        - file: the original PDF File
    
    @returns:
        - the textual content of ALL the pages
    """
    images = convert_pdf_to_img(pdf_file)
    final_text = ""
    for img in tqdm.tqdm(images):
        
        final_text += convert_image_to_text(img)
        #print("Page n°{}".format(pg))
        #print(convert_image_to_text(img))
    
    return clean_encoding(final_text)


def clean_encoding(text, encoding = "latin-1"):
    text = codecs.encode(text, encoding = encoding, errors = "ignore")
    text = codecs.decode(text, encoding=encoding, errors = "ignore")

    for bad_char in [u"\uF0D7", u"\uFFFD", u"\uf020", u"\uF0B2", u"\u61613", '\u262d']:
        text = text.replace(bad_char, "")
    
    return text.replace("\n", "   ")


def scan_PDF_PN(filename):
    text = ""
    with fitz.open(filename) as doc:
        for page in doc:
            text += page.getText()
    return clean_encoding(text), None


def scan_PDF_OCR_GC(filename):
    return get_text_from_any_pdf(filename) , None


def scan_PDF_COMBINE_OCR_TEXT(filename):
    text = ""
    with fitz.open(filename) as doc:
        for page in doc:
            text += page.getText()
    
    typeofdoc = True
    if text.isspace() or text == "":
        print("No text found in {}... performing OCR".format(filename))
        text = get_text_from_any_pdf(filename)
    else:
        print("Text found in {}... skipping OCR".format(filename))
        text = clean_encoding(text)
        typeofdoc = False
   
    return text, typeofdoc

def scan_TXT_MEDDOCAN(filename):
    text = ""
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        #text = codecs.decode(text, encoding="utf-8", errors = "ignore")
        return text, None