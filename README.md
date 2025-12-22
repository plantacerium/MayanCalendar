# 🌟 Mayan Stele - Ultimate Calendar & Fractal Pattern Analyzer

A comprehensive, visually stunning Mayan calendar application built with Python and PySide6. Convert any Gregorian date to its Mayan equivalent and discover fractal patterns in the ancient cycles.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)

## ✨ Features

### 📅 Complete Calendar Systems
- **Long Count** - Baktun.Katun.Tun.Uinal.Kin (animated odometer display)
- **Tzolkin** - 260-day sacred calendar with day sign meanings
- **Haab'** - 365-day civil calendar with month meanings
- **Calendar Round** - 52-year cycle position tracker
- **Lords of the Night** - 9-day underworld deity cycle
- **Venus Cycle** - 584-day synodic period with phase tracking
- **Mars Cycle** - 780-day synodic period
- **Lunar Phase** - Moon age and phase visualization
- **819-Day Cycle** - K'awiil deity rotation

### 🔮 Fractal Pattern Analyzer
- Multi-cycle convergence detection algorithm
- Resonance scoring (0-100%) for any date
- Visual timeline with convergence markers
- Customizable cycle selection
- Project patterns months/years into the future

### 🎨 Stunning Visuals
- **Circular Calendar Wheel** - Animated rotating rings for Haab, Tzolkin, and Lords
- **Long Count Odometer** - Smooth animated digit display
- **Fractal Timeline** - Color-coded convergence intensity
- **Stone-carved aesthetic** - Authentic Mesoamerican look

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Mayan-Calendar.git
cd Mayan-Calendar

# Install dependencies
pip install PySide6

# Run the application
python mayan-stele.py
```

## 📸 Screenshots

### Calendar View
The main calendar view features a circular wheel visualization with the date displayed in all major Mayan cycles:

![Screenshot V1](assets/Screen%20V1.JPG)
![Screenshot V2](assets/Screen%20V2.JPG)
![Screenshot V3](assets/Screen%20V3.JPG)


### Fractal Pattern Analyzer
Find dates when multiple cycles converge with the built-in analyzer that detects harmonic alignments across all Mayan cycles.

## 🌍 Calendar Systems Explained

### Long Count
The Long Count is a linear count of days since the Mayan creation date (August 11, 3114 BCE). It uses a modified vigesimal (base-20) system:

| Unit | Days | Calculation |
|------|------|-------------|
| Kin | 1 | 1 day |
| Uinal | 20 | 20 kins |
| Tun | 360 | 18 uinals |
| Katun | 7,200 | 20 tuns |
| Baktun | 144,000 | 20 katuns |

### Tzolkin (Sacred Calendar)
260-day cycle combining:
- 13 day numbers (1-13)
- 20 day names (Ahau, Imix, Ik, etc.)

### Haab' (Civil Calendar)
365-day solar calendar:
- 18 months of 20 days each
- 5 "unlucky" days (Wayeb)

### Calendar Round
The combination of Tzolkin and Haab' creates a unique position every 18,980 days (~52 years).

## 🧮 Fractal Pattern Detection

The analyzer calculates a "resonance score" based on how closely aligned multiple cycles are on any given date. High-scoring dates indicate rare convergences that the ancient Maya may have considered significant.

```python
# Example: Find convergences for 2025
analyzer = FractalPatternAnalyzer(converter)
events = analyzer.find_convergences(2025, months_ahead=12)
```

## 🗓️ Historical Dates

Test the converter with these significant dates:

| Gregorian | Long Count | Tzolkin | Haab' | Event |
|-----------|------------|---------|-------|-------|
| Aug 11, 3114 BCE | 0.0.0.0.0 | 4 Ahau | 8 Cumku | Creation |
| Dec 21, 2012 | 13.0.0.0.0 | 4 Ahau | 3 Kankin | 13th Baktun |
| Dec 22, 2025 | 13.0.13.2.7 | 6 Manik | 10 Kankin | Today |

## 📁 Project Structure

```
Mayan-Calendar/
├── mayan-stele.py       # Main application (complete)
├── mayan_calendar_app.py # Legacy basic converter
└── README.md            # This file
```

## 🔧 Technical Details

- **Correlation**: GMT (Goodman-Martinez-Thompson) = 584,283
- **Framework**: PySide6 (Qt for Python)
- **Style**: Fusion theme with custom stone-carved aesthetic
- **Animations**: Smooth Qt property animations

## 📜 License

MIT License - Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Mayan calendar mathematics based on scholarly research
- GMT correlation (584,283) is the most widely accepted
- Glyphs and meanings derived from archaeological studies

---

*"Time is not a line, but a circle of cycles within cycles."*

