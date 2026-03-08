import re
import numpy as np
from pathlib import Path
import concurrent.futures

from dialects.transliterator import force_latin
from kokoro_onnx import Kokoro
from voice_manager.scanner import SmartVoiceManager
from sound_engine.player import SoundStation
from dialects import get_dialect_by_name, get_language_names

def sturdy_split(text, max_length=200):
    paragraphs =[p.strip() for p in text.split('\n') if p.strip()]
    sentences =[]
    
    for p in paragraphs:
        parts = re.split(r'([.!?。！？]+(?:[\s]*))', p)
        current_sentence = ""
        for part in parts:
            current_sentence += part
            if re.search(r'[.!?。！？]', part):
                sentences.append(current_sentence.strip())
                current_sentence = ""
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
    final_chunks =[]
    for sentence in sentences:
        if len(sentence) <= max_length:
            final_chunks.append(sentence)
        else:
            sub_parts = re.split(r'([,;:—，、；：]+[\s]*)', sentence)
            current_chunk = ""
            for part in sub_parts:
                if len(current_chunk) + len(part) <= max_length:
                    current_chunk += part
                else:
                    if re.fullmatch(r'[,;:—，、；：]+[\s]*', part):
                        current_chunk += part
                        if current_chunk.strip():
                            final_chunks.append(current_chunk.strip())
                        current_chunk = ""
                    else:
                        if current_chunk.strip():
                            final_chunks.append(current_chunk.strip())
                        current_chunk = part
                        while len(current_chunk) > max_length:
                            space_idx = current_chunk.rfind(' ', 0, max_length)
                            if space_idx == -1:
                                final_chunks.append(current_chunk[:max_length].strip())
                                current_chunk = current_chunk[max_length:]
                            else:
                                final_chunks.append(current_chunk[:space_idx].strip())
                                current_chunk = current_chunk[space_idx+1:]
            if current_chunk.strip():
                final_chunks.append(current_chunk.strip())
    return [s for s in final_chunks if s]


class KokoroConductor:
    def __init__(self):
        # Your optimized core count
        self.GENERATION_THREADS = 3
        
        # Turned OFF by default so French apostrophes don't break. 
        # (Turn this on only if you want European voices to read Asian characters)
        self.USE_TRANSLITERATION = True 
        
        self.eyes = SmartVoiceManager()
        self.mouth = SoundStation()
        self.kokoro = None
        
        catalog = self.eyes.get_voice_details()
        if catalog.get('kokoro'):
            try:
                k_dir = Path(catalog['kokoro'][0]['path']).parent 
                bin_path = k_dir / "voices-v1.0.bin"
                
                int8_model = k_dir / "kokoro-v1.0.int8.onnx"
                fp16_model = k_dir / "kokoro-v1.0.onnx"
                
                if int8_model.exists():
                    model_to_load = int8_model
                    print("[OK] Loaded 8-bit Quantized Model")
                else:
                    model_to_load = fp16_model
                    print("[OK] Loaded Standard 16-bit Model")
                
                self.kokoro = Kokoro(str(model_to_load), str(bin_path))
            except Exception as e:
                print(f"[WARNING] Kokoro Init Error: {e}")

    def get_voices(self):
        if not self.kokoro: return ["No Voices Found"]
        try:
            return self.kokoro.get_voices()
        except:
            return["af_bella", "af_sarah", "am_adam", "ff_siwis", "jf_alpha"]

    def get_languages(self):
        return get_language_names()

    def stream_audio(self, text, voice_name, lang_name="English (US)", speed=1.0):
        if not self.kokoro or not text.strip(): 
            return

        dialect = get_dialect_by_name(lang_name)
        if not dialect:
            print(f"[ERROR] Dialect '{lang_name}' not found.")
            return

        sentences = sturdy_split(text)
        
        def _process_single_sentence(original_sentence):
            # Lowercase string to fix the ALL CAPS acronym spelling bug
            sentence_to_process = original_sentence.lower()
            
            if self.USE_TRANSLITERATION:
                sentence_to_process = force_latin(sentence_to_process)
                
            processed_data, is_phonemes_flag = dialect.process(sentence_to_process)
            
            if not processed_data or not str(processed_data).strip():
                return None
            
            try:
                samples, sr = self.kokoro.create(
                    processed_data, 
                    voice=voice_name, 
                    speed=speed, 
                    lang=dialect.code,
                    is_phonemes=is_phonemes_flag
                )
                if len(samples) > 0:
                    # Yields exactly the 4 items app.py needs for highlighting
                    return samples, sr, processed_data, original_sentence
            except Exception as e:
                print(f"[ERROR] Synthesis Error: {e}")
            
            return None

        # Unleash the 4-core parallel generation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.GENERATION_THREADS) as executor:
            for result in executor.map(_process_single_sentence, sentences):
                if result is not None:
                    yield result