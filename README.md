# Rhythm Arrow Game

A simple rhythm game that uses the librosa library to detect beats in music and generates falling arrows that the player needs to hit with the correct arrow keys.

## Requirements

- Python 3.x
- pygame
- librosa
- numpy

## Installation

1. Make sure you have Python installed.
2. Install the required libraries:
   ```
   pip install pygame librosa numpy
   ```

## How to Play

1. Create an "assets" folder in the game directory
2. Place your music file (MP3 format) in the assets folder and name it "song.mp3"
3. Run the game:
   ```
   python Main.py
   ```
4. Press the arrow keys (↑, ↓, ←, →) when the falling arrows reach the target line
5. Try to get the highest score by hitting the arrows with perfect timing!

## Gameplay Controls

- Arrow Keys: Hit the corresponding arrows
- Escape Key: Quit the game
- Space Key: Start game/Restart after game over

## Scoring

- Perfect Hit (closer to the line): 100 points
- Good Hit (slightly off): 50 points
- Miss: 0 points and combo reset

## Features

- Beat detection using librosa library
- Combo system for consecutive hits
- Dynamic arrow generation based on music beats
- Game over screen with final score and max combo

## Customization

You can modify the game settings in the Main.py file:
- ARROW_SPEED: Change how fast the arrows fall
- PERFECT_THRESHOLD and GOOD_THRESHOLD: Adjust the timing window for hits
- HIT_LINE_Y: Change the position of the hit line

## Troubleshooting

If you encounter issues with librosa:
- Make sure you have installed the required dependencies
- For Windows users, you might need to install additional C++ build tools

If no music is available, the game will run with a default beat pattern. 