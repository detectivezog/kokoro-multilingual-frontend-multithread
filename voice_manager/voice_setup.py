# .dev/py/smart-tts/voice_setup.py
import os
import requests
from pathlib import Path

# Updated for the Hugging Face structure
HF_VOICES_URL = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices"
HF_MODEL_URL = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main"

# The specific language bins for multilingual support
BINS = [
    "af_bella.bin", "af_nicole.bin", "af_sarah.bin", "af_sky.bin",
    "am_adam.bin", "am_michael.bin",
    "bf_emma.bin", "bf_isabella.bin",
    "bm_george.bin", "bm_lewis.bin",
    "ff_siwis.bin",  # French Female
    "hf_alpha.bin", "hf_beta.bin",
    "hm_omega.bin", "hm_psi.bin",
    "jf_alpha.bin", "jf_gongitsune.bin", "jf_nezumi.bin", "jf_tebukuro.bin", # Japanese
    "jm_kumo.bin"
]

def download_file(url, dest):
    print(f"[FETCHING] {url.split('/')[-1]}...")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[OK] Saved.")
        else:
            print(f"[ERROR] Failed: {response.status_code}")
    except Exception as e:
        print(f"[WARNING] Error: {e}")

def run_setup():
    # Use your established model path
    target_dir = Path("C:/.dev/py/smart-tts/voice_manager/models/kokoro")
    target_dir.mkdir(parents=True, exist_ok=True)

    print("--- Kokoro Global Voice Setup ---")
    print("1. Download FP16 Model (kokoro-v1.0.onnx)")
    print("2. Download INT8 Model (kokoro-v1.0.int8.onnx - Best for 4-threads)")
    print("3. Download ALL Voice Bins (Multilingual Support)")
    
    choice = input("Select an option: ")

    if choice == "1":
        # Standard FP16 Model
        download_file(f"{HF_MODEL_URL}/kokoro-v1.0.onnx", target_dir / "kokoro-v1.0.onnx")
    
    elif choice == "2":
        # Quantized INT8 Model (Saved as .int8.onnx to match our Conductor's auto-detect logic)
        download_file(f"{HF_MODEL_URL}/kokoro-v1.0-int8.onnx", target_dir / "kokoro-v1.0.int8.onnx")
    
    elif choice == "3":
        # Multilingual Bins
        for b in BINS:
            download_file(f"{HF_VOICES_URL}/{b}", target_dir / b)
        # Main voices.bin for backward compatibility
        download_file(f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin", target_dir / "voices-v1.0.bin")

if __name__ == "__main__":
    run_setup()
