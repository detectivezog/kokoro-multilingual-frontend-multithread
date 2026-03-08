from dialects.ja_jp import Dialect as JaDialect
from dialects.zh_cn import Dialect as ZhDialect

class GenericDialect:
    def __init__(self, code, name, use_gruut=False):
        self.code = code
        self.name = name
        self.use_gruut = use_gruut
        if self.use_gruut:
            from gruut import sentences
            self.sentences = sentences

    def process(self, text):
        if self.use_gruut:
            phonemes =[]
            try:
                for sentence in self.sentences(text, lang=self.code):
                    for word in sentence:
                        if word.phonemes:
                            phonemes.append("".join(word.phonemes))
                result = " ".join(phonemes)
                return result if result.strip() else text, True
            except Exception as e:
                print(f"[ERROR] Gruut processing failed: {e}")
                return text, False
        else:
            # Native passthrough for French, Spanish, etc.
            # Returns False to use the internal Kokoro dictionary and preserve accents!
            return text, False

# The unified, sturdy registry
REGISTRY = {
    "English (US)": GenericDialect("en-us", "English (US)", use_gruut=True),
    "French": GenericDialect("fr-fr", "French", use_gruut=False),
    "Japanese": JaDialect(),
    "Mandarin Chinese": ZhDialect(),
    "Spanish": GenericDialect("es", "Spanish", use_gruut=False),
    "German": GenericDialect("de", "German", use_gruut=False),
    "Italian": GenericDialect("it", "Italian", use_gruut=False),
    "Portuguese (Brazil)": GenericDialect("pt-br", "Portuguese (Brazil)", use_gruut=False),
}

def get_dialect_by_name(name):
    return REGISTRY.get(name)

def get_language_names():
    return list(REGISTRY.keys())