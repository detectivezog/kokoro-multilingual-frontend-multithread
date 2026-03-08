try:
    from misaki import zh
    g2p = zh.ZHG2P()
    is_ready = True
except Exception:
    is_ready = False

class Dialect:
    def __init__(self):
        self.code = "zh-cn"
        self.name = "Mandarin Chinese"
        self.is_ready = is_ready

    def process(self, text):
        if not self.is_ready: 
            return text, False
            
        text = text.replace('。', '. ').replace('、', ', ').replace('，', ', ').replace('！', '! ').replace('？', '? ')
        try:
            result = g2p(text)
            phonemes = result[0] if isinstance(result, tuple) else result
            # ALWAYS return True to bypass the espeak crash
            return phonemes, True
        except:
            return text, False