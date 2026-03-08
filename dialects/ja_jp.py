try:
    from pykakasi import Kakasi
    kakasi = Kakasi()
    is_ready = True
except ImportError:
    is_ready = False

class Dialect:
    def __init__(self):
        self.code = "ja-jp"
        self.name = "Japanese"
        self.is_ready = is_ready

    def process(self, text):
        if not self.is_ready: 
            return text, False
            
        # Clean punctuation just in case Transliterator is off
        text = text.replace('。', '. ').replace('、', ', ').replace('・', ' ')
        
        jp_words =[]
        for item in kakasi.convert(text):
            jp_words.append(item['hepburn'])
            
        # ALWAYS return True to bypass the espeak crash
        return " ".join(jp_words), True