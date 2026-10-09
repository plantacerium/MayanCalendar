"""
Mayan Stele - Ultimate Mayan Calendar Application
Complete implementation with all calendar systems, fractal pattern detection,
and stunning visual displays.
"""
import sys
import math
from functools import reduce
from datetime import datetime, timedelta
import csv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QDateEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QSpinBox, QScrollArea, QGroupBox, QSplitter, QSlider, QProgressBar, QComboBox,
    QFileDialog, QMessageBox, QSizePolicy
)
from PySide6.QtCore import QDate, Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property, QRectF, Signal, QPointF, QPoint
from PySide6.QtGui import QFont, QFontMetrics, QColor, QPalette, QIcon, QPainter, QPainterPath, QPen, QBrush, QRadialGradient, QLinearGradient, QConicalGradient, QPolygonF

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
    
    def calculate_resonance_score(self, days_since_epoch, selected_cycles=None, natal_days=None):
        """Calculate how many cycles align using raw integers. No strings attached."""
        alignments = 0.0
        weights = 0.0
        
        checks = [
            ('Tzolkin', 260, 1.0),
            ('Haab', 365, 0.8),
            ('Calendar Round', 18980, 1.2),  # Reduced from 2.0 to balance double counting
            ('Lord of Night', 9, 0.5),
            ('819-Day', 819, 0.7),
            ('Venus', 584, 0.9),
            ('Mars', 780, 0.6),
            ('Tun', 360, 0.7),
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

    def find_convergences(self, start_date, total_days=365, selected_cycles=None, natal_days=None):
        """Optimized loop: Generates heavy dictionaries ONLY if the score hits the threshold."""
        if selected_cycles is None:
            selected_cycles = list(self.CYCLES.keys())
        
        events = []
        if isinstance(start_date, datetime):
            start = start_date
        else:
            start = datetime(start_date, 1, 1)
            
        # O(1) Optimization: Calculate the starting 'days_since_epoch' exactly once.
        start_jdn = self.converter._gregorian_to_jdn(start.year, start.month, start.day)
        base_days_since_epoch = start_jdn - self.converter.correlation_jdn
        
        for day_offset in range(total_days):
            # Pure integer addition instead of date manipulation
            current_days = base_days_since_epoch + day_offset
            
            # Pass the raw integer to the math engine
            score = self.calculate_resonance_score(current_days, selected_cycles, natal_days)
            
            # Condition check BEFORE building strings
            if score > 60:
                current = start + timedelta(days=day_offset)
                # Only request the heavy dictionary if it's a valid node
                data = self.converter.get_full_date(current.year, current.month, current.day)
                events.append({
                    'date': current,
                    'score': score,
                    'tzolkin': data['tzolkin'],
                    'haab': data['haab'],
                    'long_count': data['long_count'],
                    'alignments': self._get_alignments(current_days, natal_days),
                    'days_since_epoch': current_days,
                    'day_offset': day_offset
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
    
    def set_data(self, events, wave_packets=None, harmonic_links=None, start_date=None, range_days=365):
        self._events = events or []
        self._wave_packets = wave_packets or []
        self._harmonic_links = harmonic_links or []
        self._start_date = start_date
        self._range_days = max(1, range_days)
        self._hover_x = -1
        self._hover_info = None
        self.update()

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
            
            step_years = 1 if year_span <= 3 else (2 if year_span <= 10 else 5)
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

        # 5. Curva Continua de Coherencia Armónica (Osciloscopio / Envolvente Multiescala)
        if self._events and self._start_date and self._range_days > 0 and gw > 50:
            # Construir nodos de picos en espacio de píxeles para que la onda sea visible
            # tanto a 1 año como a 70 años sin perder continuidad ni diluirse
            peak_nodes = []
            if self._wave_packets:
                for pkt in self._wave_packets:
                    pk_days = (pkt['peak_date'] - self._start_date).days
                    if -50 <= pk_days <= (self._range_days + 50):
                        pk_x = left + (pk_days / self._range_days) * gw
                        # Ancho visible adaptativo en pantalla (entre 12 y 45 px)
                        dur_px = max(14.0, min(45.0, (pkt['duration'] / self._range_days) * gw * 2.5 + 16.0))
                        peak_nodes.append((pk_x, pkt['peak_score'], dur_px))
            else:
                for e in self._events:
                    e_days = (e['date'] - self._start_date).days
                    if -10 <= e_days <= (self._range_days + 10):
                        ex = left + (e_days / self._range_days) * gw
                        peak_nodes.append((ex, e['score'], 14.0))

            num_samples = max(gw, 160)
            wave_points = []
            
            for s_idx in range(num_samples + 1):
                px = left + (s_idx / num_samples) * gw
                
                # Campo de potencial continuo en la coordenada horizontal
                local_score = 0.0
                for pk_x, pk_score, pk_sigma in peak_nodes:
                    d_px = abs(px - pk_x)
                    if d_px < pk_sigma * 3.5:
                        contrib = pk_score * math.exp(-(d_px**2) / (2.0 * (pk_sigma**2)))
                        if contrib > local_score:
                            local_score = contrib
                
                py = top + gh - int((local_score / 100.0) * gh)
                wave_points.append(QPointF(px, py))
            
            # Construir trazado relleno con degradado espectral
            if wave_points:
                path_fill = QPainterPath()
                path_fill.moveTo(left, top + gh)
                for pt in wave_points:
                    path_fill.lineTo(pt)
                path_fill.lineTo(left + gw, top + gh)
                path_fill.closeSubpath()
                
                grad_wave = QLinearGradient(0, top, 0, top + gh)
                grad_wave.setColorAt(0.0, QColor(241, 196, 15, 175))   # Cima Oro puro radiante
                grad_wave.setColorAt(0.35, QColor(230, 126, 34, 125)) # Ámbar cósmico
                grad_wave.setColorAt(0.75, QColor(39, 174, 96, 45))   # Verde jade suave
                grad_wave.setColorAt(1.0, QColor(10, 8, 6, 10))
                painter.setBrush(QBrush(grad_wave))
                painter.setPen(Qt.NoPen)
                painter.drawPath(path_fill)
                
                # Trazo de la cresta superior luminiscente de la onda
                path_line = QPainterPath()
                path_line.moveTo(wave_points[0])
                for pt in wave_points[1:]:
                    path_line.lineTo(pt)
                pen_wave = QPen(QColor(241, 196, 15, 230), 1.8)
                painter.setPen(pen_wave)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path_line)

        # 5. Cúspides de las Macro-Ventanas (Solitones destacados)
        for packet in self._wave_packets:
            if self._start_date and self._range_days > 0:
                p_days = (packet['peak_date'] - self._start_date).days
                if 0 <= p_days <= self._range_days:
                    pk_x = left + int((p_days / self._range_days) * gw)
                    pk_y = top + gh - int((packet['peak_score'] / 100.0) * gh)
                    
                    # Halo concéntrico de energía
                    halo_grad = QRadialGradient(pk_x, pk_y, 14)
                    halo_grad.setColorAt(0.0, QColor(255, 215, 0, 200))
                    halo_grad.setColorAt(0.6, QColor(230, 126, 34, 80))
                    halo_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
                    painter.setBrush(QBrush(halo_grad))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(pk_x, pk_y), 14, 14)
                    
                    # Punto central radiante
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                    painter.setPen(QPen(QColor(218, 165, 32), 1.2))
                    painter.drawEllipse(QPointF(pk_x, pk_y), 3.5, 3.5)
                    
                    # Etiqueta de la Cúspide con píldora de fondo
                    painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
                    tag_text = f"{packet['peak_tzolkin']} ({packet['peak_score']:.1f}%)"
                    tag_metrics = painter.fontMetrics()
                    tag_w = tag_metrics.horizontalAdvance(tag_text) + 10
                    tag_h = tag_metrics.height() + 4
                    tag_bx = pk_x - tag_w // 2
                    tag_by = max(top + 8, pk_y - 20)
                    
                    painter.setBrush(QBrush(QColor(18, 15, 12, 220)))
                    painter.setPen(QPen(QColor(140, 115, 75), 1))
                    painter.drawRoundedRect(tag_bx, tag_by, tag_w, tag_h, 3, 3)
                    
                    painter.setPen(QPen(QColor(255, 225, 130), 1))
                    painter.drawText(tag_bx + 5, tag_by + tag_h - 4, tag_text)

        # 6. Arcos de Hiper-Enlaces Fractales entre Cúspides
        for link in self._harmonic_links[:3]:
            if self._start_date and self._range_days > 0:
                p1_days = (link['p1']['peak_date'] - self._start_date).days
                p2_days = (link['p2']['peak_date'] - self._start_date).days
                if 0 <= p1_days <= self._range_days and 0 <= p2_days <= self._range_days:
                    x1 = left + int((p1_days / self._range_days) * gw)
                    x2 = left + int((p2_days / self._range_days) * gw)
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
            hud_w, hud_h = 195, 62
            hud_x = self._hover_x + 12
            if hud_x + hud_w > w - 10:
                hud_x = self._hover_x - hud_w - 12
            hud_y = top + 8
            
            painter.setBrush(QBrush(QColor(15, 12, 10, 235)))
            painter.setPen(QPen(QColor(218, 165, 32, 190), 1.2))
            painter.drawRoundedRect(hud_x, hud_y, hud_w, hud_h, 5, 5)
            
            dt_str = self._hover_info['date'].strftime("%b %d, %Y")
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(QPen(QColor(241, 196, 15), 1))
            painter.drawText(hud_x + 8, hud_y + 16, f"⏱ {dt_str}")
            
            evt = self._hover_info.get('event')
            pkt = self._hover_info.get('packet')
            
            painter.setFont(QFont("Segoe UI", 8))
            if evt:
                painter.setPen(QPen(QColor(230, 230, 230), 1))
                painter.drawText(hud_x + 8, hud_y + 32, f"Score: {evt['score']:.1f}% • {evt['tzolkin']}")
                painter.setPen(QPen(QColor(170, 170, 170), 1))
                painter.drawText(hud_x + 8, hud_y + 48, f"{evt['long_count']}")
            elif pkt:
                painter.setPen(QPen(QColor(93, 173, 226), 1))
                painter.drawText(hud_x + 8, hud_y + 32, f"Ventana: {pkt['id']} ({pkt['duration']} días)")
                painter.setPen(QPen(QColor(170, 170, 170), 1))
                painter.drawText(hud_x + 8, hud_y + 48, f"Cúspide: {pkt['peak_tzolkin']} ({pkt['peak_score']:.1f}%)")
            else:
                painter.setPen(QPen(QColor(130, 130, 130), 1))
                painter.drawText(hud_x + 8, hud_y + 36, "Campo en equilibrio basal")


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
            
        # 1. Detección de Convergencias y Puntuación
        events = self.analyzer.find_convergences(start_datetime, total_days, selected, natal_days)
        
        # 2. Agrupamiento en Paquetes de Onda Coherente (Solitones)
        packets = self.analyzer.group_into_wave_packets(events)
        
        # 3. Detección de Hiper-Enlaces Fractales entre Cúspides
        links = self.analyzer.detect_harmonic_links(packets)
        
        self.fractal_events = events
        self.fractal_packets = packets
        self.fractal_links = links
        
        # 4. Actualizar Osciloscopio Continuo
        self.fractal_timeline.set_data(events, packets, links, start_datetime, total_days)
        
        # 5. Actualizar Barra de Resumen
        if packets:
            self.lbl_fractal_summary.setText(
                f"✦ {len(packets)} Ventanas Coherentes detectadas ({len(events)} días de alta resonancia) • {len(links)} Hiper-Enlaces Fractales"
            )
            self.lbl_fractal_summary.setStyleSheet("color: #F1C40F; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_fractal_summary.setText("No se encontraron convergencias que superen el umbral de coherencia del 60%.")
            self.lbl_fractal_summary.setStyleSheet("color: #aaa; font-size: 11px;")
            
        # 6. Renderizar Tabla y Panel de Hiper-Fractales
        self._render_fractal_table()
        self._render_harmonic_panel()
        
        if hasattr(self, 'btn_export'):
            self.btn_export.setEnabled(len(events) > 0)

    def _render_fractal_table(self):
        """Renderiza la tabla de resultados según el modo de vista seleccionado."""
        self.convergence_table.clear()
        
        if self.fractal_view_mode == "packets":
            # MODO 1: VENTANAS HOLÍSTICAS (EL TODO / PAQUETES DE ONDA)
            headers = ["ID", "Ventana Temporal", "Duración", "Cúspide / Pico", "Score Máx", "Energía Acum.", "Simetría (Solitón)", "Alineamientos Clave"]
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
                
                # Energía Acumulada
                item_en = QTableWidgetItem(f"{pkt['total_energy']:.1f}")
                item_en.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 5, item_en)
                
                # Simetría
                sym_label = "Solitón Puro" if pkt['symmetry_score'] >= 88 else ("Campana Coherente" if pkt['symmetry_score'] >= 70 else "Onda Asimétrica")
                item_sym = QTableWidgetItem(f"{pkt['symmetry_score']:.0f}% ({sym_label})")
                item_sym.setTextAlignment(Qt.AlignCenter)
                self.convergence_table.setItem(row, 6, item_sym)
                
                # Alineamientos
                self.convergence_table.setItem(row, 7, QTableWidgetItem(", ".join(pkt['alignments'])))
                
        else:
            # MODOS INDIVIDUALES: CRONOLÓGICO O SCORE DESCENDENTE
            headers = ["Fecha", "Score", "Long Count", "Tzolkin", "Ventana", "Alineamientos"]
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
                
                self.convergence_table.setItem(row, 5, QTableWidgetItem(", ".join(evt['alignments'])))
                
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
            
        for link in self.fractal_links:
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MayanSteleApp()
    window.show()
    sys.exit(app.exec())