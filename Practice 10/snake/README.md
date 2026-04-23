# 🐍 Snake

Classic snake game with levels and collision detection.

## ✨ Features
- Arrow key controls for snake movement
- Wall collision detection (game over if you hit border)
- Self-collision detection (game over if you hit yourself)
- Food spawns in valid positions (never on snake or walls)
- Level system: every 4 foods eaten → level up → speed increases
- Score and level counter displayed on screen
- Press R to restart after game over

## 🎮 Controls
| Key | Action |
|-----|--------|
| ↑ | Move Up |
| ↓ | Move Down |
| ← | Move Left |
| → | Move Right |
| R | Restart (after game over) |

## 📂 Files
- `main.py` - Game loop and input handling
- `snake.py` - Snake class with movement and collision logic
- `food.py` - Food class with smart spawning

## 🎯 Requirements Met
✅ Border collision checking  
✅ Food spawns in valid positions  
✅ Level system with speed increase  
✅ Score and level counters  
✅ Commented, organized code