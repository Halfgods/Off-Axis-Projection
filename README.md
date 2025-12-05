<div align="center">

# 🪟 Off-Axis Head-Tracked 3D Projection

### *Transform your 2D monitor into a magical 3D window*

[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-00A400?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Face_Mesh-FF6F00?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)


**Real-time "Window into 3D" illusion using Python + Pygame + MediaPipe**


---

https://github.com/Halfgods/Off-Axis-Projection/raw/main/Output%20of%20Main2.mp4

</div>

---

## 🌟 About

This project creates a stunning **"window into 3D space"** illusion using only your webcam and head movement. Watch a rotating neon cube and infinite grid tunnel shift perspective perfectly as you move — just like peering into real 3D space through your screen!

> 💡 Inspired by Neorx_'s cool project,His was way cooler than this — but **100% Python** and fully **open-source**.

---

## ✨ Live Demo

<div align="center">

> **🎮 Move your head side-to-side or lean forward/backward — the illusion is unbelievably strong!**

*Experience true motion parallax without any special hardware*

</div>

---

## 🎯 Features

<table>
<tr>
<td width="50%">

### 🎥 Real-time Head Tracking
MediaPipe Face Mesh tracks your head position instantly with **sub-20ms latency**

### 🔮 True Off-Axis Projection
Physically accurate parallax with horizontal, vertical, and depth scaling

### 🎲 Rotating Neon Cube
Depth-sorted faces with glowing wireframe using **Painter's Algorithm**

</td>
<td width="50%">

### 🌌 Infinite Neon Grid Room
Floor, ceiling, walls — full 3D tunnel that reacts to your every move

### ⚡ Zero Lag Performance
Multithreaded webcam + rendering pipeline for buttery-smooth **60 FPS**

### 🎨 Fully Customizable
Tweak depth, scale, speed, and sensitivity to your preference

</td>
</tr>
</table>

---

## 📦 Requirements

```bash
pip install pygame mediapipe opencv-python numpy
```

<details>
<summary><b>📋 System Requirements</b></summary>

- **Python:** 3.7 or higher
- **Webcam:** Built-in or external (720p recommended)
- **Distance:** 50-70 cm from screen for optimal effect
- **Lighting:** Good ambient lighting for face detection
- **OS:** Windows, macOS, or Linux

</details>

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Halfgods/Off-Axis-Projection.git
cd Off-Axis-Projection

# Install dependencies
pip install -r requirements.txt

# Run the magic ✨
python main.py
```

<div align="center">

### 🎬 Getting Started

| Step | Action |
|:----:|--------|
| 1️⃣ | Allow webcam access when prompted |
| 2️⃣ | Center your face in the frame |
| 3️⃣ | Move your head around — prepare to be amazed! |

**💡 Pro Tip:** Works best in good lighting conditions with your face clearly visible.

</div>

---

## 🧠 How It Works

### 🎯 Head Tracking

Uses **MediaPipe landmark #168** (center between eyes) to track head position:

```python
head_x = (landmark.x - 0.5) * 2.0   # Maps to -1.0 (left) → +1.0 (right)
head_y = (landmark.y - 0.5) * 2.0   # Maps to -1.0 (top)  → +1.0 (bottom)
```

### ✨ Off-Axis Projection (The Magic)

The core illusion uses **perspective-correct parallax**:

```python
ratio = EYE_DEPTH / (EYE_DEPTH + z)
screen_x = head_x + (world_x - head_x) * ratio
screen_y = head_y + (world_y - head_y) * ratio
```

<div align="center">

**This is the exact same mathematics used in:**

🥽 VR Headsets (Oculus, Vive) • 🔮 Holographic Displays (Looking Glass)  
✈️ Professional Flight Simulators • 🎬 Cinema Projection Mapping

</div>

---

## 🎨 Customization Guide

<div align="center">

**🔧 Tweak these parameters in `main.py` to personalize your experience:**

</div>

| Variable | Default | 📈 Effect when Increased | 💡 Recommendation |
|----------|---------|-------------------------|-------------------|
| `EYE_DEPTH` | `2.0` | Weaker parallax effect (feels farther back) | `1.5` for dramatic effect |
| `UNIT_SCALE` | `300` | Zooms the entire scene in (larger objects) | `400` for close-up view |
| `ROOM_DEPTH` | `8.0` | Makes the grid tunnel extend deeper | `12.0` for endless tunnel |
| `head_x * 1.5` | `1.5` | Stronger head-tracking response | `2.5` for intense parallax |
| `angle += 0.02` | `0.02` | Faster cube rotation speed | `0.05` for rapid spin |

<details>
<summary><b>🎮 Example Configuration</b></summary>

```python
# Dramatic "lean into the screen" effect
EYE_DEPTH = 1.5
UNIT_SCALE = 350
hx = tracker.head_x * 2.5
hy = tracker.head_y * 2.5
```

</details>

---

## 📁 Project Structure

```
📦 off-axis-head-tracking
┣ 📜 main.py              # Complete single-file implementation
┣ 📜 README.md            # You're reading it!
┣ 📜 requirements.txt     # Python dependencies
┗ 📂 assets/              # Optional screenshots or demo videos
```

---

## 🔬 Technical Deep Dive

### 🏗️ Rendering Pipeline

```mermaid
graph LR
    A[Webcam Capture] --> B[MediaPipe Processing]
    B --> C[Face Landmark Detection]
    C --> D[Head Position Calculation]
    D --> E[Off-Axis Projection]
    E --> F[3D Scene Rendering]
    F --> G[Display @ 60 FPS]
