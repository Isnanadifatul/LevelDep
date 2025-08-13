import re
import string
import nltk
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi stemmer (Sastrawi)
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def clean_and_stem(text: str) -> str:
    # Lowercase
    text = text.lower()
    # Hapus tanda baca
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Lakukan stemming (Sastrawi)
    text = stemmer.stem(text)
    return text