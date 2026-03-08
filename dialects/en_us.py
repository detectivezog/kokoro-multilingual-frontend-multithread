from gruut import sentences

class Dialect:
    def __init__(self):
        self.code = "en-us"
        self.name = "English (US)"
        # This dialect is always ready as long as gruut[en] is installed
        self.is_ready = True 

    def process(self, text):
        """Standard Gruut logic. Preserves 'Mister Roboto'."""
        phonemes = []
        try:
            for sentence in sentences(text, lang=self.code):
                for word in sentence:
                    if word.phonemes:
                        phonemes.append("".join(word.phonemes))
            result = " ".join(phonemes)
            
            # Returns: The Data, and True (telling Kokoro it IS phonemes)
            return result if result.strip() else text, True
        except Exception as e:
            print(f"⚠️ {self.name} Dialect Error: {e}")
            return text, False