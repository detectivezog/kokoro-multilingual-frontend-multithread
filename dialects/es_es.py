import re

class Dialect:
    def __init__(self):
        self.code = "es"
        self.name = "Spanish"
        self.is_ready = True

    def process(self, text):
        # Keep: standard letters, accented letters (À-ÿ), numbers, whitespace, and standard punctuation.
        # Destroy: everything else (Kanji, Hanzi, Cyrillic, etc.)
        filtered_text = re.sub(r'[^a-zA-ZÀ-ÿ0-9\s.,!?;:\'"()\-¡¿]', '', text)
        
        return filtered_text, False