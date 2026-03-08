# kokoro-multilingual-frontend-multithread
- Multilingual (English, French, Portuguese, Chinese, German, Spanish, Japanese, Italian)
- Duplicate any English, Spanish, Portuguese, Italian as a template to create your own extra languages.
- Edit `./dialects/__init__.py` to add new languages.
- Select language and a voice that matches it (or not, if you want it to sound like a tourist)
- Supports transliteration (Speaks like an European tourist when Chinese or Japanese is encountered in Latin letters text)
- Exports to FLAC
- Ehmm... What else... Multithreaded (Edit `self.GENERATION_THREADS = 3` in kokoro_conductor.py to adjust)
- Uses 1 thread for playback, any any extra threads to preprocess sentences.

- Splits sentences in groups of less than 500 tokens for languages that have the 501 tokens went cuckoo puff traceback.

  Should work as is. Made with Python 3.12
