import sys

import whispercpp as w

w.utils.available_audio_devices()

model_name = "tiny.en"

model = w.Whisper.from_pretrained(model_name)

iterator = None
try:
    iterator = model.stream_transcribe(model_name=model_name,
                                       device_id=0,
                                       length_ms=5000,
                                       sample_rate=w.api.SAMPLE_RATE,
                                       n_threads=8,
                                       step_ms=2000,
                                       keep_ms=200,
                                       max_tokens=32,
                                       audio_ctx=0,
                                       list_audio_devices=True)

finally:
    assert iterator is not None, "Something went wrong!"
    sys.stderr.writelines(
        ["\nTranscription (line by line):\n"] + [f"{it}\n" for it in iterator]
    )
    sys.stderr.flush()
