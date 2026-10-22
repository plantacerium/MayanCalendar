"""
Mayan Stele - Ultimate Mayan Calendar Application
Complete implementation with all calendar systems, fractal pattern detection,
and stunning visual displays.
"""
import sys
import os
import math
from pathlib import Path
from functools import reduce
from datetime import datetime, timedelta
import csv

BASE_DIR = Path(__file__).resolve().parent

def _resolve_logo(*rel_paths):
    for rel in rel_paths:
        p = BASE_DIR / rel
        if p.exists():
            return p
    return BASE_DIR / rel_paths[0]

LOGO_PATH = _resolve_logo(
    "assets/logo_fusion_quantum_pyramid_calendar.svg",
    "assets/logos/logo_fusion_quantum_pyramid_calendar.svg"
)
LOGO_JPG_PATH = _resolve_logo(
    "assets/logo_fusion_quantum_pyramid_calendar.jpg",
    "assets/logos/logo_fusion_quantum_pyramid_calendar.jpg"
)
LOGO_TRANSPARENT_PATH = _resolve_logo(
    "assets/logo_fusion_emblem_transparent.svg",
    "assets/logos/logo_fusion_emblem_transparent.svg"
)
LOGO_ICO_PATH = _resolve_logo(
    "assets/mayan_stele.ico",
    "assets/logos/mayan_stele.ico",
    "mayan_stele.ico"
)

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QDateEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
        QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
        QSpinBox, QScrollArea, QGroupBox, QSplitter, QSlider, QProgressBar, QComboBox,
        QFileDialog, QMessageBox, QSizePolicy, QDialog, QTextEdit, QPlainTextEdit,
        QRadioButton, QButtonGroup
    )
    from PySide6.QtCore import (
        QDate, Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property,
        QRectF, Signal, QPointF, QPoint, QThread, Slot
    )
    from PySide6.QtGui import (
        QFont, QFontMetrics, QColor, QPalette, QIcon, QPixmap, QPainter, QPainterPath,
        QPen, QBrush, QRadialGradient, QLinearGradient, QConicalGradient, QPolygonF
    )
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    # Fallback dummy base classes and decorators for headless / CLI / MCP use
    QApplication = QMainWindow = QWidget = QVBoxLayout = QHBoxLayout = QGridLayout = object
    QLabel = QDateEdit = QPushButton = QFrame = QGraphicsDropShadowEffect = object
    QTabWidget = QTableWidget = QTableWidgetItem = QHeaderView = QCheckBox = object
    QSpinBox = QScrollArea = QGroupBox = QSplitter = QSlider = QProgressBar = QComboBox = object
    QFileDialog = QMessageBox = QSizePolicy = QDialog = QTextEdit = QPlainTextEdit = object
    QRadioButton = QButtonGroup = object
    QDate = Qt = QSize = QTimer = QPropertyAnimation = QEasingCurve = QRectF = QPointF = QPoint = QThread = object
    QFont = QFontMetrics = QColor = QPalette = QIcon = QPixmap = QPainter = QPainterPath = object
    QPen = QBrush = QRadialGradient = QLinearGradient = QConicalGradient = QPolygonF = object
    def Signal(*args, **kwargs): return None
    def Slot(*args, **kwargs): return lambda f: f
    def Property(*args, **kwargs): return lambda f: f

# Import modular exporter and biocymatic dictionary
try:
    from mayan_exporter import MayanProfileExporter
except ImportError:
    MayanProfileExporter = None

try:
    from resonaxers import RESONANCE_MAP
except ImportError:
    RESONANCE_MAP = None

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: MAYAN CALENDAR ARITHMETIC CORE
# ══════════════════════════════════════════════════════════════════════════════

