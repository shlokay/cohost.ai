from vosk import Model, KaldiRecognizer
import wave
import json
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile

vosk_model = Model("model")  # Make sure Vosk model is in `model/`

def transcribe_audio(wav_path):
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())
    rec.SetWords(True)

    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result_text += json.loads(rec.Result())["text"] + " "

    final_result = json.loads(rec.FinalResult())["text"]
    result_text += final_result
    return result_text.strip()



def record_and_transcribe(return_audio_path=False):
    duration = 4  # seconds
    samplerate = 16000
    print("Say something...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    
    text = transcribe_with_vosk(audio, samplerate)

    if return_audio_path:
        temp_path = tempfile.mktemp(suffix=".wav")
        sf.write(temp_path, audio, samplerate)  # audio is a NumPy array with dtype=int16
        return text, temp_path

    return text


def transcribe_with_vosk(audio_np_array, samplerate):
    model = vosk.Model("model")  # Make sure you have a Vosk model in a folder named "model"
    
    # Save NumPy audio as a temporary WAV file for Vosk to process
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        import soundfile as sf
        sf.write(temp_wav.name, audio_np_array, samplerate)
    
        wf = wave.open(temp_wav.name, "rb")
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        result = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                partial_result = json.loads(rec.Result())
                result += partial_result.get("text", "") + " "
        final_result = json.loads(rec.FinalResult())
        result += final_result.get("text", "")
    
    return result.strip()
