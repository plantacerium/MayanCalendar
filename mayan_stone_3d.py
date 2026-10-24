#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
MAYAN STONE 3D & RTI SHADING ENGINE (AH POL TUN ENGINE)
══════════════════════════════════════════════════════════════════════════════
Motor de sombreado arqueológico en bajo relieve, reflectancia lítica y emulación
de Reflectance Transformation Imaging (RTI) con luz rasante móvil.

Soporta 5 Materiales Históricos Mesoamericanos:
  1. Caliza de Palenque (Sedimentaria marfil cálida, textura fina)
  2. Toba Volcánica de Copán (Grano poroso verdoso-grisáceo)
  3. Estuco Policromado Clásico (Cal viva, Cinabrio rojo y Azul Maya)
  4. Obsidiana y Basalto de Quiriguá (Cristal volcánico vítreo)
  5. Madera Fósil de Chicozapote de Tikal (Hierro vegetal pulido)
══════════════════════════════════════════════════════════════════════════════
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any, List

import numpy as np
from PIL import Image

# Verificación de PySide6 para rasterización vectorial por hardware
try:
    from PySide6.QtCore import QByteArray, QRectF, Qt
    from PySide6.QtGui import QImage, QPainter, QColor
    from PySide6.QtSvg import QSvgRenderer
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@dataclass
class StoneMaterial:
    """Propiedades ópticas y de reflectancia de un material lítico mesoamericano."""
    name: str
    description: str
    albedo_base: Tuple[float, float, float]       # Color base en el plano intermedio (R, G, B en 0..1)
    albedo_recess: Tuple[float, float, float]     # Color en las cavidades y cortes profundos de cincel
    albedo_apex: Tuple[float, float, float]       # Color en las crestas y aristas biseladas
    diffuse_kd: float = 0.85                      # Coeficiente difuso de Lambert
    specular_ks: float = 0.15                     # Coeficiente especular de Blinn-Phong
    specular_power: float = 24.0                  # Exponente de brillo (rugosidad inversa)
    ao_intensity: float = 0.65                    # Intensidad de oclusión ambiental / sombra de grieta
    is_polychrome: bool = False                   # True para estuco pintado con cinabrio y azul maya


class MayanStoneMaterials:
    """Catálogo de Materiales Arqueológicos Clásicos calibrados."""

    PALENQUE_LIMESTONE = StoneMaterial(
        name="caliza_palenque",
        description="Piedra Caliza de Palenque: Tono marfil cálido con grano sedimentario suave y cortes nítidos de cincel.",
        albedo_base=(0.88, 0.84, 0.74),
        albedo_recess=(0.42, 0.38, 0.31),
        albedo_apex=(0.96, 0.93, 0.86),
        diffuse_kd=0.88,
        specular_ks=0.12,
        specular_power=18.0,
        ao_intensity=0.70
    )

    COPAN_TUFF = StoneMaterial(
        name="toba_copan",
        description="Toba Volcánica de Copán: Roca verde-grisácea andesítica de grano poroso que permitió el altorrelieve 3D.",
        albedo_base=(0.48, 0.54, 0.47),
        albedo_recess=(0.22, 0.26, 0.21),
        albedo_apex=(0.65, 0.72, 0.63),
        diffuse_kd=0.92,
        specular_ks=0.08,
        specular_power=12.0,
        ao_intensity=0.85
    )

    POLYCHROME_STUCCO = StoneMaterial(
        name="estuco_policromado",
        description="Estuco Policromado Clásico: Fondo de cal blanca, relieve principal en Rojo Cinabrio y detalles en Azul Maya.",
        albedo_base=(0.95, 0.93, 0.88),       # Base estuco cal
        albedo_recess=(0.20, 0.15, 0.12),     # Sombras y delineado en carbón
        albedo_apex=(0.82, 0.16, 0.16),       # Rojo Cinabrio / Hematita en la cúspide
        diffuse_kd=0.85,
        specular_ks=0.18,
        specular_power=26.0,
        ao_intensity=0.60,
        is_polychrome=True
    )

    QUIRIGUA_OBSIDIAN = StoneMaterial(
        name="obsidiana_quirigua",
        description="Obsidiana y Basalto de Quiriguá: Roca volcánica vítrea oscura con alta reflectancia especular y brillos prismáticos.",
        albedo_base=(0.14, 0.15, 0.18),
        albedo_recess=(0.04, 0.04, 0.06),
        albedo_apex=(0.32, 0.35, 0.42),
        diffuse_kd=0.45,
        specular_ks=0.55,
        specular_power=75.0,
        ao_intensity=0.80
    )

    TIKAL_CHICOZAPOTE = StoneMaterial(
        name="madera_tikal",
        description="Madera de Chicozapote de Tikal: Hierro vegetal ultra denso pulido al aceite, con veta rojiza profunda.",
        albedo_base=(0.42, 0.22, 0.13),
        albedo_recess=(0.18, 0.08, 0.04),
        albedo_apex=(0.60, 0.35, 0.22),
        diffuse_kd=0.82,
        specular_ks=0.22,
        specular_power=32.0,
        ao_intensity=0.65
    )

    CATALOG: Dict[str, StoneMaterial] = {
        "caliza_palenque": PALENQUE_LIMESTONE,
        "toba_copan": COPAN_TUFF,
        "estuco_policromado": POLYCHROME_STUCCO,
        "obsidiana_quirigua": QUIRIGUA_OBSIDIAN,
        "madera_tikal": TIKAL_CHICOZAPOTE,
    }

    @classmethod
    def get_material(cls, name: str) -> StoneMaterial:
        clean = name.lower().strip()
        for k, mat in cls.CATALOG.items():
            if k in clean or clean in k:
                return mat
        return cls.PALENQUE_LIMESTONE


