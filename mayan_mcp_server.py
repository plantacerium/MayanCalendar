#!/usr/bin/env python3
"""
Mayan Stele MCP Server
Model Context Protocol (MCP) server for Mayan Calendar calculations, astronomical cycles,
harmonic resonance detection, and chronological epigraphy.
Compatible with Antigravity IDE, Cursor, Claude Desktop, and standard JSON-RPC 2.0 stdio MCP clients.
"""
import sys
import json
import traceback
from datetime import datetime

# Ensure UTF-8 I/O encoding across platforms, particularly on Windows consoles
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import Mayan core engines
import importlib
try:
    stele_module = importlib.import_module("mayan-stele")
    MayanConverter = stele_module.MayanConverter
    FractalPatternAnalyzer = stele_module.FractalPatternAnalyzer
except Exception as e:
    # Fallback to local import if needed
    sys.path.append(".")
    stele_module = importlib.import_module("mayan-stele")
    MayanConverter = stele_module.MayanConverter
    FractalPatternAnalyzer = stele_module.FractalPatternAnalyzer

try:
    from mayan_exporter import MayanProfileExporter
except ImportError:
    import mayan_exporter
    MayanProfileExporter = mayan_exporter.MayanProfileExporter

# Instantiate core converter and analyzer with standard GMT correlation
converter = MayanConverter(correlation_jdn=584283)
analyzer = FractalPatternAnalyzer(converter)