class MayanConverter:
    """Advanced Mayan Calendar converter with all major cycles."""
    
    def __init__(self, correlation_jdn=584283):
        # 584283 = GMT, 584285 = GMT+2, 489384 = Spinden
        self.correlation_jdn = correlation_jdn
    
    # Tzolkin day names with meanings and glyphs
    TZOLKIN_DATA = [
        ("Ahau", "Lord/Sun", "☀"), ("Imix", "Crocodile/Water Lily", "🐊"), 
        ("Ik", "Wind/Breath", "💨"), ("Akbal", "Night/Darkness", "🌙"),
        ("Kan", "Corn/Seed", "🌽"), ("Chicchan", "Serpent", "🐍"), 
        ("Cimi", "Death/Transformation", "💀"), ("Manik", "Deer/Hand", "🦌"),
        ("Lamat", "Rabbit/Venus", "🐇"), ("Muluc", "Water/Jade", "💧"), 
        ("Oc", "Dog/Guide", "🐕"), ("Chuen", "Monkey/Artisan", "🐒"),
        ("Eb", "Grass/Road", "🌿"), ("Ben", "Reed/Pillar", "🎋"), 
        ("Ix", "Jaguar/Earth", "🐆"), ("Men", "Eagle/Wise One", "🦅"),
        ("Cib", "Vulture/Owl", "🦉"), ("Caban", "Earthquake/Earth", "🌍"), 
        ("Etznab", "Flint/Knife", "🔪"), ("Cauac", "Rain/Storm", "⛈")
    ]
    
    # Haab months with meanings
    HAAB_DATA = [
        ("Pop", "Mat/Jaguar"), ("Uo", "Black Conjunction"), ("Zip", "Red Conjunction"),
        ("Zotz", "Bat"), ("Tzec", "Skull"), ("Xul", "Dog/End"),
        ("Yaxkin", "New/First Sun"), ("Mol", "Water/Jade"), ("Chen", "Black Storm/Cave"),
        ("Yax", "Green Storm"), ("Zac", "White Storm"), ("Ceh", "Red Storm"),
        ("Mac", "Enclosure"), ("Kankin", "Yellow Sun"), ("Muan", "Owl/Screech"),
        ("Pax", "Planting Time"), ("Kayab", "Turtle"), ("Cumku", "Granary/Dark"),
        ("Wayeb", "Nameless Days - Unlucky")
    ]
    
    LORDS_OF_NIGHT = [
        ("G1", "Xiuhtecuhtli - Fire Lord"),
        ("G2", "Itztli - Obsidian Knife"),
        ("G3", "Piltzintecuhtli - Young Sun"),
        ("G4", "Centeotl - Maize God"),
        ("G5", "Mictlantecuhtli - Death Lord"),
        ("G6", "Chalchiuhtlicue - Water Goddess"),
        ("G7", "Tlazolteotl - Filth Eater"),
        ("G8", "Tepeyollotl - Jaguar Heart"),
        ("G9", "Tlaloc - Rain God")
    ]
    
    # 819-day cycle colors and directions
    KAWIIL_COLORS = ["Red (East)", "White (North)", "Black (West)", "Yellow (South)"]
    
    def _gregorian_to_jdn(self, year, month, day):
        """Astronomical Julian Day Number calculation."""
        if month <= 2:
            year -= 1
            month += 12
        A = year // 100
        B = 2 - A + (A // 4)
        JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        # JD above is at 0h UT (ends in .5); the integer JDN (noon) is JD + 0.5.
        # Without this, every date was shifted one day back (13.0.0.0.0 fell on 22-Dec-2012).
        return int(JD + 0.5)
    
    def _jdn_to_gregorian(self, jdn):
        """Convert JDN back to Gregorian date."""
        jdn = jdn + 0.5
        Z = int(jdn)
        F = jdn - Z
        if Z < 2299161:
            A = Z
        else:
            alpha = int((Z - 1867216.25) / 36524.25)
            A = Z + 1 + alpha - (alpha // 4)
        B = A + 1524
        C = int((B - 122.1) / 365.25)
        D = int(365.25 * C)
        E = int((B - D) / 30.6001)
        day = B - D - int(30.6001 * E) + F
        month = E - 1 if E < 14 else E - 13
        year = C - 4716 if month > 2 else C - 4715
        return (int(year), int(month), int(day))

    def get_full_date(self, year, month, day):
        """Returns comprehensive Mayan date data."""
        jdn = self._gregorian_to_jdn(year, month, day)
        days_since_epoch = jdn - self.correlation_jdn

        # Deep Time Long Count Cycles
        temp_days = days_since_epoch
        alautun = temp_days // 23040000000
        temp_days %= 23040000000
        kinchiltun = temp_days // 1152000000
        temp_days %= 1152000000
        kalabtun = temp_days // 57600000
        temp_days %= 57600000
        piktun = temp_days // 2880000
        temp_days %= 2880000
        baktun = temp_days // 144000
        temp_days %= 144000
        katun = temp_days // 7200
        temp_days %= 7200
        tun = temp_days // 360
        temp_days %= 360
        uinal = temp_days // 20
        kin = temp_days % 20
        
        if alautun > 0 or kinchiltun > 0 or kalabtun > 0 or piktun > 0:
            long_count_str = f"{piktun}.{baktun}.{katun}.{tun}.{uinal}.{kin}"
        else:
            long_count_str = f"{baktun}.{katun}.{tun}.{uinal}.{kin}"
            
        long_count_parts = [baktun, katun, tun, uinal, kin]
        deep_long_count = [alautun, kinchiltun, kalabtun, piktun, baktun, katun, tun, uinal, kin]

        # Tzolkin (260 days) — anchored to Creation 0.0.0.0.0 = 4 Ahau
        tz_num = (days_since_epoch + 3) % 13 + 1
        tz_idx = days_since_epoch % 20  # TZOLKIN_DATA index 0 = Ahau
        tz_name, tz_meaning, tz_glyph = self.TZOLKIN_DATA[tz_idx]

        # Haab (365 days)
        haab_day_of_year = (days_since_epoch + 348) % 365
        if haab_day_of_year < 360:
            haab_idx = haab_day_of_year // 20
            haab_day = haab_day_of_year % 20
        else:
            haab_idx = 18
            haab_day = haab_day_of_year - 360
        haab_month, haab_meaning = self.HAAB_DATA[haab_idx]

        # Calendar Round position
        calendar_round_pos = days_since_epoch % 18980
        calendar_round_years = calendar_round_pos / 365.25

        # Lord of the Night (9 days)
        lord_idx = (days_since_epoch + 8) % 9
        lord_code, lord_name = self.LORDS_OF_NIGHT[lord_idx]

        # 819-day cycle (K'awiil)
        kawiil_pos = days_since_epoch % 819
        kawiil_color_idx = (days_since_epoch // 819) % 4
        kawiil_color = self.KAWIIL_COLORS[kawiil_color_idx % 4]

        # Venus cycle (584 days) — Dresden Codex canonical Venus Table.
        # Base: heliacal rising of Morning Star on 9.9.9.16.0 1 Ahau 18 Kayab (1,364,360 days).
        venus_pos = (days_since_epoch - 1364360) % 584
        if venus_pos < 236: venus_phase = "Morning Star"
        elif venus_pos < 326: venus_phase = "Superior Conjunction"
        elif venus_pos < 576: venus_phase = "Evening Star"
        else: venus_phase = "Inferior Conjunction"

        # Mars cycle (780 days)
        mars_pos = days_since_epoch % 780

        # Lunar Supplementary Series (Glyphs G, F, C, X, B, A)
        # Anchored to a real astronomical new moon (2000-01-06 18:14 UT, JD 2451550.26)
        lunar_cycle = 29.530588853
        total_lunar_days = jdn - 2451550.26
        lunation_number = int(total_lunar_days / lunar_cycle)
        moon_age = total_lunar_days % lunar_cycle
        
        if moon_age < 0:
            moon_age += lunar_cycle
            lunation_number -= 1
            
        glyph_c = (lunation_number % 6) + 1  # 1 to 6 lunations per semester
        glyph_a = 30 if (lunation_number % 2 == 0) else 29
        
        glyph_x_deities = {
            1: "God C (Young Moon)", 2: "God of Num 10", 
            3: "Jaguar God of Underworld", 4: "Death God", 
            5: "Old Earth Deity", 6: "Young God"
        }
        glyph_x = glyph_x_deities.get(glyph_c, "Unknown")

        if moon_age < 1.85: moon_phase = "New Moon 🌑"
        elif moon_age < 7.38: moon_phase = "Waxing Crescent 🌒"
        elif moon_age < 9.23: moon_phase = "First Quarter 🌓"
        elif moon_age < 14.77: moon_phase = "Waxing Gibbous 🌔"
        elif moon_age < 16.61: moon_phase = "Full Moon 🌕"
        elif moon_age < 22.15: moon_phase = "Waning Gibbous 🌖"
        elif moon_age < 23.99: moon_phase = "Last Quarter 🌗"
        else: moon_phase = "Waning Crescent 🌘"

        # Cálculo trigonométrico de iluminación de disco lunar (algoritmo Jean Meeus)
        moon_angle = (moon_age / lunar_cycle) * 2.0 * math.pi
        moon_illum_pct = int(((1.0 - math.cos(moon_angle)) / 2.0) * 100)
        
        # Posición astrométrica real de Venus (período sinódico NASA 583.92136 días)
        venus_astro_pos = round((days_since_epoch - 1364360) % 583.92136, 1)

        return {
            "long_count": long_count_str,
            "long_count_parts": long_count_parts,
            "deep_long_count": deep_long_count,
            "tzolkin": f"{tz_num} {tz_name}",
            "tzolkin_num": tz_num,
            "tzolkin_name": tz_name,
            "tzolkin_meaning": tz_meaning,
            "tzolkin_glyph": tz_glyph,
            "tzolkin_idx": tz_idx,
            "haab": f"{haab_day} {haab_month}",
            "haab_day": haab_day,
            "haab_month": haab_month,
            "haab_meaning": haab_meaning,
            "haab_idx": haab_idx,
            "calendar_round": f"{tz_num} {tz_name} {haab_day} {haab_month}",
            "calendar_round_pos": calendar_round_pos,
            "calendar_round_years": calendar_round_years,
            "lord": lord_code,
            "lord_name": lord_name,
            "kawiil_pos": kawiil_pos,
            "kawiil_color": kawiil_color,
            "venus_pos": venus_pos,
            "venus_phase": venus_phase,
            "venus_astro_pos": venus_astro_pos,
            "mars_pos": mars_pos,
            "moon_age": moon_age,
            "moon_phase": moon_phase,
            "moon_illumination": f"{moon_illum_pct}%",
            "glyph_c": glyph_c,
            "glyph_a": glyph_a,
            "glyph_x": glyph_x,
            "jdn": jdn,
            "days_since_epoch": days_since_epoch
        }

    def long_count_to_gregorian(self, baktun, katun, tun, uinal, kin, piktun=0, kalabtun=0):
        """Convert Long Count (including deep cycles) to Gregorian date."""
        days = kalabtun * 57600000 + piktun * 2880000 + baktun * 144000 + katun * 7200 + tun * 360 + uinal * 20 + kin
        jdn = self.correlation_jdn + days
        return self._jdn_to_gregorian(jdn)
        
    def add_distance_number(self, base_jdn, days):
        """Vital mathematical function: Add or subtract a Distance Number (in days)."""
        new_jdn = base_jdn + days
        return self._jdn_to_gregorian(new_jdn)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: FRACTAL PATTERN ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class FractalPatternAnalyzer:
    """Detect harmonic convergences, Kuramoto synchronization, and Dresden Eclipse patterns in Mayan cycles."""
    
    CYCLES = {
        'Tzolkin': 260,
        'Haab': 365,
        'Calendar Round': 18980,
        'Tun': 360,
        'Katun': 7200,
        'Baktun': 144000,
        'Lord of Night': 9,
        '819-Day': 819,
        'Venus': 584,
        'Mars': 780,
        'Dresden Eclipse': 11960,
        'Eclipse Node': 173.31,
        'Lunar': 30,
    }
    
    def __init__(self, converter):
        self.converter = converter

    def get_dresden_eclipse_info(self, days_since_epoch):
        """
        Calcula la correlación con la Tabla de Eclipses del Códice de Dresde (pp. 51a-58b).
        405 lunaciones = 11,960 días = 46 Tzolk'ins.
        Medio año dracónico de eclipses = 173.3100 días.
        """
        # Distancia al nodo en el medio año de eclipses (173.31 días)
        node_cycle = 173.3100
        node_pos = days_since_epoch % node_cycle
        dist_to_node = min(node_pos, node_cycle - node_pos)
        
        # Fase lunar sinódica (29.530588853 días)
        synodic_cycle = 29.530588853
        lunar_age = (days_since_epoch + 14.765) % synodic_cycle
        
        dist_to_new_moon = min(lunar_age, synodic_cycle - lunar_age)
        dist_to_full_moon = abs(lunar_age - (synodic_cycle / 2.0))
        
        is_near_new_moon = dist_to_new_moon <= 1.8
        is_near_full_moon = dist_to_full_moon <= 1.8
        is_node_window = dist_to_node <= 17.5
        
        is_eclipse = is_node_window and (is_near_new_moon or is_near_full_moon)
        eclipse_type = None
        if is_eclipse:
            eclipse_type = "Solar (Luna Nueva)" if is_near_new_moon else "Lunar (Luna Llena)"
                
        dresden_day = int(days_since_epoch % 11960)
        
        return {
            "is_eclipse_window": is_eclipse,
            "eclipse_type": eclipse_type,
            "dist_to_node_days": round(dist_to_node, 2),
            "lunar_age_days": round(lunar_age, 2),
            "dresden_cycle_day": dresden_day,
            "dresden_total_days": 11960,
            "warning": f"⚠️ ALERTA DRESDE: Eclipse {eclipse_type} (Fos. 51a-58b)" if is_eclipse else None
        }

    def calculate_kuramoto_order(self, days_since_epoch, selected_cycles=None, natal_days=None):
        """
        Calcula el parámetro de orden macroscópico de Kuramoto (R, Ψ) para los osciladores mayas.
        R ∈ [0, 1] mide la coherencia y sincronización de fase global.
        Ψ ∈ [0°, 360°) representa el Vector Director Cósmico (fase resultante colectiva).
        """
        import math
        checks = [
            ('Tzolkin', 260.0, 1.0, 0.0),
            ('Haab', 365.0, 0.8, 348.0),
            ('Calendar Round', 18980.0, 1.2, 0.0),
            ('Tun', 360.0, 0.7, 0.0),
            ('Venus', 584.0, 0.9, 448.0),
            ('Mars', 780.0, 0.6, 0.0),
            ('819-Day', 819.0, 0.7, 0.0),
            ('Lord of Night', 9.0, 0.5, 8.0),
            ('Dresden Eclipse', 11960.0, 0.85, 0.0),
            ('Eclipse Node', 173.3100, 0.8, 0.0),
            ('Lunar Synodic', 29.53059, 0.6, 0.0),
        ]
        
        sum_cos = 0.0
        sum_sin = 0.0
        sum_cos2 = 0.0
        sum_sin2 = 0.0
        total_w = 0.0
        
        d_val = days_since_epoch if natal_days is None else (days_since_epoch - natal_days)
        
        for name, cycle, weight, offset in checks:
            if selected_cycles is not None and name not in selected_cycles:
                continue
            phase = 2.0 * math.pi * (((d_val + offset) % cycle) / cycle)
            
            sum_cos += weight * math.cos(phase)
            sum_sin += weight * math.sin(phase)
            sum_cos2 += weight * math.cos(2.0 * phase)
            sum_sin2 += weight * math.sin(2.0 * phase)
            total_w += weight
            
        if total_w == 0.0:
            return {"r": 0.0, "psi_deg": 0.0, "r_score": 0.0, "is_locked": False, "r2": 0.0}
            
        r1 = math.sqrt(sum_cos**2 + sum_sin**2) / total_w
        r2 = math.sqrt(sum_cos2**2 + sum_sin2**2) / total_w
        psi_rad = math.atan2(sum_sin, sum_cos)
        psi_deg = (math.degrees(psi_rad)) % 360.0
        
        r_composite = ((r1 * 1.0 + r2 * 0.4) / 1.4) * 100.0
        is_locked = r1 >= 0.45 or r_composite >= 55.0
        
        return {
            "r": round(r1, 4),
            "r2": round(r2, 4),
            "psi_deg": round(psi_deg, 1),
            "r_score": round(r_composite, 2),
            "is_locked": is_locked
        }
    
    def calculate_resonance_score(self, days_since_epoch, selected_cycles=None, natal_days=None):
        """Calculate how many cycles align using raw integers. No strings attached."""
        alignments = 0.0
        weights = 0.0
        
        checks = [
            ('Tzolkin', 260, 1.0),
            ('Haab', 365, 0.8),
            ('Calendar Round', 18980, 1.2),
            ('Lord of Night', 9, 0.5),
            ('819-Day', 819, 0.7),
            ('Venus', 584, 0.9),
            ('Mars', 780, 0.6),
            ('Tun', 360, 0.7),
            ('Dresden Eclipse', 11960, 0.8),
            ('Eclipse Node', 173.31, 0.75),
        ]
        
        harmonics = [
            (0.0, 1.0),           # Conjunction / Return (covers 1.0 as well via wrap-around)
            (0.5, 0.8),           # Opposition (Halfway)
            (0.25, 0.6),          # Square (Quarter)
            (0.75, 0.6),          # Square (Three-quarters)
            (0.618034, 0.7),      # Golden Ratio (Phi)
            (0.7836, 0.85),       # Braden Ratio (Fractal Time Constant)
        ]
        
        for name, cycle, weight in checks:
            if selected_cycles is not None and name not in selected_cycles:
                continue
                
            pos = days_since_epoch % cycle
            if natal_days is not None:
                # Shift the 0-point to the user's birth position
                pos = (days_since_epoch - natal_days) % cycle
                
            best_alignment = 0.0
            # Cap the window to a Trecena (13 days) or 5% of cycle, whichever is smaller
            max_window = min(cycle * 0.05, 13.0)
            
            for h_frac, h_weight in harmonics:
                node_pos = cycle * h_frac
                dist = abs(pos - node_pos)
                
                # Cyclic wrap-around (e.g., pos 0 and pos 259 are 1 day apart in Tzolkin)
                if dist > cycle / 2.0:
                    dist = cycle - dist
                
                if dist <= max_window and max_window > 0:
                    alignment = (1.0 - (dist / max_window)) * h_weight
                    if alignment > best_alignment:
                        best_alignment = alignment
                    
            alignments += best_alignment * weight
            weights += weight
        
        return (alignments / weights) * 100.0 if weights > 0 else 0.0

    def find_convergences(self, start_date, total_days=365, selected_cycles=None, natal_days=None, progress_callback=None):
        """Optimized loop: Precomputes cycle harmonic nodes and generates heavy dictionaries ONLY if the score hits the threshold."""
        if selected_cycles is None:
            selected_cycles = list(self.CYCLES.keys())
        
        events = []
        if isinstance(start_date, datetime):
            start = start_date
        else:
            start = datetime(start_date, 1, 1)
            
        checks = [
            ('Tzolkin', 260, 1.0),
            ('Haab', 365, 0.8),
            ('Calendar Round', 18980, 1.2),
            ('Lord of Night', 9, 0.5),
            ('819-Day', 819, 0.7),
            ('Venus', 584, 0.9),
            ('Mars', 780, 0.6),
            ('Tun', 360, 0.7),
        ]
        harmonics = [
            (0.0, 1.0),
            (0.5, 0.8),
            (0.25, 0.6),
            (0.75, 0.6),
            (0.618034, 0.7),
            (0.7836, 0.85),
        ]
        
        precomputed = []
        total_weight = 0.0
        for name, cycle, weight in checks:
            if selected_cycles is not None and name not in selected_cycles:
                continue
            total_weight += weight
            max_w = min(cycle * 0.05, 13.0)
            inv_max_w = 1.0 / max_w if max_w > 0 else 0.0
            half_c = cycle / 2.0
            nodes = [(cycle * hf, hw) for hf, hw in harmonics]
            precomputed.append((cycle, weight, half_c, max_w, inv_max_w, nodes))
            
        scale = (100.0 / total_weight) if total_weight > 0 else 0.0

        # O(1) Optimization: Calculate the starting 'days_since_epoch' exactly once.
        start_jdn = self.converter._gregorian_to_jdn(start.year, start.month, start.day)
        base_days_since_epoch = start_jdn - self.converter.correlation_jdn
        
        # Report progress in chunks of 20,000 days or 2%
        step_progress = max(10000, total_days // 50)
        
        for day_offset in range(total_days):
            if progress_callback and (day_offset % step_progress == 0 or day_offset == total_days - 1):
                progress_callback(day_offset + 1, total_days)
                
            current_days = base_days_since_epoch + day_offset
            eval_days = current_days if natal_days is None else (current_days - natal_days)
            
            alignments = 0.0
            for cycle, weight, half_c, max_w, inv_max_w, nodes in precomputed:
                pos = eval_days % cycle
                best_al = 0.0
                for node_pos, hw in nodes:
                    dist = abs(pos - node_pos)
                    if dist > half_c:
                        dist = cycle - dist
                    if dist <= max_w:
                        al = (1.0 - dist * inv_max_w) * hw
                        if al > best_al:
                            best_al = al
                alignments += best_al * weight
                
            score = alignments * scale
            
            # Condition check BEFORE building strings
            if score > 60.0:
                current = start + timedelta(days=day_offset)
                data = self.converter.get_full_date(current.year, current.month, current.day)
                km = self.calculate_kuramoto_order(current_days, selected_cycles, natal_days)
                ecl = self.get_dresden_eclipse_info(current_days)
                al_list = self._get_alignments(current_days, natal_days)
                events.append({
                    'date': current,
                    'score': score,
                    'tzolkin': data['tzolkin'],
                    'haab': data['haab'],
                    'long_count': data['long_count'],
                    'alignments': al_list,
                    'days_since_epoch': current_days,
                    'day_offset': day_offset,
                    'kuramoto': km,
                    'eclipse': ecl
                })
        
        # Mantener los eventos ordenados por score por defecto
        events.sort(key=lambda x: x['score'], reverse=True)
        return events

    def group_into_wave_packets(self, events, max_gap_days=2):
        """
        Agrupa los eventos discretos en Paquetes de Onda / Ventanas de Resonancia Coherente (Solitones).
        Cada ventana representa un continuo armónico donde la energía se acumula hacia una cúspide
        y luego se disipa armónicamente.
        """
        if not events:
            return []
            
        sorted_events = sorted(events, key=lambda x: x['date'])
        packets = []
        current_cluster = [sorted_events[0]]
        
        for evt in sorted_events[1:]:
            prev_evt = current_cluster[-1]
            gap = (evt['date'] - prev_evt['date']).days
            if gap <= max_gap_days:
                current_cluster.append(evt)
            else:
                packets.append(self._build_packet_dict(current_cluster, len(packets) + 1))
                current_cluster = [evt]
                
        if current_cluster:
            packets.append(self._build_packet_dict(current_cluster, len(packets) + 1))
            
        # Ordenar los paquetes por su cúspide de score descendente
        packets.sort(key=lambda p: p['peak_score'], reverse=True)
        return packets

    def _build_packet_dict(self, cluster, packet_id):
        peak_evt = max(cluster, key=lambda x: x['score'])
        start_d = cluster[0]['date']
        end_d = cluster[-1]['date']
        duration = (end_d - start_d).days + 1
        scores = [e['score'] for e in cluster]
        total_energy = sum(scores)
        mean_score = total_energy / len(scores)
        
        # Calcular simetría respecto al pico (Índice de Solitón)
        peak_idx = cluster.index(peak_evt)
        left_scores = [e['score'] for e in cluster[:peak_idx]]
        right_scores = [e['score'] for e in cluster[peak_idx + 1:]]
        min_arms = min(len(left_scores), len(right_scores))
        if min_arms > 0:
            diffs = [abs(left_scores[-(i+1)] - right_scores[i]) for i in range(min_arms)]
            avg_diff = sum(diffs) / len(diffs)
            symmetry_score = max(0.0, 100.0 - (avg_diff * 4.0))
        elif len(cluster) == 1:
            symmetry_score = 100.0
        else:
            symmetry_score = 75.0
            
        all_alignments = []
        for e in cluster:
            for a in e.get('alignments', []):
                if a not in all_alignments:
                    all_alignments.append(a)
                    
        peak_km = peak_evt.get('kuramoto', {})
        has_ecl = any(e.get('eclipse', {}).get('is_eclipse_window') for e in cluster)
        ecl_type = None
        for e in cluster:
            if e.get('eclipse', {}).get('is_eclipse_window'):
                ecl_type = e['eclipse']['eclipse_type']
                break

        return {
            'id': f"W{packet_id}",
            'start_date': start_d,
            'end_date': end_d,
            'duration': duration,
            'peak_event': peak_evt,
            'peak_date': peak_evt['date'],
            'peak_score': peak_evt['score'],
            'peak_tzolkin': peak_evt['tzolkin'],
            'peak_long_count': peak_evt['long_count'],
            'total_energy': total_energy,
            'mean_score': mean_score,
            'symmetry_score': symmetry_score,
            'days': cluster,
            'alignments': all_alignments,
            'peak_kuramoto': peak_km,
            'has_eclipse': has_ecl,
            'eclipse_type': ecl_type,
            'archetype': f"Solitón Solar {peak_evt['tzolkin']}" if 'Ahau' in peak_evt['tzolkin'] else f"Resonancia {peak_evt['tzolkin']}"
        }

    def detect_harmonic_links(self, wave_packets):
        """
        Detecta enlaces hiper-fractales entre las cúspides de las macro-ventanas.
        Calcula resonancia en Tuns (360), Tzolkins (260), Haabs (365), Venus (584), etc.
        """
        links = []
        if len(wave_packets) < 2:
            return links
            
        sorted_p = sorted(wave_packets, key=lambda p: p['peak_date'])
        for i in range(len(sorted_p)):
            for j in range(i + 1, len(sorted_p)):
                p1 = sorted_p[i]
                p2 = sorted_p[j]
                d1 = p1['peak_date']
                d2 = p2['peak_date']
                delta_days = (d2 - d1).days
                
                harmonics = []
                # 1. Tuns (360)
                tun_f = delta_days / 360.0
                if abs(tun_f - round(tun_f)) < 0.03:
                    harmonics.append(f"{int(round(tun_f))} Tuns exactos (360d)")
                elif abs(tun_f - round(tun_f * 2) / 2.0) < 0.03:
                    harmonics.append(f"{round(tun_f * 2) / 2.0} Tuns (Media Octava)")
                    
                # 2. Tzolkins (260)
                tz_f = delta_days / 260.0
                if abs(tz_f - round(tz_f)) < 0.03:
                    harmonics.append(f"{int(round(tz_f))} Tzolkins exactos (260d)")
                    
                # 3. Venus (584)
                v_f = delta_days / 584.0
                if abs(v_f - round(v_f)) < 0.05:
                    harmonics.append(f"{int(round(v_f))} Ciclos Venusianos (~584d)")
                    
                # 4. Señores de la Noche (9)
                if delta_days % 9 == 0:
                    harmonics.append(f"{delta_days // 9} Ciclos de 9 Señores")
                    
                # 5. Katun (7200)
                k_f = delta_days / 7200.0
                if abs(k_f - round(k_f)) < 0.05:
                    harmonics.append(f"{int(round(k_f))} Katun")
                    
                if harmonics:
                    summary = " • ".join(harmonics)
                    links.append({
                        'p1': p1,
                        'p2': p2,
                        'delta_days': delta_days,
                        'harmonics': harmonics,
                        'summary': summary,
                        'label': f"{harmonics[0]}" if harmonics else f"{delta_days}d"
                    })
        # Sort links by number of resonant harmonic coincidences and the sum of peak scores
        links.sort(key=lambda l: (len(l['harmonics']), l['p1']['peak_score'] + l['p2']['peak_score']), reverse=True)
        return links

    def _get_alignments(self, days_since_epoch, natal_days=None):
        """Refactored to accept raw integer directly."""
        alignments = []
        
        checks = {
            "Tzolkin": 260, "Haab": 365, "Tun": 360, "Venus": 584, "819-Day": 819, "Calendar Round": 18980
        }
        
        for name, cycle in checks.items():
            pos = days_since_epoch % cycle
            if natal_days is not None:
                pos = (days_since_epoch - natal_days) % cycle
            
            nodes = [0, cycle * 0.25, cycle * 0.5, cycle * 0.618034, cycle * 0.75, cycle * 0.7836]
            
            # Wrap-around distance calculation
            min_dist = min([min(abs(pos - n), cycle - abs(pos - n)) for n in nodes])
            
            # Cap window at 13 days
            max_window = min(cycle * 0.05, 13.0)
            
            if min_dist <= max_window and max_window > 0:
                alignments.append(name)
            
        ecl = self.get_dresden_eclipse_info(days_since_epoch)
        if ecl.get("is_eclipse_window"):
            alignments.append(f"Dresden {ecl['eclipse_type']}")
            
        return alignments

    def find_exact_returns(self, start_days, cycle1_len, target1, cycle2_len, target2, max_steps=1000):
        """Algorithmic Search using CRT/Stepper to instantly find cycle overlaps (MCM)."""
        d = start_days
        # Step forward until cycle1 matches
        while d % cycle1_len != target1:
            d += 1
            
        # Jump by cycle1_len until cycle2 matches
        for _ in range(max_steps):
            if d % cycle2_len == target2:
                return d
            d += cycle1_len
            
        return None # No solution if exact overlap is impossible (GCD constraints)

    def find_cycle_overlap(self, start_days, c1_name, t1, c2_name, t2, max_steps=5000):
        """
        Buscador de conjunción sagrada multivariante.
        Resuelve el Teorema del Resto Chino considerando los desfases epocales mayas.
        """
        cycle_lengths = {
            "Tzolkin": 260, "Haab": 365, "Tun": 360, "Venus": 584, "Mars": 780,
            "819-Day": 819, "LordOfNight": 9
        }
        def get_cycle_pos(c_name, days_val):
            if c_name == "Tzolkin":
                # Posición lineal de 0..259 días en el ciclo Tzolk'in sagrado (4 Ahau = 0)
                return days_val % 260
            elif c_name == "Haab":
                return (days_val + 348) % 365
            elif c_name == "Venus":
                return (days_val - 1364360) % 584
            elif c_name == "Tun":
                return days_val % 360
            elif c_name == "Mars":
                return days_val % 780
            elif c_name == "819-Day":
                return days_val % 819
            elif c_name == "LordOfNight":
                return (days_val + 8) % 9
            return days_val % 260

        c1_len = cycle_lengths.get(c1_name, 260)
        c2_len = cycle_lengths.get(c2_name, 365)
        t1 = t1 % c1_len
        t2 = t2 % c2_len

        cur_d = start_days
        while get_cycle_pos(c1_name, cur_d) != t1:
            cur_d += 1

        for _ in range(max_steps):
            if get_cycle_pos(c2_name, cur_d) == t2:
                return cur_d
            cur_d += c1_len

        return None
    
    def project_pattern(self, base_date, pattern_days, count=10):
        """Project a pattern forward in time."""
        projections = []
        current = base_date
        
        for i in range(count):
            next_date = current + timedelta(days=pattern_days)
            data = self.converter.get_full_date(next_date.year, next_date.month, next_date.day)
            projections.append({
                'date': next_date,
                'long_count': data['long_count'],
                'calendar_round': data['calendar_round']
            })
            current = next_date
        
        return projections


class FractalAnalysisWorker(QThread):
    """
    Worker asíncrono para cálculo de resonancias y patrones fractales.
    Ejecuta el escaneo en un hilo en segundo plano para mantener la GUI 100% fluida y receptiva.
    """
    progress = Signal(int, int)  # (current_day, total_days)
    result_ready = Signal(list, list, list)  # (events, packets, links)

    def __init__(self, analyzer, start_datetime, total_days, selected, natal_days):
        super().__init__()
        self.analyzer = analyzer
        self.start_datetime = start_datetime
        self.total_days = total_days
        self.selected = selected
        self.natal_days = natal_days

    def run(self):
        def _cb(curr, total):
            self.progress.emit(curr, total)

        events = self.analyzer.find_convergences(
            self.start_datetime,
            self.total_days,
            self.selected,
            self.natal_days,
            progress_callback=_cb
        )
        packets = self.analyzer.group_into_wave_packets(events)
        links = self.analyzer.detect_harmonic_links(packets)
        self.result_ready.emit(events, packets, links)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: CUSTOM UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

class StoneLabel(QLabel):
    """A label styled to look like an engraving."""
    def __init__(self, text, size=14, is_bold=False, color="#e0c090"):
        super().__init__(text)
        weight = "bold" if is_bold else "normal"
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: 'Segoe UI', 'Georgia', serif;
                font-size: {size}px;
                font-weight: {weight};
                background: transparent;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)


class CircularCalendarWidget(QWidget):
    """Circular visualization of Tzolkin and Haab calendars with labelled segments."""
    
    HAAB_LABELS = [
        "Pop", "Uo", "Zip", "Zotz", "Tzec", "Xul", "Yaxkin", "Mol", "Chen",
        "Yax", "Zac", "Ceh", "Mac", "Kankin", "Muan", "Pax", "Kayab", "Cumku", "Wayeb"
    ]
    TZOLKIN_LABELS = [
        "Ahau", "Imix", "Ik", "Akbal", "Kan", "Chicchan", "Cimi", "Manik",
        "Lamat", "Muluc", "Oc", "Chuen", "Eb", "Ben", "Ix", "Men",
        "Cib", "Caban", "Etznab", "Cauac"
    ]
    LORD_LABELS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(380, 380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tzolkin_idx = 0
        self._haab_idx = 0
        self._lord_idx = 0
        self._tzolkin_str = "4 Ahau"
        self._tzolkin_glyph = "☀"
        self._haab_str = "8 Cumku"
        self._rotation = 0.0
        
        # Animation
        self._anim = QPropertyAnimation(self, b"rotation")
        self._anim.setDuration(500)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
    
    def get_rotation(self):
        return self._rotation
    
    def set_rotation(self, val):
        self._rotation = val
        self.update()
    
    rotation = Property(float, get_rotation, set_rotation)
    
    def update_data(self, tzolkin_idx, haab_idx, lord_idx, tzolkin_str="4 Ahau", tzolkin_glyph="☀", haab_str="8 Cumku"):
        old_rot = self._rotation
        self._tzolkin_idx = tzolkin_idx
        self._haab_idx = haab_idx
        self._lord_idx = lord_idx
        self._tzolkin_str = tzolkin_str
        self._tzolkin_glyph = tzolkin_glyph
        self._haab_str = haab_str
        
        new_rot = old_rot + 15
        self._anim.setStartValue(old_rot)
        self._anim.setEndValue(new_rot)
        self._anim.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        max_r = min(w, h) // 2 - 8
        if max_r < 40:
            return
        
        # Background disk
        bg = QRadialGradient(cx, cy, max_r)
        bg.setColorAt(0, QColor(40, 35, 30))
        bg.setColorAt(1, QColor(20, 18, 15))
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - max_r, cy - max_r, max_r * 2, max_r * 2)
        
        # Proportional concentric ring dimensions
        r_haab_out = max_r - 2
        r_haab_in = int(max_r * 0.77)
        
        r_tz_out = r_haab_in - 2
        r_tz_in = int(max_r * 0.54)
        
        r_lord_out = r_tz_in - 2
        r_lord_in = int(max_r * 0.36)
        
        center_r = r_lord_in - 2
        
        # Outer ring - Haab (19 segments)
        self._draw_ring(painter, cx, cy, r_haab_out, r_haab_in, 19, self._haab_idx, 
                       QColor(139, 90, 43), QColor(210, 150, 80), self.HAAB_LABELS)
        
        # Middle ring - Tzolkin (20 segments)
        self._draw_ring(painter, cx, cy, r_tz_out, r_tz_in, 20, self._tzolkin_idx,
                       QColor(80, 100, 60), QColor(150, 180, 100), self.TZOLKIN_LABELS)
        
        # Inner ring - Lords (9 segments)
        self._draw_ring(painter, cx, cy, r_lord_out, r_lord_in, 9, self._lord_idx,
                       QColor(100, 50, 50), QColor(180, 80, 80), self.LORD_LABELS)
        
        # Center circle - Sacred Kin/Sun Core
        if center_r > 15:
            # Radial glowing gold gradient
            center_grad = QRadialGradient(cx, cy, center_r)
            center_grad.setColorAt(0, QColor(62, 50, 26))
            center_grad.setColorAt(0.65, QColor(36, 28, 18))
            center_grad.setColorAt(1, QColor(18, 15, 12))
            painter.setBrush(QBrush(center_grad))
            painter.setPen(QPen(QColor(212, 175, 55, 220), 2))
            painter.drawEllipse(cx - center_r, cy - center_r, center_r * 2, center_r * 2)

            # Inner subtle gold decorative ring
            inner_ring_r = center_r - 6
            if inner_ring_r > 10:
                painter.setPen(QPen(QColor(241, 196, 15, 120), 1, Qt.DashLine))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(cx - inner_ring_r, cy - inner_ring_r, inner_ring_r * 2, inner_ring_r * 2)

            # Glyph and Sacred Text
            glyph_font = QFont("Segoe UI", max(14, int(center_r * 0.40)))
            painter.setFont(glyph_font)
            painter.setPen(QColor(244, 208, 63))
            painter.drawText(cx - center_r, cy - int(center_r * 0.65), center_r * 2, int(center_r * 0.65), Qt.AlignCenter, self._tzolkin_glyph)

            tz_font = QFont("Segoe UI", max(8, int(center_r * 0.22)), QFont.Bold)
            painter.setFont(tz_font)
            painter.setPen(QColor(241, 196, 15))
            painter.drawText(cx - center_r, cy + int(center_r * 0.05), center_r * 2, int(center_r * 0.38), Qt.AlignCenter, self._tzolkin_str)

            haab_font = QFont("Segoe UI", max(7, int(center_r * 0.16)))
            painter.setFont(haab_font)
            painter.setPen(QColor(210, 180, 140, 220))
            painter.drawText(cx - center_r, cy + int(center_r * 0.42), center_r * 2, int(center_r * 0.35), Qt.AlignCenter, self._haab_str)
    
    def _draw_ring(self, painter, cx, cy, outer_r, inner_r, segments, highlight_idx, base_color, highlight_color, labels=None):
        segment_angle = 360 / segments
        
        for i in range(segments):
            start_angle = int((i * segment_angle + self._rotation) * 16)
            span_angle = int(segment_angle * 16) - 16
            
            if i == highlight_idx:
                color = highlight_color
                pen_color = QColor(255, 215, 0)
            else:
                color = base_color
                pen_color = QColor(60, 50, 40)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(pen_color, 1))
            
            path_rect = QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
            painter.drawPie(path_rect, start_angle, span_angle)
        
        # Draw labels on each segment
        if labels and outer_r > 30:
            mid_r = (outer_r + inner_r) / 2
            ring_thickness = outer_r - inner_r
            arc_len = mid_r * math.radians(segment_angle)
            base_font_size = max(7, min(13, int(min(ring_thickness * 0.24, arc_len * 0.22))))
            
            for i in range(segments):
                mid_angle_deg = i * segment_angle + segment_angle / 2 + self._rotation
                mid_angle_rad = math.radians(mid_angle_deg)
                
                # Position at midpoint of segment arc
                lx = cx + mid_r * math.cos(mid_angle_rad)
                ly = cy - mid_r * math.sin(mid_angle_rad)
                
                label = labels[i] if i < len(labels) else ""
                
                # Dynamically fit text within the segment arc to prevent collision/overlap
                cur_font_size = base_font_size
                label_font = QFont("Segoe UI", cur_font_size, QFont.Bold)
                fm = QFontMetrics(label_font)
                tw = fm.horizontalAdvance(label)
                max_w = arc_len * 0.85
                
                while tw > max_w and cur_font_size > 6:
                    cur_font_size -= 1
                    label_font = QFont("Segoe UI", cur_font_size, QFont.Bold)
                    fm = QFontMetrics(label_font)
                    tw = fm.horizontalAdvance(label)
                
                painter.setFont(label_font)
                
                # Text colour: bright for highlighted, subtle for others
                if i == highlight_idx:
                    painter.setPen(QColor(30, 20, 10))
                else:
                    painter.setPen(QColor(220, 200, 170, 180))
                
                # Rotate text to follow the arc, ensuring human readability (never upside down)
                painter.save()
                painter.translate(lx, ly)
                
                rot = (-mid_angle_deg + 90) % 360
                if rot > 180:
                    rot -= 360
                if rot > 90:
                    rot -= 180
                elif rot < -90:
                    rot += 180
                painter.rotate(rot)
                
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(label)
                th = fm.height()
                painter.drawText(int(-tw / 2), int(th / 4), label)
                painter.restore()


class LongCountDisplay(QWidget):
    """Animated odometer-style Long Count display with authentic Classic Maya Dot-and-Bar notation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(105)
        self._parts = [13, 0, 0, 0, 0]  # baktun.katun.tun.uinal.kin
        self._labels = ["Baktun", "Katun", "Tun", "Uinal", "Kin"]
        
    def set_long_count(self, parts):
        self._parts = parts
        self.update()
        
    def _draw_maya_number(self, painter, cx, cy, val):
        """
        Draws Classic Maya vigesimal notation:
        - 0: Ceremonial shell glyph (concha / cero)
        - 1-4: Dots (•)
        - 5, 10, 15: Horizontal bars (—)
        """
        painter.save()
        dot_color = QColor(244, 208, 63)
        bar_color = QColor(220, 160, 50)
        
        if val == 0:
            # Shell glyph
            painter.setPen(QPen(bar_color, 1.5))
            painter.setBrush(QBrush(QColor(50, 40, 25)))
            shell_w, shell_h = 22, 12
            painter.drawEllipse(int(cx - shell_w / 2), int(cy - shell_h / 2), shell_w, shell_h)
            painter.setPen(QPen(dot_color, 1))
            painter.drawLine(int(cx - shell_w / 2 + 3), int(cy), int(cx + shell_w / 2 - 3), int(cy))
            painter.drawArc(int(cx - shell_w / 4), int(cy - shell_h / 2 + 2), int(shell_w / 2), shell_h - 4, 0, 180 * 16)
        else:
            bars = val // 5
            dots = val % 5
            bar_w = 22
            bar_h = 4
            dot_r = 2.2
            
            total_h = (bars * 6) + (7 if dots > 0 else 0)
            current_y = cy - total_h / 2
            
            if dots > 0:
                dot_spacing = 6.5
                dot_start_x = cx - ((dots - 1) * dot_spacing) / 2
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(dot_color))
                for d in range(dots):
                    painter.drawEllipse(QPointF(dot_start_x + d * dot_spacing, current_y + dot_r), dot_r, dot_r)
                current_y += 7
                
            if bars > 0:
                painter.setPen(QPen(QColor(140, 95, 25), 0.8))
                painter.setBrush(QBrush(bar_color))
                for b in range(bars):
                    painter.drawRoundedRect(QRectF(cx - bar_w / 2, current_y, bar_w, bar_h), 1.5, 1.5)
                    current_y += 6
        painter.restore()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        box_w = w // 5 - 10
        box_h = 74
        y_offset = (h - box_h - 18) // 2
        
        for i, (val, label) in enumerate(zip(self._parts, self._labels)):
            x = 5 + i * (box_w + 10)
            
            # Box background
            grad = QLinearGradient(x, y_offset, x, y_offset + box_h)
            grad.setColorAt(0, QColor(50, 45, 40))
            grad.setColorAt(0.5, QColor(70, 60, 50))
            grad.setColorAt(1, QColor(40, 35, 30))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(100, 90, 70), 2))
            painter.drawRoundedRect(x, y_offset, box_w, box_h, 6, 6)
            
            # 1. Arabic Number (Top)
            painter.setPen(QColor(244, 208, 63))
            font = QFont("Consolas", 18, QFont.Bold)
            painter.setFont(font)
            painter.drawText(x, y_offset + 3, box_w, 24, Qt.AlignCenter, str(val))
            
            # 2. Maya Dot-and-Bar Drawing (Middle)
            self._draw_maya_number(painter, x + box_w // 2, y_offset + 48, val)
            
            # 3. Label (Bottom outside box)
            painter.setPen(QColor(160, 150, 130))
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(x, y_offset + box_h + 2, box_w, 18, Qt.AlignCenter, label)
            
            # Separator dot
            if i < 4:
                painter.setPen(QColor(200, 180, 140))
                painter.setFont(QFont("Consolas", 14, QFont.Bold))
                painter.drawText(x + box_w, y_offset + 10, 10, 30, Qt.AlignCenter, ".")


class VenusPhaseBar(QWidget):
    """
    Barra visual de las 4 fases sinódicas de Venus según el Códice de Dresde (584 días):
    - 0..236:   Estrella de la Mañana (236 d) - Conjunción helíaca matutina
    - 236..326: Conjunción Superior (90 d)   - Detrás del Sol (Invisible)
    - 326..576: Estrella Vespertina (250 d)  - Ocaso vespertino
    - 576..584: Conjunción Inferior (8 d)    - Frente al Sol (Invisible)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self._pos = 0
        
    def set_position(self, pos):
        self._pos = max(0, min(584, pos))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if w < 10:
            return
            
        quadrants = [
            (236, QColor(41, 128, 185)),  # Matutina (Azul)
            (90,  QColor(70, 60, 50)),    # Conjunción Superior (Oscuro)
            (250, QColor(175, 122, 197)), # Vespertina (Púrpura/Ocaso)
            (8,   QColor(192, 57, 43))    # Conjunción Inferior (Rojo)
        ]
        
        x = 0.0
        bar_h = 8
        y = (h - bar_h) / 2.0
        
        # Base track
        for duration, color in quadrants:
            qw = (duration / 584.0) * w
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(25, 20, 15), 1))
            painter.drawRect(QRectF(x, y, qw, bar_h))
            x += qw
            
        # Current position marker (glowing diamond)
        marker_x = (self._pos / 584.0) * w
        painter.setBrush(QBrush(QColor(255, 235, 59)))
        painter.setPen(QPen(QColor(20, 15, 10), 1.5))
        
        poly = QPolygonF([
            QPointF(marker_x, y - 3),
            QPointF(marker_x + 4, y + bar_h / 2.0),
            QPointF(marker_x, y + bar_h + 3),
            QPointF(marker_x - 4, y + bar_h / 2.0)
        ])
        painter.drawPolygon(poly)


