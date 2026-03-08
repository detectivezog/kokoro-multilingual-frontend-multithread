# .dev/py/smart-tts/voice_manager/scanner.py
import json
from pathlib import Path

class SmartVoiceManager:
    def __init__(self, folder_name="voices"):
        self.component_dir = Path(__file__).parent
        self.voices_root = (self.component_dir / folder_name).resolve()

    def get_voice_details(self):
        catalog = {"kokoro": [], "piper": []}
        if not self.voices_root.exists(): return catalog

        # Check for Kokoro files
        k_dir = self.voices_root / "kokoro"
        if k_dir.exists():
            for onnx in k_dir.glob("*.onnx"):
                catalog["kokoro"].append({"name": "Kokoro V1", "path": str(onnx)})

        # Check for Piper files (recursively)
        p_dir = self.voices_root / "piper"
        if p_dir.exists():
            for onnx in p_dir.rglob("*.onnx"):
                # Piper must have a matching .json config
                config = onnx.with_suffix(".json")
                if not config.exists():
                    config = Path(str(onnx) + ".json") # Alternative naming
                
                if config.exists():
                    catalog["piper"].append({
                        "name": onnx.stem,
                        "path": str(onnx),
                        "config": str(config)
                    })
        return catalog