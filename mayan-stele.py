"""
Mayan Stele - Ultimate Mayan Calendar Application
Complete implementation with all calendar systems, fractal pattern detection,
and stunning visual displays.
"""
import sys
import math
from functools import reduce
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QDateEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QSpinBox, QScrollArea, QGroupBox, QSplitter, QSlider, QProgressBar
)
from PySide6.QtCore import QDate, Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property, QRectF
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QPen, QBrush, QRadialGradient, QLinearGradient, QConicalGradient

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: MAYAN CALENDAR ARITHMETIC CORE
# ══════════════════════════════════════════════════════════════════════════════

class MayanConverter:
    """Advanced Mayan Calendar converter with all major cycles."""
    
    MAYA_EPOCH_JDN = 584283  # GMT Correlation (13.0.0.0.0 = 4 Ahau 8 Cumku)
    
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
        JDN = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        return int(JDN)
    
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
        days_since_epoch = jdn - self.MAYA_EPOCH_JDN

        # Long Count
        temp_days = days_since_epoch
        baktun = temp_days // 144000
        temp_days %= 144000
        katun = temp_days // 7200
        temp_days %= 7200
        tun = temp_days // 360
        temp_days %= 360
        uinal = temp_days // 20
        kin = temp_days % 20
        long_count_str = f"{baktun}.{katun}.{tun}.{uinal}.{kin}"
        long_count_parts = [baktun, katun, tun, uinal, kin]

        # Tzolkin (260 days)
        tz_num = (jdn + 4) % 13
        if tz_num == 0: tz_num = 13
        tz_idx = (jdn + 19) % 20
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

        # Venus cycle (584 days)
        venus_pos = days_since_epoch % 584
        if venus_pos < 236: venus_phase = "Morning Star"
        elif venus_pos < 326: venus_phase = "Superior Conjunction"
        elif venus_pos < 576: venus_phase = "Evening Star"
        else: venus_phase = "Inferior Conjunction"

        # Mars cycle (780 days)
        mars_pos = days_since_epoch % 780

        # Lunar data (approximation)
        lunar_cycle = 29.53059
        moon_age = (jdn - 2451550.1) % lunar_cycle
        if moon_age < 1.85: moon_phase = "New Moon 🌑"
        elif moon_age < 7.38: moon_phase = "Waxing Crescent 🌒"
        elif moon_age < 9.23: moon_phase = "First Quarter 🌓"
        elif moon_age < 14.77: moon_phase = "Waxing Gibbous 🌔"
        elif moon_age < 16.61: moon_phase = "Full Moon 🌕"
        elif moon_age < 22.15: moon_phase = "Waning Gibbous 🌖"
        elif moon_age < 23.99: moon_phase = "Last Quarter 🌗"
        else: moon_phase = "Waning Crescent 🌘"

        return {
            "long_count": long_count_str,
            "long_count_parts": long_count_parts,
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
            "mars_pos": mars_pos,
            "moon_age": moon_age,
            "moon_phase": moon_phase,
            "jdn": jdn,
            "days_since_epoch": days_since_epoch
        }

    def long_count_to_gregorian(self, baktun, katun, tun, uinal, kin):
        """Convert Long Count to Gregorian date."""
        days = baktun * 144000 + katun * 7200 + tun * 360 + uinal * 20 + kin
        jdn = self.MAYA_EPOCH_JDN + days
        return self._jdn_to_gregorian(jdn)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: FRACTAL PATTERN ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class FractalPatternAnalyzer:
    """Detect harmonic convergences and fractal patterns in Mayan cycles."""
    
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
        'Lunar': 30,
    }
    
    def __init__(self, converter):
        self.converter = converter
    
    def calculate_resonance_score(self, year, month, day, selected_cycles=None):
        """Calculate how many cycles align on this date (0-100%)."""
        data = self.converter.get_full_date(year, month, day)
        days = data['days_since_epoch']
        
        alignments = 0
        weights = 0
        
        checks = [
            ('Tzolkin', days % 260, 260, 1.0),
            ('Haab', days % 365, 365, 0.8),
            ('Calendar Round', days % 18980, 18980, 2.0),
            ('Lord of Night', days % 9, 9, 0.5),
            ('819-Day', days % 819, 819, 0.7),
            ('Venus', days % 584, 584, 0.9),
            ('Mars', days % 780, 780, 0.6),
            ('Tun', days % 360, 360, 0.7),
        ]
        
        for name, pos, cycle, weight in checks:
            if selected_cycles is not None and name not in selected_cycles:
                continue
            proximity = min(pos, cycle - pos) / cycle
            alignment = 1.0 - (proximity * 2)
            alignments += alignment * weight
            weights += weight
        
        return (alignments / weights) * 100 if weights > 0 else 0
    
    def find_convergences(self, start_date, months_ahead=12, selected_cycles=None):
        """Find dates with high convergence scores starting from the given date."""
        if selected_cycles is None:
            selected_cycles = list(self.CYCLES.keys())
        
        events = []
        # Start from the provided date object or create from year
        if isinstance(start_date, datetime):
            start = start_date
        else:
            start = datetime(start_date, 1, 1)
        
        total_days = months_ahead * 30
        for day_offset in range(total_days):
            current = start + timedelta(days=day_offset)
            score = self.calculate_resonance_score(current.year, current.month, current.day, selected_cycles)
            
            if score > 60:
                data = self.converter.get_full_date(current.year, current.month, current.day)
                events.append({
                    'date': current,
                    'score': score,
                    'tzolkin': data['tzolkin'],
                    'haab': data['haab'],
                    'long_count': data['long_count'],
                    'alignments': self._get_alignments(data)
                })
        
        events.sort(key=lambda x: x['score'], reverse=True)
        return events[:20]
    
    def _get_alignments(self, data):
        """Get list of cycles that are at or near alignment."""
        alignments = []
        days = data['days_since_epoch']
        
        if days % 260 < 5 or days % 260 > 255:
            alignments.append("Tzolkin")
        if days % 365 < 5 or days % 365 > 360:
            alignments.append("Haab")
        if days % 360 < 5 or days % 360 > 355:
            alignments.append("Tun")
        if days % 584 < 10 or days % 584 > 574:
            alignments.append("Venus")
        if days % 819 < 10 or days % 819 > 809:
            alignments.append("819-Day")
            
        return alignments
    
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
        self.setMinimumSize(300, 300)
        self._tzolkin_idx = 0
        self._haab_idx = 0
        self._lord_idx = 0
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
    
    def update_data(self, tzolkin_idx, haab_idx, lord_idx):
        old_rot = self._rotation
        self._tzolkin_idx = tzolkin_idx
        self._haab_idx = haab_idx
        self._lord_idx = lord_idx
        
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
        max_r = min(w, h) // 2 - 10
        
        # Background
        bg = QRadialGradient(cx, cy, max_r)
        bg.setColorAt(0, QColor(40, 35, 30))
        bg.setColorAt(1, QColor(20, 18, 15))
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - max_r, cy - max_r, max_r * 2, max_r * 2)
        
        # Outer ring - Haab (19 segments)
        self._draw_ring(painter, cx, cy, max_r - 5, max_r - 40, 19, self._haab_idx, 
                       QColor(139, 90, 43), QColor(210, 150, 80), self.HAAB_LABELS)
        
        # Middle ring - Tzolkin (20 segments)
        self._draw_ring(painter, cx, cy, max_r - 45, max_r - 80, 20, self._tzolkin_idx,
                       QColor(80, 100, 60), QColor(150, 180, 100), self.TZOLKIN_LABELS)
        
        # Inner ring - Lords (9 segments)
        self._draw_ring(painter, cx, cy, max_r - 85, max_r - 110, 9, self._lord_idx,
                       QColor(100, 50, 50), QColor(180, 80, 80), self.LORD_LABELS)
        
        # Center circle
        center_grad = QRadialGradient(cx, cy, max_r - 115)
        center_grad.setColorAt(0, QColor(60, 55, 50))
        center_grad.setColorAt(1, QColor(30, 28, 25))
        painter.setBrush(QBrush(center_grad))
        painter.setPen(QPen(QColor(100, 90, 70), 2))
        painter.drawEllipse(cx - (max_r - 115), cy - (max_r - 115), 
                           (max_r - 115) * 2, (max_r - 115) * 2)
    
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
            font_size = max(6, min(9, int(ring_thickness * 0.28)))
            label_font = QFont("Segoe UI", font_size)
            label_font.setBold(True)
            painter.setFont(label_font)
            
            for i in range(segments):
                mid_angle_deg = i * segment_angle + segment_angle / 2 + self._rotation
                mid_angle_rad = math.radians(mid_angle_deg)
                
                # Position at midpoint of segment arc
                lx = cx + mid_r * math.cos(mid_angle_rad)
                ly = cy - mid_r * math.sin(mid_angle_rad)
                
                label = labels[i] if i < len(labels) else ""
                # Truncate long labels to fit
                if ring_thickness < 40 and len(label) > 4:
                    label = label[:4]
                
                # Text colour: bright for highlighted, subtle for others
                if i == highlight_idx:
                    painter.setPen(QColor(30, 20, 10))
                else:
                    painter.setPen(QColor(220, 200, 170, 180))
                
                # Rotate text to follow the arc
                painter.save()
                painter.translate(lx, ly)
                text_rotation = -mid_angle_deg + 90
                if 90 < mid_angle_deg % 360 < 270:
                    text_rotation += 180
                painter.rotate(text_rotation)
                
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(label)
                th = fm.height()
                painter.drawText(int(-tw / 2), int(th / 4), label)
                painter.restore()


