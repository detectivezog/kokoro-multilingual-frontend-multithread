import re

try:
    from pykakasi import Kakasi
    import pypinyin
    kakasi = Kakasi()
    is_ready = True
except ImportError:
    is_ready = False

def force_latin(text):
    """Converts Asian scripts to Latin, and sanitizes Asian punctuation."""
    if not is_ready:
        return text

    # 1. Sanitize Asian Punctuation to Latin equivalents
    text = text.replace('。', '. ').replace('、', ', ').replace('・', ' ')
    text = text.replace('「', '"').replace('」', '"').replace('『', '"').replace('』', '"')
    text = text.replace('，', ', ').replace('！', '! ').replace('？', '? ')

    # 2. Target only Kanji, Hiragana, Katakana, and Hanzi
    asian_pattern = re.compile(r'[\u4e00-\u9FFF\u3040-\u309F\u30A0-\u30FF]+')

    def translate_block(match):
        asian_str = match.group(0)
        
        jp_words =[]
        for item in kakasi.convert(asian_str):
            jp_words.append(item['hepburn'])
        intermediate = " ".join(jp_words)
        
        pinyin_list = pypinyin.lazy_pinyin(intermediate)
        return " ".join(pinyin_list)

    final_text = asian_pattern.sub(translate_block, text)
    return " ".join(final_text.split())