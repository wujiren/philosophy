from src.tts import process, VoiceType
import os

if __name__ == "__main__":
    base_dir = "dataset/summary"
    voice_type = VoiceType(
        VOICETYPE=501000,
        CODEC="mp3",
        SAMPLE_RATE=24000,
        ENABLE_SUBTITLE=False,
    )

    files = [f for f in os.listdir(base_dir) if f.endswith(".md")]
    output_dir = (
        f"output/大模型语音合成-{voice_type['VOICETYPE']}-{voice_type['SAMPLE_RATE']}"
    )
    for file_name in files:
        if os.path.exists(f"{output_dir}/{file_name.replace('.md', '.mp3')}"):
            continue
        with open(f"{base_dir}/{file_name}", "r") as f:
            content = f.read()
        texts = [f"{l}\n\n" for l in content.split("\n") if l.strip()]
        process(
            texts=texts,
            output_dir=output_dir,
            output_file_prefix=file_name.replace(".md", ""),
            voice_type=voice_type,
        )
