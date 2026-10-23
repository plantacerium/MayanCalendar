"""
Mayan Profile Exporter - Multiformat Generator (SVG, Markdown, Plain Text, JSON)
Generates high-precision archaeological, astronomical, and cosmological Mayan profiles.
"""
import json
import math
from datetime import datetime, date

# Import biological & vibrational resonance dictionary from resonaxers if available
try:
    from resonaxers import RESONANCE_MAP
except ImportError:
    RESONANCE_MAP = None

class MayanProfileExporter:
    """Exports full Mayan calendar data into SVG, Markdown, Plain Text, and JSON formats."""

    @staticmethod
    def _extract_bio_resonance(tzolkin_name):
        """Finds matching amino acid and vibrational mapping from RESONANCE_MAP."""
        if not RESONANCE_MAP:
            return None
        
        name_clean = tzolkin_name.strip()
        for item in RESONANCE_MAP:
            seal_str = item.get("seal", "")
            if name_clean.lower() in seal_str.lower():
                return item
        return None

    @classmethod
    def _get_kuramoto_and_eclipse(cls, full_data):
        days = full_data.get("days_since_epoch", 0)
        try:
            import importlib
            stele_module = importlib.import_module("mayan-stele")
            converter = stele_module.MayanConverter()
            analyzer = stele_module.FractalPatternAnalyzer(converter)
            km = analyzer.calculate_kuramoto_order(days)
            ecl = analyzer.get_dresden_eclipse_info(days)
            return km, ecl
        except Exception:
            return None, None

    @classmethod
    def export_json(cls, full_data, correlation_name="GMT (584283)", natal_days=None, indent=2):
        """Produces a structured JSON dictionary."""
        tz_name = full_data.get("tzolkin_name", "")
        bio = cls._extract_bio_resonance(tz_name)
        km, ecl = cls._get_kuramoto_and_eclipse(full_data)
        
        payload = {
            "version": "1.0.0",
            "system": "Mayan Stele Chrono-Cosmology Core",
            "generated_at": datetime.now().isoformat(),
            "correlation": {
                "name": correlation_name,
                "jdn_offset": full_data.get("jdn", 0) - full_data.get("days_since_epoch", 0)
            },
            "gregorian": {
                "julian_day_number": full_data.get("jdn"),
                "days_since_epoch": full_data.get("days_since_epoch"),
            },
            "long_count": {
                "notation": full_data.get("long_count"),
                "parts": {
                    "baktun": full_data.get("long_count_parts", [0]*5)[0],
                    "katun": full_data.get("long_count_parts", [0]*5)[1],
                    "tun": full_data.get("long_count_parts", [0]*5)[2],
                    "uinal": full_data.get("long_count_parts", [0]*5)[3],
                    "kin": full_data.get("long_count_parts", [0]*5)[4],
                },
                "deep_time_cycles": {
                    "alautun": full_data.get("deep_long_count", [0]*9)[0],
                    "kinchiltun": full_data.get("deep_long_count", [0]*9)[1],
                    "kalabtun": full_data.get("deep_long_count", [0]*9)[2],
                    "piktun": full_data.get("deep_long_count", [0]*9)[3],
                }
            },
            "tzolkin": {
                "full": full_data.get("tzolkin"),
                "number": full_data.get("tzolkin_num"),
                "name": full_data.get("tzolkin_name"),
                "glyph": full_data.get("tzolkin_glyph"),
                "meaning": full_data.get("tzolkin_meaning"),
                "index_20": full_data.get("tzolkin_idx"),
                "kin_in_tzolkin": ((full_data.get("days_since_epoch", 0) + 159) % 260) + 1
            },
            "haab": {
                "full": full_data.get("haab"),
                "day": full_data.get("haab_day"),
                "month": full_data.get("haab_month"),
                "meaning": full_data.get("haab_meaning"),
                "month_index": full_data.get("haab_idx")
            },
            "calendar_round": {
                "notation": full_data.get("calendar_round"),
                "position_in_52_years": full_data.get("calendar_round_pos"),
                "elapsed_years": round(full_data.get("calendar_round_years", 0), 2),
                "cycle_total_days": 18980
            },
            "astronomical_cycles": {
                "lord_of_night": {
                    "code": full_data.get("lord"),
                    "name": full_data.get("lord_name")
                },
                "venus": {
                    "canonical_pos_584": full_data.get("venus_pos"),
                    "phase": full_data.get("venus_phase"),
                    "nasa_synodic_pos": full_data.get("venus_astro_pos")
                },
                "mars": {
                    "canonical_pos_780": full_data.get("mars_pos")
                },
                "paris_codex_zodiac": {
                    "constellation_idx": full_data.get("zodiac_idx"),
                    "name": full_data.get("zodiac_name"),
                    "spanish_name": full_data.get("zodiac_spanish"),
                    "glyph": full_data.get("zodiac_glyph"),
                    "western_equivalent": full_data.get("zodiac_western"),
                    "solar_ecliptic_deg": full_data.get("zodiac_ecliptic_deg"),
                    "sector_range": full_data.get("zodiac_range"),
                    "cosmovision": full_data.get("zodiac_meaning")
                },
                "computing_year_364": full_data.get("season_364_data", {}),
                "dresden_mars_table": full_data.get("mars_dresden_data", {}),
                "madrid_codex_almanacs": full_data.get("madrid_almanac_data", {}),
                "kawiil_819": {
                    "position_819": full_data.get("kawiil_pos"),
                    "quadrant_direction": full_data.get("kawiil_color")
                },
                "lunar": {
                    "moon_age_days": round(full_data.get("moon_age", 0), 2),
                    "phase": full_data.get("moon_phase"),
                    "illumination": full_data.get("moon_illumination"),
                    "supplementary_series": {
                        "glyph_c_lunation": full_data.get("glyph_c"),
                        "glyph_a_duration": full_data.get("glyph_a"),
                        "glyph_x_deity": full_data.get("glyph_x")
                    }
                }
            }
        }
        
        if bio:
            payload["biomolecular_resonance"] = {
                "amino_acid": bio.get("amino"),
                "formula": bio.get("formula"),
                "group": bio.get("group"),
                "bija_mantra": bio.get("bija"),
                "kototama": bio.get("kototama"),
                "instruction": bio.get("instruction"),
                "codons": [c.get("triplet") for c in bio.get("codons", [])]
            }

        if km:
            payload["kuramoto_coherence"] = km
        if ecl:
            payload["dresden_eclipse_table"] = ecl

        return json.dumps(payload, ensure_ascii=False, indent=indent)

    @classmethod
    def export_markdown(cls, full_data, gregorian_date_str="", correlation_name="GMT (584283)"):
        """Generates a sacred archaeological and cosmological markdown report."""
        tz_name = full_data.get("tzolkin_name", "")
        bio = cls._extract_bio_resonance(tz_name)
        km, ecl = cls._get_kuramoto_and_eclipse(full_data)
        lc = full_data.get("long_count", "0.0.0.0.0")
        tz = full_data.get("tzolkin", "")
        hb = full_data.get("haab", "")
        cr = full_data.get("calendar_round", "")
        lord = f"{full_data.get('lord', '')} — {full_data.get('lord_name', '')}"
        v_phase = full_data.get("venus_phase", "")
        v_pos = full_data.get("venus_pos", 0)
        v_nasa = full_data.get("venus_astro_pos", 0)
        m_phase = full_data.get("moon_phase", "")
        m_age = full_data.get("moon_age", 0)
        m_illum = full_data.get("moon_illumination", "")
        kaw = f"{full_data.get('kawiil_color', '')} (Día {full_data.get('kawiil_pos', 0)}/819)"
        c_parts = full_data.get("long_count_parts", [0]*5)
        deep = full_data.get("deep_long_count", [0]*9)

        md = []
        md.append("# ⚱ PERFIL ASTRONÓMICO Y CRONOLÓGICO MAYA")
        md.append(f"> **Fecha Gregoriana:** `{gregorian_date_str}` • **Correlación:** `{correlation_name}` • **JDN:** `{full_data.get('jdn', 0):,}`")
        md.append("")
        
        md.append("## 🏛️ Cuenta Larga de la Estela")
        md.append("```text")
        md.append(f"┌────────────────────────────────────────────────────────────────────────┐")
        md.append(f"│  ESTELA PRINCIPAL: {lc:<51} │")
        md.append(f"│  {c_parts[0]} Baktún • {c_parts[1]} Katún • {c_parts[2]} Tún • {c_parts[3]} Uinal • {c_parts[4]} K'in{' ' * (37 - len(str(c_parts)))}│")
        md.append(f"│  Días desde el Día Cero (4 Ahau 8 Cumku): {full_data.get('days_since_epoch', 0):<26,} │")
        md.append(f"└────────────────────────────────────────────────────────────────────────┘")
        md.append("```")
        md.append("")

        md.append("## 🔮 Rueda Calendárica Sagrada & Civil")
        md.append("| Parámetro | Valor | Arquetipo y Significado |")
        md.append("| :--- | :--- | :--- |")
        md.append(f"| **Tzolkin (Sagrado 260d)** | `{tz}` {full_data.get('tzolkin_glyph','')} | {full_data.get('tzolkin_meaning','')} |")
        md.append(f"| **Haab' (Civil 365d)** | `{hb}` | {full_data.get('haab_meaning','')} |")
        md.append(f"| **Rueda Calendárica** | `{cr}` | Posición {full_data.get('calendar_round_pos', 0):,} / 18,980 días ({round(full_data.get('calendar_round_years',0),1)} años solares) |")
        md.append(f"| **Señor de la Noche** | `{full_data.get('lord','')}` | {full_data.get('lord_name','')} (Ciclo de 9 Noches) |")
        md.append(f"| **Ciclo K'awiil (819d)** | `{kaw}` | Deidad cuatripartita en 4 cuadrantes cósmicos |")
        md.append("")

        md.append("## 🌌 Observatorio Planetario & Serie Lunar")
        md.append("| Ciclo Celeste | Posición | Fase / Arquetipo |")
        md.append("| :--- | :--- | :--- |")
        if full_data.get("zodiac_name"):
            md.append(f"| **Zodíaco Maya (Códice de París)** | {full_data.get('zodiac_glyph','')} **{full_data.get('zodiac_name','')}** ({full_data.get('zodiac_spanish','')}) | Región: `{full_data.get('zodiac_western','')}` • Solar: `{full_data.get('zodiac_ecliptic_deg', 0)}°` ({full_data.get('zodiac_range','')}) |")
        if full_data.get("season_364_station"):
            md.append(f"| **Año Estacional 364d (Dresde)** | {full_data.get('season_364_glyph','')} **{full_data.get('season_364_station','')}** ({full_data.get('season_364_quarter_name','')}) | Día `{full_data.get('season_364_day_in_quarter', 1)}`/91 (Año: `{full_data.get('season_364_day', 0)}`/364d) • {full_data.get('season_364_deity','')} |")
        md.append(f"| **Venus (Códice Dresde)** | Día `{v_pos}` / 584d | **{v_phase}** (Astrométrico NASA: `{v_nasa}`d) |")
        if full_data.get("mars_station_tzolkin"):
            m_retro = " [⚠️ Bucle Retrógrado - Bestia Celeste]" if full_data.get("mars_is_retrograde") else ""
            md.append(f"| **Marte (Códice Dresde pp. 43b-45b)** | Día `{full_data.get('mars_pos',0)}` / 780d | {full_data.get('mars_station_glyph','')} **{full_data.get('mars_station_tzolkin','')}** • Día `{full_data.get('mars_day_in_station',1)}`/78 • {full_data.get('mars_phase_name','')}{m_retro} |")
        else:
            md.append(f"| **Marte (Sinódico)** | Día `{full_data.get('mars_pos',0)}` / 780d | Ciclo bélico y agrícola de 780 días |")
        md.append(f"| **Luna (Fase & Disco)** | Edad `{m_age:.1f}` días | {m_phase} • Iluminación: `{m_illum}` |")
        md.append(f"| **Serie Suplementaria** | Lunación `{full_data.get('glyph_c', 1)}` de 6 | Glifo C: {full_data.get('glyph_c', 1)} • Glifo A: {full_data.get('glyph_a', 30)}d • Glifo X: {full_data.get('glyph_x', '')} |")
        md.append("")

        if full_data.get("madrid_almanac_data"):
            mad = full_data["madrid_almanac_data"]
            yb = mad.get("madrid_bearer", "")
            y_card = f"{mad.get('madrid_cardinal', '')} ({mad.get('madrid_color', '')})"
            uayeb_txt = f"⚠️ EN UAYEB (Día {mad.get('uayeb_day', 1)}/5)" if mad.get("is_uayeb") else f"Faltan {mad.get('days_to_uayeb', 0)} días (Año Nuevo en {mad.get('days_to_next_year', 0)}d)"
            md.append("## 🌽 Almanaques del Códice de Madrid (Tro-Cortesiano)")
            md.append("| Ciclo / Tratado | Registro en Códice | Interpretación y Presagio |")
            md.append("| :--- | :--- | :--- |")
            md.append(f"| **Portador del Año (Cuch Hab)** | {mad.get('madrid_glyph','')} **{yb}** ({y_card}) | Presagio: {mad.get('madrid_climate_omen','')} • {mad.get('madrid_crop_omen','')} |")
            md.append(f"| **Tránsito del Uayeb** | {uayeb_txt} | Patrono: {mad.get('madrid_uayeb_patron','')} • Ritual: {mad.get('madrid_ritual','')} |")
            md.append(f"| **Fisiología de la Lluvia (Chac)** | {mad.get('chac_vessel_glyph','')} **{mad.get('chac_vessel_name','')}** | {mad.get('chac_manifestation','')} • {mad.get('chac_action','')} |")
            md.append(f"| **Fenología del Maíz (Ixim)** | {mad.get('maize_glyph','')} **{mad.get('maize_stage_name','')}** | {mad.get('maize_action','')} • Consejo: *{mad.get('maize_advice','')}* |")
            md.append(f"| **Apicultura Melipona (Xunán Kab)** | 🐝 **Ah Muzencab** (Día {mad.get('melipona_day_in_52', 1)}/52) | Fase: {mad.get('melipona_phase','')} • {mad.get('melipona_ritual','')} |")
            md.append("")

        if km and ecl:
            md.append("## 🌀 Dinámica No Lineal de Kuramoto & Eclipses de Dresde")
            md.append("| Métrica / Ciclo | Valor | Significado / Fase |")
            md.append("| :--- | :--- | :--- |")
            lock_str = "Sincronización Bloqueada (Phase-Locking)" if km.get('is_locked') else "Fase en Dispersión Dinámica"
            md.append(f"| **Parámetro Kuramoto (R)** | **{km.get('r',0)*100:.1f}%** | {lock_str} |")
            md.append(f"| **Vector Director Cósmico (Ψ)** | **{km.get('psi_deg',0):.0f}°** | Orientación de Fase Colectiva |")
            ecl_status = ecl.get('eclipse_type') if ecl.get('is_eclipse_window') else "Sin eclipse cercano (Ventana basal)"
            md.append(f"| **Alerta Eclipse de Dresde** | **{ecl_status}** | Distancia al Nodo Dracónico: `{ecl.get('dist_to_node_days', 0)}` días |")
            md.append(f"| **Ciclo Dresde de 405 Lunas** | Día `{ecl.get('dresden_cycle_day',0)}` / 11,960 | Códice de Dresde pp. 51a-58b (46 Tzolk'in) |")
            md.append("")

        md.append("## ⏳ Eras Cósmicas del Tiempo Profundo")
        md.append(f"- **Piktun (2,880,000 días):** `{deep[3]}`")
        md.append(f"- **Kalabtun (57,600,000 días):** `{deep[2]}`")
        md.append(f"- **Kinchiltun (1,152,000,000 días):** `{deep[1]}`")
        md.append(f"- **Alautun (23,040,000,000 días):** `{deep[0]}`")
        md.append("")

        if bio:
            md.append("## 🧬 Resonancia Biológica y Cimática (Matriz Resonaxers)")
            md.append(f"- **Sello / Glifo:** `{bio.get('seal', '')}`")
            md.append(f"- **Aminoácido Correspondiente:** **{bio.get('amino', '')}** (`{bio.get('formula', '')}`)")
            md.append(f"- **Grupo Químico:** `{bio.get('group', '')}`")
            md.append(f"- **Kototama (Vibración Vocal):** `{bio.get('kototama', '')}` • **Bīja Mantra:** `{bio.get('bija', '')}`")
            md.append(f"- **Instrucción de Enlace:** *{bio.get('instruction', '')}*")
            if bio.get("codons"):
                triplets = ", ".join([f"`{c['triplet']}` ({c.get('action','')})" for c in bio.get("codons", [])])
                md.append(f"- **Codones de ARN:** {triplets}")
            md.append("")

        md.append("---")
        md.append("*Generado automáticamente por Mayan Stele — Herramienta Arqueológica y Fractal Universal.*")
        return "\n".join(md)

    @classmethod
    def export_text(cls, full_data, gregorian_date_str="", correlation_name="GMT (584283)"):
        """Generates a clean Unicode/ASCII stone monument text profile."""
        tz_name = full_data.get("tzolkin_name", "")
        bio = cls._extract_bio_resonance(tz_name)
        lc = full_data.get("long_count", "0.0.0.0.0")
        c_parts = full_data.get("long_count_parts", [0]*5)
        tz = full_data.get("tzolkin", "")
        hb = full_data.get("haab", "")
        cr = full_data.get("calendar_round", "")
        lord = f"{full_data.get('lord', '')} ({full_data.get('lord_name', '')})"
        v_phase = full_data.get("venus_phase", "")
        v_pos = full_data.get("venus_pos", 0)
        m_phase = full_data.get("moon_phase", "")
        m_illum = full_data.get("moon_illumination", "")
        kaw = f"{full_data.get('kawiil_color', '')} (Día {full_data.get('kawiil_pos', 0)}/819)"
        
        lines = [
            "╔══════════════════════════════════════════════════════════════════════════╗",
            "║                      ESTELA CRONOLÓGICA MAYA                             ║",
            "╠══════════════════════════════════════════════════════════════════════════╣",
            f"║  Fecha Gregoriana:   {gregorian_date_str:<51} ║",
            f"║  Correlación:        {correlation_name:<51} ║",
            f"║  Día Juliano (JDN):  {full_data.get('jdn', 0):<51,} ║",
            f"║  Días desde Era 0:   {full_data.get('days_since_epoch', 0):<51,} ║",
            "╟──────────────────────────────────────────────────────────────────────────╢",
            f"║  Cuenta Larga:       {lc:<51} ║",
            f"║  Desglose:           {c_parts[0]} Baktún . {c_parts[1]} Katún . {c_parts[2]} Tún . {c_parts[3]} Uinal . {c_parts[4]} K'in{' ' * (30 - len(str(c_parts)))} ║",
            f"║  Tzolk'in (260d):    {tz} ({full_data.get('tzolkin_meaning', '')}){' ' * max(0, 32 - len(tz) - len(full_data.get('tzolkin_meaning', '')))} ║",
            f"║  Haab' (365d):       {hb} ({full_data.get('haab_meaning', '')}){' ' * max(0, 35 - len(hb) - len(full_data.get('haab_meaning', '')))} ║",
            f"║  Rueda Calendárica:  {cr:<51} ║",
            f"║  Señor de la Noche:  {lord:<51} ║",
            f"║  Ciclo 819 (K'awiil):{kaw:<51} ║",
            "╟──────────────────────────────────────────────────────────────────────────╢",
            f"║  Zodíaco París:      {full_data.get('zodiac_glyph','')} {full_data.get('zodiac_name','')} ({full_data.get('zodiac_spanish','')}) • Solar: {full_data.get('zodiac_ecliptic_deg', 0)}°{' ' * 20} ║",
            f"║  Año 364d (Dresde):  {full_data.get('season_364_glyph','')} {full_data.get('season_364_station','')} ({full_data.get('season_364_cardinal','')}) • Día {full_data.get('season_364_day_in_quarter', 1)}/91{' ' * 10} ║",
            f"║  Ciclo de Venus:     Día {v_pos}/584 • {v_phase:<39} ║",
            f"║  Marte (Dresde 780d): Día {full_data.get('mars_pos',0):<3}/780 • {full_data.get('mars_station_glyph','')} {full_data.get('mars_station_tzolkin','')} ({full_data.get('mars_day_in_station',1)}/78d){' [RETRÓGRADO]' if full_data.get('mars_is_retrograde') else ''}{' ' * 15} ║",
            f"║  Portador Año Madrid: {full_data.get('madrid_glyph','')} {full_data.get('madrid_year_bearer','')} ({full_data.get('madrid_cardinal','')}) • Uayeb en {full_data.get('days_to_uayeb', 0):<3}d{' ' * 12} ║",
            f"║  Chac & Maíz Madrid: {full_data.get('chac_vessel_glyph','')} {full_data.get('chac_vessel_name','')} • {full_data.get('maize_glyph','')} {full_data.get('maize_stage_name','')}{' ' * 20} ║",
            f"║  Melipona (52d):     🐝 Día {full_data.get('melipona_day',1)}/52 • {full_data.get('melipona_phase','')}{' ' * 20} ║",
            f"║  Ciclo Lunar:        {m_phase} • Ilum: {m_illum:<36} ║",
            f"║  Serie Lunar:        Glifo C: {full_data.get('glyph_c', 1)} • Glifo A: {full_data.get('glyph_a', 30)}d • {full_data.get('glyph_x', ''):<24} ║",
        ]

        km, ecl = cls._get_kuramoto_and_eclipse(full_data)
        if km or ecl:
            lines.append("╟──────────────────────────────────────────────────────────────────────────╢")
            if km:
                lines.append(f"║  Sincronía Kuramoto: R = {km.get('r',0)*100:.1f}% • Vector Ψ = {km.get('psi_deg',0):.0f}°{' ' * 28} ║")
            if ecl and ecl.get('is_eclipse_window'):
                lines.append(f"║  ⚠️ ALERTA DRESDE:    {ecl.get('eclipse_type'):<50} ║")
            elif ecl:
                lines.append(f"║  Códice Dresde 405L: Día {ecl.get('dresden_cycle_day',0):<5}/11960 • Dist. Nodo: {ecl.get('dist_to_node_days',0):<4}d{' ' * 17} ║")
        
        if bio:
            lines.append("╟──────────────────────────────────────────────────────────────────────────╢")
            lines.append(f"║  Aminoácido Sello:   {bio.get('amino', ''):<51} ║")
            lines.append(f"║  Fórmula / Grupo:    {bio.get('formula', '')} • {bio.get('group', ''):<38} ║")
            lines.append(f"║  Kototama / Bija:    {bio.get('kototama', '')} • Mantra: {bio.get('bija', ''):<32} ║")
            
        lines.append("╚══════════════════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    @classmethod
    def export_svg(cls, full_data, gregorian_date_str="", width=800, height=600):
        """
        Renders a stunning standalone SVG vector Mayan Stele / Monument with:
        - Deep stone carved background with golden and obsidian gradient
        - Long Count glyph cartouches and numerical bar-and-dot symbols
        - Tzolkin & Haab concentric seal shields
        - Lords of Night and Venus Phase indicators
        - Moon phase illumination disc
        """
        lc = full_data.get("long_count", "0.0.0.0.0")
        c_parts = full_data.get("long_count_parts", [0]*5)
        tz = full_data.get("tzolkin", "")
        tz_glyph = full_data.get("tzolkin_glyph", "☀")
        hb = full_data.get("haab", "")
        cr = full_data.get("calendar_round", "")
        lord = full_data.get("lord", "G1")
        lord_name = full_data.get("lord_name", "").split(" - ")[0]
        v_phase = full_data.get("venus_phase", "")
        v_pos = full_data.get("venus_pos", 0)
        m_phase = full_data.get("moon_phase", "")
        m_illum = full_data.get("moon_illumination", "100%")
        jdn = full_data.get("jdn", 0)
        
        # Helper to draw Mayan dot and bar numerals
        def render_mayan_numeral(val, cx, cy):
            bars = val // 5
            dots = val % 5
            svg_num = []
            
            # Draw dots
            if dots > 0:
                dot_r = 3.5
                dot_spacing = 11
                start_x = cx - ((dots - 1) * dot_spacing) / 2.0
                dot_y = cy - (bars * 6) - 4
                for d in range(dots):
                    svg_num.append(f'<circle cx="{start_x + d * dot_spacing:.1f}" cy="{dot_y:.1f}" r="{dot_r}" fill="#F1C40F" stroke="#221C11" stroke-width="1"/>')
            
            # Draw bars
            if bars > 0:
                bar_w = 32
                bar_h = 4
                for b in range(bars):
                    by = cy - ((bars - 1 - b) * 7)
                    svg_num.append(f'<rect x="{cx - bar_w/2:.1f}" y="{by:.1f}" width="{bar_w}" height="{bar_h}" rx="2" fill="#E67E22" stroke="#221C11" stroke-width="1"/>')
                    
            if val == 0:
                # Mayan zero shell glyph symbol
                svg_num.append(f'<ellipse cx="{cx}" cy="{cy}" rx="14" ry="7" fill="#C0392B" stroke="#F1C40F" stroke-width="1.2"/>')
                svg_num.append(f'<line x1="{cx-10}" y1="{cy}" x2="{cx+10}" y2="{cy}" stroke="#F1C40F" stroke-width="1"/>')
                
            return "".join(svg_num)

        # Build Long Count Cartouches (Baktun, Katun, Tun, Uinal, Kin)
        lc_labels = ["BAKTUN", "KATUN", "TUN", "UINAL", "K'IN"]
        cartouche_svg = []
        c_start_x = 110
        c_spacing = 120
        c_y = 190
        for idx, (label, val) in enumerate(zip(lc_labels, c_parts)):
            cx = c_start_x + idx * c_spacing
            num_art = render_mayan_numeral(val, cx, c_y + 12)
            cartouche_svg.append(f"""
            <!-- Cartouche {label} -->
            <g>
                <rect x="{cx - 50}" y="{c_y - 35}" width="100" height="75" rx="8" fill="#24201A" stroke="#7A684D" stroke-width="1.5"/>
                <rect x="{cx - 46}" y="{c_y - 31}" width="92" height="67" rx="6" fill="#181512" stroke="#3D3325" stroke-width="1"/>
                <text x="{cx}" y="{c_y - 18}" font-family="'Segoe UI', Georgia, serif" font-size="10" font-weight="bold" fill="#8A9A5B" text-anchor="middle" letter-spacing="1">{label}</text>
                {num_art}
                <text x="{cx}" y="{c_y + 32}" font-family="'Segoe UI', Georgia, serif" font-size="12" font-weight="bold" fill="#F4D03F" text-anchor="middle">{val}</text>
            </g>
            """)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <!-- Background Gradients -->
    <linearGradient id="steleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E1A16"/>
      <stop offset="50%" stop-color="#14110E"/>
      <stop offset="100%" stop-color="#0B0907"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#B7950B"/>
      <stop offset="50%" stop-color="#F1C40F"/>
      <stop offset="100%" stop-color="#D4AC0D"/>
    </linearGradient>
    <radialGradient id="centerGlow" cx="50%" cy="30%" r="60%">
      <stop offset="0%" stop-color="#D4AC0D" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.8"/>
    </filter>
  </defs>

  <!-- Background Base -->
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0A0806"/>
  <rect x="15" y="15" width="{width-30}" height="{height-30}" rx="14" fill="url(#steleGrad)" stroke="#554632" stroke-width="2.5"/>
  <rect x="25" y="25" width="{width-50}" height="{height-50}" rx="10" fill="none" stroke="#2B2319" stroke-width="1.2"/>
  <rect x="15" y="15" width="{width-30}" height="{height-30}" fill="url(#centerGlow)"/>

  <!-- Ornamental Mayan Corner Glyphs -->
  <path d="M 30,55 L 55,30 M 30,65 L 65,30 M 30,75 L 75,30" stroke="#7A684D" stroke-width="1.5"/>
  <path d="M {width-30},55 L {width-55},30 M {width-30},65 L {width-65},30 M {width-30},75 L {width-75},30" stroke="#7A684D" stroke-width="1.5"/>
  <path d="M 30,{height-55} L 55,{height-30} M 30,{height-65} L 65,{height-30} M 30,{height-75} L 75,{height-30}" stroke="#7A684D" stroke-width="1.5"/>
  <path d="M {width-30},{height-55} L {width-55},{height-30} M {width-30},{height-65} L {width-65},{height-30} M {width-30},{height-75} L {width-75},{height-30}" stroke="#7A684D" stroke-width="1.5"/>

  <!-- Stele Header -->
  <text x="{width/2}" y="62" font-family="'Segoe UI', Georgia, serif" font-size="24" font-weight="900" fill="url(#goldGrad)" text-anchor="middle" letter-spacing="4" filter="url(#dropShadow)">⚱ ESTELA SAGRADA MAYA ⚱</text>
  <text x="{width/2}" y="88" font-family="'Segoe UI', Georgia, serif" font-size="12" fill="#BDC3C7" text-anchor="middle">FECHA GREGORIANA: {gregorian_date_str.upper()} • JDN {jdn:,}</text>

  <!-- Divider Line -->
  <line x1="80" y1="102" x2="{width-80}" y2="102" stroke="#7A684D" stroke-width="1.5"/>
  <circle cx="{width/2}" cy="102" r="4.5" fill="#F1C40F"/>

  <!-- Long Count Banner -->
  <rect x="180" y="118" width="{width-360}" height="32" rx="6" fill="#1C1814" stroke="#B7950B" stroke-width="1.2"/>
  <text x="{width/2}" y="139" font-family="'Segoe UI', Georgia, serif" font-size="15" font-weight="bold" fill="#F4D03F" text-anchor="middle" letter-spacing="2">CUENTA LARGA: {lc}</text>

  <!-- Cartouches Row -->
  {"".join(cartouche_svg)}

  <!-- Left Column Card: Tzolkin & Haab -->
  <g transform="translate(60, 290)">
    <rect width="320" height="255" rx="10" fill="#181512" stroke="#4A3D2C" stroke-width="1.5" filter="url(#dropShadow)"/>
    
    <!-- Tzolkin Header -->
    <rect x="15" y="15" width="290" height="42" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="41" font-size="20">{tz_glyph}</text>
    <text x="62" y="32" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">TZOLK'IN SAGRADO (260 DÍAS)</text>
    <text x="62" y="49" font-family="'Segoe UI', serif" font-size="16" fill="#F1C40F" font-weight="bold">{tz}</text>

    <!-- Haab Header -->
    <rect x="15" y="68" width="290" height="42" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="94" font-size="20">🌽</text>
    <text x="62" y="85" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">HAAB' CIVIL (365 DÍAS)</text>
    <text x="62" y="102" font-family="'Segoe UI', serif" font-size="16" fill="#F1C40F" font-weight="bold">{hb}</text>

    <!-- Calendar Round -->
    <rect x="15" y="121" width="290" height="58" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="139" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">RUEDA CALENDÁRICA (52 AÑOS)</text>
    <text x="30" y="158" font-family="'Segoe UI', serif" font-size="15" fill="#E67E22" font-weight="bold">{cr}</text>
    <text x="30" y="172" font-family="'Segoe UI', serif" font-size="10" fill="#AAA">Posición {full_data.get('calendar_round_pos', 0):,} de 18,980 kines</text>

    <!-- Lord of the Night -->
    <rect x="15" y="190" width="290" height="50" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="209" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">SEÑOR DE LA NOCHE (G1-G9)</text>
    <text x="30" y="228" font-family="'Segoe UI', serif" font-size="14" fill="#E74C3C" font-weight="bold">{lord}: {lord_name}</text>
  </g>

  <!-- Right Column Card: Astronomical Observations -->
  <g transform="translate(420, 290)">
    <rect width="320" height="255" rx="10" fill="#181512" stroke="#4A3D2C" stroke-width="1.5" filter="url(#dropShadow)"/>

    <!-- Venus Cycle -->
    <rect x="15" y="15" width="290" height="68" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="34" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">CICLO VENUSIANO (584 DÍAS)</text>
    <text x="30" y="53" font-family="'Segoe UI', serif" font-size="15" fill="#5DADE2" font-weight="bold">Día {v_pos} / 584 • {v_phase}</text>
    <text x="30" y="70" font-family="'Segoe UI', serif" font-size="10" fill="#AAA">Cánon Dresde • Posición NASA: {full_data.get('venus_astro_pos', 0)}d</text>

    <!-- Moon & Lunar Series -->
    <rect x="15" y="94" width="290" height="74" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="113" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">OBSERVACIÓN LUNAR &amp; SERIE SUPLEMENTARIA</text>
    <text x="30" y="132" font-family="'Segoe UI', serif" font-size="14" fill="#F5B041" font-weight="bold">{m_phase} ({m_illum})</text>
    <text x="30" y="150" font-family="'Segoe UI', serif" font-size="11" fill="#DDD">Glifo C: {full_data.get('glyph_c', 1)} • Glifo A: {full_data.get('glyph_a', 30)}d • {full_data.get('glyph_x', '')}</text>

    <!-- 819-Day Cycle K'awiil -->
    <rect x="15" y="179" width="290" height="61" rx="6" fill="#241E17" stroke="#7A684D" stroke-width="1"/>
    <text x="30" y="198" font-family="'Segoe UI', serif" font-size="10" fill="#8A9A5B" font-weight="bold">CICLO K'AWIIL DE 819 DÍAS</text>
    <text x="30" y="217" font-family="'Segoe UI', serif" font-size="14" fill="#F1C40F" font-weight="bold">{full_data.get('kawiil_color', 'Red (East)')}</text>
    <text x="30" y="231" font-family="'Segoe UI', serif" font-size="10" fill="#AAA">Posición día {full_data.get('kawiil_pos', 0)} / 819 en los 4 cuadrantes</text>
  </g>

  <!-- Stele Bottom Plaque / Stamp -->
  <text x="{width/2}" y="{height - 24}" font-family="'Segoe UI', Georgia, serif" font-size="10" fill="#7A684D" text-anchor="middle" letter-spacing="1">ESCULPIDO POR MAYAN STELE CHRONO-CORE • CORRELACIÓN GMT 584283</text>
</svg>"""
        return svg