TOOLS = [
    {
        "name": "mayan_convert_gregorian",
        "description": "Convierte una fecha gregoriana (año, mes, día) al sistema de calendario maya completo: Cuenta Larga, Tzolk'in sagrado, Haab' civil, Rueda Calendárica de 52 años, Señor de la Noche (G1-G9), ciclo de Venus (Cánon Dresde y astrométrico NASA), fase lunar, serie suplementaria y ciclo K'awiil de 819 días.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Año gregoriano (ej. 2026, 1993, 716)"},
                "month": {"type": "integer", "description": "Mes gregoriano (1 a 12)"},
                "day": {"type": "integer", "description": "Día del mes gregoriano (1 a 31)"},
                "correlation": {
                    "type": "string",
                    "enum": ["GMT", "GMT+2", "Spinden"],
                    "description": "Correlación arqueológica. Por defecto GMT (584283)."
                }
            },
            "required": ["year", "month", "day"]
        }
    },
    {
        "name": "mayan_convert_long_count",
        "description": "Convierte una Cuenta Larga maya (Baktún, Katún, Tún, Uinal, K'in) a su fecha gregoriana equivalente.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "baktun": {"type": "integer", "description": "Baktún (ciclo de 144,000 días)"},
                "katun": {"type": "integer", "description": "Katún (ciclo de 7,200 días)"},
                "tun": {"type": "integer", "description": "Tún (ciclo de 360 días)"},
                "uinal": {"type": "integer", "description": "Uinal (ciclo de 20 días)"},
                "kin": {"type": "integer", "description": "K'in (1 día solar)"},
                "piktun": {"type": "integer", "default": 0, "description": "Piktún (era mayor, opcional)"},
                "correlation": {
                    "type": "string",
                    "enum": ["GMT", "GMT+2", "Spinden"],
                    "description": "Correlación arqueológica. Por defecto GMT (584283)."
                }
            },
            "required": ["baktun", "katun", "tun", "uinal", "kin"]
        }
    },
    {
        "name": "mayan_add_distance_number",
        "description": "Calcula un salto cronológico sumando o restando un Número de Distancia maya (Distance Number) a una fecha base, devolviendo la fecha gregoriana y maya resultante.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_year": {"type": "integer", "description": "Año gregoriano base"},
                "base_month": {"type": "integer", "description": "Mes gregoriano base"},
                "base_day": {"type": "integer", "description": "Día gregoriano base"},
                "direction": {
                    "type": "string",
                    "enum": ["forward", "backward"],
                    "description": "Hacia el futuro ('forward') o hacia el pasado ('backward')"
                },
                "days": {"type": "integer", "description": "Número total de días a sumar/restar (opcional si se desglosa en partes)"},
                "piktun": {"type": "integer", "default": 0, "description": "Piktunes (x 2,880,000 días, macro era)"},
                "baktun": {"type": "integer", "default": 0, "description": "Baktunes (x 144,000 días)"},
                "katun": {"type": "integer", "default": 0, "description": "Katunes (x 7200 días)"},
                "tun": {"type": "integer", "default": 0, "description": "Tunes (x 360 días)"},
                "uinal": {"type": "integer", "default": 0, "description": "Uinales (x 20 días)"},
                "kin": {"type": "integer", "default": 0, "description": "Kines (x 1 día)"}
            },
            "required": ["base_year", "base_month", "base_day"]
        }
    },
    {
        "name": "mayan_calculate_resonance",
        "description": "Calcula la coherencia armónica y resonancia fractal multiescala (0 a 100%) para una fecha dada respecto a los ciclos cósmicos mayas (Tzolk'in, Haab, Venus, Marte, 819-Day, Tun, etc.) con opción de resonancia natal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Año gregoriano a evaluar"},
                "month": {"type": "integer", "description": "Mes gregoriano a evaluar"},
                "day": {"type": "integer", "description": "Día gregoriano a evaluar"},
                "natal_year": {"type": "integer", "description": "Año natal para calcular resonancia biográfica (opcional)"},
                "natal_month": {"type": "integer", "description": "Mes natal (opcional)"},
                "natal_day": {"type": "integer", "description": "Día natal (opcional)"},
                "selected_cycles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de ciclos a considerar (Tzolkin, Haab, Venus, Mars, 819-Day, Tun). Por defecto todos."
                }
            },
            "required": ["year", "month", "day"]
        }
    },
    {
        "name": "mayan_find_convergences",
        "description": "Escanea un rango temporal para detectar ventanas de alta coherencia armónica (Solitones), días de máxima resonancia (>60%) y puentes hiper-fractales entre cúspides.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_year": {"type": "integer", "description": "Año de inicio del escaneo"},
                "start_month": {"type": "integer", "default": 1, "description": "Mes de inicio"},
                "start_day": {"type": "integer", "default": 1, "description": "Día de inicio"},
                "total_days": {"type": "integer", "default": 365, "description": "Duración del escaneo en días (ej. 365, 1825, 3650)"},
                "min_score": {"type": "number", "default": 60.0, "description": "Umbral mínimo de score (por defecto 60%)"},
                "natal_year": {"type": "integer", "description": "Año natal opcional para filtrar por resonancia personal"},
                "natal_month": {"type": "integer", "description": "Mes natal opcional"},
                "natal_day": {"type": "integer", "description": "Día natal opcional"}
            },
            "required": ["start_year"]
        }
    },
    {
        "name": "mayan_exact_cycle_returns",
        "description": "Calcula el próximo retorno exacto o conjunción sagrada entre dos ciclos mayas cualesquiera usando el Teorema del Resto Chino / Algoritmo CRT (ej. ¿cuándo coincide 4 Ahau con Venus en conjunción inferior o con el ciclo K'awiil en el Este?).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_year": {"type": "integer", "description": "Año gregoriano desde donde buscar"},
                "start_month": {"type": "integer", "default": 1, "description": "Mes gregoriano"},
                "start_day": {"type": "integer", "default": 1, "description": "Día gregoriano"},
                "cycle1_name": {
                    "type": "string",
                    "enum": ["Tzolkin", "Haab", "Tun", "Venus", "Mars", "819-Day", "LordOfNight"],
                    "description": "Nombre del primer ciclo"
                },
                "cycle1_target": {
                    "description": "Posición objetivo en el ciclo: entero (ej. 0..259) o nombre epigráfico (ej. '4 Ahau', '1 Imix', '8 Cumku', 'G9')"
                },
                "cycle2_name": {
                    "type": "string",
                    "enum": ["Tzolkin", "Haab", "Tun", "Venus", "Mars", "819-Day", "LordOfNight"],
                    "description": "Nombre del segundo ciclo"
                },
                "cycle2_target": {
                    "description": "Posición objetivo en el segundo ciclo: entero o nombre epigráfico (ej. '8 Cumku', '0 Pop', '4 Ahau')"
                },
                "max_steps": {"type": "integer", "default": 1000, "description": "Máximo de iteraciones de búsqueda (por defecto 1000)"}
            },
            "required": ["start_year", "cycle1_name", "cycle1_target", "cycle2_name", "cycle2_target"]
        }
    },
    {
        "name": "mayan_project_pattern",
        "description": "Proyecta un intervalo armónico cíclico (ej. 7,200 días de Katún, 360 de Tún, 584 de Venus, 260 de Tzolk'in o intervalo personalizado de solitón) hacia el futuro o pasado a través de múltiples ciclos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_year": {"type": "integer", "description": "Año gregoriano base"},
                "base_month": {"type": "integer", "description": "Mes gregoriano base"},
                "base_day": {"type": "integer", "description": "Día gregoriano base"},
                "interval_days": {"type": "integer", "description": "Días del intervalo de proyección (ej. 7200, 360, 584, 260)"},
                "count": {"type": "integer", "default": 10, "description": "Cantidad de saltos a proyectar (por defecto 10)"}
            },
            "required": ["base_year", "base_month", "base_day", "interval_days"]
        }
    },
    {
        "name": "mayan_get_biomolecular_profile",
        "description": "Consulta el perfil biocimático y de resonancia biológica (aminoácido canónico, codones de ARN, fonética Kototama, mantra Bīja y arquetipo molecular) asociado a cualquiera de los 20 sellos solares del Tzolk'in.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tzolkin_sign": {
                    "type": "string",
                    "description": "Nombre del glifo/signo Tzolk'in (ej. 'Ahau', 'Imix', 'Ik', 'Akbal', 'Kan', 'Cib', 'Manik', 'Lamat', etc.)"
                }
            },
            "required": ["tzolkin_sign"]
        }
    },
    {
        "name": "mayan_export_profile",
        "description": "Genera una exportación completa de perfil astrológico y cronológico maya en el formato especificado: Markdown enriquecido, JSON estructurado, Texto plano estela o SVG vectorial.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Año gregoriano"},
                "month": {"type": "integer", "description": "Mes gregoriano"},
                "day": {"type": "integer", "description": "Día gregoriano"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "json", "text", "svg"],
                    "description": "Formato de salida deseado. Por defecto 'markdown'."
                },
                "correlation": {
                    "type": "string",
                    "enum": ["GMT", "GMT+2", "Spinden"],
                    "description": "Correlación arqueológica. Por defecto GMT (584283)."
                }
            },
            "required": ["year", "month", "day"]
        }
    }
]