class MayanStone3DEngine:
    """
    Motor físico de sombreado arqueológico en 3D y análisis RTI.
    Convierte mapas de altura vectoriales en superficies pétreas iluminadas dinámicamente.
    """

    @classmethod
    def rasterize_svg_to_height_grid(
        cls,
        svg_str: str,
        target_width: int = 512,
        target_height: int = 512
    ) -> np.ndarray:
        """
        Rasteriza un SVG vectorial a una matriz NumPy flotante Z ∈ [0.0, 1.0]
        usando QSvgRenderer con interpolación y anti-aliasing por hardware.
        """
        if not PYSIDE6_AVAILABLE:
            return np.zeros((target_height, target_width), dtype=np.float32)

        import sys
        try:
            from PySide6.QtWidgets import QApplication
            _app = QApplication.instance()
            if not _app:
                _app = QApplication(sys.argv)
        except Exception:
            pass

        renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
        if not renderer.isValid():
            return np.zeros((target_height, target_width), dtype=np.float32)

        img = QImage(target_width, target_height, QImage.Format_Grayscale8)
        img.fill(0)

        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        renderer.render(p, QRectF(0, 0, target_width, target_height))
        p.end()

        # Extraer buffer de píxeles
        ptr = img.bits()
        # QImage en formato Grayscale8 tiene 1 byte por píxel
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((target_height, img.bytesPerLine()))
        arr = arr[:, :target_width]  # Recortar padding de línea si existiese

        # Normalizar a Z ∈ [0.0, 1.0]
        z_grid = arr.astype(np.float32) / 255.0
        return z_grid

    @classmethod
    def synthesize_volumetric_relief(
        cls,
        z_raw: np.ndarray,
        pillow_radius: float = 22.0,
        groove_depth: float = 0.28,
        groove_width: float = 3.8,
        add_rock_grain: bool = True
    ) -> np.ndarray:
        """
        Arquitectura Procedural:
        Convierte una silueta o mapa 2D plano en una auténtica escultura lítica tridimensional:
          1. Multi-tier S-Curve Bevels: Curvas de transición no lineal (Hermite S-curve) para aristas y biseles.
          2. Coronación parabólica central: Abomba orgánicamente el vientre de las masas de piedra.
          3. Cincelado en V profundo: Talla las incisiones y líneas internas como ranuras biseladas hacia abajo.
          4. Sedimentary Bedding: Estratificación geológica sutil de roca caliza sedimentaria.
          5. Edge Chipping Wear & Slope Blur: Micro-desprendimientos y lascas líticas en los bordes tallados.
          6. Chisel Toolmarks: Estrías de percutor de obsidiana y azuela en el fondo desbastado.
          7. Preservación limpia y nítida de inscripciones epigráficas y glosas finas.
        """
        try:
            from scipy import ndimage as ndi
        except ImportError:
            return z_raw

        h, w = z_raw.shape

        # Normalizar rango a [0.0, 1.0]
        z_min = float(z_raw.min())
        z_max = float(z_raw.max())
        if z_max - z_min > 1e-4:
            z_norm = (z_raw - z_min) / (z_max - z_min)
        else:
            z_norm = z_raw.copy()

        # Identificar máscaras jerárquicas
        is_floor = z_norm < 0.20
        is_stone = z_norm > 0.32
        is_glyph = z_norm >= 0.58
        is_deep_trench = z_norm < 0.08

        # 1. Función de transición Hermite cúbica no lineal (Substance Curve / Smoothstep)
        def s_curve(dist_map: np.ndarray, radius: float) -> np.ndarray:
            t = np.clip(dist_map / max(1.0, radius), 0.0, 1.0)
            return t * t * (3.0 - 2.0 * t)

        d_stone = ndi.distance_transform_edt(is_stone)
        d_glyph = ndi.distance_transform_edt(is_glyph)

        # Distinguir bloques monumentales de trazos y letras finas
        is_large_block = d_stone > 2.8

        # Biselado S-curve orgánico
        stone_bevel = s_curve(d_stone, pillow_radius)
        glyph_bevel = s_curve(d_glyph, pillow_radius * 1.2)
        # Coronación parabólica central en la cúspide del glifo
        glyph_crown = np.sqrt(np.clip(d_glyph / max(1.0, pillow_radius * 3.5), 0.0, 1.0)) * 0.22

        z_sculpt = np.full((h, w), 0.08, dtype=np.float32)
        z_sculpt[is_deep_trench] = 0.03
        z_sculpt[is_large_block] = 0.26 + stone_bevel[is_large_block] * 0.40
        z_sculpt[is_glyph] += glyph_bevel[is_glyph] * 0.22 + glyph_crown[is_glyph]

        # 2. Letras y glosas finas: relieve nítido sin distorsión
        is_fine = is_stone & (~is_large_block)
        z_sculpt[is_fine] = 0.26 + (z_norm[is_fine] * 0.36)

        # 3. Detección y grabado en V de incisiones internas (fauces, ojos, perlas, volutas)
        gy, gx = np.gradient(z_norm)
        g_mag = np.sqrt(gx * gx + gy * gy)
        line_seeds = (g_mag > 0.06) | (z_norm > 0.88)

        # Erodir la máscara para no morder el contorno exterior
        eroded_glyph = ndi.binary_erosion(is_glyph, iterations=max(2, int(pillow_radius * 0.22)))
        internal_lines = line_seeds & eroded_glyph

        if np.any(internal_lines):
            d_incise = ndi.distance_transform_edt(~internal_lines)
            groove_mask = (d_incise < groove_width) & eroded_glyph
            # Perfil en V cónico
            groove_falloff = np.clip(1.0 - (d_incise / groove_width), 0.0, 1.0) ** 1.4 * groove_depth
            z_sculpt[groove_mask] -= groove_falloff[groove_mask]

        # 4. Capas Procedurales de Material:
        if add_rock_grain:
            np.random.seed(42)
            yy, xx = np.indices((h, w), dtype=np.float32)

            # A) Estratificación geológica sedimentaria (Bedding planes de roca caliza)
            bedding = np.sin(yy * 0.035 + xx * 0.015) * 0.016

            # B) Textura mineral media (granulometría de matriz lítica)
            n_med = (ndi.gaussian_filter(np.random.randn(h, w), 2.2) * 0.022).astype(np.float32)

            # C) Micro-cristales de calcita y brillo mineral
            n_fine = (np.random.randn(h, w) * 0.007).astype(np.float32)

            # D) Micro-desprendimientos y lascas en los filos tallados (Slope-blur wear)
            ny_grad, nx_grad = np.gradient(n_med)
            edge_chipping = (nx_grad * gx + ny_grad * gy) * 0.12

            # E) Estrías de desbastado con azuela/percutor en el lecho del fondo
            chisel_toolmarks = np.sin(xx * 0.22 + yy * 0.11 + n_med * 8.0) * 0.014

            z_sculpt = z_sculpt + bedding + n_med + n_fine + edge_chipping
            z_sculpt[is_floor] += chisel_toolmarks[is_floor]

        # Suavizado gaussiano sutil para desgaste milenario de intemperie
        z_sculpt = ndi.gaussian_filter(z_sculpt, sigma=0.45)
        return np.clip(z_sculpt, 0.0, 1.0)

    @classmethod
    def compute_cast_shadows(
        cls,
        z_grid: np.ndarray,
        light_azimuth_deg: float,
        light_elevation_deg: float,
        relief_depth_mm: float = 16.0,
        num_steps: int = 26,
        step_size_px: float = 2.0
    ) -> np.ndarray:
        """
        Calcula sombras arrojadas direccionales mediante trazado de rayos en el horizonte (Horizon Raymarching).
        Las masas de relieve elevadas proyectan sombras profundas con penumbra suave sobre el fondo desbastado.
        """
        phi = math.radians(light_azimuth_deg)
        theta = math.radians(max(4.0, min(86.0, light_elevation_deg)))
        tan_theta = math.tan(theta)

        h, w = z_grid.shape
        z_mm = z_grid * relief_depth_mm

        # Vector de paso hacia la fuente de luz
        step_x = -math.cos(phi) * step_size_px
        step_y = math.sin(phi) * step_size_px  # Y crece hacia abajo en coordenadas de pantalla

        yy, xx = np.indices((h, w), dtype=np.float32)
        cast_shadow = np.ones((h, w), dtype=np.float32)

        penumbra = 0.85
        scale_mm_per_px = 150.0 / float(max(w, 1))

        for i in range(1, num_steps + 1):
            dist_px = i * step_size_px
            dist_mm = dist_px * scale_mm_per_px
            sx = np.clip(np.round(xx + i * step_x).astype(np.int32), 0, w - 1)
            sy = np.clip(np.round(yy + i * step_y).astype(np.int32), 0, h - 1)

            z_sample = z_mm[sy, sx]
            ray_z = z_mm + dist_mm * tan_theta
            diff = z_sample - ray_z

            occl = np.clip(diff / penumbra, 0.0, 1.0)
            cast_shadow = np.minimum(cast_shadow, 1.0 - occl)

        return cast_shadow

    @classmethod
    def compute_normal_map(cls, z_grid: np.ndarray, relief_scale: float = 16.0) -> np.ndarray:
        """
        Calcula el campo vectorial de Normales tridimensionales N(x, y) = (-∂Z/∂x, -∂Z/∂y, 1)
        usando operadores gradiente centrados para relieve escultórico profundo.
        """
        # Escalar altura Z
        z_scaled = z_grid * relief_scale

        # Derivadas espaciales centradas
        dz_dy, dz_dx = np.gradient(z_scaled)

        # Vector normal N = normalize(-dz_dx, -dz_dy, 1.0)
        nx = -dz_dx
        ny = -dz_dy
        nz = np.ones_like(z_grid, dtype=np.float32)

        length = np.sqrt(nx * nx + ny * ny + nz * nz)
        length = np.maximum(length, 1e-6)

        normals = np.dstack((nx / length, ny / length, nz / length))
        return normals

    @classmethod
    def compute_ambient_occlusion(cls, z_grid: np.ndarray, strength: float = 0.80) -> np.ndarray:
        """
        Calcula Oclusión Ambiental (AO) multi-escala:
          • Micro-AO (radio 4): oscurece aristas de cincelado finas.
          • Macro-AO (radio 24): simula acumulación de pátina milenaria y polvo en fosos profundos.
        """
        try:
            from scipy.ndimage import uniform_filter
            # Micro-AO
            z_mean_micro = uniform_filter(z_grid, size=9)
            diff_micro = np.clip(z_mean_micro - z_grid, 0.0, 1.0)
            ao_micro = 1.0 - np.clip(diff_micro * 2.2 * strength, 0.0, 0.85)

            # Macro-AO
            z_mean_macro = uniform_filter(z_grid, size=49)
            diff_macro = np.clip(z_mean_macro - z_grid, 0.0, 1.0)
            ao_macro = 1.0 - np.clip(diff_macro * 1.5 * strength, 0.0, 0.75)

            return np.clip(ao_micro * ao_macro, 0.15, 1.0)
        except Exception:
            return np.ones_like(z_grid)

    @classmethod
    def shade_stone_relief(
        cls,
        z_grid: np.ndarray,
        light_azimuth_deg: float = 45.0,
        light_elevation_deg: float = 24.0,
        material: Optional[StoneMaterial] = None,
        relief_scale: float = 16.0,
        enable_cast_shadows: bool = True,
        enable_volumetric_sculpt: bool = True
    ) -> np.ndarray:
        """
        Renderiza la superficie lítica 3D completa calculando el sombreado RTI de alto impacto:
          • Abocelado y coronación volumétrica (si enable_volumetric_sculpt está activo).
          • Sombras arrojadas direccionales por trazado de rayos en el horizonte.
          • Normales de alto relieve con curvatura convexa.
          • Luz solar rasante cálida contra luz ambiental celeste fría.
          • Oclusión ambiental multi-escala y albedos PBR de materiales mesoamericanos.
        """
        if material is None:
            material = MayanStoneMaterials.PALENQUE_LIMESTONE

        # 1. Aplicar escultura volumétrica si la matriz es plana (típica de un SVG rasterizado)
        if enable_volumetric_sculpt:
            # Comprobar si la matriz tiene mesetas planas
            z_effective = cls.synthesize_volumetric_relief(z_grid)
        else:
            z_effective = z_grid

        h, w = z_effective.shape

        # 2. Vector de luz normalizado L
        phi = math.radians(light_azimuth_deg)
        theta = math.radians(max(4.0, min(86.0, light_elevation_deg)))
        lx = math.cos(phi) * math.cos(theta)
        ly = math.sin(phi) * math.cos(theta)
        lz = math.sin(theta)

        # 3. Vector intermedio de Blinn-Phong H
        vx, vy, vz = 0.0, 0.0, 1.0
        hx, hy, hz = lx + vx, ly + vy, lz + vz
        hlen = math.sqrt(hx * hx + hy * hy + hz * hz)
        hx, hy, hz = hx / hlen, hy / hlen, hz / hlen

        # 4. Campo de normales N(x, y)
        normals = cls.compute_normal_map(z_effective, relief_scale=relief_scale)
        nx = normals[:, :, 0]
        ny = normals[:, :, 1]
        nz = normals[:, :, 2]

        # 5. Difusa de Lambert
        diffuse = np.maximum(0.0, nx * lx + ny * ly + nz * lz)

        # 6. Especular Blinn-Phong
        n_dot_h = np.maximum(0.0, nx * hx + ny * hy + nz * hz)
        specular = np.power(n_dot_h, material.specular_power)

        # 7. Sombras arrojadas direccionales (Horizon Raymarching)
        if enable_cast_shadows:
            cast_shadow = cls.compute_cast_shadows(
                z_effective,
                light_azimuth_deg=light_azimuth_deg,
                light_elevation_deg=light_elevation_deg,
                relief_depth_mm=relief_scale
            )
        else:
            cast_shadow = np.ones((h, w), dtype=np.float32)

        # 8. Oclusión Ambiental multi-escala
        ao = cls.compute_ambient_occlusion(z_effective, strength=material.ao_intensity)

        # 9. Albedo PBR según material
        albedo = np.zeros((h, w, 3), dtype=np.float32)
        t_z = np.clip(z_effective, 0.0, 1.0)

        if material.is_polychrome:
            # Estuco Policromado Clásico:
            # Fondo de cal blanca desbastada, detalles e incisiones en Azul Maya, relieves altos en Rojo Cinabrio
            stucco_base = np.array([0.90, 0.88, 0.82], dtype=np.float32)
            maya_blue = np.array([0.14, 0.48, 0.68], dtype=np.float32)
            cinnabar_red = np.array([0.78, 0.14, 0.12], dtype=np.float32)

            for c in range(3):
                col = np.full((h, w), stucco_base[c], dtype=np.float32)
                t_blue = np.clip((t_z - 0.26) / 0.28, 0.0, 1.0)
                col = np.where(t_z > 0.26, (1.0 - t_blue) * stucco_base[c] + t_blue * maya_blue[c], col)
                t_red = np.clip((t_z - 0.56) / 0.36, 0.0, 1.0)
                col = np.where(t_z > 0.56, (1.0 - t_red) * maya_blue[c] + t_red * cinnabar_red[c], col)
                albedo[:, :, c] = np.where(t_z < 0.12, 0.22 * stucco_base[c], col)
        else:
            c_base = np.array(material.albedo_base, dtype=np.float32)
            c_recess = np.array(material.albedo_recess, dtype=np.float32)
            c_apex = np.array(material.albedo_apex, dtype=np.float32)

            # Mapa de curvatura para realce de aristas y desgaste de cantos (Substance Curvature)
            try:
                from scipy import ndimage as ndi
                lap = ndi.gaussian_filter(t_z, 1.0) - ndi.gaussian_filter(t_z, 3.2)
                edge_wear = np.clip(lap * 3.8, 0.0, 1.0)
            except Exception:
                edge_wear = np.zeros_like(t_z)

            for c in range(3):
                col_low = (1.0 - t_z) * c_recess[c] + t_z * c_base[c]
                col = np.where(
                    t_z > 0.50,
                    (1.0 - (t_z - 0.50) / 0.50) * c_base[c] + ((t_z - 0.50) / 0.50) * c_apex[c],
                    col_low
                )
                # Acumulación de pátina milenaria y sombra de contacto en cavidades
                col = col * (0.35 + 0.65 * ao)
                # Realce de calcita / cuarzo en las aristas vivas
                col = col + edge_wear * 0.16 * c_apex[c]
                albedo[:, :, c] = col

        # 10. Iluminación Espectral de Museo:
        # Luz solar directa cálida (3800K) + Luz ambiental celeste fría (7500K)
        sun_color = np.array([1.12, 1.05, 0.94], dtype=np.float32)
        sky_color = np.array([0.16, 0.20, 0.26], dtype=np.float32)

        ambient = sky_color * ao[:, :, None] * 0.40
        lit_diffuse = diffuse[:, :, None] * cast_shadow[:, :, None] * material.diffuse_kd * sun_color
        lit_specular = specular[:, :, None] * cast_shadow[:, :, None] * material.specular_ks * sun_color

        rgb = (ambient + lit_diffuse * 0.95) * albedo + lit_specular

        # Clamp final a uint8 [0..255]
        shaded_uint8 = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
        return shaded_uint8

    @classmethod
    def render_stone_image(
        cls,
        svg_str: str,
        light_azimuth_deg: float = 45.0,
        light_elevation_deg: float = 24.0,
        material_name: str = "caliza_palenque",
        relief_scale: float = 16.0,
        width: int = 512,
        height: int = 512,
        enable_cast_shadows: bool = True
    ) -> Image.Image:
        """
        Entrada todo-en-uno de alto impacto: Toma un SVG de estela o cartucho y devuelve una imagen PIL
        de la piedra esculpida en 3D con iluminación rasante RTI, sombras arrojadas y volumen físico.
        """
        z_raw = cls.rasterize_svg_to_height_grid(svg_str, target_width=width, target_height=height)
        z_sculpted = cls.synthesize_volumetric_relief(z_raw)
        mat = MayanStoneMaterials.get_material(material_name)
        shaded = cls.shade_stone_relief(
            z_grid=z_sculpted,
            light_azimuth_deg=light_azimuth_deg,
            light_elevation_deg=light_elevation_deg,
            material=mat,
            relief_scale=relief_scale,
            enable_cast_shadows=enable_cast_shadows,
            enable_volumetric_sculpt=False  # Ya esculpido arriba
        )
        return Image.fromarray(shaded)


if __name__ == "__main__":
    print("[OK] MayanStone3DEngine cargado. Materiales disponibles:")
    for k, v in MayanStoneMaterials.CATALOG.items():
        print(f"  • {k:<22}: {v.description}")
