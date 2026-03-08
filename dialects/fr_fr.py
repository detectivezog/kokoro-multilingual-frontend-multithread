class Dialect:
    def __init__(self):
        # We tell Kokoro explicitly: use the French dictionary
        self.code = "fr-fr" 
        self.name = "French"
        self.is_ready = True

    def process(self, text):
        # We perform NO phonemization here.
        # We return is_phonemes=False.
        # This tells Kokoro: "Don't use Gruut, don't use Espeak, use your INTERNAL French model."
        return text, False