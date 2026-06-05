import wave
import math
import struct
import os

def generate_tone(filename, frequency, duration, volume=0.5, wave_type="sine"):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            if wave_type == "sine":
                value = math.sin(2.0 * math.pi * frequency * t)
            elif wave_type == "square":
                value = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == "noise":
                value = (math.sin(2.0 * math.pi * frequency * t * (i%10)) + math.cos(i)) % 2 - 1
            
            # Envelope (fade out)
            envelope = 1.0 - (i / num_samples)
            value *= envelope * volume
            
            # Convert to 16-bit integer
            sample = int(value * 32767.0)
            wav_file.writeframesraw(struct.pack('<h', sample))

os.makedirs('assets', exist_ok=True)

# Generate Coin Sound (High pitched beep)
generate_tone('assets/coin.wav', 1200, 0.2, 0.4, "sine")

# Generate Crash Sound (Low pitched noise-like)
generate_tone('assets/crash.wav', 100, 0.5, 0.8, "noise")

print("Sounds generated successfully!")