```

<table>
<tr>
<td width="50%">

### 🧵 Thread 1: Webcam
- Continuously captures frames
- Processes face landmarks
- Updates head position
- Runs at ~30 FPS

</td>
<td width="50%">

### 🎨 Thread 2: Rendering
- Renders 3D scene at 60 FPS
- Off-axis frustum calculation
- Depth sorting (Painter's Algorithm)
- Display update

</td>
</tr>
</table>

### 🧩 Why This Feels So Real

Because it's **physically accurate motion parallax** — the same depth cue your brain uses in everyday life to perceive 3D space.

> 🧠 When you move your head, objects closer to the screen shift more than distant objects, **exactly like looking through a real window**. Your brain is tricked into perceiving depth that doesn't exist!

<div align="center">

**No glasses • No special screen • Just pure mathematics and head tracking**

</div>

---

## 🎓 Educational Value

Perfect for learning about:

<table>
<tr>
<td align="center">📐</td>
<td><b>3D Projection Mathematics</b><br/>Understand perspective and parallax</td>
<td align="center">👁️</td>
<td><b>Computer Vision</b><br/>Real-time face tracking with MediaPipe</td>
</tr>
<tr>
<td align="center">⚡</td>
<td><b>Performance Optimization</b><br/>Multithreading and efficient rendering</td>
<td align="center">🐍</td>
<td><b>Python Game Development</b><br/>Pygame graphics programming</td>
</tr>
</table>

---

## 🤝 Contributing

Contributions are what make the open-source community amazing! Any contributions you make are **greatly appreciated**.

<details>
<summary><b>💡 Ideas for Improvements</b></summary>

- [ ] Hand gesture controls for interaction
- [ ] Multiple object types (spheres, pyramids, etc.)
- [ ] VR headset integration for dual-eye tracking
- [ ] Stereo rendering (anaglyph 3D mode)
- [ ] Recording/replay mode for demos
- [ ] Custom 3D model loading (.obj, .stl)
- [ ] Multi-user support with position tracking
- [ ] Mobile app version (iOS/Android)

</details>

### 🛠️ How to Contribute

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

This means you're free to use this project in your own work, commercially or otherwise!

---

## ⭐ Show Your Support

<div align="center">

**If this project blew your mind, please star this repository!** ⭐

It helps others discover this magical illusion and motivates continued development.

[![GitHub stars](https://img.shields.io/github/stars/Halfgods/Off-Axis-Projection?style=social)](https://github.com/Halfgods/Off-Axis-Projection/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Halfgods/Off-Axis-Projection?style=social)](https://github.com/Halfgods/Off-Axis-Projection/network/members)

</div>

---

## 👨‍💻 Author

<div align="center">

**Made with math and neon by [Halfgods](https://github.com/Halfgods)** 🔮

[![GitHub](https://img.shields.io/badge/GitHub-Halfgods-181717?style=for-the-badge&logo=github)](https://github.com/Halfgods)

💬 Questions? [Open an issue](https://github.com/Halfgods/Off-Axis-Projection/issues) or reach out!

</div>

---

<div align="center">

### 🎥 Thank You :)


**Share this project with friends who love cool tech!** 🚀

---

*Built with 💙 Python • Powered by 🧠 MediaPipe • Rendered with 🎮 Pygame*

</div>
