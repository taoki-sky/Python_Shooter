import os
import wave
import numpy as np
import pygame
import math
import struct
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Ensure asset directories exist
os.makedirs('assets/images', exist_ok=True)
os.makedirs('assets/sounds', exist_ok=True)

# Function to generate a simple sound
def generate_simple_sound(filename, frequency=440, duration=0.3, volume=0.5, type="sine"):
    # Generate sine wave audio for sound effects
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    audio = np.zeros(num_samples, dtype=np.float32)
    
    # Generate waveform
    for i in range(num_samples):
        t = float(i) / sample_rate
        if type == "sine":
            audio[i] = np.sin(2 * np.pi * frequency * t)
        elif type == "square":
            audio[i] = 1.0 if np.sin(2 * np.pi * frequency * t) >= 0 else -1.0
        elif type == "saw":
            audio[i] = 2 * (t * frequency - math.floor(0.5 + t * frequency))
        elif type == "noise":
            audio[i] = np.random.uniform(-1, 1)
    
    # Apply fade-out
    fade_samples = int(sample_rate * 0.1)  # 100ms fade
    if fade_samples < num_samples:
        for i in range(num_samples - fade_samples, num_samples):
            audio[i] *= (num_samples - i) / fade_samples
    
    # Apply volume
    audio *= volume
    
    # Convert to 16-bit PCM
    audio = np.int16(audio * 32767)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wave_file:
        wave_file.setnchannels(1)  # Mono
        wave_file.setsampwidth(2)  # 2 bytes (16 bits)
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(audio.tobytes())
    
    print(f"Generated sound: {filename}")

# Generate sound effects
sounds_to_generate = [
    ("assets/sounds/hit.wav", 200, 0.2, 0.5, "square"),
    ("assets/sounds/powerup.wav", 600, 0.3, 0.6, "sine"),
    ("assets/sounds/shoot.wav", 150, 0.15, 0.4, "saw"),
    ("assets/sounds/boss_appear.wav", 100, 0.5, 0.7, "square"),
    ("assets/sounds/level_up.wav", 800, 0.4, 0.6, "sine"),
    ("assets/sounds/game_over.wav", 150, 0.5, 0.7, "saw")
]

for sound_info in sounds_to_generate:
    generate_simple_sound(*sound_info)

# Function to generate simple game graphics
def generate_simple_graphic(filename, width, height, color_data, shape="rect"):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if isinstance(color_data, tuple):  # Single color
        if shape == "rect":
            pygame.draw.rect(surface, color_data, (0, 0, width, height))
        elif shape == "circle":
            pygame.draw.circle(surface, color_data, (width//2, height//2), min(width, height)//2)
        elif shape == "triangle":
            pygame.draw.polygon(surface, color_data, [(0, height), (width//2, 0), (width, height)])
    elif isinstance(color_data, list):  # Gradient or multi-color
        if shape == "rect" and len(color_data) >= 2:
            for y in range(height):
                # Calculate color based on position
                blend_factor = y / (height - 1) if height > 1 else 0
                color = [
                    int(color_data[0][0] * (1 - blend_factor) + color_data[1][0] * blend_factor),
                    int(color_data[0][1] * (1 - blend_factor) + color_data[1][1] * blend_factor),
                    int(color_data[0][2] * (1 - blend_factor) + color_data[1][2] * blend_factor)
                ]
                pygame.draw.line(surface, color, (0, y), (width, y))
        elif shape == "pattern" and len(color_data) >= 2:
            # Create a checkerboard pattern
            block_size = 8  # Size of each block in the pattern
            for x in range(0, width, block_size):
                for y in range(0, height, block_size):
                    color = color_data[0] if (x // block_size + y // block_size) % 2 == 0 else color_data[1]
                    pygame.draw.rect(surface, color, (x, y, min(block_size, width-x), min(block_size, height-y)))
    
    # Add a border
    pygame.draw.rect(surface, (255, 255, 255), (0, 0, width, height), 1)
    
    # Save the image
    pygame.image.save(surface, filename)
    print(f"Generated image: {filename}")

# Generate game graphics
graphics_to_generate = [
    ("assets/images/paddle.png", 100, 20, (0, 0, 255), "rect"),
    ("assets/images/ball.png", 10, 10, (255, 255, 255), "circle"),
    ("assets/images/bullet.png", 5, 15, (0, 255, 0), "rect"),
    ("assets/images/block_red.png", 80, 30, [(255, 0, 0), (200, 0, 0)], "rect"),
    ("assets/images/block_orange.png", 80, 30, [(255, 165, 0), (200, 120, 0)], "rect"),
    ("assets/images/block_yellow.png", 80, 30, [(255, 255, 0), (200, 200, 0)], "rect"),
    ("assets/images/block_green.png", 80, 30, [(0, 255, 0), (0, 200, 0)], "rect"),
    ("assets/images/block_purple.png", 80, 30, [(128, 0, 128), (100, 0, 100)], "rect"),
    ("assets/images/boss.png", 100, 100, [(255, 0, 0), (100, 0, 0)], "pattern"),
    ("assets/images/powerup_damage.png", 20, 20, (255, 255, 0), "triangle"),
    ("assets/images/powerup_multi.png", 20, 20, (0, 255, 0), "circle"),
    ("assets/images/powerup_life.png", 20, 20, (255, 0, 0), "circle")
]

for graphic_info in graphics_to_generate:
    generate_simple_graphic(*graphic_info)

print("\nAll game assets have been generated!")
print("You can now run paddle_game.py to play the game with these assets.") 