class StonePanel(QFrame):
    """A container widget that looks like a chiseled stone block."""
    def __init__(self, title, main_text, sub_text=""):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 15, 10, 15)

        self.lbl_title = StoneLabel(title.upper(), size=10, color="#8a9a5b")
        layout.addWidget(self.lbl_title)

        self.lbl_main = StoneLabel(main_text, size=22, is_bold=True, color="#f4d03f")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(2)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(2, 2)
        self.lbl_main.setGraphicsEffect(shadow)
        layout.addWidget(self.lbl_main)

        self.lbl_sub = StoneLabel(sub_text, size=12, color="#aaaaaa")
        self.lbl_sub.setWordWrap(True)
        layout.addWidget(self.lbl_sub)

        self.setStyleSheet("""
            StonePanel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #2b2b2b);
                border: 2px solid #555;
                border-top-color: #666;
                border-left-color: #666;
                border-right-color: #1a1a1a;
                border-bottom-color: #1a1a1a;
                border-radius: 8px;
            }
        """)

    def update_data(self, main_text, sub_text=""):
        self.lbl_main.setText(main_text)
        self.lbl_sub.setText(sub_text)


class FractalTimelineWidget(QWidget):
    """
    Osciloscopio Continuo de Coherencia Armónica Maya.
    Renderiza la envolvente de resonancia como una onda continua de probabilidad/campo,
    destaca las cúspides de los paquetes de onda, traza arcos de hiper-enlaces fractales
    y proporciona retícula interactiva con HUD en tiempo real.
    """
    date_clicked = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(155)
        self.setMouseTracking(True)
        self._events = []
        self._wave_packets = []
        self._harmonic_links = []
        self._start_date = None
        self._range_days = 365
        self._hover_x = -1
        self._hover_date = None
        self._hover_info = None
        
        # GPU/Vector Path Caches para repintado instantáneo (60+ FPS sin recálculos)
        self._cached_wave_fill = None
        self._cached_wave_line = None
        self._cached_peak_markers = []
        self._cached_peak_tags = []
        self._cached_w = 0
        self._cached_h = 0
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rebuild_wave_cache()

    def set_data(self, events, wave_packets=None, harmonic_links=None, start_date=None, range_days=365):
        self._events = events or []
        self._wave_packets = wave_packets or []
        self._harmonic_links = harmonic_links or []
        self._start_date = start_date
        self._range_days = max(1, range_days)
        self._hover_x = -1
        self._hover_info = None
        self._rebuild_wave_cache()
        self.update()

    def _rebuild_wave_cache(self):
        """Precomputa las trayectorias de onda y marcadores con LOD adaptativo anti-colisión."""
        w, h = self.width(), self.height()
        left, right = 45, 35
        top, bottom = 32, 28
        gw = w - left - right
        gh = h - top - bottom

        self._cached_wave_fill = None
        self._cached_wave_line = None
        self._cached_peak_markers = []
        self._cached_peak_tags = []
        self._cached_w = w
        self._cached_h = h

        if not self._events or not self._start_date or self._range_days <= 0 or gw <= 50:
            return

        # 1. Nodos de picos en espacio de coordenadas
        peak_nodes = []
        if self._wave_packets:
            for pkt in self._wave_packets:
                pk_days = (pkt['peak_date'] - self._start_date).days
                if -50 <= pk_days <= (self._range_days + 50):
                    pk_x = left + (pk_days / self._range_days) * gw
                    dur_px = max(14.0, min(45.0, (pkt['duration'] / self._range_days) * gw * 2.5 + 16.0))
                    peak_nodes.append((pk_x, pkt['peak_score'], dur_px))
        else:
            for e in self._events:
                e_days = (e['date'] - self._start_date).days
                if -10 <= e_days <= (self._range_days + 10):
                    ex = left + (e_days / self._range_days) * gw
                    peak_nodes.append((ex, e['score'], 14.0))

        # 2. Muestreo de onda continua
        num_samples = max(gw, 160)
        wave_points = []
        for s_idx in range(num_samples + 1):
            px = left + (s_idx / num_samples) * gw
            local_score = 0.0
            for pk_x, pk_score, pk_sigma in peak_nodes:
                d_px = abs(px - pk_x)
                if d_px < pk_sigma * 3.5:
                    contrib = pk_score * math.exp(-(d_px**2) / (2.0 * (pk_sigma**2)))
                    if contrib > local_score:
                        local_score = contrib
            py = top + gh - int((local_score / 100.0) * gh)
            wave_points.append(QPointF(px, py))

        if wave_points:
            p_fill = QPainterPath()
            p_fill.moveTo(left, top + gh)
            for pt in wave_points:
                p_fill.lineTo(pt)
            p_fill.lineTo(left + gw, top + gh)
            p_fill.closeSubpath()
            self._cached_wave_fill = p_fill

            p_line = QPainterPath()
            p_line.moveTo(wave_points[0])
            for pt in wave_points[1:]:
                p_line.lineTo(pt)
            self._cached_wave_line = p_line

        # 3. Marcadores de picos y etiquetas adaptativas anti-colisión
        packets_in_view = []
        for packet in self._wave_packets:
            p_days = (packet['peak_date'] - self._start_date).days
            if 0 <= p_days <= self._range_days:
                pk_x = left + int((p_days / self._range_days) * gw)
                pk_y = top + gh - int((packet['peak_score'] / 100.0) * gh)
                self._cached_peak_markers.append((pk_x, pk_y, packet['peak_score']))
                packets_in_view.append((pk_x, pk_y, packet))

        # LOD Inteligente: badges de texto sin solapamiento
        fm = QFontMetrics(QFont("Segoe UI", 8, QFont.Bold))
        placed_intervals = []
        # Priorizar picos de mayor score
        sorted_pkts = sorted(packets_in_view, key=lambda x: x[2]['peak_score'], reverse=True)
        max_tags = 22 if len(sorted_pkts) > 22 else len(sorted_pkts)

        for pk_x, pk_y, packet in sorted_pkts:
            tag_text = f"{packet['peak_tzolkin']} ({packet['peak_score']:.1f}%)"
            tag_w = fm.horizontalAdvance(tag_text) + 10
            tag_h = fm.height() + 4
            tag_bx = pk_x - tag_w // 2
            tag_by = max(top + 8, pk_y - 20)

            # Evitar solapamientos horizontales
            overlap = False
            for prev_l, prev_r in placed_intervals:
                if not (tag_bx + tag_w < prev_l or tag_bx > prev_r):
                    overlap = True
                    break

            if not overlap and len(self._cached_peak_tags) < max_tags:
                placed_intervals.append((tag_bx - 6, tag_bx + tag_w + 6))
                self._cached_peak_tags.append((tag_bx, tag_by, tag_w, tag_h, tag_text))

    def set_events(self, events, range_days=365):
        """Retrocompatibilidad."""
        self.set_data(events, range_days=range_days)
    
    def mouseMoveEvent(self, event):
        pos = event.position()
        self._hover_x = pos.x()
        w = self.width()
        left, right = 45, 35
        gw = w - left - right
        
        if gw > 0 and self._start_date and left <= self._hover_x <= (left + gw):
            t_frac = (self._hover_x - left) / gw
            day_offset = int(t_frac * self._range_days)
            cur_date = self._start_date + timedelta(days=day_offset)
            self._hover_date = cur_date
            
            # Buscar evento cercano a menos de 4 días
            closest_evt = None
            min_d = 5
            for e in self._events:
                d_diff = abs((e['date'] - cur_date).days)
                if d_diff < min_d:
                    min_d = d_diff
                    closest_evt = e
            
            # Buscar paquete al que pertenezca
            parent_packet = None
            for p in self._wave_packets:
                if p['start_date'] <= cur_date <= p['end_date']:
                    parent_packet = p
                    break
                    
            self._hover_info = {
                'date': cur_date,
                'event': closest_evt,
                'packet': parent_packet
            }
        else:
            self._hover_info = None
            self._hover_x = -1
            
        self.update()

    def leaveEvent(self, event):
        self._hover_x = -1
        self._hover_info = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._hover_info:
            target_date = self._hover_info['date']
            if self._hover_info.get('event'):
                target_date = self._hover_info['event']['date']
            self.date_clicked.emit(target_date)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        left, right = 45, 35
        top, bottom = 32, 28
        gw = w - left - right
        gh = h - top - bottom
        
        # 1. Fondo Oscuro estilo Estela Maya con marco sutil
        painter.fillRect(0, 0, w, h, QColor(20, 18, 15))
        painter.setPen(QPen(QColor(48, 42, 34), 1))
        painter.drawRect(left, top, gw, gh)
        
        # 2. Gradilla Horizontal de Score (50%, 65%, 75%, 85%)
        font_axis = QFont("Segoe UI", 8)
        painter.setFont(font_axis)
        
        score_levels = [(50, "50%"), (65, "65%"), (75, "75%"), (85, "85%")]
        for s_val, s_lbl in score_levels:
            y_s = top + gh - int((s_val / 100.0) * gh)
            if top <= y_s <= top + gh:
                painter.setPen(QPen(QColor(42, 37, 30), 1, Qt.DashLine))
                painter.drawLine(left, y_s, left + gw, y_s)
                painter.setPen(QPen(QColor(130, 115, 95), 1))
                painter.drawText(8, y_s + 4, s_lbl)
                
        # 3. Gradilla Vertical de Tiempo (Años)
        if self._start_date and self._range_days > 0 and gw > 50:
            start_year = self._start_date.year
            end_date = self._start_date + timedelta(days=self._range_days)
            end_year = end_date.year
            year_span = end_year - start_year
            
            if year_span <= 3:
                step_years = 1
            elif year_span <= 10:
                step_years = 2
            elif year_span <= 30:
                step_years = 5
            elif year_span <= 80:
                step_years = 10
            elif year_span <= 200:
                step_years = 25
            elif year_span <= 500:
                step_years = 50
            elif year_span <= 1000:
                step_years = 100
            elif year_span <= 2500:
                step_years = 250
            else:
                step_years = 500

            first_mark = (start_year // step_years + 1) * step_years
            
            for y in range(first_mark, end_year + 1, step_years):
                dt_mark = datetime(y, 1, 1)
                days_mark = (dt_mark - self._start_date).days
                if 0 <= days_mark <= self._range_days:
                    x_mark = left + int((days_mark / self._range_days) * gw)
                    painter.setPen(QPen(QColor(38, 33, 26), 1, Qt.DotLine))
                    painter.drawLine(x_mark, top, x_mark, top + gh)
                    painter.setPen(QPen(QColor(140, 125, 100), 1))
                    painter.drawText(x_mark - 14, h - 8, str(y))

        # 4. Línea de Umbral de Coherencia Armónica (60%)
        y_60 = top + gh - int((60.0 / 100.0) * gh)
        painter.setPen(QPen(QColor(218, 165, 32, 70), 1, Qt.DashLine))
        painter.drawLine(left, y_60, left + gw, y_60)
        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor(218, 165, 32, 110), 1))
        painter.drawText(left + 6, y_60 - 3, "--- Umbral de Coherencia Armónica (60%) ---")

        # Check if cache is valid or needs lazy rebuild
        if self._cached_w != w or self._cached_h != h or (self._events and self._cached_wave_fill is None):
            self._rebuild_wave_cache()

        # 5. Curva Continua de Coherencia Armónica (Osciloscopio desde Cache Vectorial Instantáneo)
        if self._cached_wave_fill and self._cached_wave_line:
            grad_wave = QLinearGradient(0, top, 0, top + gh)
            grad_wave.setColorAt(0.0, QColor(241, 196, 15, 175))   # Cima Oro puro radiante
            grad_wave.setColorAt(0.35, QColor(230, 126, 34, 125)) # Ámbar cósmico
            grad_wave.setColorAt(0.75, QColor(39, 174, 96, 45))   # Verde jade suave
            grad_wave.setColorAt(1.0, QColor(10, 8, 6, 10))
            painter.setBrush(QBrush(grad_wave))
            painter.setPen(Qt.NoPen)
            painter.drawPath(self._cached_wave_fill)

            pen_wave = QPen(QColor(241, 196, 15, 230), 1.8)
            painter.setPen(pen_wave)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self._cached_wave_line)

        # 5b. Cúspides de las Macro-Ventanas (Solitones destacados con LOD)
        for pk_x, pk_y, score in self._cached_peak_markers:
            halo_r = 14 if score >= 75 else 10
            halo_grad = QRadialGradient(pk_x, pk_y, halo_r)
            halo_grad.setColorAt(0.0, QColor(255, 215, 0, 200))
            halo_grad.setColorAt(0.6, QColor(230, 126, 34, 80))
            halo_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(halo_grad))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(pk_x, pk_y), halo_r, halo_r)

            # Punto central radiante
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(218, 165, 32), 1.2))
            painter.drawEllipse(QPointF(pk_x, pk_y), 3.5, 3.5)

        # Etiquetas legibles sin solapamiento (LOD adaptativo)
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for tag_bx, tag_by, tag_w, tag_h, tag_text in self._cached_peak_tags:
            painter.setBrush(QBrush(QColor(18, 15, 12, 220)))
            painter.setPen(QPen(QColor(140, 115, 75), 1))
            painter.drawRoundedRect(tag_bx, tag_by, tag_w, tag_h, 3, 3)

            painter.setPen(QPen(QColor(255, 225, 130), 1))
            painter.drawText(tag_bx + 5, tag_by + tag_h - 4, tag_text)

        # 6. Arcos de Hiper-Enlaces Fractales entre Cúspides
        placed_arc_x = []
        for link in self._harmonic_links[:3]:
            if self._start_date and self._range_days > 0:
                p1_days = (link['p1']['peak_date'] - self._start_date).days
                p2_days = (link['p2']['peak_date'] - self._start_date).days
                if 0 <= p1_days <= self._range_days and 0 <= p2_days <= self._range_days:
                    x1 = left + int((p1_days / self._range_days) * gw)
                    x2 = left + int((p2_days / self._range_days) * gw)
                    if abs(x2 - x1) < 45:
                        continue
                    y1 = top + gh - int((link['p1']['peak_score'] / 100.0) * gh)
                    y2 = top + gh - int((link['p2']['peak_score'] / 100.0) * gh)
                    
                    # Arco cuadrático elevado de Bézier
                    mid_x = (x1 + x2) / 2.0
                    apex_y = max(top - 14, min(y1, y2) - 30)
                    
                    path_arc = QPainterPath()
                    path_arc.moveTo(x1, y1)
                    path_arc.quadTo(mid_x, apex_y, x2, y2)
                    
                    pen_arc = QPen(QColor(218, 165, 32, 170), 1.3, Qt.DashLine)
                    painter.setPen(pen_arc)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path_arc)
                    
                    # Píldora de texto en el ápice del arco
                    lbl_arc = f"✦ {link['label']} ✦"
                    painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
                    arc_metrics = painter.fontMetrics()
                    arc_w = arc_metrics.horizontalAdvance(lbl_arc) + 12
                    arc_h = arc_metrics.height() + 4
                    arc_bx = int(mid_x - arc_w // 2)
                    arc_by = int(apex_y - arc_h // 2)
                    
                    if not any(abs(arc_bx - px) < (arc_w + 10) for px in placed_arc_x):
                        placed_arc_x.append(arc_bx)
                        painter.setBrush(QBrush(QColor(18, 15, 12, 235)))
                        painter.setPen(QPen(QColor(218, 165, 32, 200), 1))
                        painter.drawRoundedRect(arc_bx, arc_by, arc_w, arc_h, 4, 4)
                        
                        painter.setPen(QPen(QColor(245, 215, 110), 1))
                        painter.drawText(arc_bx + 6, arc_by + arc_h - 4, lbl_arc)

        # 7. Retícula de Cursor y HUD Flotante (Hover)
        if self._hover_x >= left and self._hover_x <= (left + gw) and self._hover_info:
            # Línea vertical del osciloscopio
            painter.setPen(QPen(QColor(0, 220, 255, 140), 1.2, Qt.SolidLine))
            painter.drawLine(self._hover_x, top, self._hover_x, top + gh)
            
            # Dibujar caja HUD flotante
            hud_w, hud_h = 225, 76
            hud_x = self._hover_x + 12
            if hud_x + hud_w > w - 10:
                hud_x = self._hover_x - hud_w - 12
            hud_y = top + 8
            
            painter.setBrush(QBrush(QColor(15, 12, 10, 240)))
            painter.setPen(QPen(QColor(218, 165, 32, 200), 1.2))
            painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 6, 6)
            
            dt_str = self._hover_info['date'].strftime("%b %d, %Y")
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(QPen(QColor(241, 196, 15), 1))
            painter.drawText(hud_x + 8, hud_y + 16, f"⏱ {dt_str}")
            
            evt = self._hover_info.get('event')
            pkt = self._hover_info.get('packet')
            
            painter.setFont(QFont("Segoe UI", 8))
            if evt:
                painter.setPen(QPen(QColor(230, 230, 230), 1))
                painter.drawText(hud_x + 8, hud_y + 31, f"Score: {evt['score']:.1f}% • {evt['tzolkin']}")
                
                # Kuramoto metrics
                km = evt.get('kuramoto', {})
                km_r = km.get('r', 0.0) * 100.0
                km_psi = km.get('psi_deg', 0.0)
                painter.setPen(QPen(QColor(93, 173, 226), 1))
                painter.drawText(hud_x + 8, hud_y + 46, f"Kuramoto R: {km_r:.1f}%  Ψ: {km_psi:.0f}°")
                
                # Eclipse warning or Long Count
                ecl = evt.get('eclipse', {})
                if ecl.get('is_eclipse_window'):
                    painter.setPen(QPen(QColor(231, 76, 60), 1))
                    painter.drawText(hud_x + 8, hud_y + 61, f"⚠️ ECLIPSE: {ecl.get('eclipse_type', '')}")
                else:
                    painter.setPen(QPen(QColor(170, 170, 170), 1))
                    painter.drawText(hud_x + 8, hud_y + 61, f"{evt['long_count']}")
            elif pkt:
                painter.setPen(QPen(QColor(93, 173, 226), 1))
                painter.drawText(hud_x + 8, hud_y + 31, f"Ventana: {pkt['id']} ({pkt['duration']} días)")
                painter.setPen(QPen(QColor(170, 170, 170), 1))
                painter.drawText(hud_x + 8, hud_y + 46, f"Cúspide: {pkt['peak_tzolkin']} ({pkt['peak_score']:.1f}%)")
                if pkt.get('has_eclipse'):
                    painter.setPen(QPen(QColor(231, 76, 60), 1))
                    painter.drawText(hud_x + 8, hud_y + 61, f"⚠️ ECLIPSE DRESDE: {pkt.get('eclipse_type', '')}")
                else:
                    painter.setPen(QPen(QColor(241, 196, 15), 1))
                    painter.drawText(hud_x + 8, hud_y + 61, f"Simetría Solitón: {pkt['symmetry_score']:.0f}%")
            else:
                painter.setPen(QPen(QColor(130, 130, 130), 1))
                painter.drawText(hud_x + 8, hud_y + 36, "Campo en equilibrio basal")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3.5: PROFILE EXPORT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class MayanProfileExportDialog(QDialog):
    """Diálogo completo de exportación de perfiles mayas (SVG, MD, Texto, JSON)."""
    def __init__(self, parent, full_data, gregorian_str, correlation_name="GMT (584283)"):
        super().__init__(parent)
        self.full_data = full_data
        self.gregorian_str = gregorian_str
        self.correlation_name = correlation_name
        self.setWindowTitle(f"📜 Exportador de Perfil Arqueo-Astronómico Maya — {gregorian_str}")
        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.resize(780, 640)
        self.setStyleSheet("""
            QDialog { background: #181512; color: #E0C090; }
            QTabWidget::pane { border: 1px solid #4D412F; background: #201C17; border-radius: 6px; }
            QTabBar::tab { background: #2B251E; color: #BBB; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background: #4D412F; color: #F1C40F; font-weight: bold; }
            QPlainTextEdit { background: #12100E; color: #F4D03F; border: 1px solid #3A3225; font-family: 'Consolas', 'Courier New', monospace; font-size: 11px; padding: 8px; border-radius: 4px; }
            QPushButton { background: #3E3224; color: #FFF; border: 1px solid #7A684D; border-radius: 4px; padding: 8px 14px; font-weight: bold; }
            QPushButton:hover { background: #554532; border-color: #F1C40F; color: #F1C40F; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header Banner
        header = QFrame()
        header.setStyleSheet("background: #24201A; border: 1px solid #4D412F; border-radius: 6px; padding: 10px;")
        h_layout = QHBoxLayout(header)
        h_info = (
            f"<b>✦ ESTELA: {full_data.get('long_count', '')}</b> • "
            f"Tzolk'in: <b style='color:#F1C40F'>{full_data.get('tzolkin', '')}</b> • "
            f"Haab': <b style='color:#E67E22'>{full_data.get('haab', '')}</b> • "
            f"Señor: <b style='color:#5DADE2'>{full_data.get('lord', '')}</b>"
        )
        lbl_h = QLabel(h_info)
        lbl_h.setStyleSheet("font-size: 13px; color: #E0C090;")
        h_layout.addWidget(lbl_h)
        layout.addWidget(header)

        # Precompute exports
        if MayanProfileExporter:
            self.svg_text = MayanProfileExporter.export_svg(full_data, gregorian_date_str=gregorian_str)
            self.md_text = MayanProfileExporter.export_markdown(full_data, gregorian_date_str=gregorian_str, correlation_name=correlation_name)
            self.txt_text = MayanProfileExporter.export_text(full_data, gregorian_date_str=gregorian_str, correlation_name=correlation_name)
            self.json_text = MayanProfileExporter.export_json(full_data, correlation_name=correlation_name)
        else:
            self.svg_text = "<svg></svg>"
            self.md_text = "# Perfil Maya"
            self.txt_text = "Estela Maya"
            self.json_text = "{}"

        # Tabs
        self.tabs = QTabWidget()
        
        # Tab SVG
        self.edit_svg = QPlainTextEdit(self.svg_text)
        self.edit_svg.setReadOnly(True)
        self.tabs.addTab(self.edit_svg, "🖼️ SVG Vectorial")

        # Tab Markdown
        self.edit_md = QPlainTextEdit(self.md_text)
        self.edit_md.setReadOnly(True)
        self.tabs.addTab(self.edit_md, "📝 Markdown Dossier")

        # Tab Plain Text
        self.edit_txt = QPlainTextEdit(self.txt_text)
        self.edit_txt.setReadOnly(True)
        self.tabs.addTab(self.edit_txt, "📜 Texto Estela")

        # Tab JSON
        self.edit_json = QPlainTextEdit(self.json_text)
        self.edit_json.setReadOnly(True)
        self.tabs.addTab(self.edit_json, "{ } JSON Estructurado")

        layout.addWidget(self.tabs, stretch=1)

        # Actions toolbar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_copy = QPushButton("📋 Copiar Formato Activo")
        self.btn_copy.clicked.connect(self._copy_current)
        btn_bar.addWidget(self.btn_copy)

        self.btn_save = QPushButton("💾 Guardar Formato Activo...")
        self.btn_save.clicked.connect(self._save_current)
        btn_bar.addWidget(self.btn_save)

        self.btn_save_all = QPushButton("📦 Exportar Paquete Completo (4 Archivos)")
        self.btn_save_all.setStyleSheet("background: #6C3483; color: #F4D03F; border: 1px solid #BB8FCE; font-weight: bold;")
        self.btn_save_all.clicked.connect(self._save_all_bundle)
        btn_bar.addWidget(self.btn_save_all)

        btn_bar.addStretch()

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_bar.addWidget(btn_close)

        layout.addLayout(btn_bar)

    def _get_current_content_and_ext(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            return self.svg_text, "svg", "Archivos SVG (*.svg)"
        elif idx == 1:
            return self.md_text, "md", "Archivos Markdown (*.md)"
        elif idx == 2:
            return self.txt_text, "txt", "Archivos de Texto (*.txt)"
        else:
            return self.json_text, "json", "Archivos JSON (*.json)"

    def _copy_current(self):
        content, ext, _ = self._get_current_content_and_ext()
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        QMessageBox.information(self, "Copiado", f"El contenido en formato .{ext} se ha copiado al portapapeles.")

    def _save_current(self):
        content, ext, flt = self._get_current_content_and_ext()
        clean_date = self.gregorian_str.replace(" ", "_").replace(",", "")
        default_name = f"Estela_Maya_{clean_date}.{ext}"
        path, _ = QFileDialog.getSaveFileName(self, f"Guardar como .{ext}", default_name, flt)
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Guardado", f"Archivo guardado exitosamente en:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def _save_all_bundle(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Exportar el Paquete")
        if folder:
            clean_date = self.gregorian_str.replace(" ", "_").replace(",", "")
            import os
            base_filename = os.path.join(folder, f"Estela_Maya_{clean_date}")
            try:
                with open(f"{base_filename}.svg", "w", encoding="utf-8") as f:
                    f.write(self.svg_text)
                with open(f"{base_filename}.md", "w", encoding="utf-8") as f:
                    f.write(self.md_text)
                with open(f"{base_filename}.txt", "w", encoding="utf-8") as f:
                    f.write(self.txt_text)
                with open(f"{base_filename}.json", "w", encoding="utf-8") as f:
                    f.write(self.json_text)
                QMessageBox.information(
                    self, "Paquete Exportado",
                    f"¡Se han generado exitosamente los 4 formatos (.svg, .md, .txt, .json) en:\n{folder}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando el paquete:\n{str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class MayanSteleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = MayanConverter()
        self.analyzer = FractalPatternAnalyzer(self.converter)
        self.fractal_events = []
        self.fractal_packets = []
        self.fractal_links = []
        self.fractal_view_mode = "packets"
        self.setWindowTitle("MAYAN STELE - Ultimate Calendar & Fractal Pattern Analyzer")
        if LOGO_ICO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_ICO_PATH)))
        elif LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.resize(1000, 800)
        self._apply_global_style()
        self._setup_ui()
        self._set_initial_date()
        
        # Live Mayan date clock in status bar
        self.statusBar().setStyleSheet(
            "QStatusBar { background: #1a1815; color: #d4af37; font-size: 12px; "
            "border-top: 1px solid #444; padding: 4px; }"
        )
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_live_clock)
        self._clock_timer.start(60000)  # refresh every minute
        self._update_live_clock()       # initial display

    def _apply_global_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1815; }
            QWidget { font-family: 'Segoe UI', 'Georgia', serif; color: #e0c090; }
            QTabWidget::pane { border: 2px solid #3E3426; background-color: #181512; border-radius: 8px; }
            QTabBar::tab { background: #28241F; color: #aaa; padding: 10px 20px; margin: 2px;
                          border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #3E3529; color: #f4d03f; font-weight: bold; }
            QDateEdit { background-color: #24201A; color: #e0c090; border: 2px solid #555;
                       padding: 8px; font-size: 14px; border-radius: 6px; }
            QDateEdit::drop-down { border-left: 1px solid #555; background: #383127; }
            QPushButton { background-color: #4A3A2A; color: #fff; font-weight: bold;
                         border: 2px solid #5C4834; border-radius: 6px; padding: 10px 16px; }
            QPushButton:hover { background-color: #634E39; border-color: #F1C40F; }
            QPushButton:pressed { background-color: #2E241A; }
            QTableWidget { background-color: #161310; color: #e0c090; gridline-color: #383023;
                          border: 1px solid #443725; }
            QTableWidget::item:selected { background-color: #4D3B1E; color: #F4D03F; }
            QHeaderView::section { background-color: #241E17; color: #f4d03f; padding: 6px;
                                  border: 1px solid #3A3020; font-weight: bold; }
            QCheckBox { color: #e0c090; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QGroupBox { border: 2px solid #444; border-radius: 8px; margin-top: 10px;
                       padding-top: 10px; color: #f4d03f; background-color: #181512; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QScrollArea { border: none; background-color: #181512; }
            QScrollArea > QWidget { background-color: #181512; }
            QScrollArea > QWidget > QWidget { background-color: #181512; }
            QScrollBar:vertical { background: #151310; width: 10px; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #4D3F2C; min-height: 25px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #F1C40F; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal { background: #151310; height: 10px; margin: 0px; border-radius: 4px; }
            QScrollBar::handle:horizontal { background: #4D3F2C; min-width: 25px; border-radius: 4px; }
            QScrollBar::handle:horizontal:hover { background: #F1C40F; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
            QSpinBox { background: #24201A; color: #e0c090; border: 1px solid #555;
                      padding: 5px; border-radius: 4px; }
        """)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Vector Logo Icon in top-left (replacing the old urn/pot)
        target_logo = LOGO_TRANSPARENT_PATH if LOGO_TRANSPARENT_PATH.exists() else LOGO_PATH
        if target_logo.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(target_logo)).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_lbl.setFixedSize(46, 46)
            logo_lbl.setStyleSheet("background: transparent; border: none;")
            header_layout.addWidget(logo_lbl)

        title = StoneLabel("MAYAN STELE", size=26, is_bold=True, color="#d4af37")
        subtitle = StoneLabel("Ultimate Calendar & Fractal Pattern Analyzer", size=14, color="#888")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.combo_correlation = QComboBox()
        self.combo_correlation.addItems(["GMT (584283)", "GMT+2 (584285)", "Spinden (489384)"])
        self.combo_correlation.setStyleSheet("QComboBox { background: #333; color: #d4af37; padding: 5px; border-radius: 4px; }")
        self.combo_correlation.currentIndexChanged.connect(self._change_correlation)
        header_layout.addWidget(self.combo_correlation)
        
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # Date input row
        input_layout = QHBoxLayout()
        input_layout.addWidget(StoneLabel("Gregorian Date:", size=12, color="#aaa"))
        
        self.date_edit = QDateEdit()
        self.date_edit.setMinimumDate(QDate(100, 1, 1))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("MMMM d, yyyy")
        self.date_edit.dateChanged.connect(self.convert_date)
        input_layout.addWidget(self.date_edit)
        
        self.btn_today = QPushButton("Today")
        self.btn_today.clicked.connect(self._go_today)
        input_layout.addWidget(self.btn_today)
        
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_prev.clicked.connect(lambda: self._adjust_date(-1))
        input_layout.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("Next ▶")
        self.btn_next.clicked.connect(lambda: self._adjust_date(1))
        input_layout.addWidget(self.btn_next)
        
        input_layout.addSpacing(15)
        self.btn_export_profile = QPushButton("📜 Exportar Perfil (SVG/MD/TXT/JSON)")
        self.btn_export_profile.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E44AD, stop:1 #4A235A);
                color: #F4D03F;
                border: 2px solid #BB8FCE;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9B59B6, stop:1 #5B2C6F);
                color: #FFF;
            }
        """)
        self.btn_export_profile.clicked.connect(self._open_export_profile_dialog)
        input_layout.addWidget(self.btn_export_profile)

        input_layout.addStretch()
        main_layout.addLayout(input_layout)

        # Long Count → Gregorian reverse conversion row
        lc_layout = QHBoxLayout()
        lc_layout.addWidget(StoneLabel("Long Count:", size=12, color="#aaa"))
        
        self.lc_spins = []
        lc_names = [("Baktun", 0, 19), ("Katun", 0, 19), ("Tun", 0, 19), ("Uinal", 0, 17), ("Kin", 0, 19)]
        for name, lo, hi in lc_names:
            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(13 if name == "Baktun" else 0)
            spin.setPrefix(f"{name}: ")
            spin.setFixedWidth(110)
            self.lc_spins.append(spin)
            lc_layout.addWidget(spin)
            if name != "Kin":
                dot = StoneLabel(".", size=16, is_bold=True, color="#888")
                dot.setFixedWidth(10)
                lc_layout.addWidget(dot)
        
        self.btn_lc_convert = QPushButton("⟶ To Gregorian")
        self.btn_lc_convert.clicked.connect(self._convert_long_count)
        lc_layout.addWidget(self.btn_lc_convert)
        
        lc_layout.addStretch()
        main_layout.addLayout(lc_layout)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Calendar View
        self._setup_calendar_tab()
        
        # Tab 2: Fractal Patterns
        self._setup_fractal_tab()

        # Tab 3: Operaciones Sagradas & Retornos
        self._setup_operations_tab()

        # Tab 4: Resonancia Biológica y Cimática
        self._setup_biological_tab()
        
        # Tab 5: Reference
        self._setup_reference_tab()

        # Footer
        footer = StoneLabel("GMT Correlation 584283 • Current Era: 13th Baktun", size=10, color="#555")
        main_layout.addWidget(footer)

    def _setup_calendar_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)
        
        # Left: Circular Calendar
        left_panel = QVBoxLayout()
        self.circular_calendar = CircularCalendarWidget()
        left_panel.addWidget(self.circular_calendar, stretch=1)
        
        legend = StoneLabel("Outer: Haab │ Middle: Tzolkin │ Inner: Lords", size=11, color="#888")
        legend.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(legend)
        
        self.btn_sync_fractal = QPushButton("🔮 Sintonizar Resonancia Fractal")
        self.btn_sync_fractal.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3A3225, stop:1 #221E18);
                color: #F1C40F;
                border: 2px solid #B7950B;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4D4230, stop:1 #2D271F);
                border-color: #F4D03F;
                color: #FFF;
            }
            QPushButton:pressed {
                background: #1A1713;
            }
        """)
        self.btn_sync_fractal.clicked.connect(self._jump_to_fractal_analysis)
        left_panel.addWidget(self.btn_sync_fractal)
        
        layout.addLayout(left_panel, 5)
        
        # Right: Info panels
        right_panel = QVBoxLayout()
        
        # Long Count Display
        self.long_count_display = LongCountDisplay()
        right_panel.addWidget(self.long_count_display)
        
        # Grid of panels
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.panel_tzolkin = StonePanel("Tzolkin", "4 Ahau", "Sacred 260-day Calendar")
        self.panel_haab = StonePanel("Haab'", "8 Cumku", "Civil 365-day Calendar")
        self.panel_calendar_round = StonePanel("Calendar Round", "4 Ahau 8 Cumku", "52-year Cycle")
        self.panel_lord = StonePanel("Lord of Night", "G9", "9-day Cycle")
        self.panel_venus = StonePanel("Venus Cycle", "Day 0", "584-day Cycle")
        self.venus_bar = VenusPhaseBar()
        self.panel_venus.layout().addWidget(self.venus_bar)
        
        self.panel_moon = StonePanel("Moon Phase", "🌕", "Lunar Cycle")
        self.panel_lunar_series = StonePanel("Lunar Series", "Glyph C: 1", "Glyphs C, A, X")
        self.panel_deep_time = StonePanel("Deep Cycles", "0 Piktun", "Macro Eras")
        
        grid.addWidget(self.panel_tzolkin, 0, 0)
        grid.addWidget(self.panel_haab, 0, 1)
        grid.addWidget(self.panel_calendar_round, 1, 0)
        grid.addWidget(self.panel_lord, 1, 1)
        grid.addWidget(self.panel_venus, 2, 0)
        grid.addWidget(self.panel_moon, 2, 1)
        grid.addWidget(self.panel_lunar_series, 3, 0)
        grid.addWidget(self.panel_deep_time, 3, 1)
        
        right_panel.addLayout(grid)
        layout.addLayout(right_panel, 6)
        
        self.tabs.addTab(tab, "📅 Calendar")

    def _setup_fractal_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controls
        controls = QHBoxLayout()
        
        controls.addWidget(StoneLabel("Start Date:", size=12, color="#aaa"))
        self.date_fractal_start = QDateEdit()
        self.date_fractal_start.setMinimumDate(QDate(100, 1, 1))
        self.date_fractal_start.setCalendarPopup(True)
        self.date_fractal_start.setDisplayFormat("yyyy-MM-dd")
        self.date_fractal_start.setDate(QDate.currentDate())
        controls.addWidget(self.date_fractal_start)
        
        controls.addWidget(StoneLabel("End Date:", size=12, color="#aaa"))
        
        self.date_fractal_end = QDateEdit()
        self.date_fractal_end.setMinimumDate(QDate(100, 1, 1))
        self.date_fractal_end.setCalendarPopup(True)
        self.date_fractal_end.setDisplayFormat("yyyy-MM-dd")
        self.date_fractal_end.setDate(QDate.currentDate().addYears(1))
        controls.addWidget(self.date_fractal_end)
        
        self.btn_analyze = QPushButton("🔮 Find Convergences")
        self.btn_analyze.clicked.connect(self._analyze_patterns)
        controls.addWidget(self.btn_analyze)
        
        self.btn_export = QPushButton("💾 Export CSV")
        self.btn_export.clicked.connect(self._export_fractal_results)
        self.btn_export.setEnabled(False)
        controls.addWidget(self.btn_export)
        
        controls.addStretch()
        
        # Natal Resonance Mode
        controls.addWidget(StoneLabel(" | Natal Resonance:", size=12, color="#aaa"))
        self.cb_natal_mode = QCheckBox("Enable")
        self.cb_natal_mode.setChecked(False)
        controls.addWidget(self.cb_natal_mode)
        
        self.date_natal = QDateEdit()
        self.date_natal.setMinimumDate(QDate(100, 1, 1))
        self.date_natal.setCalendarPopup(True)
        self.date_natal.setDisplayFormat("yyyy-MM-dd")
        # Configure to show empty text when at minimum date
        self.date_natal.setSpecialValueText(" (No Date) ")
        self.date_natal.setDate(self.date_natal.minimumDate())
        self.date_natal.setEnabled(False)
        
        # When enabled via checkbox, if it's still minimum date, set it to today's date so calendar doesn't open in 1752
        def on_natal_mode_toggled(checked):
            self.date_natal.setEnabled(checked)
            if checked and self.date_natal.date() == self.date_natal.minimumDate():
                self.date_natal.setDate(QDate.currentDate())
                
        self.cb_natal_mode.toggled.connect(on_natal_mode_toggled)
        controls.addWidget(self.date_natal)
        
        layout.addLayout(controls)
        
        # Cycle checkboxes
        cycle_group = QGroupBox("Cycles to Analyze")
        cycle_layout = QHBoxLayout(cycle_group)
        self.cycle_checks = {}
        for name in ['Tzolkin', 'Haab', 'Venus', 'Mars', '819-Day', 'Tun']:
            cb = QCheckBox(name)
            cb.setChecked(True)
            self.cycle_checks[name] = cb
            cycle_layout.addWidget(cb)
        layout.addWidget(cycle_group)
        
        # ── BARRA DE MODOS DE VISTA & RESUMEN DE COHERENCIA ──
        mode_toolbar = QHBoxLayout()
        mode_toolbar.addWidget(StoneLabel("Modo de Vista:", size=11, color="#aaa"))
        
        self.btn_view_packets = QPushButton("🌊 Ventanas Holísticas (Solitones)")
        self.btn_view_packets.setStyleSheet("background: #2E4053; color: #F1C40F; border: 1px solid #F1C40F; font-size: 11px; padding: 6px 12px;")
        self.btn_view_packets.clicked.connect(lambda: self.switch_fractal_view_mode("packets"))
        mode_toolbar.addWidget(self.btn_view_packets)
        
        self.btn_view_chrono = QPushButton("⏱ Cronológico Continuo")
        self.btn_view_chrono.setStyleSheet("background: #252220; color: #aaa; border: 1px solid #444; font-size: 11px; padding: 6px 12px;")
        self.btn_view_chrono.clicked.connect(lambda: self.switch_fractal_view_mode("chrono"))
        mode_toolbar.addWidget(self.btn_view_chrono)
        
        self.btn_view_score = QPushButton("⚡ Picos de Potencia")
        self.btn_view_score.setStyleSheet("background: #252220; color: #aaa; border: 1px solid #444; font-size: 11px; padding: 6px 12px;")
        self.btn_view_score.clicked.connect(lambda: self.switch_fractal_view_mode("score"))
        mode_toolbar.addWidget(self.btn_view_score)
        
        mode_toolbar.addSpacing(15)
        self.lbl_fractal_summary = StoneLabel("Presiona 'Find Convergences' para analizar el continuo armónico.", size=11, color="#888")
        mode_toolbar.addWidget(self.lbl_fractal_summary, stretch=1)
        layout.addLayout(mode_toolbar)
        
        # Timeline / Osciloscopio Continuo
        self.fractal_timeline = FractalTimelineWidget()
        self.fractal_timeline.date_clicked.connect(self._on_timeline_date_clicked)
        layout.addWidget(self.fractal_timeline)
        
        # Splitter: Tabla a la izquierda, Panel de Hiper-Fractales y Simetría a la derecha
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #332E27; width: 4px; }")
        
        # Results table
        self.convergence_table = QTableWidget()
        self.convergence_table.setAlternatingRowColors(True)
        self.convergence_table.cellClicked.connect(self._on_table_cell_clicked)
        splitter.addWidget(self.convergence_table)
        
        # Panel Derecho: Hiper-Enlaces Fractales y Desglose de Simetría
        harmonic_frame = QFrame()
        harmonic_frame.setStyleSheet("""
            QFrame { background: #1C1916; border: 1px solid #3A332A; border-radius: 6px; }
        """)
        harmonic_layout = QVBoxLayout(harmonic_frame)
        harmonic_layout.setContentsMargins(10, 10, 10, 10)
        harmonic_layout.setSpacing(8)
        
        h_title = StoneLabel("🔗 PUENTES HIPER-FRACTALES", size=11, is_bold=True, color="#F1C40F")
        harmonic_layout.addWidget(h_title)
        
        h_scroll = QScrollArea()
        h_scroll.setWidgetResizable(True)
        h_scroll.setStyleSheet("background: transparent; border: none;")
        self.harmonic_content = QWidget()
        self.harmonic_content_layout = QVBoxLayout(self.harmonic_content)
        self.harmonic_content_layout.setContentsMargins(0, 0, 0, 0)
        self.harmonic_content_layout.setSpacing(6)
        h_scroll.setWidget(self.harmonic_content)
        harmonic_layout.addWidget(h_scroll, stretch=1)
        
        # Caja inferior de Desglose de Ventana Seleccionada
        self.window_detail_box = QLabel("Selecciona una ventana en la tabla para ver su curva de simetría y respiración.")
        self.window_detail_box.setWordWrap(True)
        self.window_detail_box.setStyleSheet("""
            background: #141210; border: 1px solid #2B251E; border-radius: 4px;
            padding: 8px; font-size: 11px; color: #BDC3C7; line-height: 140%;
        """)
        harmonic_layout.addWidget(self.window_detail_box)
        
        splitter.addWidget(harmonic_frame)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, stretch=1)
        
        self.tabs.addTab(tab, "🔮 Fractal Patterns")

    def _setup_operations_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: #181512; color: #E0C090;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: #181512; border: none; }")
        if scroll.viewport():
            scroll.viewport().setStyleSheet("background-color: #181512;")
        content = QWidget()
        content.setStyleSheet("background-color: #181512;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(12, 12, 12, 12)

        box_qss = """
            QGroupBox {
                border: 2px solid #4D3F2C;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                color: #F4D03F;
                font-weight: bold;
                background-color: #181512;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                color: #F1C40F;
                font-size: 13px;
            }
        """

        # ── SECCIÓN 1: NÚMEROS DE DISTANCIA (DISTANCE NUMBERS) ──
        dn_group = QGroupBox("🏛️ 1. Calculadora de Número de Distancia (Distance Numbers / Cuentas Secundarias)")
        dn_group.setStyleSheet(box_qss)
        dn_layout = QVBoxLayout(dn_group)
        dn_layout.setSpacing(12)
        dn_layout.setContentsMargins(14, 16, 14, 14)

        dn_desc = (
            "En la epigrafía maya clásica (ej. Palenque, Quiriguá, Yaxchilán), los Números de Distancia unen fechas clave "
            "sumando o restando intervalos de K'ines (1d), Uinales (20d), Tunes (360d) y Katunes (7,200d)."
        )
        lbl_dn_desc = StoneLabel(dn_desc, size=11, color="#BDC3C7")
        lbl_dn_desc.setWordWrap(True)
        dn_layout.addWidget(lbl_dn_desc)

        # Row 1: Fecha Base + Modo
        dn_top_row = QHBoxLayout()
        dn_top_row.setSpacing(10)
        dn_top_row.addWidget(StoneLabel("Fecha Base:", size=11, is_bold=True, color="#E0C090"))
        
        self.dn_base_date = QDateEdit()
        self.dn_base_date.setCalendarPopup(True)
        self.dn_base_date.setDisplayFormat("yyyy-MM-dd")
        self.dn_base_date.setDate(QDate.currentDate())
        self.dn_base_date.setStyleSheet("QDateEdit { background: #24201A; color: #F4D03F; border: 1px solid #5A4A32; padding: 5px 8px; border-radius: 4px; font-weight: bold; }")
        dn_top_row.addWidget(self.dn_base_date)

        btn_sync_dn = QPushButton("🔄 Usar Fecha Activa")
        btn_sync_dn.setStyleSheet("""
            QPushButton {
                background: #2E261D; color: #E0C090; border: 1px solid #63523B;
                padding: 5px 12px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background: #423628; color: #F1C40F; border-color: #F1C40F; }
        """)
        btn_sync_dn.clicked.connect(lambda: self.dn_base_date.setDate(self.date_edit.date()))
        dn_top_row.addWidget(btn_sync_dn)

        dn_top_row.addSpacing(16)
        self.dn_dir_forward = QRadioButton("➕ Hacia el Futuro")
        self.dn_dir_forward.setChecked(True)
        self.dn_dir_forward.setStyleSheet("QRadioButton { color: #52BE80; font-weight: bold; spacing: 6px; }")
        self.dn_dir_backward = QRadioButton("➖ Hacia el Pasado")
        self.dn_dir_backward.setStyleSheet("QRadioButton { color: #E74C3C; font-weight: bold; spacing: 6px; }")
        dn_top_row.addWidget(self.dn_dir_forward)
        dn_top_row.addWidget(self.dn_dir_backward)
        dn_top_row.addStretch()
        dn_layout.addLayout(dn_top_row)

        # Row 2: Jerarquía de Unidades Mayas
        spins_frame = QFrame()
        spins_frame.setStyleSheet("background: #14110E; border: 1px solid #382F22; border-radius: 6px; padding: 8px;")
        spins_layout = QHBoxLayout(spins_frame)
        spins_layout.setSpacing(10)
        spins_layout.setContentsMargins(8, 6, 8, 6)

        spin_style = "QSpinBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px; border-radius: 4px; font-weight: bold; min-width: 90px; }"
        self.dn_spin_baktun = QSpinBox(); self.dn_spin_baktun.setRange(0, 999); self.dn_spin_baktun.setPrefix("Baktun: "); self.dn_spin_baktun.setStyleSheet(spin_style)
        self.dn_spin_katun = QSpinBox(); self.dn_spin_katun.setRange(0, 999); self.dn_spin_katun.setPrefix("Katun: "); self.dn_spin_katun.setStyleSheet(spin_style)
        self.dn_spin_tun = QSpinBox(); self.dn_spin_tun.setRange(0, 999); self.dn_spin_tun.setPrefix("Tun: "); self.dn_spin_tun.setStyleSheet(spin_style)
        self.dn_spin_uinal = QSpinBox(); self.dn_spin_uinal.setRange(0, 17); self.dn_spin_uinal.setPrefix("Uinal: "); self.dn_spin_uinal.setStyleSheet(spin_style)
        self.dn_spin_kin = QSpinBox(); self.dn_spin_kin.setRange(0, 19); self.dn_spin_kin.setPrefix("Kin: "); self.dn_spin_kin.setStyleSheet(spin_style)
        self.dn_spin_days = QSpinBox(); self.dn_spin_days.setRange(0, 99999999); self.dn_spin_days.setPrefix("Días: "); self.dn_spin_days.setStyleSheet(spin_style)

        def _update_dn_from_parts():
            b = self.dn_spin_baktun.value()
            k = self.dn_spin_katun.value()
            t = self.dn_spin_tun.value()
            u = self.dn_spin_uinal.value()
            kin = self.dn_spin_kin.value()
            total = b * 144000 + k * 7200 + t * 360 + u * 20 + kin
            self.dn_spin_days.blockSignals(True)
            self.dn_spin_days.setValue(total)
            self.dn_spin_days.blockSignals(False)

        def _update_dn_from_days():
            tot = self.dn_spin_days.value()
            b = tot // 144000
            rem = tot % 144000
            k = rem // 7200
            rem %= 7200
            t = rem // 360
            rem %= 360
            u = rem // 20
            kin = rem % 20
            self.dn_spin_baktun.blockSignals(True)
            self.dn_spin_katun.blockSignals(True)
            self.dn_spin_tun.blockSignals(True)
            self.dn_spin_uinal.blockSignals(True)
            self.dn_spin_kin.blockSignals(True)
            self.dn_spin_baktun.setValue(b)
            self.dn_spin_katun.setValue(k)
            self.dn_spin_tun.setValue(t)
            self.dn_spin_uinal.setValue(u)
            self.dn_spin_kin.setValue(kin)
            self.dn_spin_baktun.blockSignals(False)
            self.dn_spin_katun.blockSignals(False)
            self.dn_spin_tun.blockSignals(False)
            self.dn_spin_uinal.blockSignals(False)
            self.dn_spin_kin.blockSignals(False)

        for s in (self.dn_spin_baktun, self.dn_spin_katun, self.dn_spin_tun, self.dn_spin_uinal, self.dn_spin_kin):
            s.valueChanged.connect(_update_dn_from_parts)
            spins_layout.addWidget(s)
        self.dn_spin_days.valueChanged.connect(_update_dn_from_days)
        spins_layout.addWidget(self.dn_spin_days)

        self.btn_calc_dn = QPushButton("⚡ Calcular Salto Epigráfico")
        self.btn_calc_dn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E8449, stop:1 #117864);
                color: #FFF; font-weight: bold; border: 1px solid #52BE80; border-radius: 5px;
                padding: 7px 16px; font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27AE60, stop:1 #16A085);
                border-color: #F1C40F; color: #F1C40F;
            }
        """)
        self.btn_calc_dn.clicked.connect(self._exec_distance_number)
        spins_layout.addWidget(self.btn_calc_dn)
        dn_layout.addWidget(spins_frame)

        # Result Integrated Card
        dn_card = QFrame()
        dn_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #25201A, stop:1 #181512);
                border: 1px solid #4D3F2C;
                border-left: 4px solid #F1C40F;
                border-radius: 6px;
            }
        """)
        dn_card_layout = QHBoxLayout(dn_card)
        dn_card_layout.setContentsMargins(14, 10, 14, 10)
        dn_card_layout.setSpacing(15)

        self.dn_result_box = QLabel("Configura un Número de Distancia y presiona 'Calcular Salto Epigráfico' para proyectar la fecha resultante.")
        self.dn_result_box.setStyleSheet("color: #E0C090; font-size: 12px; background: transparent; border: none;")
        self.dn_result_box.setWordWrap(True)
        dn_card_layout.addWidget(self.dn_result_box, stretch=1)

        self.btn_goto_dn = QPushButton("📍 Sincronizar en Estela")
        self.btn_goto_dn.setEnabled(False)
        self.btn_goto_dn.setCursor(Qt.PointingHandCursor)
        self.btn_goto_dn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9A7D0A, stop:1 #6E5606);
                color: #FFF; border: 1px solid #F4D03F; border-radius: 5px;
                padding: 9px 18px; font-weight: bold; font-size: 11px; min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #B7950B, stop:1 #7D6608);
                border-color: #FFF; color: #F1C40F;
            }
            QPushButton:disabled {
                background: #25211B; color: #665D4F; border: 1px solid #3D3528;
            }
        """)
        self.btn_goto_dn.clicked.connect(self._jump_from_dn_result)
        dn_card_layout.addWidget(self.btn_goto_dn)
        dn_layout.addWidget(dn_card)
        content_layout.addWidget(dn_group)

        # ── SECCIÓN 2: BUSCADOR DE RETORNOS SAGRADOS (CRT SOLVER) ──
        ret_group = QGroupBox("🔍 2. Buscador de Retornos Sagrados y Conjunciones (Teorema del Resto Chino / CRT)")
        ret_group.setStyleSheet(box_qss)
        ret_layout = QVBoxLayout(ret_group)
        ret_layout.setSpacing(12)
        ret_layout.setContentsMargins(14, 16, 14, 14)

        ret_desc = (
            "Permite resolver intersecciones sagradas: ¿cuándo volverá a coincidir un determinado signo Tzolk'in "
            "con un mes/día Haab', una fase de Venus, o un cuadrante del ciclo de 819 días?"
        )
        lbl_ret_desc = StoneLabel(ret_desc, size=11, color="#BDC3C7")
        lbl_ret_desc.setWordWrap(True)
        ret_layout.addWidget(lbl_ret_desc)

        # Presets Bar
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(StoneLabel("Preajustes Sagrados:", size=11, is_bold=True, color="#BB8FCE"))
        self.ret_preset_combo = QComboBox()
        self.ret_preset_combo.addItems([
            "⚙️ (Seleccionar Preajuste Sagrado o Configurar Manualmente...)",
            "🏛️ 4 Ahau 8 Cumku (Creación Cósmica / Fin 13 Baktún)",
            "⭐ 4 Ahau + Venus en Conjunción Inferior",
            "🔥 4 Ahau + K'awiil Cuadrante Este (Rojo)",
            "👑 4 Ahau + Señor de la Noche G9",
            "🌱 1 Caban 0 Pop (Año Nuevo Maya)",
            "🌌 Venus Estrella Matutina + Haab 0 Pop"
        ])
        self.ret_preset_combo.setStyleSheet("QComboBox { background: #261E2E; color: #D7BDE2; border: 1px solid #6C3483; padding: 5px 10px; border-radius: 4px; font-weight: bold; }")
        self.ret_preset_combo.currentIndexChanged.connect(self._on_ret_preset_changed)
        preset_layout.addWidget(self.ret_preset_combo, stretch=1)
        ret_layout.addLayout(preset_layout)

        # Custom Controls Form
        ret_form_frame = QFrame()
        ret_form_frame.setStyleSheet("background: #14110E; border: 1px solid #382F22; border-radius: 6px; padding: 8px;")
        ret_form = QHBoxLayout(ret_form_frame)
        ret_form.setSpacing(8)
        ret_form.setContentsMargins(8, 6, 8, 6)

        ret_form.addWidget(StoneLabel("Ciclo 1:", size=11, color="#E0C090"))
        self.ret_c1_combo = QComboBox()
        self.ret_c1_combo.addItems(["Tzolkin", "Haab", "Venus", "Tun", "819-Day", "LordOfNight"])
        self.ret_c1_combo.setStyleSheet("QComboBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px; border-radius: 4px; font-weight: bold; }")
        ret_form.addWidget(self.ret_c1_combo)

        ret_form.addWidget(StoneLabel("Objetivo 1:", size=11, color="#E0C090"))
        self.ret_c1_val = QSpinBox(); self.ret_c1_val.setRange(0, 819); self.ret_c1_val.setValue(60) # 60 = 4 Ahau
        self.ret_c1_val.setStyleSheet("QSpinBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px; border-radius: 4px; font-weight: bold; min-width: 65px; }")
        ret_form.addWidget(self.ret_c1_val)

        self.lbl_ret_c1_info = QLabel("✦ 4 Ahau")
        self.lbl_ret_c1_info.setStyleSheet("color: #F1C40F; background: #262118; border: 1px solid #5A4A32; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        ret_form.addWidget(self.lbl_ret_c1_info)

        ret_form.addSpacing(10)
        ret_form.addWidget(StoneLabel("Ciclo 2:", size=11, color="#E0C090"))
        self.ret_c2_combo = QComboBox()
        self.ret_c2_combo.addItems(["Haab", "Tzolkin", "Venus", "Tun", "819-Day", "LordOfNight"])
        self.ret_c2_combo.setCurrentIndex(0)
        self.ret_c2_combo.setStyleSheet("QComboBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px; border-radius: 4px; font-weight: bold; }")
        ret_form.addWidget(self.ret_c2_combo)

        ret_form.addWidget(StoneLabel("Objetivo 2:", size=11, color="#E0C090"))
        self.ret_c2_val = QSpinBox(); self.ret_c2_val.setRange(0, 819); self.ret_c2_val.setValue(348) # 348 = 8 Cumku
        self.ret_c2_val.setStyleSheet("QSpinBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px; border-radius: 4px; font-weight: bold; min-width: 65px; }")
        ret_form.addWidget(self.ret_c2_val)

        self.lbl_ret_c2_info = QLabel("✦ 8 Cumku")
        self.lbl_ret_c2_info.setStyleSheet("color: #E67E22; background: #262118; border: 1px solid #5A4A32; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        ret_form.addWidget(self.lbl_ret_c2_info)

        self.ret_c1_combo.currentIndexChanged.connect(self._update_ret_labels)
        self.ret_c1_val.valueChanged.connect(self._update_ret_labels)
        self.ret_c2_combo.currentIndexChanged.connect(self._update_ret_labels)
        self.ret_c2_val.valueChanged.connect(self._update_ret_labels)

        self.btn_calc_ret = QPushButton("🔮 Encontrar Conjunción")
        self.btn_calc_ret.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C3483, stop:1 #4A235A);
                color: #FFF; font-weight: bold; border: 1px solid #BB8FCE; border-radius: 5px;
                padding: 7px 16px; font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E44AD, stop:1 #5B2C6F);
                border-color: #F4D03F; color: #F4D03F;
            }
        """)
        self.btn_calc_ret.clicked.connect(self._exec_cycle_overlap)
        ret_form.addWidget(self.btn_calc_ret)
        ret_layout.addWidget(ret_form_frame)

        # Result Integrated Card
        ret_card = QFrame()
        ret_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #25201A, stop:1 #181512);
                border: 1px solid #4D3F2C;
                border-left: 4px solid #BB8FCE;
                border-radius: 6px;
            }
        """)
        ret_card_layout = QHBoxLayout(ret_card)
        ret_card_layout.setContentsMargins(14, 10, 14, 10)
        ret_card_layout.setSpacing(15)

        self.ret_result_box = QLabel("Configura los ciclos y presiona 'Encontrar Conjunción'. (Ej. Tzolk'in 60 [4 Ahau] + Haab 348 [8 Cumku] halla el fin de era 4 Ahau 8 Cumku).")
        self.ret_result_box.setStyleSheet("color: #E0C090; font-size: 12px; background: transparent; border: none;")
        self.ret_result_box.setWordWrap(True)
        ret_card_layout.addWidget(self.ret_result_box, stretch=1)

        self.btn_goto_ret = QPushButton("📍 Sincronizar en Estela")
        self.btn_goto_ret.setEnabled(False)
        self.btn_goto_ret.setCursor(Qt.PointingHandCursor)
        self.btn_goto_ret.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6C3483, stop:1 #4A235A);
                color: #FFF; border: 1px solid #BB8FCE; border-radius: 5px;
                padding: 9px 18px; font-weight: bold; font-size: 11px; min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E44AD, stop:1 #5B2C6F);
                border-color: #FFF; color: #F4D03F;
            }
            QPushButton:disabled {
                background: #25211B; color: #665D4F; border: 1px solid #3D3528;
            }
        """)
        self.btn_goto_ret.clicked.connect(self._jump_from_ret_result)
        ret_card_layout.addWidget(self.btn_goto_ret)
        ret_layout.addWidget(ret_card)
        content_layout.addWidget(ret_group)

        # ── SECCIÓN 3: PROYECTOR DE PATRONES ARMÓNICOS ──
        proj_group = QGroupBox("🚀 3. Proyector de Patrones y Líneas de Tiempo Armónicas")
        proj_group.setStyleSheet(box_qss)
        proj_layout = QVBoxLayout(proj_group)
        proj_layout.setSpacing(12)
        proj_layout.setContentsMargins(14, 16, 14, 14)

        proj_desc = (
            "Proyecta pulsos armónicos en el tiempo a través de múltiplos de Katunes (7,200d), Tunes (360d), "
            "Ciclos de Venus (584d) o ventanas de solitón, generando una serie cronológica completa."
        )
        lbl_proj_desc = StoneLabel(proj_desc, size=11, color="#BDC3C7")
        lbl_proj_desc.setWordWrap(True)
        proj_layout.addWidget(lbl_proj_desc)

        proj_form_frame = QFrame()
        proj_form_frame.setStyleSheet("background: #14110E; border: 1px solid #382F22; border-radius: 6px; padding: 8px;")
        proj_form = QHBoxLayout(proj_form_frame)
        proj_form.setSpacing(10)
        proj_form.setContentsMargins(8, 6, 8, 6)

        proj_form.addWidget(StoneLabel("Intervalo de Proyección:", size=11, is_bold=True, color="#E0C090"))
        self.proj_interval_combo = QComboBox()
        self.proj_interval_combo.addItems([
            "1 Katún (7,200 días • ~19.7 años)",
            "1 Tún (360 días • ~0.98 años)",
            "1 Rueda Calendárica (18,980 días • 52 años)",
            "1 Ciclo de Venus (584 días • ~1.6 años)",
            "1 Ciclo Tzolk'in (260 días)",
            "1 Ciclo K'awiil (819 días)",
            "Ventana Solitón Coherente (52 días)",
            "Personalizado..."
        ])
        self.proj_interval_combo.setStyleSheet("QComboBox { background: #201C16; color: #F4D03F; border: 1px solid #4D3F2C; padding: 5px 10px; border-radius: 4px; font-weight: bold; }")
        proj_form.addWidget(self.proj_interval_combo, stretch=1)

        self.proj_custom_days = QSpinBox()
        self.proj_custom_days.setRange(1, 999999)
        self.proj_custom_days.setValue(7200)
        self.proj_custom_days.setPrefix("Días: ")
        self.proj_custom_days.setStyleSheet(spin_style)
        self.proj_custom_days.setVisible(False)
        proj_form.addWidget(self.proj_custom_days)

        def _on_proj_combo_changed(idx):
            self.proj_custom_days.setVisible(idx == 7)
        self.proj_interval_combo.currentIndexChanged.connect(_on_proj_combo_changed)

        proj_form.addWidget(StoneLabel("Saltos:", size=11, color="#E0C090"))
        self.proj_count_spin = QSpinBox(); self.proj_count_spin.setRange(1, 50); self.proj_count_spin.setValue(10)
        self.proj_count_spin.setStyleSheet(spin_style)
        proj_form.addWidget(self.proj_count_spin)

        self.btn_exec_proj = QPushButton("🌟 Proyectar Serie")
        self.btn_exec_proj.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2E4053, stop:1 #1B2631);
                color: #5DADE2; border: 1px solid #5DADE2; border-radius: 5px;
                padding: 7px 18px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34495E, stop:1 #212F3D);
                border-color: #F1C40F; color: #F1C40F;
            }
        """)
        self.btn_exec_proj.clicked.connect(self._exec_pattern_projection)
        proj_form.addWidget(self.btn_exec_proj)
        proj_layout.addWidget(proj_form_frame)

        # Projections Table
        self.proj_table = QTableWidget()
        self.proj_table.setMinimumHeight(220)
        self.proj_table.setStyleSheet("""
            QTableWidget {
                background-color: #15120F; color: #E0C090; border: 1px solid #443725;
                gridline-color: #2D251A; font-size: 11px; selection-background-color: #4D3B1E;
            }
            QHeaderView::section {
                background-color: #241E17; color: #F1C40F; border: 1px solid #3A3020;
                padding: 6px; font-weight: bold;
            }
        """)
        self.proj_table.cellClicked.connect(self._on_proj_cell_clicked)
        proj_layout.addWidget(self.proj_table)
        content_layout.addWidget(proj_group)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "⏳ Operaciones & Retornos")

    def _get_cycle_target_desc(self, c_name, val):
        try:
            if c_name == "Tzolkin":
                val = val % 260
                tone = (val + 3) % 13 + 1
                sign_idx = val % 20
                sign_name = self.converter.TZOLKIN_DATA[sign_idx][0] if sign_idx < len(self.converter.TZOLKIN_DATA) else "Ahau"
                return f"✦ {tone} {sign_name}"
            elif c_name == "Haab":
                val = val % 365
                month_idx = min(val // 20, 18)
                day_in_month = val % 20 if month_idx < 18 else val - 360
                m_name = self.converter.HAAB_DATA[month_idx][0] if month_idx < len(self.converter.HAAB_DATA) else "Pop"
                return f"✦ {day_in_month} {m_name}"
            elif c_name == "LordOfNight":
                val = val % 9
                return f"✦ G{val + 1} ({self.converter.LORDS_OF_NIGHT[val][1]})"
            elif c_name == "Venus":
                val = val % 584
                if val < 8: return f"✦ Conjunción Inferior (d{val})"
                elif val < 244: return f"✦ Estrella Matutina (d{val})"
                elif val < 334: return f"✦ Conjunción Superior (d{val})"
                else: return f"✦ Estrella Vespertina (d{val})"
            elif c_name == "819-Day":
                val = val % 819
                q = (val // (819 // 4)) % 4
                dirs = ["Este (Rojo)", "Norte (Blanco)", "Oeste (Negro)", "Sur (Amarillo)"]
                return f"✦ {dirs[q]}"
            return f"✦ Posición {val}"
        except Exception:
            return f"✦ Pos {val}"

    def _update_ret_labels(self):
        c1 = self.ret_c1_combo.currentText()
        v1 = self.ret_c1_val.value()
        self.lbl_ret_c1_info.setText(self._get_cycle_target_desc(c1, v1))

        c2 = self.ret_c2_combo.currentText()
        v2 = self.ret_c2_val.value()
        self.lbl_ret_c2_info.setText(self._get_cycle_target_desc(c2, v2))

    def _on_ret_preset_changed(self, idx):
        presets = {
            1: ("Tzolkin", 0, "Haab", 348),         # 4 Ahau 8 Cumku (Era / Rueda Calendárica)
            2: ("Tzolkin", 0, "Venus", 0),          # 4 Ahau + Venus Inf. Conj.
            3: ("Tzolkin", 0, "819-Day", 0),        # 4 Ahau + K'awiil Este
            4: ("Tzolkin", 0, "LordOfNight", 8),    # 4 Ahau + G9
            5: ("Tzolkin", 257, "Haab", 0),         # 1 Caban 0 Pop
            6: ("Venus", 100, "Haab", 0),           # Venus Matutina + 0 Pop
        }
        if idx in presets:
            c1, v1, c2, v2 = presets[idx]
            self.ret_c1_combo.setCurrentText(c1)
            self.ret_c1_val.setValue(v1)
            self.ret_c2_combo.setCurrentText(c2)
            self.ret_c2_val.setValue(v2)
            self._update_ret_labels()

    def _exec_distance_number(self):
        b_date = self.dn_base_date.date()
        base_jdn = self.converter._gregorian_to_jdn(b_date.year(), b_date.month(), b_date.day())
        
        days_val = self.dn_spin_days.value()
        is_forward = self.dn_dir_forward.isChecked()
        signed_days = days_val if is_forward else -days_val
        
        dest_y, dest_m, dest_d = self.converter.add_distance_number(base_jdn, signed_days)
        dest_data = self.converter.get_full_date(dest_y, dest_m, dest_d)
        
        self._last_dn_dest_date = QDate(dest_y, dest_m, dest_d)
        self.btn_goto_dn.setEnabled(True)
        
        dir_sign = "+" if is_forward else "-"
        res_text = (
            f"<b>📍 FECHA DESTINO: <span style='color:#F4D03F; font-size:13px;'>{dest_d:02d}/{dest_m:02d}/{dest_y:04d}</span> "
            f"({dir_sign}{days_val:,} días)</b><br>"
            f"• <b>Cuenta Larga:</b> <span style='color:#F1C40F'>{dest_data['long_count']}</span> • "
            f"<b>Tzolk'in:</b> {dest_data['tzolkin_glyph']} {dest_data['tzolkin']} ({dest_data['tzolkin_meaning']})<br>"
            f"• <b>Haab':</b> {dest_data['haab']} ({dest_data['haab_meaning']}) • "
            f"<b>Rueda Calendárica:</b> {dest_data['calendar_round']} • <b>Señor:</b> {dest_data['lord']}"
        )
        self.dn_result_box.setText(res_text)

    def _jump_from_dn_result(self):
        if hasattr(self, '_last_dn_dest_date'):
            self.date_edit.setDate(self._last_dn_dest_date)
            self.tabs.setCurrentIndex(0)

    def _exec_cycle_overlap(self):
        cur_d = self.date_edit.date()
        base_jdn = self.converter._gregorian_to_jdn(cur_d.year(), cur_d.month(), cur_d.day())
        start_days = base_jdn - self.converter.correlation_jdn
        
        c1 = self.ret_c1_combo.currentText()
        t1 = self.ret_c1_val.value()
        c2 = self.ret_c2_combo.currentText()
        t2 = self.ret_c2_val.value()
        
        match_days = self.analyzer.find_cycle_overlap(start_days + 1, c1, t1, c2, t2, max_steps=5000)
        if match_days is not None:
            dest_jdn = self.converter.correlation_jdn + match_days
            ry, rm, rd = self.converter._jdn_to_gregorian(dest_jdn)
            r_data = self.converter.get_full_date(ry, rm, rd)
            self._last_ret_date = QDate(ry, rm, rd)
            self.btn_goto_ret.setEnabled(True)
            
            delta = match_days - start_days
            self.ret_result_box.setText(
                f"<b>⭐ CONJUNCIÓN ENCONTRADA: <span style='color:#F4D03F; font-size:13px;'>{rd:02d}/{rm:02d}/{ry:04d}</span> "
                f"(+{delta:,} días desde hoy)</b><br>"
                f"• <b>Cuenta Larga:</b> <span style='color:#F1C40F'>{r_data['long_count']}</span> • "
                f"<b>Rueda Calendárica:</b> {r_data['calendar_round']} • <b>Señor:</b> {r_data['lord']}<br>"
                f"• <b>Fase Venus:</b> {r_data['venus_phase']} • <b>Luna:</b> {r_data['moon_phase']}"
            )
        else:
            self.ret_result_box.setText("❌ No se encontró coincidencia en los próximos 5,000 ciclos analizados.")
            self.btn_goto_ret.setEnabled(False)

    def _jump_from_ret_result(self):
        if hasattr(self, '_last_ret_date'):
            self.date_edit.setDate(self._last_ret_date)
            self.tabs.setCurrentIndex(0)

    def _exec_pattern_projection(self):
        cur_d = self.date_edit.date()
        base_dt = datetime(cur_d.year(), cur_d.month(), cur_d.day())
        
        idx = self.proj_interval_combo.currentIndex()
        preset_days = [7200, 360, 18980, 584, 260, 819, 52]
        interval = preset_days[idx] if idx < len(preset_days) else self.proj_custom_days.value()
        
        count = self.proj_count_spin.value()
        projections = self.analyzer.project_pattern(base_dt, interval, count)
        
        headers = ["Paso", "Fecha Gregoriana", "Días Acumulados", "Cuenta Larga", "Tzolk'in", "Haab'", "Señor", "Venus"]
        self.proj_table.clear()
        self.proj_table.setColumnCount(len(headers))
        self.proj_table.setHorizontalHeaderLabels(headers)
        self.proj_table.setRowCount(len(projections))
        
        self._proj_dates = []
        for row, p in enumerate(projections):
            dt = p["date"]
            self._proj_dates.append(QDate(dt.year, dt.month, dt.day))
            d_data = self.converter.get_full_date(dt.year, dt.month, dt.day)
            
            self.proj_table.setItem(row, 0, QTableWidgetItem(f"+{row + 1}"))
            self.proj_table.setItem(row, 1, QTableWidgetItem(dt.strftime("%Y-%m-%d")))
            self.proj_table.setItem(row, 2, QTableWidgetItem(f"+{(row + 1) * interval:,}d"))
            self.proj_table.setItem(row, 3, QTableWidgetItem(d_data["long_count"]))
            self.proj_table.setItem(row, 4, QTableWidgetItem(d_data["tzolkin"]))
            self.proj_table.setItem(row, 5, QTableWidgetItem(d_data["haab"]))
            self.proj_table.setItem(row, 6, QTableWidgetItem(d_data["lord"]))
            self.proj_table.setItem(row, 7, QTableWidgetItem(d_data["venus_phase"]))
            
        self.proj_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.proj_table.horizontalHeader().setStretchLastSection(True)

    def _on_proj_cell_clicked(self, row, col):
        if hasattr(self, '_proj_dates') and row < len(self._proj_dates):
            target_date = self._proj_dates[row]
            self.date_edit.setDate(target_date)
            self.tabs.setCurrentIndex(0)

    def _setup_biological_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: #181512; color: #E0C090;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: #181512; border: none; }")
        if scroll.viewport():
            scroll.viewport().setStyleSheet("background-color: #181512;")
        content = QWidget()
        content.setStyleSheet("background-color: #181512;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(14, 14, 14, 14)

        # Header Info Banner
        header_box = QGroupBox("🧬 Matriz de Resonancia Biológica y Cimática (Tzolk'in ➔ Aminoácidos)")
        header_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #27AE60;
                border-left: 6px solid #2ECC71;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                color: #2ECC71;
                font-weight: bold;
                background-color: #151A16;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                color: #58D68D;
                font-size: 13px;
            }
        """)
        h_box_layout = QVBoxLayout(header_box)
        h_box_layout.setContentsMargins(14, 12, 14, 14)
        bio_intro = (
            "Cada uno de los 20 sellos solares del Tzolk'in maya corresponde de forma isomorfa a uno de los 20 aminoácidos "
            "canónicos esenciales del código genético universal, vibrando en frecuencias vocálicas Kototama y matrices geométricas de enlace."
        )
        lbl_intro = StoneLabel(bio_intro, size=11, color="#BDC3C7")
        lbl_intro.setWordWrap(True)
        h_box_layout.addWidget(lbl_intro)
        content_layout.addWidget(header_box)

        # Bio details cards with custom chromatic accents
        grid = QGridLayout()
        grid.setSpacing(14)

        self.bio_card_seal = StonePanel("Sello Tzolk'in Activo", "4 Ahau", "Sol / Señor Solar")
        self.bio_card_seal.setStyleSheet("""
            StonePanel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F2E22, stop:1 #131E15);
                border: 2px solid #27AE60; border-top-color: #52BE80; border-radius: 8px;
            }
        """)
        self.bio_card_amino = StonePanel("Aminoácido Resonante", "Triptófano (Trp)", "Fórmula: C11H12N2O2")
        self.bio_card_amino.setStyleSheet("""
            StonePanel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #332B1A, stop:1 #1F190D);
                border: 2px solid #D4AC0D; border-top-color: #F4D03F; border-radius: 8px;
            }
        """)
        self.bio_card_group = StonePanel("Grupo Bioquímico", "Aromático Mayor", "Sistema Indol Bicíclico")
        self.bio_card_group.setStyleSheet("""
            StonePanel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2C1F33, stop:1 #1A1220);
                border: 2px solid #8E44AD; border-top-color: #BB8FCE; border-radius: 8px;
            }
        """)
        self.bio_card_kototama = StonePanel("Kototama & Mantra", "I ➔ A ➔ O ➔ U ➔ E", "Bīja Mantra: AUM")
        self.bio_card_kototama.setStyleSheet("""
            StonePanel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #162B2B, stop:1 #0D1C1C);
                border: 2px solid #16A085; border-top-color: #48C9B0; border-radius: 8px;
            }
        """)

        grid.addWidget(self.bio_card_seal, 0, 0)
        grid.addWidget(self.bio_card_amino, 0, 1)
        grid.addWidget(self.bio_card_group, 1, 0)
        grid.addWidget(self.bio_card_kototama, 1, 1)
        content_layout.addLayout(grid)

        # Codons and detailed instruction
        instr_group = QGroupBox("📜 Instrucción Alquímica & Codones de ARN")
        instr_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #5A4A32;
                border-left: 6px solid #E67E22;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                color: #F39C12;
                font-weight: bold;
                background-color: #171410;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                color: #F39C12;
                font-size: 13px;
            }
        """)
        instr_layout = QVBoxLayout(instr_group)
        instr_layout.setContentsMargins(14, 14, 14, 14)
        instr_layout.setSpacing(10)

        self.lbl_bio_instruction = QLabel("")
        self.lbl_bio_instruction.setStyleSheet("color: #F1C40F; font-size: 12px; font-weight: bold; line-height: 1.4;")
        self.lbl_bio_instruction.setWordWrap(True)
        instr_layout.addWidget(self.lbl_bio_instruction)

        self.lbl_bio_codons = QLabel("")
        self.lbl_bio_codons.setStyleSheet("color: #E0C090; font-size: 11px;")
        self.lbl_bio_codons.setWordWrap(True)
        instr_layout.addWidget(self.lbl_bio_codons)
        content_layout.addWidget(instr_group)

        # Copy button
        self.btn_copy_bio = QPushButton("📋 Copiar Perfil Bio-Vibracional al Portapapeles")
        self.btn_copy_bio.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F618D, stop:1 #154360);
                color: #F4D03F; border: 1px solid #5DADE2; border-radius: 6px;
                padding: 10px 18px; font-weight: bold; font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2980B9, stop:1 #1B4F72);
                color: #FFF; border-color: #F4D03F;
            }
        """)
        self.btn_copy_bio.clicked.connect(self._copy_bio_profile)
        content_layout.addWidget(self.btn_copy_bio)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "🧬 Resonancia Biológica")

    def _update_biological_tab(self, data):
        if not hasattr(self, 'bio_card_seal'):
            return
        tz_name = data.get("tzolkin_name", "")
        tz_full = f"{data.get('tzolkin_glyph', '')} {data.get('tzolkin', '')}"
        self.bio_card_seal.update_data(tz_full, data.get("tzolkin_meaning", ""))
        
        bio = MayanProfileExporter._extract_bio_resonance(tz_name) if MayanProfileExporter else None
        if bio:
            self.bio_card_amino.update_data(bio.get("amino", ""), f"Fórmula: {bio.get('formula', '')}")
            self.bio_card_group.update_data(bio.get("group", ""), "Clasificación estructural")
            self.bio_card_kototama.update_data(bio.get("kototama", ""), f"Bīja Mantra: {bio.get('bija', '')}")
            self.lbl_bio_instruction.setText(f"✦ Instrucción: {bio.get('instruction', '')}")
            
            codon_cards = []
            for c in bio.get("codons", []):
                codon_cards.append(
                    f"<div style='margin-bottom: 6px;'>"
                    f"<span style='background:#2C3E50; color:#F4D03F; border:1px solid #5DADE2; padding:2px 8px; border-radius:4px; font-family:Consolas, monospace; font-weight:bold;'>Triplete {c['triplet']}</span> "
                    f"<span style='color:#ECF0F1;'>— {c.get('action', '')}</span> "
                    f"<span style='color:#85929E; font-size:10px;'>[Kototama: {c.get('kototama', '')}]</span>"
                    f"</div>"
                )
            self.lbl_bio_codons.setText("".join(codon_cards))
        else:
            self.bio_card_amino.update_data("Información no disponible", "")
            self.lbl_bio_instruction.setText("")
            self.lbl_bio_codons.setText("")

    def _copy_bio_profile(self):
        tz_name = self.panel_tzolkin.lbl_main.text()
        text = f"Perfil Bio-Vibracional Maya: {tz_name}\nAminoácido: {self.bio_card_amino.lbl_main.text()}\nGrupo: {self.bio_card_group.lbl_main.text()}\nKototama & Mantra: {self.bio_card_kototama.lbl_main.text()}\n{self.lbl_bio_instruction.text()}\n{self.lbl_bio_codons.text()}"
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copiado", "Perfil bio-vibracional copiado al portapapeles.")

    def _open_export_profile_dialog(self):
        if not hasattr(self, '_current_mayan_data') or not self._current_mayan_data:
            gregorian_date = self.date_edit.date()
            self._current_mayan_data = self.converter.get_full_date(
                gregorian_date.year(), gregorian_date.month(), gregorian_date.day()
            )
        gregorian_str = self.date_edit.date().toString("MMMM d, yyyy")
        corr_str = self.combo_correlation.currentText()
        dialog = MayanProfileExportDialog(self, self._current_mayan_data, gregorian_str, corr_str)
        dialog.exec()

    def _setup_reference_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: #181512; color: #E0C090;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: #181512; border: none; }")
        if scroll.viewport():
            scroll.viewport().setStyleSheet("background-color: #181512;")
        content = QWidget()
        content.setStyleSheet("background-color: #181512;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(15, 15, 15, 15)

        # Banner del Emblema Maestro (Logo Cuántico y Calendario Maya)
        ref_logo = LOGO_TRANSPARENT_PATH if LOGO_TRANSPARENT_PATH.exists() else LOGO_PATH
        if ref_logo.exists():
            banner_card = QFrame()
            banner_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1D1812, stop:1 #110E0B);
                    border: 1px solid #4D3F2C; border-left: 5px solid #F4D03F;
                    border-radius: 10px;
                }
            """)
            b_layout = QHBoxLayout(banner_card)
            b_layout.setContentsMargins(18, 14, 18, 14)
            b_layout.setSpacing(22)
            
            logo_img_lbl = QLabel()
            pix_banner = QPixmap(str(ref_logo)).scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img_lbl.setPixmap(pix_banner)
            logo_img_lbl.setFixedSize(134, 134)
            logo_img_lbl.setAlignment(Qt.AlignCenter)
            logo_img_lbl.setStyleSheet("""
                QLabel {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.6, fx:0.5, fy:0.5, stop:0 #101826, stop:1 #06090F);
                    border: 2px solid #D4AC0D;
                    border-radius: 14px;
                    padding: 2px;
                }
            """)
            b_layout.addWidget(logo_img_lbl)
            
            text_layout = QVBoxLayout()
            text_layout.setSpacing(6)
            lbl_title = QLabel("✦ EMBLEMA OFICIAL: QUANTUM PYRAMID & CALENDAR CORE")
            lbl_title.setStyleSheet("color: #F4D03F; font-size: 16px; font-weight: bold; font-family: 'Georgia', serif; background: transparent;")
            lbl_sub = QLabel("Insignia de Integración Vigesimal, Sincronización de Kuramoto y Códice de Dresde")
            lbl_sub.setStyleSheet("color: #00E5FF; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent;")
            lbl_desc = QLabel(
                "• <b>Rueda Calendárica Holográfica:</b> Anillos concéntricos del Tzolk'in (260d) y Haab' (365d) engranados en oro solar.<br>"
                "• <b>Pirámide Voxel de Kukulkán:</b> Templo levitante en terrazas de basalto con filos de neón turquesa y escaleras sagradas.<br>"
                "• <b>Máscara Solar 4 Ahau:</b> La coordenada de la Creación y del Solitón 2032 con el Tercer Ojo Kuramoto (Ψ) y el rayo Axis Mundi."
            )
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("color: #D5C2A5; font-size: 12px; line-height: 1.6; background: transparent;")
            text_layout.addWidget(lbl_title)
            text_layout.addWidget(lbl_sub)
            text_layout.addWidget(lbl_desc)
            b_layout.addLayout(text_layout, stretch=1)
            
            content_layout.addWidget(banner_card)

        # Tzolkin reference
        tz_group = QGroupBox("Tzolkin Day Signs (20 Days)")
        tz_layout = QGridLayout(tz_group)
        for i, (name, meaning, glyph) in enumerate(self.converter.TZOLKIN_DATA):
            row, col = i // 4, i % 4
            lbl = StoneLabel(f"{glyph} {name}\n{meaning}", size=11, color="#ccc")
            tz_layout.addWidget(lbl, row, col)
        content_layout.addWidget(tz_group)
        
        # Haab reference
        haab_group = QGroupBox("Haab' Months (19 Months)")
        haab_layout = QGridLayout(haab_group)
        for i, (name, meaning) in enumerate(self.converter.HAAB_DATA):
            row, col = i // 4, i % 4
            lbl = StoneLabel(f"{name}\n{meaning}", size=11, color="#ccc")
            haab_layout.addWidget(lbl, row, col)
        content_layout.addWidget(haab_group)
        
        # Lords reference
        lords_group = QGroupBox("Lords of the Night (G1-G9)")
        lords_layout = QVBoxLayout(lords_group)
        for code, name in self.converter.LORDS_OF_NIGHT:
            lbl = StoneLabel(f"{code}: {name}", size=11, color="#ccc")
            lbl.setAlignment(Qt.AlignLeft)
            lords_layout.addWidget(lbl)
        content_layout.addWidget(lords_group)
        
        self._build_advanced_reference(content_layout)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "📚 Reference")

    def _build_advanced_reference(self, layout):
        # 1. 13 Galactic Tones
        tones_group = QGroupBox("Tzolkin Numerals / Galactic Tones (1-13)")
        tones_layout = QGridLayout(tones_group)
        tones_data = [
            ("1. Hun", "Magnetic / Purpose"), ("2. Ca", "Lunar / Challenge"),
            ("3. Ox", "Electric / Service"), ("4. Can", "Self-Existing / Form"),
            ("5. Ho", "Overtone / Radiance"), ("6. Uac", "Rhythmic / Equality"),
            ("7. Uuc", "Resonant / Attunement"), ("8. Uaxac", "Galactic / Integrity"),
            ("9. Bolon", "Solar / Intention"), ("10. Lahun", "Planetary / Manifest"),
            ("11. Buluc", "Spectral / Liberation"), ("12. Lahca", "Crystal / Cooperation"),
            ("13. Oxlahun", "Cosmic / Presence")
        ]
        for i, (name, meaning) in enumerate(tones_data):
            row, col = i // 4, i % 4
            lbl = StoneLabel(f"{name}\n{meaning}", size=11, color="#ccc")
            tones_layout.addWidget(lbl, row, col)
        layout.addWidget(tones_group)
        
        # 2. Lunar Series
        lunar_group = QGroupBox("Lunar Supplementary Series (Moon)")
        lunar_layout = QVBoxLayout(lunar_group)
        lunar_info = (
            "The Supplementary Series tracks precise lunar data over a 6-month semester.\n"
            "• Glyph C: The current lunation number in the 6-month cycle (1 to 6).\n"
            "• Glyph A: Length of current lunar month (alternates 29 or 30 days).\n"
            "• Glyph X: Patron Deity of the lunation:\n"
            "    C1 = God C (Young Moon)   | C2 = God of No. 10\n"
            "    C3 = Jaguar God of Underworld | C4 = Death God\n"
            "    C5 = Old Earth Deity      | C6 = Young God"
        )
        lunar_lbl = StoneLabel(lunar_info, size=11, color="#ccc")
        lunar_lbl.setAlignment(Qt.AlignLeft)
        lunar_layout.addWidget(lunar_lbl)
        layout.addWidget(lunar_group)
        
        # 3. Deep Time Eras
        deep_group = QGroupBox("Long Count Deep Time Eras")
        deep_layout = QGridLayout(deep_group)
        eras = [
            ("Kin", "1 Day"), ("Uinal", "20 Days"), ("Tun", "360 Days (~1 Year)"),
            ("Katun", "7,200 Days (~20 Yrs)"), ("Baktun", "144,000 Days (~394 Yrs)"),
            ("Piktun", "2.88 Million Days (~7,885 Yrs)"),
            ("Kalabtun", "57.6 Million Days (~157,700 Yrs)"),
            ("Kinchiltun", "1.15 Billion Days (~3.15M Yrs)"),
            ("Alautun", "23 Billion Days (~63M Yrs)")
        ]
        for i, (name, val) in enumerate(eras):
            row, col = i // 3, i % 3
            lbl = StoneLabel(f"{name}\n{val}", size=11, color="#ccc")
            deep_layout.addWidget(lbl, row, col)
        layout.addWidget(deep_group)
        
        # 4. Venus Cycle
        venus_group = QGroupBox("Synodic Cycle of Venus (584 Days)")
        venus_layout = QVBoxLayout(venus_group)
        venus_info = (
            "Dresden Codex Venus Phases:\n"
            "• Days 0-236: Morning Star (Visible in East)\n"
            "• Days 236-326: Superior Conjunction (90 days invisible in the Underworld)\n"
            "• Days 326-576: Evening Star (250 days visible in West)\n"
            "• Days 576-584: Inferior Conjunction (8 days invisible in the Underworld)"
        )
        venus_lbl = StoneLabel(venus_info, size=11, color="#ccc")
        venus_lbl.setAlignment(Qt.AlignLeft)
        venus_layout.addWidget(venus_lbl)
        layout.addWidget(venus_group)
        
        # 5. Correlations & 819-Day
        misc_group = QGroupBox("Correlations & K'awiil Cycle")
        misc_layout = QVBoxLayout(misc_group)
        misc_info = (
            "819-Day Cycle: Associated with God K'awiil moving across 4 quadrants.\n"
            "Red (East) -> White (North) -> Black (West) -> Yellow (South). 819 = 9 x 7 x 13.\n\n"
            "Correlations (Syncing Mayan to Gregorian Time):\n"
            "• GMT (584283): Standard archaeological consensus (Goodman-Martinez-Thompson).\n"
            "• GMT+2 (584285): Adjusted by astronomers to better match eclipse data.\n"
            "• Spinden (489384): Early correlation mapping 13.0.0.0.0 to 3373 BC instead of 3114 BC."
        )
        misc_lbl = StoneLabel(misc_info, size=11, color="#ccc")
        misc_lbl.setAlignment(Qt.AlignLeft)
        misc_layout.addWidget(misc_lbl)
        layout.addWidget(misc_group)

    def _set_initial_date(self):
        self.date_edit.setDate(QDate.currentDate())
        self.convert_date()

    def _go_today(self):
        self.date_edit.setDate(QDate.currentDate())

    def _adjust_date(self, delta):
        current = self.date_edit.date()
        self.date_edit.setDate(current.addDays(delta))

    def convert_date(self):
        gregorian_date = self.date_edit.date()
        data = self.converter.get_full_date(
            gregorian_date.year(),
            gregorian_date.month(),
            gregorian_date.day()
        )

        # Update circular calendar
        self.circular_calendar.update_data(
            data["tzolkin_idx"],
            data["haab_idx"],
            (data["days_since_epoch"] + 8) % 9,
            data["tzolkin"],
            data["tzolkin_glyph"],
            data["haab"]
        )
        
        # Update Long Count display
        self.long_count_display.set_long_count(data["long_count_parts"])
        
        # Sync Long Count spin boxes (reverse conversion row)
        for spin, val in zip(self.lc_spins, data["long_count_parts"]):
            spin.blockSignals(True)
            spin.setValue(val)
            spin.blockSignals(False)
        
        # Update panels
        self.panel_tzolkin.update_data(
            f"{data['tzolkin_glyph']} {data['tzolkin']}",
            data["tzolkin_meaning"]
        )
        self.panel_haab.update_data(data["haab"], data["haab_meaning"])
        self.panel_calendar_round.update_data(
            data["calendar_round"],
            f"Position: {data['calendar_round_pos']:,} / 18,980 days"
        )
        self.panel_lord.update_data(data["lord"], data["lord_name"])
        self.panel_venus.update_data(
            f"Day {data['venus_pos']} / 584",
            f"Canon 584d • NASA: {data['venus_astro_pos']}d\n{data['venus_phase']}"
        )
        if hasattr(self, 'venus_bar'):
            self.venus_bar.set_position(data["venus_pos"])
            
        self.panel_moon.update_data(
            data["moon_phase"],
            f"Moon Age: {data['moon_age']:.1f}d • {data['moon_illumination']} Iluminada"
        )
        self.panel_lunar_series.update_data(
            f"C: {data['glyph_c']} | A: {data['glyph_a']}",
            f"Glyph X: {data['glyph_x']}"
        )
        # Deep cycles are [alautun, kinchiltun, kalabtun, piktun, baktun, katun, tun, uinal, kin]
        dc = data["deep_long_count"]
        self.panel_deep_time.update_data(
            f"{dc[3]} Piktun",
            f"Kalabtun: {dc[2]} | Kinchiltun: {dc[1]}"
        )
        self._current_mayan_data = data
        if hasattr(self, '_update_biological_tab'):
            self._update_biological_tab(data)

    def _jump_to_fractal_analysis(self):
        """Sincroniza la fecha activa del calendario con el analizador fractal (±2 años) y ejecuta la detección."""
        current_date = self.date_edit.date()
        self.date_fractal_start.setDate(current_date.addYears(-2))
        self.date_fractal_end.setDate(current_date.addYears(2))
        self.tabs.setCurrentIndex(1)
        self._analyze_patterns()

    def switch_fractal_view_mode(self, mode):
        """Alterna entre el modo Ventanas Holísticas (Solitones), Cronológico y Picos de Potencia."""
        self.fractal_view_mode = mode
        
        style_active = "background: #2E4053; color: #F1C40F; border: 1px solid #F1C40F; font-size: 11px; padding: 6px 12px; font-weight: bold;"
        style_inactive = "background: #252220; color: #aaa; border: 1px solid #444; font-size: 11px; padding: 6px 12px;"
        
        self.btn_view_packets.setStyleSheet(style_active if mode == "packets" else style_inactive)
        self.btn_view_chrono.setStyleSheet(style_active if mode == "chrono" else style_inactive)
        self.btn_view_score.setStyleSheet(style_active if mode == "score" else style_inactive)
        
        self._render_fractal_table()

    def _analyze_patterns(self):
        # Evitar ejecuciones concurrentes si ya hay un cálculo activo
        if hasattr(self, '_analysis_worker') and self._analysis_worker and self._analysis_worker.isRunning():
            return

        start_date = self.date_fractal_start.date()
        end_date = self.date_fractal_end.date()
        total_days = start_date.daysTo(end_date)
        if total_days < 1:
            total_days = 1
            
        start_datetime = datetime(start_date.year(), start_date.month(), start_date.day())
        selected = [name for name, cb in self.cycle_checks.items() if cb.isChecked()]
        
        natal_days = None
        if hasattr(self, 'cb_natal_mode') and self.cb_natal_mode.isChecked():
            n_date = self.date_natal.date()
            if n_date != self.date_natal.minimumDate():
                natal_data = self.converter.get_full_date(n_date.year(), n_date.month(), n_date.day())
                natal_days = natal_data['days_since_epoch']

        # Actualizar estado visual de la UI (bloqueo suave del botón y feedback inmediato)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("⏳ Analizando resonancia...")
        if hasattr(self, 'btn_export'):
            self.btn_export.setEnabled(False)

        self.lbl_fractal_summary.setText("Iniciando escaneo armónico multiescala...")
        self.lbl_fractal_summary.setStyleSheet("color: #F1C40F; font-size: 11px;")

        self._analysis_start_datetime = start_datetime
        self._analysis_total_days = total_days

        # Lanzar worker en segundo plano
        self._analysis_worker = FractalAnalysisWorker(
            self.analyzer, start_datetime, total_days, selected, natal_days
        )
        self._analysis_worker.progress.connect(self._on_analysis_progress)
        self._analysis_worker.result_ready.connect(self._on_analysis_finished)
        self._analysis_worker.start()

    def _on_analysis_progress(self, current, total):
        pct = (current / total) * 100.0
        self.lbl_fractal_summary.setText(f"⏳ Analizando resonancias: {pct:.0f}% ({current:,} / {total:,} días)...")

    def _on_analysis_finished(self, events, packets, links):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔮 Find Convergences")

        self.fractal_events = events
        self.fractal_packets = packets
        self.fractal_links = links

        # Actualizar Osciloscopio Continuo
        self.fractal_timeline.set_data(events, packets, links, self._analysis_start_datetime, self._analysis_total_days)

        # Actualizar Barra de Resumen
        if packets:
            self.lbl_fractal_summary.setText(
                f"✦ {len(packets)} Ventanas Coherentes detectadas ({len(events)} días de alta resonancia) • {len(links)} Hiper-Enlaces Fractales"
            )
            self.lbl_fractal_summary.setStyleSheet("color: #F1C40F; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_fractal_summary.setText("No se encontraron convergencias que superen el umbral de coherencia del 60%.")
            self.lbl_fractal_summary.setStyleSheet("color: #aaa; font-size: 11px;")

        # Renderizar Tabla y Panel de Hiper-Fractales
        self._render_fractal_table()
        self._render_harmonic_panel()

        if hasattr(self, 'btn_export'):
            self.btn_export.setEnabled(len(events) > 0)

    def _render_fractal_table(self):
        """Renderiza la tabla de resultados según el modo de vista seleccionado."""
        self.convergence_table.clear()
        
        if self.fractal_view_mode == "packets":
            # MODO 1: VENTANAS HOLÍSTICAS (EL TODO / PAQUETES DE ONDA)
            headers = ["ID", "Ventana Temporal", "Duración", "Cúspide / Pico", "Score Máx", "Kuramoto R", "Simetría (Solitón)", "Eclipse Dresde", "Alineamientos Clave"]
            self.convergence_table.setColumnCount(len(headers))
            self.convergence_table.setHorizontalHeaderLabels(headers)
            self.convergence_table.setRowCount(len(self.fractal_packets))
            
            for row, pkt in enumerate(self.fractal_packets):
                # ID
                item_id = QTableWidgetItem(pkt['id'])
                item_id.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 0, item_id)
                
                # Ventana Temporal
                w_str = f"{pkt['start_date'].strftime('%b %d, %Y')} ➔ {pkt['end_date'].strftime('%b %d, %Y')}"
                self.convergence_table.setItem(row, 1, QTableWidgetItem(w_str))
                
                # Duración
                item_dur = QTableWidgetItem(f"{pkt['duration']} días")
                item_dur.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 2, item_dur)
                
                # Cúspide
                pk_str = f"{pkt['peak_date'].strftime('%b %d')} [{pkt['peak_tzolkin']} - {pkt['peak_long_count']}]"
                self.convergence_table.setItem(row, 3, QTableWidgetItem(pk_str))
                
                # Score Máx
                item_sc = QTableWidgetItem(f"{pkt['peak_score']:.1f}%")
                item_sc.setTextAlignment(Qt.AlignCenter)
                if pkt['peak_score'] >= 75:
                    item_sc.setForeground(QColor("#F1C40F"))
                self.convergence_table.setItem(row, 4, item_sc)
                
                # Kuramoto R
                p_km = pkt.get('peak_kuramoto', {})
                km_val = p_km.get('r', 0.0) * 100.0
                item_km = QTableWidgetItem(f"{km_val:.1f}%")
                item_km.setTextAlignment(Qt.AlignCenter)
                if p_km.get('is_locked'):
                    item_km.setForeground(QColor("#00DCFF"))
                self.convergence_table.setItem(row, 5, item_km)
                
                # Simetría
                sym_label = "Solitón Puro" if pkt['symmetry_score'] >= 88 else ("Campana Coherente" if pkt['symmetry_score'] >= 70 else "Onda Asimétrica")
                item_sym = QTableWidgetItem(f"{pkt['symmetry_score']:.0f}% ({sym_label})")
                item_sym.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 6, item_sym)

                # Eclipse Dresde
                ecl_str = pkt.get('eclipse_type') or "—"
                item_ecl = QTableWidgetItem(ecl_str)
                item_ecl.setTextAlignment(Qt.AlignCenter)
                if pkt.get('has_eclipse'):
                    item_ecl.setForeground(QColor("#E74C3C"))
                    item_ecl.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.convergence_table.setItem(row, 7, item_ecl)
                
                # Alineamientos
                self.convergence_table.setItem(row, 8, QTableWidgetItem(", ".join(pkt['alignments'])))
                
        else:
            # MODOS INDIVIDUALES: CRONOLÓGICO O SCORE DESCENDENTE
            headers = ["Fecha", "Score", "Long Count", "Tzolkin", "Ventana", "Kuramoto R (Ψ)", "Eclipse Dresde", "Alineamientos"]
            self.convergence_table.setColumnCount(len(headers))
            self.convergence_table.setHorizontalHeaderLabels(headers)
            
            if self.fractal_view_mode == "chrono":
                display_events = sorted(self.fractal_events, key=lambda x: x['date'])
            else:
                display_events = sorted(self.fractal_events, key=lambda x: x['score'], reverse=True)
                
            self.convergence_table.setRowCount(len(display_events))
            
            # Mapear fecha a ID de ventana
            date_to_pkt = {}
            for pkt in self.fractal_packets:
                for d in pkt['days']:
                    date_to_pkt[d['date'].strftime('%Y-%m-%d')] = pkt['id']
                    
            for row, evt in enumerate(display_events):
                self.convergence_table.setItem(row, 0, QTableWidgetItem(evt['date'].strftime("%b %d, %Y")))
                
                item_sc = QTableWidgetItem(f"{evt['score']:.1f}%")
                item_sc.setTextAlignment(Qt.AlignCenter)
                if evt['score'] >= 75:
                    item_sc.setForeground(QColor("#F1C40F"))
                self.convergence_table.setItem(row, 1, item_sc)
                
                self.convergence_table.setItem(row, 2, QTableWidgetItem(evt['long_count']))
                self.convergence_table.setItem(row, 3, QTableWidgetItem(evt['tzolkin']))
                
                pkt_id = date_to_pkt.get(evt['date'].strftime('%Y-%m-%d'), "—")
                item_pkt = QTableWidgetItem(pkt_id)
                item_pkt.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 4, item_pkt)

                # Kuramoto R (Ψ)
                km = evt.get('kuramoto', {})
                km_r = km.get('r', 0.0) * 100.0
                km_psi = km.get('psi_deg', 0.0)
                item_km = QTableWidgetItem(f"{km_r:.1f}% ({km_psi:.0f}°)")
                item_km.setTextAlignment(Qt.AlignCenter)
                if km.get('is_locked'):
                    item_km.setForeground(QColor("#00DCFF"))
                self.convergence_table.setItem(row, 5, item_km)

                # Eclipse Dresde
                ecl = evt.get('eclipse', {})
                ecl_str = ecl.get('eclipse_type') or "—"
                item_ecl = QTableWidgetItem(ecl_str)
                item_ecl.setTextAlignment(Qt.AlignCenter)
                if ecl.get('is_eclipse_window'):
                    item_ecl.setForeground(QColor("#E74C3C"))
                    item_ecl.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.convergence_table.setItem(row, 6, item_ecl)
                
                self.convergence_table.setItem(row, 7, QTableWidgetItem(", ".join(evt['alignments'])))
                
        self.convergence_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.convergence_table.horizontalHeader().setStretchLastSection(True)
        self.convergence_table.viewport().update()

    def _render_harmonic_panel(self):
        """Renderiza las tarjetas de hiper-enlaces fractales en el panel lateral."""
        # Limpiar contenido anterior
        while self.harmonic_content_layout.count() > 0:
            item = self.harmonic_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not self.fractal_links:
            lbl_empty = StoneLabel("No se detectaron hiper-enlaces armónicos entre las cúspides en el rango actual.", size=10, color="#777")
            lbl_empty.setWordWrap(True)
            self.harmonic_content_layout.addWidget(lbl_empty)
            self.harmonic_content_layout.addStretch()
            return

        total_links = len(self.fractal_links)
        max_cards = 40
        display_links = self.fractal_links[:max_cards]

        if total_links > max_cards:
            lbl_info = QLabel(f"Mostrando los {max_cards} hiper-enlaces de mayor orden armónico (de {total_links:,} detectados):")
            lbl_info.setStyleSheet("color: #E67E22; font-size: 10px; font-style: italic; margin-bottom: 4px;")
            lbl_info.setWordWrap(True)
            self.harmonic_content_layout.addWidget(lbl_info)

        for link in display_links:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #24201A;
                    border: 1px solid #4D412F;
                    border-radius: 5px;
                    padding: 6px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(4)
            
            p1_name = f"{link['p1']['peak_tzolkin']} ({link['p1']['peak_date'].year})"
            p2_name = f"{link['p2']['peak_tzolkin']} ({link['p2']['peak_date'].year})"
            header = QLabel(f"🌟 {p1_name} ➔ {p2_name}")
            header.setStyleSheet("color: #F1C40F; font-weight: bold; font-size: 11px;")
            card_layout.addWidget(header)
            
            sub = QLabel(f"Distancia temporal: {link['delta_days']:,} días terrestres")
            sub.setStyleSheet("color: #BDC3C7; font-size: 10px;")
            card_layout.addWidget(sub)
            
            for h in link['harmonics']:
                lbl_h = QLabel(f"• {h}")
                lbl_h.setStyleSheet("color: #5DADE2; font-size: 10px;")
                card_layout.addWidget(lbl_h)
                
            card_layout.addWidget(QLabel(""))
            self.harmonic_content_layout.addWidget(card)
            
        self.harmonic_content_layout.addStretch()

    def _on_table_cell_clicked(self, row, col):
        """Muestra el desglose de simetría y secuencia de respiración de la ventana seleccionada."""
        if self.fractal_view_mode == "packets" and row < len(self.fractal_packets):
            pkt = self.fractal_packets[row]
            
            lines = [
                f"<b>📍 VENTANA {pkt['id']}: {pkt['start_date'].strftime('%d %b %Y')} ➔ {pkt['end_date'].strftime('%d %b %Y')}</b>",
                f"• <b>Cúspide:</b> {pkt['peak_tzolkin']} ({pkt['peak_score']:.1f}%) el {pkt['peak_date'].strftime('%d %b %Y')} [{pkt['peak_long_count']}]",
                f"• <b>Simetría de Solitón:</b> {pkt['symmetry_score']:.0f}% • Duración: {pkt['duration']} días",
                f"• <b>Secuencia de Respiración Diaria:</b>"
            ]
            
            for d in pkt['days']:
                is_peak = (d['date'] == pkt['peak_date'])
                prefix = "  ⭐ " if is_peak else "  ▫ "
                lines.append(f"{prefix}{d['date'].strftime('%d %b')}: {d['tzolkin']} — <b>{d['score']:.1f}%</b> ({d['long_count']})")
                
            self.window_detail_box.setText("<br>".join(lines))
        elif self.fractal_view_mode in ("chrono", "score") and row < len(self.fractal_events):
            if self.fractal_view_mode == "chrono":
                display_events = sorted(self.fractal_events, key=lambda x: x['date'])
            else:
                display_events = sorted(self.fractal_events, key=lambda x: x['score'], reverse=True)
            evt = display_events[row]
            self.window_detail_box.setText(
                f"<b>📅 {evt['date'].strftime('%d %b %Y')}</b><br>"
                f"• Score: <b>{evt['score']:.1f}%</b><br>"
                f"• Tzolkin: {evt['tzolkin']} • Long Count: {evt['long_count']}<br>"
                f"• Alineamientos: {', '.join(evt['alignments'])}"
            )

    def _on_timeline_date_clicked(self, date):
        """Navega el calendario principal a la fecha clickeada en el osciloscopio."""
        self.date_edit.setDate(QDate(date.year, date.month, date.day))
        self.convert_date()
        self.tabs.setCurrentIndex(0)  # Llevar al usuario a la vista de calendario

    def _export_fractal_results(self):
        if self.convergence_table.rowCount() == 0:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Export Fractal Results", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [self.convergence_table.horizontalHeaderItem(i).text() for i in range(self.convergence_table.columnCount())]
                writer.writerow(headers)
                
                for row in range(self.convergence_table.rowCount()):
                    row_data = []
                    for col in range(self.convergence_table.columnCount()):
                        item = self.convergence_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Export Successful", f"Resultados exitosamente exportados en modo '{self.fractal_view_mode}' a:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Ocurrió un error al exportar:\n{str(e)}")

    def _change_correlation(self):
        index = self.combo_correlation.currentIndex()
        if index == 0:
            self.converter.correlation_jdn = 584283  # GMT
        elif index == 1:
            self.converter.correlation_jdn = 584285  # GMT+2
        elif index == 2:
            self.converter.correlation_jdn = 489384  # Spinden
        self.convert_date()

    def _convert_long_count(self):
        """Convert Long Count spin box values to Gregorian and set the date picker."""
        parts = [spin.value() for spin in self.lc_spins]
        year, month, day = self.converter.long_count_to_gregorian(*parts)
        # Block signals to avoid circular update loop
        self.date_edit.blockSignals(True)
        self.date_edit.setDate(QDate(year, month, day))
        self.date_edit.blockSignals(False)
        self.convert_date()

    def _update_live_clock(self):
        """Update the status bar with the current Mayan date in real-time."""
        now = datetime.now()
        data = self.converter.get_full_date(now.year, now.month, now.day)
        clock_text = (
            f"  Now: {data['long_count']}  •  "
            f"{data['tzolkin_glyph']} {data['tzolkin']}  •  "
            f"{data['haab']}  •  "
            f"{data['lord']}  •  "
            f"{data['venus_phase']}  •  "
            f"{data['moon_phase']}"
        )
        self.statusBar().showMessage(clock_text)

    def closeEvent(self, event):
        """Asegurar que el hilo de cálculo fractal termine limpiamente al cerrar la ventana."""
        if hasattr(self, '_analysis_worker') and self._analysis_worker and self._analysis_worker.isRunning():
            self._analysis_worker.quit()
            self._analysis_worker.wait(500)
        event.accept()

if __name__ == "__main__":
    if not HAS_PYSIDE6:
        print("\n" + "=" * 65)
        print(" [!] PySide6 no está instalado en este entorno de Python.")
        print(" Para abrir la aplicación gráfica de la Estela Maya:")
        print("     pip install -r requirements.txt")
        print("=" * 65)
        print(" Nota: El servidor MCP ('mayan_mcp_server.py') y las funciones")
        print(" matemáticas funcionan con Python puro estándar sin dependencias.\n")
        sys.exit(1)
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('plantacerium.mayanstele.calendar.v2')
        except Exception:
            pass
    app = QApplication(sys.argv)
    if LOGO_ICO_PATH.exists():
        app.setWindowIcon(QIcon(str(LOGO_ICO_PATH)))
    elif LOGO_PATH.exists():
        app.setWindowIcon(QIcon(str(LOGO_PATH)))
    app.setStyle("Fusion")
    window = MayanSteleApp()
    window.show()
    sys.exit(app.exec())