class LongCountDisplay(QWidget):
    """Animated odometer-style Long Count display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self._parts = [13, 0, 0, 0, 0]  # baktun.katun.tun.uinal.kin
        self._labels = ["Baktun", "Katun", "Tun", "Uinal", "Kin"]
        
    def set_long_count(self, parts):
        self._parts = parts
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        box_w = w // 5 - 10
        box_h = 50
        y_offset = (h - box_h - 20) // 2
        
        for i, (val, label) in enumerate(zip(self._parts, self._labels)):
            x = 5 + i * (box_w + 10)
            
            # Box background
            grad = QLinearGradient(x, y_offset, x, y_offset + box_h)
            grad.setColorAt(0, QColor(50, 45, 40))
            grad.setColorAt(0.5, QColor(70, 60, 50))
            grad.setColorAt(1, QColor(40, 35, 30))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(100, 90, 70), 2))
            painter.drawRoundedRect(x, y_offset, box_w, box_h, 5, 5)
            
            # Number
            painter.setPen(QColor(244, 208, 63))
            font = QFont("Consolas", 24, QFont.Bold)
            painter.setFont(font)
            painter.drawText(x, y_offset, box_w, box_h, Qt.AlignCenter, str(val))
            
            # Label
            painter.setPen(QColor(150, 140, 120))
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(x, y_offset + box_h + 2, box_w, 18, Qt.AlignCenter, label)
            
            # Separator dot
            if i < 4:
                painter.setPen(QColor(200, 180, 140))
                painter.drawText(x + box_w, y_offset, 10, box_h, Qt.AlignCenter, ".")


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
    """Visual timeline showing cycle convergences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self._events = []
        self._range_days = 365
    
    def set_events(self, events, range_days=365):
        self._events = events
        self._range_days = range_days
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Background
        painter.fillRect(0, 0, w, h, QColor(25, 23, 20))
        
        # Timeline
        y_mid = h // 2
        painter.setPen(QPen(QColor(100, 90, 70), 2))
        painter.drawLine(20, y_mid, w - 20, y_mid)
        
        # Events
        if self._events and self._range_days > 0:
            today = datetime.now()
            for evt in self._events:
                days_from_now = (evt['date'] - today).days
                if 0 <= days_from_now <= self._range_days:
                    x = 20 + int((days_from_now / self._range_days) * (w - 40))
                    
                    # Score determines size and color
                    score = evt['score']
                    radius = int(5 + (score / 100) * 15)
                    
                    if score > 80:
                        color = QColor(255, 215, 0)  # Gold
                    elif score > 70:
                        color = QColor(255, 140, 0)  # Orange
                    else:
                        color = QColor(100, 180, 100)  # Green
                    
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(color.darker(150), 1))
                    painter.drawEllipse(x - radius, y_mid - radius, radius * 2, radius * 2)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class MayanSteleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = MayanConverter()
        self.analyzer = FractalPatternAnalyzer(self.converter)
        self.setWindowTitle("🌟 MAYAN STELE - Ultimate Calendar & Fractal Pattern Analyzer")
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
            QTabWidget::pane { border: 2px solid #444; background: #222; border-radius: 8px; }
            QTabBar::tab { background: #333; color: #aaa; padding: 10px 20px; margin: 2px;
                          border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #444; color: #f4d03f; }
            QDateEdit { background-color: #333; color: #e0c090; border: 2px solid #555;
                       padding: 8px; font-size: 14px; border-radius: 6px; }
            QDateEdit::drop-down { border-left: 1px solid #555; background: #444; }
            QPushButton { background-color: #5d4037; color: #fff; font-weight: bold;
                         border: 2px solid #3e2723; border-radius: 6px; padding: 10px 16px; }
            QPushButton:hover { background-color: #6d4c41; }
            QPushButton:pressed { background-color: #3e2723; }
            QTableWidget { background-color: #252220; color: #e0c090; gridline-color: #444;
                          border: 1px solid #444; }
            QTableWidget::item:selected { background-color: #5d4037; }
            QHeaderView::section { background-color: #333; color: #f4d03f; padding: 6px;
                                  border: 1px solid #444; }
            QCheckBox { color: #e0c090; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QGroupBox { border: 2px solid #444; border-radius: 8px; margin-top: 10px;
                       padding-top: 10px; color: #f4d03f; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QScrollArea { border: none; background: transparent; }
            QSpinBox { background: #333; color: #e0c090; border: 1px solid #555;
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
        title = StoneLabel("⚱ MAYAN STELE", size=28, is_bold=True, color="#d4af37")
        subtitle = StoneLabel("Ultimate Calendar & Fractal Pattern Analyzer", size=14, color="#888")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # Date input row
        input_layout = QHBoxLayout()
        input_layout.addWidget(StoneLabel("Gregorian Date:", size=12, color="#aaa"))
        
        self.date_edit = QDateEdit()
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
        
        # Tab 3: Reference
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
        left_panel.addWidget(self.circular_calendar)
        
        legend = StoneLabel("Outer: Haab │ Middle: Tzolkin │ Inner: Lords", size=10, color="#777")
        left_panel.addWidget(legend)
        layout.addLayout(left_panel, 1)
        
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
        self.panel_moon = StonePanel("Moon Phase", "🌕", "Lunar Cycle")
        
        grid.addWidget(self.panel_tzolkin, 0, 0)
        grid.addWidget(self.panel_haab, 0, 1)
        grid.addWidget(self.panel_calendar_round, 1, 0)
        grid.addWidget(self.panel_lord, 1, 1)
        grid.addWidget(self.panel_venus, 2, 0)
        grid.addWidget(self.panel_moon, 2, 1)
        
        right_panel.addLayout(grid)
        layout.addLayout(right_panel, 2)
        
        self.tabs.addTab(tab, "📅 Calendar")

    def _setup_fractal_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(StoneLabel("Search Range:", size=12, color="#aaa"))
        
        self.spin_months = QSpinBox()
        self.spin_months.setRange(1, 120)
        self.spin_months.setValue(12)
        self.spin_months.setSuffix(" months")
        controls.addWidget(self.spin_months)
        
        self.btn_analyze = QPushButton("🔮 Find Convergences")
        self.btn_analyze.clicked.connect(self._analyze_patterns)
        controls.addWidget(self.btn_analyze)
        
        controls.addStretch()
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
        
        # Timeline
        self.fractal_timeline = FractalTimelineWidget()
        layout.addWidget(self.fractal_timeline)
        
        # Results table
        self.convergence_table = QTableWidget()
        self.convergence_table.setColumnCount(5)
        self.convergence_table.setHorizontalHeaderLabels(["Date", "Score", "Long Count", "Tzolkin", "Alignments"])
        self.convergence_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.convergence_table.setAlternatingRowColors(True)
        layout.addWidget(self.convergence_table)
        
        self.tabs.addTab(tab, "🔮 Fractal Patterns")

    def _setup_reference_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
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
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "📚 Reference")

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
            (data["days_since_epoch"] + 8) % 9
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
            f"Day {data['venus_pos']}",
            data["venus_phase"]
        )
        self.panel_moon.update_data(
            data["moon_phase"],
            f"Moon Age: {data['moon_age']:.1f} days"
        )

    def _analyze_patterns(self):
        current_date = self.date_edit.date()
        months = self.spin_months.value()
        
        # Convert QDate to Python datetime
        start_datetime = datetime(current_date.year(), current_date.month(), current_date.day())
        
        selected = [name for name, cb in self.cycle_checks.items() if cb.isChecked()]
        events = self.analyzer.find_convergences(start_datetime, months, selected)
        
        # Update timeline
        self.fractal_timeline.set_events(events, months * 30)
        
        # Clear and update table
        self.convergence_table.clearContents()
        self.convergence_table.setRowCount(len(events))
        
        for row, evt in enumerate(events):
            self.convergence_table.setItem(row, 0, QTableWidgetItem(evt['date'].strftime("%b %d, %Y")))
            self.convergence_table.setItem(row, 1, QTableWidgetItem(f"{evt['score']:.1f}%"))
            self.convergence_table.setItem(row, 2, QTableWidgetItem(evt['long_count']))
            self.convergence_table.setItem(row, 3, QTableWidgetItem(evt['tzolkin']))
            self.convergence_table.setItem(row, 4, QTableWidgetItem(", ".join(evt['alignments'])))
        
        # Force UI refresh
        self.convergence_table.viewport().update()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MayanSteleApp()
    window.show()
    sys.exit(app.exec())