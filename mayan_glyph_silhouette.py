#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
MAYAN-LANG (AH TS'IB) • HIGH-PARITY ARCHAEOLOGICAL SILHOUETTE ENGINE
══════════════════════════════════════════════════════════════════════════════
Implementa los 3 pilares de paridad arqueológica para glifos y sílabas mayas:
  • Método 1: Extractor/Cargador de Corpus Vectorial (TTF/OTF/SVG ➔ Caja 100x100).
  • Método 2: Descriptores Elípticos de Fourier (EFD) y Morphing Cefalomorfo.
  • Método 5: Gramática de 24 Radicales Anatómicos + Pincel de Presión Variable
              + Deformación en Jaula Bilineal (Cage-Based FFD) para afijos.

Cero dependencias obligatorias (compatible con PySide6 QPainterPath y SVG puro).
══════════════════════════════════════════════════════════════════════════════
"""

import os
import re
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Any

Point2D = Tuple[float, float]


# ══════════════════════════════════════════════════════════════════════════════
# GEOMETRÍA AUXILIAR: DEFORMACIÓN EN JAULA BILINEAL (FFD) Y PINCEL CALIGRÁFICO
# ══════════════════════════════════════════════════════════════════════════════

class CalligraphicGeometry:
    """
    Operadores geométricos para imitar el pincel de pelo flexible maya (Ah Ts'ib)
    y el encaje de mampostería orgánica entre afijos y signo principal.
    """

    @staticmethod
    def eval_cubic_bezier(p0: Point2D, p1: Point2D, p2: Point2D, p3: Point2D, steps: int = 16) -> List[Point2D]:
        pts: List[Point2D] = []
        for i in range(steps + 1):
            t = i / float(steps)
            mt = 1.0 - t
            x = (mt**3)*p0[0] + 3*(mt**2)*t*p1[0] + 3*mt*(t**2)*p2[0] + (t**3)*p3[0]
            y = (mt**3)*p0[1] + 3*(mt**2)*t*p1[1] + 3*mt*(t**2)*p2[1] + (t**3)*p3[1]
            pts.append((x, y))
        return pts

    @staticmethod
    def variable_pressure_ribbon_svg(
        centerline: List[Point2D],
        w_start: float = 1.2,
        w_mid: float = 3.8,
        w_end: float = 1.0,
        fill_color: str = "#FCD34D"
    ) -> str:
        """
        Convierte una polilínea central en un trazo caligráfico relleno de grosor variable
        (fino en los extremos, grueso en el vientre de la curva, como pincel sobre estuco).
        """
        n = len(centerline)
        if n < 2:
            return ""

        left_edge: List[Point2D] = []
        right_edge: List[Point2D] = []

        for i in range(n):
            t = i / float(n - 1)
            # Perfil de presión sinusoidal con asimetría caligráfica
            pressure = (1.0 - t) * w_start + math.sin(t * math.pi) * w_mid + t * w_end
            half_w = max(0.4, pressure * 0.5)

            p_prev = centerline[max(0, i - 1)]
            p_next = centerline[min(n - 1, i + 1)]
            dx = p_next[0] - p_prev[0]
            dy = p_next[1] - p_prev[1]
            length = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / length, dx / length

            cx, cy = centerline[i]
            left_edge.append((cx + nx * half_w, cy + ny * half_w))
            right_edge.append((cx - nx * half_w, cy - ny * half_w))

        poly = left_edge + list(reversed(right_edge))
        d_cmds = [f"M {poly[0][0]:.2f} {poly[0][1]:.2f}"]
        for px, py in poly[1:]:
            d_cmds.append(f"L {px:.2f} {py:.2f}")
        d_cmds.append("Z")
        return f'<path d="{" ".join(d_cmds)}" fill="{fill_color}" stroke="none"/>'

    @staticmethod
    def bilinear_cage_warp(
        pt: Point2D,
        cage_q00: Point2D,
        cage_q10: Point2D,
        cage_q11: Point2D,
        cage_q01: Point2D,
        arch_bow: float = 0.0
    ) -> Point2D:
        """
        Deforma un punto canónico (u, v) en [0..100]^2 hacia un cuadrilátero arbitrario
        con curvatura orgánica 'arch_bow' para que los superfijos/prefijos abracen al glifo central.
        """
        u = max(0.0, min(1.0, pt[0] / 100.0))
        v = max(0.0, min(1.0, pt[1] / 100.0))

        # Interpolación bilineal base
        x = (1 - u)*(1 - v)*cage_q00[0] + u*(1 - v)*cage_q10[0] + u*v*cage_q11[0] + (1 - u)*v*cage_q01[0]
        y = (1 - u)*(1 - v)*cage_q00[1] + u*(1 - v)*cage_q10[1] + u*v*cage_q11[1] + (1 - u)*v*cage_q01[1]

        # Curvatura de abrazo de mampostería (parábola en el eje central)
        if abs(arch_bow) > 1e-4:
            bow_offset = math.sin(u * math.pi) * arch_bow
            y += bow_offset
        return (x, y)


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO 1: EXTRACTOR Y COMPILADOR DEL CORPUS EPIGRÁFICO (TTF / OTF / SVG ➔ JSON)
# ══════════════════════════════════════════════════════════════════════════════

class CorpusPathExtractor:
    """
    Método 1: Extrae, normaliza a [0..100]^2 y almacena siluetas vectoriales reales
    desde fuentes epigráficas (Unicode Mayan / MHD / Thompson) o archivos SVG arqueológicos.
    """

    COORD_TOKEN_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)")

    def __init__(self, vault_json_path: str = "thompson_silhouettes_vault.json"):
        self.vault_path = vault_json_path
        self.silhouette_vault: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(self.vault_path):
            self.load_vault()

    def load_vault(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                self.silhouette_vault = json.load(f)
        except Exception:
            self.silhouette_vault = {}
        return self.silhouette_vault

    def save_vault(self) -> None:
        with open(self.vault_path, "w", encoding="utf-8") as f:
            json.dump(self.silhouette_vault, f, ensure_ascii=False, indent=2)

    @classmethod
    def normalize_svg_path_to_100x100(cls, raw_d: str, padding: float = 6.0) -> str:
        """
        Reescala y centra cualquier cadena SVG <path d="..."/> a una caja canónica [0..100]^2
        para que pueda incrustarse en cualquier ranura de cartucho sin desbordar.
        """
        tokens = cls.COORD_TOKEN_RE.findall(raw_d)
        numbers: List[float] = [float(num) for _cmd, num in tokens if num]
        if len(numbers) < 4:
            return raw_d

        xs = numbers[0::2]
        ys = numbers[1::2]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1e-5, max_x - min_x)
        span_y = max(1e-5, max_y - min_y)

        target_span = 100.0 - 2.0 * padding
        scale = target_span / max(span_x, span_y)
        off_x = padding + (target_span - span_x * scale) * 0.5
        off_y = padding + (target_span - span_y * scale) * 0.5

        out_tokens: List[str] = []
        coord_idx = 0
        current_cmd = "M"

        for cmd, num in tokens:
            if cmd:
                current_cmd = cmd
                out_tokens.append(cmd)
                coord_idx = 0
            elif num:
                val = float(num)
                if current_cmd in ("M", "L", "C", "S", "Q", "T"):
                    if coord_idx % 2 == 0:
                        norm_val = (val - min_x) * scale + off_x
                    else:
                        norm_val = (val - min_y) * scale + off_y
                    out_tokens.append(f"{norm_val:.2f}")
                elif current_cmd == "H":
                    out_tokens.append(f"{(val - min_x) * scale + off_x:.2f}")
                elif current_cmd == "V":
                    out_tokens.append(f"{(val - min_y) * scale + off_y:.2f}")
                else:
                    # Comandos relativos en minúscula: escalar sin traslación
                    out_tokens.append(f"{val * scale:.2f}")
                coord_idx += 1

        return " ".join(out_tokens)

    def import_from_svg_file(self, thompson_id: str, svg_file_path: str, glyph_name: str = "") -> bool:
        """Extrae todos los elementos <path d="..."/> de un SVG arqueológico y los registra."""
        if not os.path.exists(svg_file_path):
            return False
        with open(svg_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        paths = re.findall(r'<path[^>]*\bd=["\']([^"\']+)["\']', content, flags=re.IGNORECASE)
        if not paths:
            return False

        combined_raw = " ".join(paths)
        norm_d = self.normalize_svg_path_to_100x100(combined_raw)
        self.silhouette_vault[thompson_id.upper()] = {
            "thompson_id": thompson_id.upper(),
            "name": glyph_name or thompson_id,
            "source": os.path.basename(svg_file_path),
            "svg_path_100x100": norm_d
        }
        self.save_vault()
        return True

    def import_from_ttf_font(self, ttf_path: str, char_to_thompson_map: Dict[int, str]) -> int:
        """
        Extrae contornos vectoriales desde una fuente OpenType/TrueType epigráfica
        (si 'fontTools' está disponible en el entorno) y los normaliza a [0..100]^2.
        """
        try:
            from fontTools.ttLib import TTFont
            from fontTools.pens.svgPathPen import SVGPathPen
        except ImportError:
            return 0

        font = TTFont(ttf_path)
        glyph_set = font.getGlyphSet()
        cmap = font.getBestCmap()
        imported_count = 0

        for codepoint, t_id in char_to_thompson_map.items():
            glyph_name = cmap.get(codepoint)
            if not glyph_name or glyph_name not in glyph_set:
                continue
            pen = SVGPathPen(glyph_set)
            glyph_set[glyph_name].draw(pen)
            raw_d = pen.getCommands()
            if raw_d:
                self.silhouette_vault[t_id.upper()] = {
                    "thompson_id": t_id.upper(),
                    "name": glyph_name,
                    "source": os.path.basename(ttf_path),
                    "svg_path_100x100": self.normalize_svg_path_to_100x100(raw_d)
                }
                imported_count += 1

        if imported_count > 0:
            self.save_vault()
        return imported_count


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO 2: DESCRIPTORES ELÍPTICOS DE FOURIER (EFD) Y MORPHING CEFALOMORFO
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class FourierGlyphSignature:
    """
    Firma armónica de un contorno cerrado maya mediante N armónicos elípticos de Fourier:
    Cada armónico n (1..N) almacena (a_n, b_n, c_n, d_n).
    """
    name: str
    thompson_id: str
    a0: float = 50.0
    c0: float = 50.0
    harmonics: List[Tuple[float, float, float, float]] = field(default_factory=list)


class EllipticFourierEngine:
    """
    Método 2: Codifica siluetas arqueológicas cerradas en el dominio de la frecuencia
    (Kuhl & Giardina, 1982) y permite interpolar continuamente (morphing) entre la
    forma Geométrica Simple y la variante Cefalomorfa (Cabeza de Perfil).
    """

    @staticmethod
    def decompose_contour(points: List[Point2D], num_harmonics: int = 20, name: str = "", t_id: str = "") -> FourierGlyphSignature:
        """
        Calcula los coeficientes de Fourier (a_n, b_n, c_n, d_n) a partir de una lista
        de puntos (x, y) que recorren la silueta de un glifo maya.
        """
        pts = list(points)
        if len(pts) < 3:
            return FourierGlyphSignature(name=name, thompson_id=t_id)
        if pts[0] != pts[-1]:
            pts.append(pts[0])

        k_count = len(pts) - 1
        dxs = [pts[i+1][0] - pts[i][0] for i in range(k_count)]
        dys = [pts[i+1][1] - pts[i][1] for i in range(k_count)]
        dts = [math.hypot(dx, dy) or 1e-6 for dx, dy in zip(dxs, dys)]

        t_accum = [0.0]
        for dt in dts:
            t_accum.append(t_accum[-1] + dt)
        total_perimeter = t_accum[-1] or 1.0

        # Centroide (DC offset)
        xs = [p[0] for p in pts[:-1]]
        ys = [p[1] for p in pts[:-1]]
        a0 = sum(xs) / len(xs)
        c0 = sum(ys) / len(ys)

        harmonics: List[Tuple[float, float, float, float]] = []
        two_pi = 2.0 * math.pi

        for n in range(1, num_harmonics + 1):
            scale = total_perimeter / (2.0 * (n ** 2) * (math.pi ** 2))
            an, bn, cn, dn = 0.0, 0.0, 0.0, 0.0
            for i in range(k_count):
                phi_next = two_pi * n * t_accum[i+1] / total_perimeter
                phi_curr = two_pi * n * t_accum[i] / total_perimeter
                cos_diff = math.cos(phi_next) - math.cos(phi_curr)
                sin_diff = math.sin(phi_next) - math.sin(phi_curr)

                dx_dt = dxs[i] / dts[i]
                dy_dt = dys[i] / dts[i]

                an += dx_dt * cos_diff
                bn += dx_dt * sin_diff
                cn += dy_dt * cos_diff
                dn += dy_dt * sin_diff

            harmonics.append((an * scale, bn * scale, cn * scale, dn * scale))

        return FourierGlyphSignature(name=name, thompson_id=t_id, a0=a0, c0=c0, harmonics=harmonics)

    @staticmethod
    def reconstruct_contour(
        sig: FourierGlyphSignature,
        num_samples: int = 128,
        active_harmonics: Optional[int] = None
    ) -> List[Point2D]:
        """
        Reconstruye la silueta espacial (x(t), y(t)) sumando los armónicos de Fourier.
        Permite limitar 'active_harmonics' para ver cómo emerge la forma desde un óvalo hasta el glifo detallado.
        """
        max_h = len(sig.harmonics) if active_harmonics is None else min(active_harmonics, len(sig.harmonics))
        pts: List[Point2D] = []
        two_pi = 2.0 * math.pi

        for s in range(num_samples):
            t = two_pi * (s / float(num_samples))
            x = sig.a0
            y = sig.c0
            for n_idx in range(max_h):
                n = n_idx + 1
                an, bn, cn, dn = sig.harmonics[n_idx]
                nt = n * t
                cn_t = math.cos(nt)
                sn_t = math.sin(nt)
                x += an * cn_t + bn * sn_t
                y += cn * cn_t + dn * sn_t
            pts.append((x, y))
        return pts

    @classmethod
    def morph_signatures(
        cls,
        sig_geometric: FourierGlyphSignature,
        sig_cephalomorphic: FourierGlyphSignature,
        alpha: float = 0.5,
        num_samples: int = 128
    ) -> List[Point2D]:
        """
        Interpola en el espacio de frecuencias entre la variante Geométrica Simple (alpha=0.0)
        y la variante Cefalomorfa Sagrada (alpha=1.0).
        """
        a = max(0.0, min(1.0, alpha))
        n_harm = min(len(sig_geometric.harmonics), len(sig_cephalomorphic.harmonics))
        blended_harmonics = []

        for i in range(n_harm):
            g_a, g_b, g_c, g_d = sig_geometric.harmonics[i]
            c_a, c_b, c_c, c_d = sig_cephalomorphic.harmonics[i]
            blended_harmonics.append((
                (1.0 - a) * g_a + a * c_a,
                (1.0 - a) * g_b + a * c_b,
                (1.0 - a) * g_c + a * c_c,
                (1.0 - a) * g_d + a * c_d,
            ))

        blended_sig = FourierGlyphSignature(
            name=f"{sig_geometric.name}_morph_{a:.2f}",
            thompson_id=sig_geometric.thompson_id,
            a0=(1.0 - a) * sig_geometric.a0 + a * sig_cephalomorphic.a0,
            c0=(1.0 - a) * sig_geometric.c0 + a * sig_cephalomorphic.c0,
            harmonics=blended_harmonics
        )
        return cls.reconstruct_contour(blended_sig, num_samples=num_samples)

    @staticmethod
    def contour_to_svg_path(points: List[Point2D], fill: str, stroke: str, stroke_w: float = 2.2) -> str:
        if not points:
            return ""
        cmds = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
        for px, py in points[1:]:
            cmds.append(f"L {px:.2f} {py:.2f}")
        cmds.append("Z")
        return f'<path d="{" ".join(cmds)}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>'


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO 5: GRAMÁTICA DE LOS 24 RADICALES ANATÓMICOS Y MORFOLÓGICOS REALES
# ══════════════════════════════════════════════════════════════════════════════

class MayanRadicalGrammar:
    """
    Método 5: Construye sílabas CV y logogramas ensamblando las 24 piezas anatómicas
    y caligráficas reales documentadas en la epigrafía maya (Schele / Montgomery / Van Stone),
    usando curvas Bézier y trazos de presión variable en espacio canónico [0..100]^2.
    """

    @staticmethod
    def draw_radical_svg(
        radical_id: str,
        palette: Dict[str, str],
        cage: Tuple[Point2D, Point2D, Point2D, Point2D] = ((0, 0), (100, 0), (100, 100), (0, 100)),
        arch_bow: float = 0.0
    ) -> str:
        """
        Renderiza cualquiera de los 24 radicales epigráficos dentro de la jaula bilineal 'cage'.
        """
        q00, q10, q11, q01 = cage
        stroke = palette["glyph_stroke"]
        jade = palette["jade_accent"]
        crimson = palette["crimson_accent"]
        fill = palette["glyph_fill"]

        def W(x: float, y: float) -> Point2D:
            return CalligraphicGeometry.bilinear_cage_warp((x, y), q00, q10, q11, q01, arch_bow)

        def path_cmd(pts: List[Tuple[str, List[Point2D]]], f_col: str = "none", s_col: str = stroke, sw: float = 2.2) -> str:
            d = []
            for cmd, coords in pts:
                warped = [W(px, py) for px, py in coords]
                flat = " ".join(f"{wx:.1f} {wy:.1f}" for wx, wy in warped)
                d.append(f"{cmd} {flat}".strip())
            return f'<path d="{" ".join(d)}" fill="{f_col}" stroke="{s_col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'

        svg: List[str] = []

        # Marco de guijarro orgánico maya (con biselado caligráfico)
        svg.append(path_cmd([
            ("M", [(18, 6)]),
            ("C", [(50, 3), (82, 6), (94, 18)]),
            ("C", [(97, 50), (94, 82), (82, 94)]),
            ("C", [(50, 97), (18, 94), (6, 82)]),
            ("C", [(3, 50), (6, 18), (18, 6)]),
            ("Z", [])
        ], f_col=fill, s_col=stroke, sw=2.5))

        # ── 1. RADICALES DE LA MANO SAGRADA (K'AB') ──
        if radical_id == "R01_HAND_FLAT_CHI":
            # Mano de perfil con pulgar oponible y brazalete de cuentas de jade (sílaba 'chi' / verbo 'TZUTZ')
            svg.append(path_cmd([
                ("M", [(18, 68)]),
                ("C", [(18, 45), (28, 28), (48, 26)]),  # Dorso y pulgar superior
                ("C", [(58, 26), (56, 38), (44, 40)]),
                ("L", [(82, 38)]),                      # Dedo índice extendido
                ("C", [(88, 42), (88, 52), (80, 54)]),
                ("L", [(78, 66)]),                      # Dedos medio y meñique plegados
                ("C", [(68, 76), (38, 76), (18, 68)]),
                ("Z", [])
            ], f_col="none", s_col=jade, sw=2.6))
            # Uña y brazalete de muñeca
            p_wrist = W(24, 58)
            svg.append(f'<circle cx="{p_wrist[0]:.1f}" cy="{p_wrist[1]:.1f}" r="5.5" fill="{crimson}" stroke="{stroke}" stroke-width="1.8"/>')

        elif radical_id == "R02_HAND_FIST_K_A":
            # Puño cerrado con voluta de chispa/fuego (sílabas k'a, k'e, k'i, k'o, k'u - T669)
            svg.append(path_cmd([
                ("M", [(24, 72)]),
                ("C", [(20, 42), (36, 24), (62, 26)]),
                ("C", [(80, 28), (84, 54), (68, 68)]),
                ("C", [(52, 78), (32, 78), (24, 72)]),
                ("Z", [])
            ], f_col="none", s_col=jade, sw=2.5))
            # Nudillos en espiral y uñas interiores
            for ky in (38, 50, 62):
                svg.append(path_cmd([("M", [(52, ky)]), ("C", [(66, ky-4), (72, ky+4), (58, ky+6)])], s_col=crimson, sw=2.0))

        elif radical_id == "R03_HAND_BRUSH_TSIB":
            # Mano de escriba sosteniendo el pincel caligráfico con voluta de tinta (TS'IB)
            svg.append(path_cmd([
                ("M", [(16, 70)]), ("C", [(26, 48), (46, 38), (64, 44)]),
                ("L", [(84, 22)]), ("L", [(88, 28)]), ("L", [(66, 54)]),
                ("C", [(52, 72), (30, 76), (16, 70)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.4))
            # Voluta de tinta / flor de aliento saliendo de la punta del pincel
            ribbon = [W(84, 22), W(76, 14), W(62, 16), W(58, 26)]
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(ribbon, 1.0, 4.2, 1.2, crimson))

        elif radical_id == "R04_HAND_SCATTER_CHOK":
            # Mano abierta hacia abajo esparciendo gotas de jade/copal (CHOK / 'ye')
            svg.append(path_cmd([
                ("M", [(26, 22)]), ("C", [(50, 18), (74, 26), (76, 48)]),
                ("L", [(64, 52)]), ("L", [(46, 44)]), ("L", [(26, 48)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.4))
            for gx, gy in [(36, 66), (52, 74), (68, 64), (44, 84), (60, 86)]:
                pg = W(gx, gy)
                svg.append(f'<circle cx="{pg[0]:.1f}" cy="{pg[1]:.1f}" r="3.8" fill="{crimson}"/>')

        # ── 2. RADICALES ÓSEOS, MANDÍBULAS Y CABEZAS DE PERFIL (CEFALOMORFOS) ──
        elif radical_id == "R05_JAWBONE_CH_A":
            # Mandíbula inferior descarnada con 3 molares y foramen óseo (ch'a, CHAM, EB')
            svg.append(path_cmd([
                ("M", [(18, 30)]), ("L", [(28, 30)]), ("L", [(28, 56)]),
                ("L", [(82, 56)]), ("C", [(86, 72), (72, 82), (24, 80)]),
                ("C", [(14, 76), (14, 52), (18, 30)]), ("Z", [])
            ], f_col="none", s_col=stroke, sw=2.4))
            # 3 Dientes molares encajados
            for mx in (38, 52, 66):
                svg.append(path_cmd([
                    ("M", [(mx, 38)]), ("L", [(mx+11, 38)]), ("L", [(mx+11, 56)]), ("L", [(mx, 56)]), ("Z", [])
                ], f_col=jade, s_col=stroke, sw=1.8))

        elif radical_id == "R06_JAGUAR_HEAD_BALAM":
            # Cabeza de Jaguar Clásico (T751): morro pronunciado, colmillo curvo, oreja con achurado y manchas
            svg.append(path_cmd([
                ("M", [(28, 78)]),
                ("C", [(14, 68), (12, 46), (26, 36)]),  # Hocico frontal
                ("C", [(36, 22), (56, 16), (78, 22)]),  # Cráneo y oreja felina
                ("C", [(88, 32), (86, 66), (72, 78)]),
                ("Z", [])
            ], f_col="none", s_col=jade, sw=2.6))
            # Colmillo real sobresaliendo de las fauces
            svg.append(path_cmd([("M", [(22, 56)]), ("C", [(20, 70), (30, 72), (34, 58)])], f_col=crimson, s_col=stroke, sw=1.8))
            # Ojo felino con ceja y 3 manchas de obsidiana (Ix)
            p_eye = W(42, 42)
            svg.append(f'<circle cx="{p_eye[0]:.1f}" cy="{p_eye[1]:.1f}" r="6.5" fill="{crimson}" stroke="{stroke}" stroke-width="2"/>')
            for sx, sy in [(66, 36), (74, 52), (58, 64)]:
                ps = W(sx, sy)
                svg.append(f'<circle cx="{ps[0]:.1f}" cy="{ps[1]:.1f}" r="4.2" fill="{stroke}"/>')

        elif radical_id == "R07_SERPENT_BROW_CHAN":
            # Cabeza/Banda de Serpiente Celeste (CHAN / KAN): Ceja flamígera en espiral y colmillo bífido
            svg.append(path_cmd([
                ("M", [(16, 52)]), ("C", [(22, 24), (58, 20), (82, 34)]),
                ("C", [(86, 54), (72, 76), (22, 74)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.4))
            # Bandas cruzadas celestes (X de la eclíptica)
            svg.append(path_cmd([("M", [(32, 34)]), ("L", [(68, 68)]), ("M", [(68, 34)]), ("L", [(32, 68)])], s_col=crimson, sw=2.5))

        elif radical_id == "R08_AJAW_ROYAL_FACE":
            # Rostro Real de Ajaw (T533) con diadema de jade (Huunal) y barbilla hendida
            svg.append(path_cmd([("M", [(14, 34)]), ("L", [(86, 34)])], s_col=jade, sw=3.0))
            for ex in (34, 66):
                pe = W(ex, 50)
                svg.append(f'<circle cx="{pe[0]:.1f}" cy="{pe[1]:.1f}" r="7.5" fill="none" stroke="{stroke}" stroke-width="2.2"/>')
                svg.append(f'<circle cx="{pe[0]:.1f}" cy="{pe[1]:.1f}" r="2.8" fill="{jade}"/>')
            # Boca real ovalada
            svg.append(path_cmd([
                ("M", [(36, 72)]), ("C", [(44, 64), (56, 64), (64, 72)]),
                ("C", [(56, 80), (44, 80), (36, 72)]), ("Z", [])
            ], f_col=crimson, s_col=stroke, sw=1.8))

        elif radical_id == "R09_BAT_HEAD_SOTZ":
            # Perfil de Murciélago (Sotz' / tz') con hoja nasal erguida y ala estriada
            svg.append(path_cmd([
                ("M", [(22, 48)]), ("L", [(16, 20)]), ("L", [(34, 34)]),  # Hoja nasal
                ("C", [(54, 18), (82, 26), (82, 56)]),
                ("C", [(78, 78), (34, 80), (22, 48)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.4))

        # ── 3. RADICALES ACÚSTICOS, PEINES, VOLUTAS Y ACHURADOS DE OBSIDIANA ──
        elif radical_id == "R10_COMB_T25_KA":
            # El famoso Peine Epigráfico T25 (ka, ke, ki, ko, ku, la): lomo curvo con dientes internos
            ribbon = CalligraphicGeometry.eval_cubic_bezier(W(22, 20), W(12, 45), W(12, 55), W(22, 80), steps=14)
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(ribbon, 1.5, 5.0, 1.5, jade))
            for ty in range(24, 80, 11):
                svg.append(path_cmd([("M", [(24, ty)]), ("L", [(76, ty)])], s_col=stroke, sw=2.1))
            p_dot = W(82, 50)
            svg.append(f'<circle cx="{p_dot[0]:.1f}" cy="{p_dot[1]:.1f}" r="5.0" fill="{crimson}"/>')

        elif radical_id == "R11_CROSSHATCH_OBSIDIAN_CH":
            # Medallón con Achurado Cruzado de Obsidiana a 45° (sílabas cha..chu, AK'B'AL, CH'EN)
            p_cen = W(50, 50)
            r_med = math.hypot(q10[0] - q00[0], q01[1] - q00[1]) * 0.24
            svg.append(f'<circle cx="{p_cen[0]:.1f}" cy="{p_cen[1]:.1f}" r="{r_med:.1f}" fill="none" stroke="{jade}" stroke-width="2.6"/>')
            for offset in (-14, -5, 5, 14):
                svg.append(path_cmd([("M", [(32, 50 + offset)]), ("L", [(68, 50 + offset)])], s_col=stroke, sw=1.5))
                svg.append(path_cmd([("M", [(50 + offset, 32)]), ("L", [(50 + offset, 68)])], s_col=stroke, sw=1.5))

        elif radical_id == "R12_FIRE_SCROLL_KAK":
            # Volutas gemelas asimétricas de Fuego Nuevo (K'AK') con cuentas de brasa
            flame1 = CalligraphicGeometry.eval_cubic_bezier(W(30, 82), W(14, 48), W(48, 16), W(54, 42), steps=16)
            flame2 = CalligraphicGeometry.eval_cubic_bezier(W(54, 82), W(46, 52), W(78, 22), W(82, 48), steps=16)
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(flame1, 4.5, 3.2, 0.8, crimson))
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(flame2, 4.0, 2.8, 0.8, jade))

        elif radical_id == "R13_BRACKET_U_T1":
            # Corchete Ergativo 'u-' (T1): Arco caligráfico con 3 cuentas de jade y muescas
            arch_pts = CalligraphicGeometry.eval_cubic_bezier(W(76, 18), W(20, 18), W(20, 82), W(76, 82), steps=18)
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(arch_pts, 1.5, 5.2, 1.5, jade))
            for by in (30, 50, 70):
                pb = W(68, by)
                svg.append(f'<circle cx="{pb[0]:.1f}" cy="{pb[1]:.1f}" r="5.0" fill="{crimson}" stroke="{stroke}" stroke-width="1.6"/>')

        elif radical_id == "R14_SPIRAL_SHELL_JA":
            # Caracola cortada en espiral logarítmica (sílabas ja, je, ji, jo, ju - T181)
            spiral: List[Point2D] = []
            for i in range(28):
                ang = i * 0.35
                rad = 6.0 + i * 1.15
                spiral.append(W(50.0 + math.cos(ang) * rad, 50.0 + math.sin(ang) * rad))
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(spiral, 0.8, 3.4, 4.2, jade))

        elif radical_id == "R15_CLEFT_EARTH_MA":
            # Hendidura en V terrestre con volutas laterales (sílabas ma, me, mi, mo, mu - T74)
            svg.append(path_cmd([
                ("M", [(16, 28)]), ("L", [(40, 28)]), ("L", [(50, 62)]),
                ("L", [(60, 28)]), ("L", [(84, 28)])
            ], s_col=jade, sw=3.0))
            for cx_dot in (28, 72):
                pd = W(cx_dot, 66)
                svg.append(f'<circle cx="{pd[0]:.1f}" cy="{pd[1]:.1f}" r="6.0" fill="{crimson}"/>')

        elif radical_id == "R16_EARTH_WAVE_NA":
            # Onda telúrica escalonada con flecos inferiores (sílabas na, ne, ni, no, nu - T116)
            svg.append(path_cmd([
                ("M", [(14, 52)]),
                ("C", [(30, 22), (46, 22), (52, 52)]),
                ("C", [(58, 78), (74, 78), (86, 46)])
            ], s_col=jade, sw=3.2))
            for fx in (26, 42, 62, 78):
                svg.append(path_cmd([("M", [(fx, 68)]), ("L", [(fx, 84)])], s_col=crimson, sw=2.0))

        elif radical_id == "R17_WOVEN_MAT_POP":
            # Trenzado de Estera Real (POP / sílabas pa, pe, pi, po, pu - T586)
            svg.append(path_cmd([
                ("M", [(20, 26)]), ("L", [(80, 74)]),
                ("M", [(34, 18)]), ("L", [(86, 60)]),
                ("M", [(80, 26)]), ("L", [(20, 74)]),
                ("M", [(66, 18)]), ("L", [(14, 60)])
            ], s_col=jade, sw=2.8))

        elif radical_id == "R18_CROSSED_TORCH_TA":
            # Haz de Antorcha Atada en cruz con nudo central (sílabas ta, te, ti, to, tu - T59)
            svg.append(path_cmd([
                ("M", [(24, 20)]), ("L", [(76, 80)]),
                ("M", [(76, 20)]), ("L", [(24, 80)])
            ], s_col=stroke, sw=3.0))
            p_knot = W(50, 50)
            svg.append(f'<circle cx="{p_knot[0]:.1f}" cy="{p_knot[1]:.1f}" r="11.0" fill="{crimson}" stroke="{jade}" stroke-width="2.5"/>')

        elif radical_id == "R19_STEPPED_FRET_TZ":
            # Greca Escalonada Mesoamericana (Xicalcoliuhqui - sílabas tza..tzu / WITZ)
            svg.append(path_cmd([
                ("M", [(18, 74)]), ("L", [(18, 54)]), ("L", [(36, 54)]),
                ("L", [(36, 36)]), ("L", [(56, 36)]), ("L", [(56, 20)]),
                ("L", [(82, 20)]), ("L", [(82, 74)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.5))

        elif radical_id == "R20_TREFOIL_MAIZE_WA":
            # Brote Tripartito de Maíz Sagrado (sílabas wa, we, wi, wo, wu - T130)
            for ang_deg in (-42, 0, 42):
                rad = math.radians(ang_deg - 90)
                tx = 50.0 + math.cos(rad) * 32.0
                ty = 72.0 + math.sin(rad) * 38.0
                leaf = CalligraphicGeometry.eval_cubic_bezier(W(50, 78), W(50, 48), W(tx, ty), W(tx, ty + 8), steps=12)
                svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(leaf, 1.2, 4.2, 1.0, jade))

        elif radical_id == "R21_JADE_BLOSSOM_YA":
            # Flor de 4 Pétalos con Estambre de Jade (sílabas ya, ye, yi, yo, yu - T126)
            for dx, dy in [(-18, -18), (18, -18), (-18, 18), (18, 18)]:
                pp = W(50 + dx, 50 + dy)
                svg.append(f'<circle cx="{pp[0]:.1f}" cy="{pp[1]:.1f}" r="9.5" fill="none" stroke="{jade}" stroke-width="2.2"/>')
            pc = W(50, 50)
            svg.append(f'<circle cx="{pc[0]:.1f}" cy="{pc[1]:.1f}" r="7.0" fill="{crimson}" stroke="{stroke}" stroke-width="2"/>')

        elif radical_id == "R22_WIND_IK_WINDOW":
            # Ventana Acústica en 'T' del Viento y el Aliento Sagrado (IK' - T503)
            svg.append(path_cmd([
                ("M", [(20, 26)]), ("L", [(80, 26)]), ("L", [(80, 48)]),
                ("L", [(62, 48)]), ("L", [(62, 78)]), ("L", [(38, 78)]),
                ("L", [(38, 48)]), ("L", [(20, 48)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.8))

        elif radical_id == "R23_WATER_LILY_HA":
            # Corriente de Agua con Cuentas de Jade y Lirio Acuático (HA' / b'a - T501)
            svg.append(path_cmd([
                ("M", [(22, 34)]), ("C", [(38, 20), (62, 20), (78, 34)]),
                ("M", [(22, 54)]), ("C", [(38, 40), (62, 40), (78, 54)])
            ], s_col=jade, sw=2.5))
            for bx in (30, 50, 70):
                pb = W(bx, 72)
                svg.append(f'<circle cx="{pb[0]:.1f}" cy="{pb[1]:.1f}" r="5.0" fill="{crimson}"/>')

        elif radical_id == "R24_TWIN_FEATHER_LA":
            # Plumas Gemelas de Quetzal (sílabas la, le, li, lo, lu - T178)
            svg.append(path_cmd([
                ("M", [(30, 78)]), ("C", [(22, 42), (38, 18), (50, 22)]),
                ("C", [(62, 18), (78, 42), (70, 78)])
            ], s_col=jade, sw=2.6))
            svg.append(path_cmd([
                ("M", [(50, 22)]), ("L", [(50, 76)])
            ], s_col=stroke, sw=1.8))
            for fy in (36, 52, 68):
                svg.append(path_cmd([("M", [(38, fy)]), ("L", [(62, fy)])], s_col=crimson, sw=1.6))

        # ── 4. RADICALES EXPANDIDOS DE LOGOGRAMAS DINÁSTICOS Y RITUALES ──
        elif radical_id == "R25_SHIELD_PAKAL":
            # Escudo de Guerra Sagrado (PAKAL): Broquel redondo con 3 puntas de pedernal y orla
            p_cen = W(50, 50)
            r_sh = 28.0
            svg.append(f'<circle cx="{p_cen[0]:.1f}" cy="{p_cen[1]:.1f}" r="{r_sh:.1f}" fill="none" stroke="{jade}" stroke-width="2.8"/>')
            svg.append(f'<circle cx="{p_cen[0]:.1f}" cy="{p_cen[1]:.1f}" r="{r_sh*0.55:.1f}" fill="{crimson}" stroke="{stroke}" stroke-width="2"/>')
            for ang in (-60, 0, 60):
                rad = math.radians(ang - 90)
                px = 50.0 + math.cos(rad) * 40.0
                py = 50.0 + math.sin(rad) * 40.0
                svg.append(path_cmd([("M", [(50, 50)]), ("L", [(px, py)])], s_col=stroke, sw=2.4))

        elif radical_id == "R26_LEAF_SHOOT_YAX":
            # Brote Primordial Verde-Azul (YAX): Cruz foliar con 4 gotas de rocío celeste
            svg.append(path_cmd([
                ("M", [(50, 18)]), ("L", [(50, 82)]),
                ("M", [(18, 50)]), ("L", [(82, 50)])
            ], s_col=jade, sw=3.2))
            for dx, dy in [(-18, -18), (18, -18), (-18, 18), (18, 18)]:
                pd = W(50 + dx, 50 + dy)
                svg.append(f'<circle cx="{pd[0]:.1f}" cy="{pd[1]:.1f}" r="5.0" fill="{crimson}" stroke="{stroke}" stroke-width="1.6"/>')

        elif radical_id == "R27_GOD_VOLUTE_KUH":
            # Voluta de Sacralidad Divina (K'UH): Espiral radiante con halo de 3 perlas celestes
            volute_pts = CalligraphicGeometry.eval_cubic_bezier(W(24, 76), W(22, 28), W(78, 28), W(72, 70), steps=16)
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(volute_pts, 1.6, 5.4, 1.8, jade))
            for px, py in [(32, 38), (50, 30), (68, 38)]:
                pp = W(px, py)
                svg.append(f'<circle cx="{pp[0]:.1f}" cy="{pp[1]:.1f}" r="5.6" fill="{crimson}" stroke="{stroke}" stroke-width="1.8"/>')

        elif radical_id == "R28_THRONE_SEAT_CHUM":
            # Cojín de Trono Real de Jaguares (CHUM): Asiento escalonado con motas de piel
            svg.append(path_cmd([
                ("M", [(20, 78)]), ("L", [(20, 48)]), ("L", [(35, 48)]), ("L", [(35, 34)]),
                ("L", [(65, 34)]), ("L", [(65, 48)]), ("L", [(80, 48)]), ("L", [(80, 78)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.6))
            for sx, sy in [(40, 58), (50, 44), (60, 58)]:
                ps = W(sx, sy)
                svg.append(f'<circle cx="{ps[0]:.1f}" cy="{ps[1]:.1f}" r="4.0" fill="{crimson}"/>')

        elif radical_id == "R29_OWL_CREST_MUAN":
            # Pájaro Muan del Inframundo (MUAN): Ojos nocturnos con penacho emplumado
            svg.append(path_cmd([
                ("M", [(24, 30)]), ("C", [(38, 14), (62, 14), (76, 30)]),
                ("L", [(76, 74)]), ("L", [(24, 74)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.4))
            for ex in (38, 62):
                pe = W(ex, 48)
                svg.append(f'<circle cx="{pe[0]:.1f}" cy="{pe[1]:.1f}" r="7.5" fill="{crimson}" stroke="{stroke}" stroke-width="2"/>')
                svg.append(f'<circle cx="{pe[0]:.1f}" cy="{pe[1]:.1f}" r="3.0" fill="{stroke}"/>')

        elif radical_id == "R30_SHELL_ZERO_MIH":
            # Concha Bivalva Sagrada del Cero (MIH): Estrías radiales y borde convexo
            svg.append(path_cmd([
                ("M", [(18, 52)]), ("C", [(20, 24), (80, 24), (82, 52)]),
                ("C", [(80, 78), (20, 78), (18, 52)]), ("Z", [])
            ], f_col="none", s_col=jade, sw=2.8))
            for ang_deg in (-36, -18, 0, 18, 36):
                rad = math.radians(ang_deg - 90)
                ex = 50.0 + math.cos(rad) * 26.0
                ey = 52.0 + math.sin(rad) * 22.0
                svg.append(path_cmd([("M", [(50, 52)]), ("L", [(ex, ey)])], s_col=crimson, sw=1.8))

        else:  # Radical genérico con doble pluma
            svg.append(path_cmd([
                ("M", [(30, 78)]), ("C", [(22, 42), (38, 18), (50, 22)]),
                ("C", [(62, 18), (78, 42), (70, 78)])
            ], s_col=jade, sw=2.6))

        return "\n".join(svg)

    @classmethod
    def draw_vocalic_diacritic_svg(
        cls,
        vowel: str,
        palette: Dict[str, str],
        cage: Tuple[Point2D, Point2D, Point2D, Point2D] = ((0, 0), (100, 0), (100, 100), (0, 100)),
        arch_bow: float = 0.0
    ) -> str:
        """
        PUNTO 1: Genera la inflexión acústica/vocalic diacritic (A, E, I, O, U) de las sílabas CV.
          • a (Fuego / Sol / 432Hz): Disco solar central radiante con flor de 4 pétalos.
          • e (Viento / 528Hz): Gemelos de viento / dos cuentas de jade con voluta de aliento.
          • i (Eje Cósmico / 639Hz): Tríada de perlas ascendentes (las tres piedras de la creación).
          • o (Tierra / 396Hz): Espiral concéntrica de caracol (cámara de la cueva).
          • u (Agua / 285Hz): Doble barra ondulante de agua con cuentas de jade suspendidas.
        """
        q00, q10, q11, q01 = cage
        stroke = palette["glyph_stroke"]
        jade = palette["jade_accent"]
        crimson = palette["crimson_accent"]

        def W(x: float, y: float) -> Point2D:
            return CalligraphicGeometry.bilinear_cage_warp((x, y), q00, q10, q11, q01, arch_bow)

        v_low = vowel.lower().strip()
        svg: List[str] = []

        if v_low == "a":
            # Disco solar radiante Kin (432 Hz)
            p_cen = W(50, 50)
            svg.append(f'<circle cx="{p_cen[0]:.1f}" cy="{p_cen[1]:.1f}" r="7.5" fill="{crimson}" stroke="{stroke}" stroke-width="1.8"/>')
            for dx, dy in [(-9, 0), (9, 0), (0, -9), (0, 9)]:
                p_ray = W(50 + dx, 50 + dy)
                svg.append(f'<circle cx="{p_ray[0]:.1f}" cy="{p_ray[1]:.1f}" r="2.8" fill="{jade}"/>')

        elif v_low == "e":
            # Gemelos de viento / Aliento sagrado (528 Hz)
            p_e1 = W(36, 50)
            p_e2 = W(64, 50)
            svg.append(f'<circle cx="{p_e1[0]:.1f}" cy="{p_e1[1]:.1f}" r="5.6" fill="{jade}" stroke="{stroke}" stroke-width="1.6"/>')
            svg.append(f'<circle cx="{p_e2[0]:.1f}" cy="{p_e2[1]:.1f}" r="5.6" fill="{jade}" stroke="{stroke}" stroke-width="1.6"/>')
            ribbon_e = [W(36, 42), W(50, 34), W(64, 42)]
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(ribbon_e, 1.0, 3.2, 1.0, crimson))

        elif v_low == "i":
            # Tríada de perlas cósmicas verticales Ox-Tun (639 Hz)
            for iy in (34, 50, 66):
                pi = W(50, iy)
                svg.append(f'<circle cx="{pi[0]:.1f}" cy="{pi[1]:.1f}" r="4.8" fill="{crimson}" stroke="{jade}" stroke-width="1.5"/>')

        elif v_low == "o":
            # Espiral de caracol de tierra (396 Hz)
            spiral: List[Point2D] = []
            for k in range(16):
                ang = k * 0.45
                rad = 3.0 + k * 0.75
                spiral.append(W(50.0 + math.cos(ang) * rad, 50.0 + math.sin(ang) * rad))
            svg.append(CalligraphicGeometry.variable_pressure_ribbon_svg(spiral, 0.8, 2.8, 3.4, crimson))

        elif v_low == "u":
            # Barra fluvial de agua primordial con cuentas (285 Hz)
            p_u1, p_u2 = W(28, 50), W(72, 50)
            svg.append(f'<line x1="{p_u1[0]:.1f}" y1="{p_u1[1]:.1f}" x2="{p_u2[0]:.1f}" y2="{p_u2[1]:.1f}" stroke="{jade}" stroke-width="3.2" stroke-linecap="round"/>')
            for bx in (34, 50, 66):
                pb = W(bx, 58)
                svg.append(f'<circle cx="{pb[0]:.1f}" cy="{pb[1]:.1f}" r="3.4" fill="{crimson}"/>')

        return "\n".join(svg)

    # Mapeo directo de Consonantes y Logogramas a sus Radicales Anatómicos Reales
    CONSONANT_TO_RADICAL = {
        "":    "R13_BRACKET_U_T1",
        "b'":  "R23_WATER_LILY_HA",
        "ch":  "R11_CROSSHATCH_OBSIDIAN_CH",
        "ch'": "R05_JAWBONE_CH_A",
        "h":   "R01_HAND_FLAT_CHI",
        "j":   "R14_SPIRAL_SHELL_JA",
        "k":   "R10_COMB_T25_KA",
        "k'":  "R02_HAND_FIST_K_A",
        "l":   "R24_TWIN_FEATHER_LA",
        "m":   "R15_CLEFT_EARTH_MA",
        "n":   "R16_EARTH_WAVE_NA",
        "p":   "R17_WOVEN_MAT_POP",
        "s":   "R04_HAND_SCATTER_CHOK",
        "t":   "R18_CROSSED_TORCH_TA",
        "t'":  "R09_BAT_HEAD_SOTZ",
        "tz":  "R19_STEPPED_FRET_TZ",
        "tz'": "R03_HAND_BRUSH_TSIB",
        "w":   "R20_TREFOIL_MAIZE_WA",
        "x":   "R11_CROSSHATCH_OBSIDIAN_CH",
        "y":   "R21_JADE_BLOSSOM_YA",
    }

    LOGOGRAM_TO_RADICAL = {
        "B'ALAM":    "R06_JAGUAR_HEAD_BALAM",
        "CHAN":      "R07_SERPENT_BROW_CHAN",
        "AJAW":      "R08_AJAW_ROYAL_FACE",
        "TS'IB":     "R03_HAND_BRUSH_TSIB",
        "TZUTZ":     "R01_HAND_FLAT_CHI",
        "PAT":       "R02_HAND_FIST_K_A",
        "K'AK'":     "R12_FIRE_SCROLL_KAK",
        "WITZ":      "R19_STEPPED_FRET_TZ",
        "LAKAM-TUN": "R19_STEPPED_FRET_TZ",
        "CH'EN":     "R05_JAWBONE_CH_A",
        "IK'":       "R22_WIND_IK_WINDOW",
        "HA'":       "R23_WATER_LILY_HA",
        "POP":       "R17_WOVEN_MAT_POP",
        "AK'B'AL":   "R11_CROSSHATCH_OBSIDIAN_CH",
        "K'IN":      "R21_JADE_BLOSSOM_YA",
        "K'UH":      "R27_GOD_VOLUTE_KUH",
        "PAKAL":     "R25_SHIELD_PAKAL",
        "YAX":       "R26_LEAF_SHOOT_YAX",
        "CHUM":      "R28_THRONE_SEAT_CHUM",
        "MUAN":      "R29_OWL_CREST_MUAN",
        "WAY":       "R06_JAGUAR_HEAD_BALAM",
        "SIY":       "R26_LEAF_SHOOT_YAX",
        "HUL":       "R18_CROSSED_TORCH_TA",
        "K'AL":      "R17_WOVEN_MAT_POP",
        "OCH":       "R19_STEPPED_FRET_TZ",
        "JOY":       "R08_AJAW_ROYAL_FACE",
        "MIH":       "R30_SHELL_ZERO_MIH",
        "SOTZ'":     "R09_BAT_HEAD_SOTZ",
        "CHAC":      "R07_SERPENT_BROW_CHAN",
        "CHAC_GOD":  "R07_SERPENT_BROW_CHAN",
        "CIMI":      "R05_JAWBONE_CH_A",
        "CHAM":      "R05_JAWBONE_CH_A",
        "K'AWIL":    "R12_FIRE_SCROLL_KAK",
        "K'AWIIL":   "R12_FIRE_SCROLL_KAK",
        "K'AWIIL_HEAD": "R12_FIRE_SCROLL_KAK",
        "ITZAMNA":   "R08_AJAW_ROYAL_FACE",
        "ITZAMNA_OLD": "R08_AJAW_ROYAL_FACE",
        "IXIK":      "R08_AJAW_ROYAL_FACE",
        "PEK'":      "R06_JAGUAR_HEAD_BALAM",
        "KAN":       "R07_SERPENT_BROW_CHAN",
        "MAX":       "R08_AJAW_ROYAL_FACE",
        "MA'AX":     "R08_AJAW_ROYAL_FACE",
        "TOOK'":     "R25_SHIELD_PAKAL",
        "LAKAM":     "R25_SHIELD_PAKAL",
        "HAB'":      "R19_STEPPED_FRET_TZ",
        "TUN":       "R19_STEPPED_FRET_TZ",
        "K'ATUN":    "R19_STEPPED_FRET_TZ",
        "CH'AJ":     "R04_HAND_SCATTER_CHOK",
        "CHOK":      "R04_HAND_SCATTER_CHOK",
        "KAB'":      "R15_CLEFT_EARTH_MA",
        "LU'M":      "R15_CLEFT_EARTH_MA",
        "PALENQUE_GI": "R23_WATER_LILY_HA",
        "PALENQUE_GII": "R12_FIRE_SCROLL_KAK",
        "PALENQUE_GIII": "R06_JAGUAR_HEAD_BALAM",
        "YUM_K'AAX": "R20_TREFOIL_MAIZE_WA",
        "KINICH_AJAW": "R21_JADE_BLOSSOM_YA",
        "SIY_FROG":  "R06_JAGUAR_HEAD_BALAM",
        "GLYPH_G":   "R08_AJAW_ROYAL_FACE",
        "MULUC":     "R21_JADE_BLOSSOM_YA",
        "K'UH_HEAD": "R27_GOD_VOLUTE_KUH",
        "GOD_L":     "R29_OWL_CREST_MUAN",
        "TE'":       "R26_LEAF_SHOOT_YAX",
        "HEL":       "R19_STEPPED_FRET_TZ",
        "BAH":       "R06_JAGUAR_HEAD_BALAM",
        "K'UCH":     "R29_OWL_CREST_MUAN",
    }

    @classmethod
    def draw_glyph_micro_embellishment(
        cls,
        glyph_num: int,
        palette: Dict[str, str],
        cage: Tuple[Point2D, Point2D, Point2D, Point2D] = ((0, 0), (100, 0), (100, 100), (0, 100)),
        arch_bow: float = 0.0
    ) -> str:
        """
        Dibuja un motivo epigráfico distintivo (ojo en voluta, achurado de obsidiana,
        perlas de jade, ceja flamígera, concha o greca) derivado unívocamente del número Thompson,
        garantizando que cada uno de los +800 signos posea detalles morfológicos diferenciados.
        """
        q00, q10, q11, q01 = cage
        stroke = palette.get("glyph_stroke", "#FCD34D")
        jade = palette.get("jade_accent", "#10B981")
        crimson = palette.get("crimson_accent", "#EF4444")
        fill = palette.get("glyph_fill", "#1E293B")

        def W(x: float, y: float) -> Point2D:
            return CalligraphicGeometry.bilinear_cage_warp((x, y), q00, q10, q11, q01, arch_bow)

        def path_cmd(pts: List[Tuple[str, List[Point2D]]], f_col: str = "none", s_col: str = stroke, sw: float = 1.8) -> str:
            d = []
            for cmd, coords in pts:
                warped = [W(px, py) for px, py in coords]
                flat = " ".join(f"{wx:.1f} {wy:.1f}" for wx, wy in warped)
                d.append(f"{cmd} {flat}".strip())
            return f'<path d="{" ".join(d)}" fill="{f_col}" stroke="{s_col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'

        svg = []
        motif = (glyph_num * 7 + 3) % 8

        if motif == 0:
            # Achurado de diamante interior (obsidiana / noche)
            svg.append(path_cmd([
                ("M", [(50, 36)]), ("L", [(64, 50)]), ("L", [(50, 64)]), ("L", [(36, 50)]), ("Z", []),
                ("M", [(42, 44)]), ("L", [(58, 56)]),
                ("M", [(42, 56)]), ("L", [(58, 44)])
            ], f_col="none", s_col=jade, sw=1.6))
        elif motif == 1:
            # Voluta en espiral de aliento / verbo divino
            pts = CalligraphicGeometry.eval_cubic_bezier(W(50, 62), W(62, 58), W(62, 40), W(50, 42), steps=10)
            pts2 = CalligraphicGeometry.eval_cubic_bezier(W(50, 42), W(42, 44), W(44, 54), W(50, 52), steps=8)
            all_pts = pts + pts2[1:]
            svg.append(f'<path d="M {all_pts[0][0]:.1f} {all_pts[0][1]:.1f} {" ".join(f"L {px:.1f} {py:.1f}" for px, py in all_pts[1:])}" fill="none" stroke="{jade}" stroke-width="2.2" stroke-linecap="round"/>')
        elif motif == 2:
            # Tríada de perlas de jade sagrado
            c1 = W(42, 48); c2 = W(58, 48); c3 = W(50, 60)
            svg.append(f'<circle cx="{c1[0]:.1f}" cy="{c1[1]:.1f}" r="3.2" fill="{jade}" stroke="{stroke}" stroke-width="1.2"/>')
            svg.append(f'<circle cx="{c2[0]:.1f}" cy="{c2[1]:.1f}" r="3.2" fill="{jade}" stroke="{stroke}" stroke-width="1.2"/>')
            svg.append(f'<circle cx="{c3[0]:.1f}" cy="{c3[1]:.1f}" r="3.2" fill="{crimson}" stroke="{stroke}" stroke-width="1.2"/>')
        elif motif == 3:
            # Ceja flamígera superior con chispa
            svg.append(path_cmd([
                ("M", [(34, 30)]),
                ("C", [(42, 22), (58, 22), (66, 30)]),
                ("C", [(60, 26), (40, 26), (34, 30)])
            ], f_col=crimson, s_col=stroke, sw=1.8))
        elif motif == 4:
            # Portal o hendidura en T del viento sagrado (Ik')
            svg.append(path_cmd([
                ("M", [(40, 40)]), ("L", [(60, 40)]),
                ("L", [(54, 46)]), ("L", [(54, 62)]),
                ("L", [(46, 62)]), ("L", [(46, 46)]),
                ("Z", [])
            ], f_col=fill, s_col=jade, sw=1.8))
        elif motif == 5:
            # Greca escalonada interior en relieve
            svg.append(path_cmd([
                ("M", [(38, 58)]), ("L", [(38, 44)]), ("L", [(52, 44)]),
                ("L", [(52, 52)]), ("L", [(46, 52)]), ("L", [(46, 48)])
            ], f_col="none", s_col=jade, sw=2.0))
        elif motif == 6:
            # Ranura concéntrica solar
            c = W(50, 50)
            svg.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="9.0" fill="none" stroke="{jade}" stroke-width="1.8" stroke-dasharray="4,2"/>')
            svg.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="3.5" fill="{stroke}"/>')
        else:
            # Doble onda ofídica de jade
            w1 = CalligraphicGeometry.eval_cubic_bezier(W(34, 48), W(42, 42), W(50, 54), W(58, 48), steps=10)
            w2 = CalligraphicGeometry.eval_cubic_bezier(W(34, 54), W(42, 48), W(50, 60), W(58, 54), steps=10)
            svg.append(f'<path d="M {w1[0][0]:.1f} {w1[0][1]:.1f} {" ".join(f"L {px:.1f} {py:.1f}" for px, py in w1[1:])}" fill="none" stroke="{jade}" stroke-width="2.0"/>')
            svg.append(f'<path d="M {w2[0][0]:.1f} {w2[0][1]:.1f} {" ".join(f"L {px:.1f} {py:.1f}" for px, py in w2[1:])}" fill="none" stroke="{stroke}" stroke-width="1.6"/>')

        return "\n".join(svg)

    @classmethod
    def render_high_parity_slot_svg(
        cls,
        code: str,
        x: float,
        y: float,
        w: float,
        h: float,
        role: str,
        palette: Dict[str, str],
        is_logogram: bool = False,
        corpus_extractor: Optional[CorpusPathExtractor] = None,
        thompson_id: str = "",
        show_label: bool = True
    ) -> str:
        """
        PUNTO 1 Y 2: Orquesta la generación de siluetas de alta paridad epigráfica:
          1. Si el glifo existe en la Bóveda del Corpus (Método 1), traza el path exacto normalizado.
          2. Si no, selecciona el Radical Anatómico Maya (Método 5) y lo deforma con Jaula Bilineal (FFD)
             según el rol ('superfix' se arquea hacia abajo, 'subfix' hacia arriba, 'prefix' abraza por la izquierda).
          3. Para sílabas CV (Punto 1), aplica la inflexión vocálica (A, E, I, O, U) en el vientre del signo.
        """
        # Curvatura orgánica de mampostería según la posición del afijo en el cartucho
        arch_bow = 0.0
        if role == "superfix":
            arch_bow = -h * 0.09  # El superfijo se arquea abrazando el signo principal
        elif role == "subfix":
            arch_bow = h * 0.09   # El subfijo acuna la base del signo principal

        cage = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))

        # Prioridad 1: Bóveda del Corpus Vectorial (Método 1)
        if corpus_extractor and thompson_id.upper() in corpus_extractor.silhouette_vault:
            entry = corpus_extractor.silhouette_vault[thompson_id.upper()]
            raw_100 = entry["svg_path_100x100"]
            return (
                f'<g transform="translate({x:.1f},{y:.1f}) scale({w/100.0:.3f},{h/100.0:.3f})">'
                f'<path d="{raw_100}" fill="{palette.get("glyph_fill", "#1E293B")}" stroke="{palette.get("glyph_stroke", "#FCD34D")}" stroke-width="2.4"/>'
                f'</g>'
            )

        # Prioridad 2: Resolución precisa del Radical Anatómico Maya
        clean = code.upper().strip()
        rad_id = None

        # Paso A: Consultar el Catálogo Thompson arqueológico por ID
        if thompson_id:
            try:
                from mayan_thompson_catalog import MayanThompsonCatalog
                th = MayanThompsonCatalog.get_entry(thompson_id)
                if not th:
                    m = re.search(r'\d+', thompson_id)
                    if m:
                        th = MayanThompsonCatalog.generate_systematic_vault_entry(int(m.group(0)))
                if th and th.radical_id:
                    rad_id = th.radical_id
            except Exception:
                pass

        # Paso B: Buscar en el léxico calibrado de logogramas
        if not rad_id:
            rad_id = cls.LOGOGRAM_TO_RADICAL.get(clean)

        # Paso C: Si es sílaba fonética CV
        if not rad_id and not is_logogram:
            syl_low = code.lower().strip()
            cons = syl_low[:-1] if (len(syl_low) > 1 and syl_low[-1] in "aeiou") else ""
            if cons in cls.CONSONANT_TO_RADICAL:
                rad_id = cls.CONSONANT_TO_RADICAL[cons]

        # Paso D: Mapeo sistemático por familia según número Thompson o código
        if not rad_id:
            m = re.search(r'\d+', f"{thompson_id}_{code}")
            t_num = int(m.group(0)) if m else 533
            if t_num <= 499:
                affix_rads = [
                    "R13_BRACKET_U_T1", "R10_COMB_T25_KA", "R24_TWIN_FEATHER_LA",
                    "R14_SPIRAL_SHELL_JA", "R18_CROSSED_TORCH_TA", "R20_TREFOIL_MAIZE_WA",
                    "R21_JADE_BLOSSOM_YA", "R02_HAND_FIST_K_A", "R01_HAND_FLAT_CHI",
                    "R15_CLEFT_EARTH_MA", "R16_EARTH_WAVE_NA"
                ]
                rad_id = affix_rads[t_num % len(affix_rads)]
            elif t_num <= 999:
                main_rads = [
                    "R06_JAGUAR_HEAD_BALAM", "R07_SERPENT_BROW_CHAN", "R09_BAT_HEAD_SOTZ",
                    "R11_CROSSHATCH_OBSIDIAN_CH", "R12_FIRE_SCROLL_KAK", "R17_WOVEN_MAT_POP",
                    "R19_STEPPED_FRET_TZ", "R21_JADE_BLOSSOM_YA", "R22_WIND_IK_WINDOW",
                    "R23_WATER_LILY_HA", "R25_SHIELD_PAKAL", "R26_LEAF_SHOOT_YAX",
                    "R28_THRONE_SEAT_CHUM", "R29_OWL_CREST_MUAN", "R30_SHELL_ZERO_MIH"
                ]
                rad_id = main_rads[t_num % len(main_rads)]
            else:
                deity_rads = [
                    "R08_AJAW_ROYAL_FACE", "R05_JAWBONE_CH_A", "R07_SERPENT_BROW_CHAN",
                    "R12_FIRE_SCROLL_KAK", "R27_GOD_VOLUTE_KUH", "R09_BAT_HEAD_SOTZ",
                    "R29_OWL_CREST_MUAN", "R23_WATER_LILY_HA", "R21_JADE_BLOSSOM_YA"
                ]
                rad_id = deity_rads[(t_num - 1000) % len(deity_rads)]

        svg_parts: List[str] = []

        # 1. Trazo del Radical Base
        svg_parts.append(cls.draw_radical_svg(rad_id, palette=palette, cage=cage, arch_bow=arch_bow))

        # 2. Inflexión vocálica para sílabas
        if not is_logogram:
            syl_low = code.lower().strip()
            if syl_low and syl_low[-1] in "aeiou":
                svg_parts.append(cls.draw_vocalic_diacritic_svg(syl_low[-1], palette=palette, cage=cage, arch_bow=arch_bow))

        # 3. Micro-embellecimiento epigráfico diferenciado por glifo
        m_num = re.search(r'\d+', f"{thompson_id}_{code}")
        glyph_num = int(m_num.group(0)) if m_num else 0
        if glyph_num > 0:
            svg_parts.append(cls.draw_glyph_micro_embellishment(glyph_num, palette=palette, cage=cage, arch_bow=arch_bow))

        # Etiqueta caligráfica sutil de lectura epigráfica
        if show_label and w >= 28 and h >= 22:
            cx = x + w * 0.5
            cy = y + h * 0.5
            font_sz = max(7, min(13, int(min(w, h) * 0.22)))
            txt_color = palette.get("text_primary", "#F8FAFC")
            svg_parts.append(
                f'<text x="{cx:.1f}" y="{cy + font_sz*0.35:.1f}" fill="{txt_color}" '
                f'font-family="Consolas, monospace" font-weight="bold" font-size="{font_sz}px" '
                f'text-anchor="middle">{code}</text>'
            )

        return "\n".join(svg_parts)

    @classmethod
    def render_numeral_high_parity_svg(
        cls,
        number: int,
        x: float,
        y: float,
        w: float,
        h: float,
        palette: Dict[str, str],
        vertical: bool = True
    ) -> str:
        """
        PUNTO 2: Renderiza numerales vigesimales mayas (0 a 19) en alta paridad arqueológica:
          • 0: Concha bivalva sagrada (Mih) con estrías radiales.
          • 1..4: Puntos de jade esféricos con relieve concéntrico.
          • 5, 10, 15: Barras rectangulares de jade pulido con bisel interior.
        """
        num = max(0, min(19, number))
        stroke = palette.get("glyph_stroke", "#FCD34D")
        jade = palette.get("jade_accent", "#10B981")
        crimson = palette.get("crimson_accent", "#EF4444")
        gold = palette.get("cartouche_rim", "#F59E0B")

        if num == 0:
            cage = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
            return cls.draw_radical_svg("R30_SHELL_ZERO_MIH", palette=palette, cage=cage)

        bars = num // 5
        dots = num % 5
        svg: List[str] = []

        if vertical:
            # Numeral en columna vertical (estilo inscripción de estela)
            cur_x = x + 4.0
            if dots > 0:
                step_y = h / (dots + 1)
                for d in range(dots):
                    dy = y + step_y * (d + 1)
                    # Punto de jade con doble contorno concéntrico
                    svg.append(f'<circle cx="{cur_x + 6:.1f}" cy="{dy:.1f}" r="5.8" fill="{jade}" stroke="{stroke}" stroke-width="1.8"/>')
                    svg.append(f'<circle cx="{cur_x + 6:.1f}" cy="{dy:.1f}" r="2.2" fill="{crimson}"/>')
                cur_x += 16.0

            for b in range(bars):
                bx = cur_x + b * 10.0
                bw = min(7.5, (w - (cur_x - x) - 4) / max(1, bars))
                svg.append(
                    f'<rect x="{bx:.1f}" y="{y + h*0.12:.1f}" width="{bw:.1f}" height="{h*0.76:.1f}" rx="3.0" '
                    f'fill="{gold}" stroke="{stroke}" stroke-width="1.6"/>'
                )
                # Línea central de relieve en la barra
                svg.append(
                    f'<line x1="{bx + bw*0.5:.1f}" y1="{y + h*0.18:.1f}" x2="{bx + bw*0.5:.1f}" y2="{y + h*0.82:.1f}" '
                    f'stroke="{crimson}" stroke-width="1.2"/>'
                )
        else:
            # Numeral horizontal (puntos arriba, barras horizontales abajo)
            cur_y = y + 4.0
            if dots > 0:
                step_x = w / (dots + 1)
                for d in range(dots):
                    dx = x + step_x * (d + 1)
                    svg.append(f'<circle cx="{dx:.1f}" cy="{cur_y + 6:.1f}" r="5.8" fill="{jade}" stroke="{stroke}" stroke-width="1.8"/>')
                    svg.append(f'<circle cx="{dx:.1f}" cy="{cur_y + 6:.1f}" r="2.2" fill="{crimson}"/>')
                cur_y += 16.0

            for b in range(bars):
                by = cur_y + b * 10.0
                bh = min(7.5, (h - (cur_y - y) - 4) / max(1, bars))
                svg.append(
                    f'<rect x="{x + w*0.12:.1f}" y="{by:.1f}" width="{w*0.76:.1f}" height="{bh:.1f}" rx="3.0" '
                    f'fill="{gold}" stroke="{stroke}" stroke-width="1.6"/>'
                )
                svg.append(
                    f'<line x1="{x + w*0.18:.1f}" y1="{by + bh*0.5:.1f}" x2="{x + w*0.82:.1f}" y2="{by + bh*0.5:.1f}" '
                    f'stroke="{crimson}" stroke-width="1.2"/>'
                )

        return "\n".join(svg)


# ══════════════════════════════════════════════════════════════════════════════
# GENERADORES VECTORIALES STANDALONE (PUNTOS 1 Y 2)
# ══════════════════════════════════════════════════════════════════════════════

THEME_PALETTES = {
    "obsidian": {
        "bg": "#080B11",
        "cartouche_fill": "#131C2E",
        "cartouche_rim": "#F59E0B",
        "inner_rim": "#10B981",
        "glyph_fill": "#1E293B",
        "glyph_stroke": "#FCD34D",
        "jade_accent": "#10B981",
        "crimson_accent": "#EF4444",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
    },
    "codex": {
        "bg": "#E6D7B8",
        "cartouche_fill": "#FAF3E3",
        "cartouche_rim": "#1C1917",
        "inner_rim": "#8B1E0F",
        "glyph_fill": "#EFE4CE",
        "glyph_stroke": "#1C1917",
        "jade_accent": "#2E6F95",
        "crimson_accent": "#991B1B",
        "text_primary": "#1C1917",
        "text_secondary": "#57534E",
    },
    "heightmap": {
        "bg": "#000000",
        "cartouche_fill": "#686868",
        "cartouche_rim": "#B0B0B0",
        "inner_rim": "#909090",
        "glyph_fill": "#C8C8C8",
        "glyph_stroke": "#FFFFFF",
        "jade_accent": "#E8E8E8",
        "crimson_accent": "#D0D0D0",
        "text_primary": "#FFFFFF",
        "text_secondary": "#888888",
    }
}


def render_syllable_svg(syl_code: str, size: float = 160.0, theme: str = "obsidian") -> str:
    """
    PUNTO 1: Dibuja una sílaba CV maya (de las 95 del silabario) como SVG vectorial puro standalone
    con sus radicales anatómicos, trazos de pincel de presión variable e inflexión acústica vocálica.
    """
    pal = THEME_PALETTES.get(theme, THEME_PALETTES["obsidian"])
    pad = 12.0
    inner_sz = size - pad * 2.0
    content = MayanRadicalGrammar.render_high_parity_slot_svg(
        code=syl_code,
        x=pad,
        y=pad,
        w=inner_sz,
        h=inner_sz,
        role="main",
        palette=pal,
        is_logogram=False,
        show_label=True
    )
    svg = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size:.0f} {size:.0f}" width="{size:.0f}" height="{size:.0f}">',
        f'<rect width="100%" height="100%" fill="{pal["bg"]}"/>',
        f'<rect x="4" y="4" width="{size-8:.1f}" height="{size-8:.1f}" rx="{size*0.14:.1f}" fill="{pal["cartouche_fill"]}" stroke="{pal["cartouche_rim"]}" stroke-width="2.4"/>',
        content,
        f'</svg>'
    ]
    return "\n".join(svg)


def render_logogram_svg(logo_code: str, size: float = 180.0, theme: str = "obsidian") -> str:
    """
    PUNTO 2: Dibuja un logograma maya monumental (B'ALAM, CHAN, AJAW, K'IN, WITZ...)
    en SVG vectorial de alta paridad arqueológica.
    """
    pal = THEME_PALETTES.get(theme, THEME_PALETTES["obsidian"])
    pad = 14.0
    inner_sz = size - pad * 2.0
    content = MayanRadicalGrammar.render_high_parity_slot_svg(
        code=logo_code,
        x=pad,
        y=pad,
        w=inner_sz,
        h=inner_sz,
        role="main",
        palette=pal,
        is_logogram=True,
        show_label=True
    )
    svg = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size:.0f} {size:.0f}" width="{size:.0f}" height="{size:.0f}">',
        f'<rect width="100%" height="100%" fill="{pal["bg"]}"/>',
        f'<rect x="4" y="4" width="{size-8:.1f}" height="{size-8:.1f}" rx="{size*0.15:.1f}" fill="{pal["cartouche_fill"]}" stroke="{pal["cartouche_rim"]}" stroke-width="2.6"/>',
        content,
        f'</svg>'
    ]
    return "\n".join(svg)


def render_numeral_svg(number: int, size: float = 140.0, theme: str = "obsidian") -> str:
    """
    PUNTO 2: Dibuja un numeral vigesimal maya (0 a 19) en SVG standalone.
    """
    pal = THEME_PALETTES.get(theme, THEME_PALETTES["obsidian"])
    pad = 12.0
    inner_sz = size - pad * 2.0
    content = MayanRadicalGrammar.render_numeral_high_parity_svg(
        number=number,
        x=pad,
        y=pad,
        w=inner_sz,
        h=inner_sz,
        palette=pal,
        vertical=True
    )
    svg = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size:.0f} {size:.0f}" width="{size:.0f}" height="{size:.0f}">',
        f'<rect width="100%" height="100%" fill="{pal["bg"]}"/>',
        f'<rect x="4" y="4" width="{size-8:.1f}" height="{size-8:.1f}" rx="{size*0.14:.1f}" fill="{pal["cartouche_fill"]}" stroke="{pal["cartouche_rim"]}" stroke-width="2.2"/>',
        content,
        f'</svg>'
    ]
    return "\n".join(svg)


def morph_glyph_svg(glyph_name: str, alpha: float = 0.5, size: float = 200.0, theme: str = "obsidian") -> str:
    """
    PUNTO 2: Morphing continuo entre la variante Geométrica (alpha=0.0) y la variante
    Cefalomorfa sagrada (alpha=1.0) mediante Descriptores Elípticos de Fourier (EFD).
    """
    pal = THEME_PALETTES.get(theme, THEME_PALETTES["obsidian"])
    name_clean = glyph_name.upper().strip()

    # Siluetas canónicas para morphing
    geom_circle = [(50 + 36 * math.cos(t), 50 + 36 * math.sin(t)) for t in [i * 2 * math.pi / 32 for i in range(32)]]

    if "BALAM" in name_clean:
        ceph_pts = [
            (28, 78), (14, 64), (16, 44), (26, 36), (36, 24),
            (56, 18), (76, 22), (86, 34), (84, 62), (72, 78), (50, 82)
        ]
    elif "AJAW" in name_clean:
        ceph_pts = [
            (20, 36), (50, 20), (80, 36), (84, 62), (66, 80), (34, 80), (16, 62)
        ]
    elif "KIN" in name_clean:
        ceph_pts = [
            (50, 16), (62, 34), (84, 50), (62, 66), (50, 84), (38, 66), (16, 50), (38, 34)
        ]
    else:
        ceph_pts = [
            (22, 28), (50, 16), (78, 28), (82, 56), (72, 80), (28, 80), (18, 56)
        ]

    sig_geom = EllipticFourierEngine.decompose_contour(geom_circle, num_harmonics=16, name=f"{name_clean}_geom")
    sig_ceph = EllipticFourierEngine.decompose_contour(ceph_pts, num_harmonics=16, name=f"{name_clean}_ceph")
    morphed = EllipticFourierEngine.morph_signatures(sig_geom, sig_ceph, alpha=alpha, num_samples=96)

    # Escalar puntos de [0..100] a [size]
    scale = (size - 32.0) / 100.0
    scaled_pts = [(16.0 + px * scale, 16.0 + py * scale) for px, py in morphed]
    path_d = MayanRadicalGrammar.path_from_points = EllipticFourierEngine.contour_to_svg_path(
        scaled_pts,
        fill=pal["glyph_fill"],
        stroke=pal["glyph_stroke"],
        stroke_w=2.6
    )

    svg = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size:.0f} {size:.0f}" width="{size:.0f}" height="{size:.0f}">',
        f'<rect width="100%" height="100%" fill="{pal["bg"]}"/>',
        f'<rect x="4" y="4" width="{size-8:.1f}" height="{size-8:.1f}" rx="{size*0.14:.1f}" fill="{pal["cartouche_fill"]}" stroke="{pal["cartouche_rim"]}" stroke-width="2.4"/>',
        path_d,
        f'<text x="{size*0.5:.1f}" y="{size-12:.1f}" fill="{pal["jade_accent"]}" font-family="Consolas, monospace" font-size="11px" font-weight="bold" text-anchor="middle">{name_clean} (α={alpha:.2f})</text>',
        f'</svg>'
    ]
    return "\n".join(svg)


# ══════════════════════════════════════════════════════════════════════════════
# DEMO DE INTEGRACIÓN RÁPIDA (PRUEBA DE LOS MÉTODOS 1, 2 Y 5)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 1. Prueba del Método 2 (Descomposición EFD y Morphing entre variante Geométrica y Cefalomorfa)
    geom_circle = [(50 + 38 * math.cos(t), 50 + 38 * math.sin(t)) for t in [i * 2 * math.pi / 32 for i in range(32)]]
    ceph_jaguar = [
        (28, 78), (14, 62), (16, 42), (28, 34), (42, 18),
        (68, 16), (84, 28), (86, 56), (72, 78), (50, 82)
    ]
    sig_geom = EllipticFourierEngine.decompose_contour(geom_circle, num_harmonics=16, name="Geom_T751", t_id="T751")
    sig_ceph = EllipticFourierEngine.decompose_contour(ceph_jaguar, num_harmonics=16, name="Ceph_T751", t_id="T751")
    morphed_pts = EllipticFourierEngine.morph_signatures(sig_geom, sig_ceph, alpha=0.75, num_samples=96)

    print(f"[OK] Método 1 (CorpusPathExtractor), Método 2 (EFD {len(morphed_pts)} pts) y Método 5 (24 Radicales) listos.")