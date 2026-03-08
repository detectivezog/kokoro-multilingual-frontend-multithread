# .dev/py/smart-tts/sound_engine/player.py
import numpy as np
import sounddevice as sd
import soundfile as sf  # Cleaner than pydub for FLAC
from pathlib import Path

class SoundStation:
    def __init__(self, default_volume=1.0):
        self.volume = default_volume
        self.component_dir = Path(__file__).parent
        self.buffer_path = self.component_dir / "last_run_buffer.flac"

    def play_audio(self, audio_data, sample_rate):
        # Apply Volume & Normalize
        audio_np = audio_data.astype(np.float32) * self.volume
        audio_np = np.clip(audio_np, -1.0, 1.0)
        
        # Overwrite the temporary FLAC buffer
        sf.write(str(self.buffer_path), audio_np, sample_rate, format='FLAC')

        sd.play(audio_np, sample_rate)
        sd.wait()

    def export(self, filename, sample_rate):
        """Simple copy/rename of the FLAC buffer."""
        import shutil
        target_path = Path(filename)
        
        # Ensure it has .flac extension if not provided
        if target_path.suffix.lower() != ".flac":
            target_path = target_path.with_suffix(".flac")
            
        if self.buffer_path.exists():
            shutil.copy(str(self.buffer_path), str(target_path))
            print(f"✅ FLAC Export complete: {target_path.name}")