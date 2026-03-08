import customtkinter as ctk
import threading
import queue
import soundfile as sf
import numpy as np
import time
from kokoro_conductor import KokoroConductor

class KokoroStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart-TTS-2")
        self.geometry("850x550")
        
        self.conductor = KokoroConductor()
        self.last_samples = None
        self.last_sr = None
        self.STREAM_AUDIO = True 
        
        self.audio_queue = None
        self.stop_playback = False
        
        self.setup_ui()

    def setup_ui(self):
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 15))
        self.textbox.pack(padx=20, pady=(20, 5), fill="both", expand=True)
        self.textbox.insert("0.0", "Domo Arigato Mister Roboto.\nMerci Beaucoup Monsieur Roboto.\nL'abeille a butiné dans l'allée fleurie d'Anjou.\nどうもありがとう、ミスター・ロボット。\n非常感谢，机器人先生。\nMuchas gracias, señor Robot.\nVielen Dank, Herr Roboter.\nGrazie mille, signor Robot.\nMuito obrigado, senhor Robô.\nTHANK YOU VERY MUCH MISTER ROBOT IN ALL CAPS.")

        # --- HIGHLIGHT CONFIGURATION ---
        self.textbox.tag_config("highlight", background="#3498db", foreground="white")

        self.p_display = ctk.CTkEntry(self, font=("Consolas", 11), fg_color="#1a1a1a", text_color="#2ecc71")
        self.p_display.pack(padx=20, pady=5, fill="x")
        self.p_display.insert(0, "Dialect Engine Output...")
        self.p_display.configure(state="readonly")

        self.ctrl = ctk.CTkFrame(self)
        self.ctrl.pack(padx=20, pady=(5, 20), fill="x", expand=False)

        langs = self.conductor.get_languages()
        self.lang_menu = ctk.CTkOptionMenu(self.ctrl, values=langs, width=130)
        self.lang_menu.pack(side="left", padx=10, pady=10)
        self.lang_menu.bind("<MouseWheel>", lambda e: self._on_wheel(e, self.lang_menu))

        voices = self.conductor.get_voices()
        self.voice_menu = ctk.CTkOptionMenu(self.ctrl, values=voices, width=130)
        self.voice_menu.pack(side="left", padx=5)
        self.voice_menu.bind("<MouseWheel>", lambda e: self._on_wheel(e, self.voice_menu))

        self.speed_slider = ctk.CTkSlider(self.ctrl, from_=0.5, to=2.0, width=120)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=10)

        self.play_btn = ctk.CTkButton(self.ctrl, text="[PLAY]", fg_color="#2ecc71", width=90, command=self.handle_play)
        self.play_btn.pack(side="left", padx=5)

        self.export_btn = ctk.CTkButton(self.ctrl, text="[EXPORT]", fg_color="#3498db", width=90, command=self.handle_export)
        self.export_btn.pack(side="left", padx=5)

    def _on_wheel(self, event, widget):
        widget.focus_set()
        vals = widget.cget("values")
        curr = widget.get()
        if curr not in vals: return
        idx = vals.index(curr)
        new_idx = max(0, idx - 1) if event.delta > 0 else min(len(vals) - 1, idx + 1)
        widget.set(vals[new_idx])

    def handle_play(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        voice = self.voice_menu.get()
        lang = self.lang_menu.get()
        speed = self.speed_slider.get()
        
        if not text: return
        
        self.stop_playback = True
        time.sleep(0.05) 
        self.stop_playback = False
        
        self.play_btn.configure(state="disabled", text="[WAIT]")
        self.export_btn.configure(state="disabled")

        self.audio_queue = queue.Queue()

        threading.Thread(target=self._generation_thread, args=(text, voice, lang, speed), daemon=True).start()
        threading.Thread(target=self._playback_thread, daemon=True).start()

    def _generation_thread(self, text, voice, lang, speed):
        for samples, sr, processed_data, sentence in self.conductor.stream_audio(text, voice, lang, speed):
            if self.stop_playback:
                break
            self.audio_queue.put((samples, sr, processed_data, sentence))
        self.audio_queue.put(None)


    def _playback_thread(self):
        all_samples =[]
        last_sr = 24000
        
        while True:
            item = self.audio_queue.get()
            if item is None or self.stop_playback:
                break 
                
            samples, sr, processed_data, sentence = item
            
            # Catch the error if the window is closed while playing
            try:
                self.after(0, self._update_display, processed_data, sentence)
            except RuntimeError:
                break # Window closed, kill thread silently
            
            self.conductor.mouth.play_audio(samples, sr)
            all_samples.append(samples)
            last_sr = sr

        try:
            self.after(0, self._on_playback_complete, all_samples, last_sr)
        except RuntimeError:
            pass

    def _update_display(self, data_string, sentence):
        """Updates green bar and highlights the sentence in the textbox."""
        self.p_display.configure(state="normal")
        self.p_display.delete(0, "end")
        self.p_display.insert(0, f"Playing: {sentence} | Data: {data_string}")
        self.p_display.configure(state="readonly")

        # 1. Clear old highlights
        self.textbox.tag_remove("highlight", "1.0", "end")
        
        # 2. Find new sentence coordinates
        content = self.textbox.get("1.0", "end")
        start_idx = content.find(sentence)
        
        if start_idx != -1:
            def get_tk_idx(char_index):
                prefix = content[:char_index]
                line = prefix.count('\n') + 1
                col = len(prefix) - prefix.rfind('\n') - 1 if '\n' in prefix else len(prefix)
                return f"{line}.{col}"
            
            start_tk = get_tk_idx(start_idx)
            end_tk = get_tk_idx(start_idx + len(sentence))
            
            # 3. Apply highlight and auto-scroll
            self.textbox.tag_add("highlight", start_tk, end_tk)
            self.textbox.see(start_tk)

    def _on_playback_complete(self, all_samples, last_sr):
        if all_samples:
            self.last_samples = np.concatenate(all_samples)
            self.last_sr = last_sr
            
        self.play_btn.configure(state="normal", text="[PLAY]")
        self.export_btn.configure(state="normal")
        
        self.p_display.configure(state="normal")
        self.p_display.delete(0, "end")
        self.p_display.insert(0, "[Playback Finished]")
        self.p_display.configure(state="readonly")
        
        # Clear highlight when done
        self.textbox.tag_remove("highlight", "1.0", "end")

    def handle_export(self):
        if self.last_samples is not None:
            filename = "kokoro_studio_export.flac"
            try:
                sf.write(filename, self.last_samples, self.last_sr)
                print(f"[OK] Export complete: {filename}")
            except Exception as e:
                print(f"[ERROR] Export failed: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = KokoroStudioApp()
    app.mainloop()
