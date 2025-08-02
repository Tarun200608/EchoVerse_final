import edge_tts
import asyncio

async def generate_tts(text, voice="en-US-AriaNeural", file_path="output.mp3"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

def text_to_speech(text, voice_choice="Lisa"):
    voice_map = {
        "Lisa": "en-US-AriaNeural",       # Warm, professional female
        "Michael": "en-US-GuyNeural",     # Clear, authoritative male
        "Allison": "en-US-JennyNeural"    # Friendly, engaging female
    }
    voice = voice_map.get(voice_choice, "en-US-AriaNeural")
    asyncio.run(generate_tts(text, voice))
    return "output.mp3"