def _set_correlation(corr_str):
    if corr_str == "GMT+2":
        converter.correlation_jdn = 584285
    elif corr_str == "Spinden":
        converter.correlation_jdn = 489384
    else:
        converter.correlation_jdn = 584283

def execute_tool(name, args):
    """Executes the requested tool and returns a string or dictionary."""
    corr = args.get("correlation", "GMT")
    _set_correlation(corr)
    
    if name == "mayan_convert_gregorian":
        year = args["year"]
        month = args["month"]
        day = args["day"]
        data = converter.get_full_date(year, month, day)
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Add biomolecular resonance
        bio = MayanProfileExporter._extract_bio_resonance(data["tzolkin_name"])
        data_clean = dict(data)
        if bio:
            data_clean["biomolecular_resonance"] = {
                "amino_acid": bio.get("amino"),
                "formula": bio.get("formula"),
                "group": bio.get("group"),
                "bija": bio.get("bija"),
                "kototama": bio.get("kototama"),
                "codons": [c.get("triplet") for c in bio.get("codons", [])]
            }
        return json.dumps(data_clean, ensure_ascii=False, indent=2)

    elif name == "mayan_convert_long_count":
        baktun = args["baktun"]
        katun = args["katun"]
        tun = args["tun"]
        uinal = args["uinal"]
        kin = args["kin"]
        piktun = args.get("piktun", 0)
        
        y, m, d = converter.long_count_to_gregorian(baktun, katun, tun, uinal, kin, piktun=piktun)
        full_data = converter.get_full_date(y, m, d)
        result = {
            "gregorian_date": f"{y:04d}-{m:02d}-{d:02d}",
            "year": y, "month": m, "day": d,
            "long_count": full_data["long_count"],
            "tzolkin": full_data["tzolkin"],
            "haab": full_data["haab"],
            "calendar_round": full_data["calendar_round"],
            "lord": full_data["lord"],
            "venus_phase": full_data["venus_phase"],
            "moon_phase": full_data["moon_phase"],
            "jdn": full_data["jdn"]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "mayan_add_distance_number":
        y, m, d = args["base_year"], args["base_month"], args["base_day"]
        base_jdn = converter._gregorian_to_jdn(y, m, d)
        
        # Calculate total delta days
        total_delta = args.get("days", 0)
        if total_delta == 0:
            pik = args.get("piktun", 0)
            bak = args.get("baktun", 0)
            kat = args.get("katun", 0)
            tun = args.get("tun", 0)
            uin = args.get("uinal", 0)
            kin = args.get("kin", 0)
            total_delta = pik * 2880000 + bak * 144000 + kat * 7200 + tun * 360 + uin * 20 + kin
            
        direction = args.get("direction", "forward")
        signed_delta = total_delta if direction == "forward" else -total_delta
        
        dest_y, dest_m, dest_d = converter.add_distance_number(base_jdn, signed_delta)
        dest_data = converter.get_full_date(dest_y, dest_m, dest_d)
        
        return json.dumps({
            "base_date": f"{y:04d}-{m:02d}-{d:02d}",
            "direction": direction,
            "delta_days": total_delta,
            "destination_date": f"{dest_y:04d}-{dest_m:02d}-{dest_d:02d}",
            "destination_long_count": dest_data["long_count"],
            "destination_tzolkin": dest_data["tzolkin"],
            "destination_haab": dest_data["haab"],
            "destination_calendar_round": dest_data["calendar_round"],
            "destination_lord": dest_data["lord"]
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_calculate_resonance":
        y, m, d = args["year"], args["month"], args["day"]
        jdn = converter._gregorian_to_jdn(y, m, d)
        days = jdn - converter.correlation_jdn
        
        natal_days = None
        if "natal_year" in args and "natal_month" in args and "natal_day" in args:
            n_jdn = converter._gregorian_to_jdn(args["natal_year"], args["natal_month"], args["natal_day"])
            natal_days = n_jdn - converter.correlation_jdn
            
        selected_cycles = args.get("selected_cycles")
        score = analyzer.calculate_resonance_score(days, selected_cycles, natal_days)
        alignments = analyzer._get_alignments(days, natal_days)
        
        date_data = converter.get_full_date(y, m, d)
        km = analyzer.calculate_kuramoto_order(days, selected_cycles, natal_days)
        ecl = analyzer.get_dresden_eclipse_info(days)
        return json.dumps({
            "date": f"{y:04d}-{m:02d}-{d:02d}",
            "score": round(score, 2),
            "alignments": alignments,
            "is_high_resonance": score >= 60.0,
            "kuramoto": km,
            "dresden_eclipse": ecl,
            "long_count": date_data["long_count"],
            "tzolkin": date_data["tzolkin"],
            "haab": date_data["haab"]
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_find_convergences":
        sy = args["start_year"]
        sm = args.get("start_month", 1)
        sd = args.get("start_day", 1)
        total_days = args.get("total_days", 365)
        
        start_dt = datetime(sy, sm, sd)
        natal_days = None
        if "natal_year" in args and "natal_month" in args and "natal_day" in args:
            n_jdn = converter._gregorian_to_jdn(args["natal_year"], args["natal_month"], args["natal_day"])
            natal_days = n_jdn - converter.correlation_jdn
            
        events = analyzer.find_convergences(start_dt, total_days, None, natal_days)
        packets = analyzer.group_into_wave_packets(events)
        links = analyzer.detect_harmonic_links(packets)
        
        # Serialize packets cleanly
        serialized_packets = []
        for p in packets:
            serialized_packets.append({
                "id": p["id"],
                "start_date": p["start_date"].strftime("%Y-%m-%d"),
                "end_date": p["end_date"].strftime("%Y-%m-%d"),
                "duration_days": p["duration"],
                "peak_date": p["peak_date"].strftime("%Y-%m-%d"),
                "peak_score": round(p["peak_score"], 1),
                "peak_tzolkin": p["peak_tzolkin"],
                "peak_long_count": p["peak_long_count"],
                "peak_kuramoto": p.get("peak_kuramoto"),
                "has_eclipse": p.get("has_eclipse", False),
                "eclipse_type": p.get("eclipse_type"),
                "total_energy": round(p["total_energy"], 1),
                "symmetry_score": round(p["symmetry_score"], 0),
                "alignments": p["alignments"]
            })
            
        return json.dumps({
            "total_resonant_days": len(events),
            "total_soliton_windows": len(packets),
            "total_harmonic_links": len(links),
            "soliton_windows": serialized_packets[:20],
            "top_harmonic_links": [
                {
                    "p1": l["p1"]["peak_tzolkin"],
                    "p2": l["p2"]["peak_tzolkin"],
                    "delta_days": l["delta_days"],
                    "harmonics": l["harmonics"]
                }
                for l in links[:10]
            ]
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_exact_cycle_returns":
        y, m, d = args["start_year"], args.get("start_month", 1), args.get("start_day", 1)
        base_jdn = converter._gregorian_to_jdn(y, m, d)
        start_days = base_jdn - converter.correlation_jdn
        
        cycle_lengths = {
            "Tzolkin": 260, "Haab": 365, "Tun": 360, "Venus": 584, "Mars": 780,
            "819-Day": 819, "LordOfNight": 9
        }

        def parse_cycle_target(c_name, val):
            """Parses numeric target or epigraphic name into linear cycle phase."""
            if isinstance(val, str):
                val_s = val.strip().lower()
                if c_name == "Tzolkin":
                    parts = val_s.split()
                    if len(parts) >= 2 and parts[0].isdigit():
                        t = int(parts[0])
                        sign_str = parts[1]
                        s = -1
                        for idx, (name, *_) in enumerate(converter.TZOLKIN_DATA):
                            if name.lower() in sign_str:
                                s = idx
                                break
                        if 1 <= t <= 13 and s != -1:
                            # CRT Biyection: 4 Ahau at epoch (days=0) -> 0
                            return (40 * ((t - 4) % 13) - 39 * s) % 260
                elif c_name == "Haab":
                    parts = val_s.split()
                    if len(parts) >= 2 and parts[0].isdigit():
                        day_in_m = int(parts[0])
                        m_str = parts[1]
                        m_idx = -1
                        for idx, (name, *_) in enumerate(converter.HAAB_DATA):
                            if name.lower() in m_str:
                                m_idx = idx
                                break
                        if m_idx != -1:
                            return (m_idx * 20 + day_in_m) % 365
                elif c_name == "LordOfNight":
                    digits = [c for c in val_s if c.isdigit()]
                    if digits:
                        return (int("".join(digits)) - 1) % 9
                try:
                    return int(val)
                except ValueError:
                    return 0
            elif isinstance(val, (int, float)):
                return int(val)
            return 0

        def get_cycle_pos(c_name, days_val):
            if c_name == "Tzolkin":
                # Continuous linear day position in 260-day cycle (4 Ahau = 0)
                # Increments strictly +1 each day
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

        c1_name = args["cycle1_name"]
        c2_name = args["cycle2_name"]
        c1_len = cycle_lengths.get(c1_name, 260)
        c2_len = cycle_lengths.get(c2_name, 365)
        raw_t1 = args["cycle1_target"]
        raw_t2 = args["cycle2_target"]
        t1 = parse_cycle_target(c1_name, raw_t1) % c1_len
        t2 = parse_cycle_target(c2_name, raw_t2) % c2_len
        max_steps = args.get("max_steps", 5000)

        # Step forward until cycle1 matches
        cur_d = start_days
        while get_cycle_pos(c1_name, cur_d) != t1:
            cur_d += 1

        found_days = None
        for _ in range(max_steps):
            if get_cycle_pos(c2_name, cur_d) == t2:
                found_days = cur_d
                break
            cur_d += c1_len
            
        if found_days is not None:
            dest_jdn = converter.correlation_jdn + found_days
            ry, rm, rd = converter._jdn_to_gregorian(dest_jdn)
            r_data = converter.get_full_date(ry, rm, rd)
            return json.dumps({
                "success": True,
                "found_date": f"{ry:04d}-{rm:02d}-{rd:02d}",
                "days_from_start": found_days - start_days,
                "long_count": r_data["long_count"],
                "tzolkin": r_data["tzolkin"],
                "haab": r_data["haab"],
                "calendar_round": r_data["calendar_round"],
                "venus_pos": r_data["venus_pos"],
                "lord": r_data["lord"]
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"No se encontró coincidencia entre {c1_name}={t1} y {c2_name}={t2} dentro del límite de {max_steps} pasos."
            }, ensure_ascii=False, indent=2)

    elif name == "mayan_project_pattern":
        y, m, d = args["base_year"], args["base_month"], args["base_day"]
        base_dt = datetime(y, m, d)
        interval = args["interval_days"]
        count = args.get("count", 10)
        
        raw_projections = analyzer.project_pattern(base_dt, interval, count)
        clean_projections = []
        for i, p in enumerate(raw_projections, 1):
            p_dt = p["date"]
            data = converter.get_full_date(p_dt.year, p_dt.month, p_dt.day)
            clean_projections.append({
                "step": i,
                "date": p_dt.strftime("%Y-%m-%d"),
                "elapsed_days": i * interval,
                "long_count": data["long_count"],
                "tzolkin": data["tzolkin"],
                "haab": data["haab"],
                "calendar_round": data["calendar_round"],
                "lord": data["lord"],
                "venus_phase": data["venus_phase"]
            })
        return json.dumps(clean_projections, ensure_ascii=False, indent=2)

    elif name == "mayan_get_biomolecular_profile":
        sign = args["tzolkin_sign"]
        bio = MayanProfileExporter._extract_bio_resonance(sign)
        if bio:
            return json.dumps(bio, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "error": f"No se encontró mapeo biomolecular para el signo '{sign}'.",
                "available_signs": [item["seal"] for item in (mayan_exporter.RESONANCE_MAP or [])]
            }, ensure_ascii=False, indent=2)

    elif name == "mayan_export_profile":
        y, m, d = args["year"], args["month"], args["day"]
        fmt = args.get("format", "markdown").lower()
        full_data = converter.get_full_date(y, m, d)
        date_str = f"{y:04d}-{m:02d}-{d:02d}"
        corr_label = f"{corr} ({converter.correlation_jdn})"
        
        if fmt == "json":
            return MayanProfileExporter.export_json(full_data, correlation_name=corr_label)
        elif fmt == "text":
            return MayanProfileExporter.export_text(full_data, gregorian_date_str=date_str, correlation_name=corr_label)
        elif fmt == "svg":
            return MayanProfileExporter.export_svg(full_data, gregorian_date_str=date_str)
        else:
            return MayanProfileExporter.export_markdown(full_data, gregorian_date_str=date_str, correlation_name=corr_label)

    else:
        raise ValueError(f"Tool desconocido: {name}")

def run_stdio_server():
    """Runs the standard JSON-RPC 2.0 stdio loop for MCP clients."""
    # Ensure stdout is unbuffered or flushed immediately
    sys.stderr.write("[MayanStele MCP] Servidor iniciado en stdio (JSON-RPC 2.0)...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error", "data": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "mayan-stele-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            # Notification: no response required
            continue
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                output = execute_tool(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output
                            }
                        ]
                    }
                }
            except Exception as e:
                err_trace = traceback.format_exc()
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error ejecutando '{tool_name}': {str(e)}\n{err_trace}"
                            }
                        ]
                    }
                }
        else:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()
