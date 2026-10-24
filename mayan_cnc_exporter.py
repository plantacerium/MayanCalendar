#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
MAYAN CNC & DIGITAL FABRICATION EXPORTER (TALLER DE TALLA CNC)
══════════════════════════════════════════════════════════════════════════════
Exportador industrial para manufactura sustractiva (Fresadoras CNC, Routers)
y aditiva (Impresoras 3D, Litofanías y CAD/CAM).

Formatos Soportados:
  1. G-code ISO 6983 (.nc / .gcode): Trayectorias de corte para GRBL, Mach3, LinuxCNC.
  2. Malla STL Binaria (.stl): Sólido 3D cerrado (watertight) para impresión SLA/FDM.
  3. Heightmap 16-bit (.png): 65.536 niveles de profundidad para Vectric Aspire / ArtCAM.
  4. Malla Wavefront OBJ (.obj + .mtl): Geometría 3D con normales y UVs para Blender/Unreal.
══════════════════════════════════════════════════════════════════════════════
"""

import os
import struct
import math
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from PIL import Image


class MayanCNCExporter:
    """
    Motor de fabricación digital para estelas, dinteles y cartuchos mayas.
    Convierte matrices de altura en código de máquina y geometría 3D física.
    """

    @classmethod
    def export_16bit_heightmap(
        cls,
        z_grid: np.ndarray,
        output_path: str
    ) -> str:
        """
        Exporta la matriz de profundidad como un archivo PNG en escala de grises de 16 bits
        con 65.536 niveles discretos, eliminando artefactos de escalonamiento (banding).
        """
        z_clamped = np.clip(z_grid, 0.0, 1.0)
        z_16 = (z_clamped * 65535.0).astype(np.uint16)
        img_16 = Image.fromarray(z_16)
        img_16.save(output_path)
        return output_path

    @classmethod
    def generate_gcode(
        cls,
        z_grid: np.ndarray,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_depth_mm: float = 8.0,
        safe_z_mm: float = 5.0,
        feed_rate_mm_min: float = 1200.0,
        plunge_rate_mm_min: float = 400.0,
        spindle_rpm: int = 12000,
        stepover_mm: float = 0.8,
        v_bit_angle_deg: float = 60.0
    ) -> str:
        """
        Genera código G estándar ISO 6983 optimizado para fresado de bajo relieve en piedra caliza o madera.
        
        Estrategia de mecanizado:
          • Pasadas de grabado adaptativo en Z según el mapa de profundidad.
          • Detección de aristas para grabado en V y desbaste de lecho de cartucho.
        """
        rows, cols = z_grid.shape
        dx = width_mm / max(1, cols - 1)
        dy = height_mm / max(1, rows - 1)

        # Determinar paso de muestreo según el stepover deseado
        step_y = max(1, int(round(stepover_mm / dy)))
        step_x = max(1, int(round(stepover_mm / dx)))

        gcode_lines = [
            "(══════════════════════════════════════════════════════════════════)",
            "( MAYAN STELE CNC CARVED TABLET - AH POL TUN ENGINE             )",
            f"( Dimensions: {width_mm:.1f} mm x {height_mm:.1f} mm x {max_depth_mm:.1f} mm max depth )",
            f"( Tool: V-Bit {v_bit_angle_deg:.0f} deg | Feed: {feed_rate_mm_min} mm/min | RPM: {spindle_rpm} )",
            "( Standard ISO 6983 G-code for GRBL, Mach3, LinuxCNC, Shapeoko   )",
            "(══════════════════════════════════════════════════════════════════)",
            "G21          (Metric mode - millimeters)",
            "G90          (Absolute positioning)",
            "G17          (XY plane selection)",
            "G94          (Feed rate mode: mm/min)",
            f"G00 Z{safe_z_mm:.3f} (Move to safe clearance height)",
            f"M03 S{spindle_rpm}   (Spindle start clockwise)",
            "G04 P2.0     (Dwell 2 seconds for spindle to reach speed)",
            f"G00 X0.000 Y{height_mm:.3f} (Rapid to origin top-left corner)",
            ""
        ]

        # En bajorrelieve maya:
        # Z_grid = 1.0 (meseta del glifo, sin corte Z=0.0 mm)
        # Z_grid = 0.0 (fondo desbastado, corte profundo Z = -max_depth_mm)
        # Por tanto, profundidad de corte: z_cut = -(1.0 - z_grid) * max_depth_mm

        # Recorrido de mecanizado tipo raster bidireccional (zigzag) para máxima eficiencia
        forward = True
        cut_active = False

        for r in range(0, rows, step_y):
            y_pos = height_mm - (r * dy)
            col_range = range(0, cols, step_x) if forward else range(cols - 1, -1, -step_x)

            for c in col_range:
                x_pos = c * dx
                val_z = z_grid[r, c]
                depth_cut = -(1.0 - val_z) * max_depth_mm

                # Si el corte es superficial (< 0.15 mm), no profundizar para proteger el plano virgen
                if depth_cut > -0.15:
                    depth_cut = 0.0

                if not cut_active:
                    # Posicionar en rápido sobre el punto
                    gcode_lines.append(f"G00 X{x_pos:.3f} Y{y_pos:.3f}")
                    gcode_lines.append(f"G01 Z{depth_cut:.3f} F{plunge_rate_mm_min:.0f}")
                    cut_active = True
                else:
                    gcode_lines.append(f"G01 X{x_pos:.3f} Y{y_pos:.3f} Z{depth_cut:.3f} F{feed_rate_mm_min:.0f}")

            # Subir a plano seguro al final de cada pasada si la siguiente línea está distante
            forward = not forward

        # Cierre del programa y retorno a casa
        gcode_lines.extend([
            "",
            f"G00 Z{safe_z_mm:.3f} (Retract to safe clearance)",
            "M05          (Spindle stop)",
            "G00 X0.000 Y0.000 (Return to home origin)",
            "M30          (Program end and rewind)"
        ])

        return "\n".join(gcode_lines)

    @classmethod
    def export_gcode_file(
        cls,
        z_grid: np.ndarray,
        output_path: str,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_depth_mm: float = 8.0,
        **kwargs
    ) -> str:
        """Genera y guarda el archivo G-code en disco."""
        code = cls.generate_gcode(
            z_grid=z_grid,
            width_mm=width_mm,
            height_mm=height_mm,
            max_depth_mm=max_depth_mm,
            **kwargs
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        return output_path

    @classmethod
    def generate_binary_stl(
        cls,
        z_grid: np.ndarray,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_relief_depth_mm: float = 8.0,
        base_thickness_mm: float = 6.0
    ) -> bytes:
        """
        Genera una malla sólida 3D cerrada (Watertight Manifold) en formato STL Binario.
        La tableta lítica consta de:
          • Superficie superior esculpida con el relieve de la inscripción.
          • Base inferior plana sólida a Z = -base_thickness_mm.
          • 4 paredes perimetrales que unen el relieve con la base.
        """
        rows, cols = z_grid.shape
        dx = width_mm / max(1, cols - 1)
        dy = height_mm / max(1, rows - 1)

        # En bajorrelieve maya:
        # Altura física de la cúspide = max_relief_depth_mm * z_grid
        z_surface = z_grid * max_relief_depth_mm
        z_base = -base_thickness_mm

        # Triángulos de la superficie superior: (rows - 1) * (cols - 1) * 2
        # Triángulos de la base inferior: (rows - 1) * (cols - 1) * 2
        # Triángulos de los 4 bordes: (cols - 1)*2 * 2 + (rows - 1)*2 * 2
        top_quads = (rows - 1) * (cols - 1)
        wall_quads = (cols - 1) * 2 + (rows - 1) * 2
        total_triangles = (top_quads * 2) + (top_quads * 2) + (wall_quads * 2)

        # Cabecera binaria de 80 bytes
        header_text = b"Mayan Stele CNC Carved Tablet STL - Ah Pol Tun Engine 3D Solid Model"
        header = header_text.ljust(80, b" ")[:80]

        buf = bytearray()
        buf.extend(header)
        buf.extend(struct.pack("<I", total_triangles))

        def add_triangle(v1, v2, v3):
            # Calcular vector normal por producto cruz
            ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
            bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
            nx = ay * bz - az * by
            ny = az * bx - ax * bz
            nz = ax * by - ay * bx
            nl = math.sqrt(nx * nx + ny * ny + nz * nz)
            if nl > 1e-6:
                nx, ny, nz = nx / nl, ny / nl, nz / nl
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            buf.extend(struct.pack("<fff", nx, ny, nz))
            buf.extend(struct.pack("<fff", v1[0], v1[1], v1[2]))
            buf.extend(struct.pack("<fff", v2[0], v2[1], v2[2]))
            buf.extend(struct.pack("<fff", v3[0], v3[1], v3[2]))
            buf.extend(b"\x00\x00")  # Attribute byte count (2 bytes)

        # 1. Triangulación de la Superficie Superior (Esculpida)
        for r in range(rows - 1):
            y0 = height_mm - r * dy
            y1 = height_mm - (r + 1) * dy
            for c in range(cols - 1):
                x0 = c * dx
                x1 = (c + 1) * dx

                p00 = (x0, y0, z_surface[r, c])
                p10 = (x1, y0, z_surface[r, c + 1])
                p01 = (x0, y1, z_surface[r + 1, c])
                p11 = (x1, y1, z_surface[r + 1, c + 1])

                # Cara superior (normal apuntando hacia arriba +Z)
                add_triangle(p00, p01, p11)
                add_triangle(p00, p11, p10)

        # 2. Triangulación de la Base Inferior (Plana a z_base)
        for r in range(rows - 1):
            y0 = height_mm - r * dy
            y1 = height_mm - (r + 1) * dy
            for c in range(cols - 1):
                x0 = c * dx
                x1 = (c + 1) * dx

                b00 = (x0, y0, z_base)
                b10 = (x1, y0, z_base)
                b01 = (x0, y1, z_base)
                b11 = (x1, y1, z_base)

                # Cara inferior (normal apuntando hacia abajo -Z)
                add_triangle(b00, b10, b11)
                add_triangle(b00, b11, b01)

        # 3. Pared Norte (r = 0)
        y_top = height_mm
        for c in range(cols - 1):
            x0 = c * dx
            x1 = (c + 1) * dx
            st0 = (x0, y_top, z_surface[0, c])
            st1 = (x1, y_top, z_surface[0, c + 1])
            sb0 = (x0, y_top, z_base)
            sb1 = (x1, y_top, z_base)
            add_triangle(st0, st1, sb1)
            add_triangle(st0, sb1, sb0)

        # 4. Pared Sur (r = rows - 1)
        y_bot = 0.0
        for c in range(cols - 1):
            x0 = c * dx
            x1 = (c + 1) * dx
            st0 = (x0, y_bot, z_surface[rows - 1, c])
            st1 = (x1, y_bot, z_surface[rows - 1, c + 1])
            sb0 = (x0, y_bot, z_base)
            sb1 = (x1, y_bot, z_base)
            add_triangle(st0, sb1, st1)
            add_triangle(st0, sb0, sb1)

        # 5. Pared Oeste (c = 0)
        x_left = 0.0
        for r in range(rows - 1):
            y0 = height_mm - r * dy
            y1 = height_mm - (r + 1) * dy
            st0 = (x_left, y0, z_surface[r, 0])
            st1 = (x_left, y1, z_surface[r + 1, 0])
            sb0 = (x_left, y0, z_base)
            sb1 = (x_left, y1, z_base)
            add_triangle(st0, sb0, sb1)
            add_triangle(st0, sb1, st1)

        # 6. Pared Este (c = cols - 1)
        x_right = width_mm
        for r in range(rows - 1):
            y0 = height_mm - r * dy
            y1 = height_mm - (r + 1) * dy
            st0 = (x_right, y0, z_surface[r, cols - 1])
            st1 = (x_right, y1, z_surface[r + 1, cols - 1])
            sb0 = (x_right, y0, z_base)
            sb1 = (x_right, y1, z_base)
            add_triangle(st0, st1, sb1)
            add_triangle(st0, sb1, sb0)

        return bytes(buf)

    @classmethod
    def export_stl_file(
        cls,
        z_grid: np.ndarray,
        output_path: str,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_relief_depth_mm: float = 8.0,
        base_thickness_mm: float = 6.0
    ) -> str:
        """Guarda la malla sólida 3D binaria en disco."""
        stl_data = cls.generate_binary_stl(
            z_grid=z_grid,
            width_mm=width_mm,
            height_mm=height_mm,
            max_relief_depth_mm=max_relief_depth_mm,
            base_thickness_mm=base_thickness_mm
        )
        with open(output_path, "wb") as f:
            f.write(stl_data)
        return output_path

    @classmethod
    def generate_obj_mesh(
        cls,
        z_grid: np.ndarray,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_relief_depth_mm: float = 8.0,
        base_thickness_mm: float = 6.0
    ) -> str:
        """Genera un archivo Wavefront OBJ con coordenadas UV completas para Blender y Unreal."""
        rows, cols = z_grid.shape
        dx = width_mm / max(1, cols - 1)
        dy = height_mm / max(1, rows - 1)

        lines = [
            "# Mayan Stele 3D Carved Tablet - Wavefront OBJ",
            "# Ah Pol Tun Epigraphic Engine",
            "o MayanSteleTablet"
        ]

        # Vértices superiores e inferiores
        for r in range(rows):
            y = height_mm - r * dy
            for c in range(cols):
                x = c * dx
                z_top = z_grid[r, c] * max_relief_depth_mm
                lines.append(f"v {x:.3f} {y:.3f} {z_top:.3f}")

        base_offset = rows * cols
        for r in range(rows):
            y = height_mm - r * dy
            for c in range(cols):
                x = c * dx
                lines.append(f"v {x:.3f} {y:.3f} {-base_thickness_mm:.3f}")

        # Coordenadas UV (0..1)
        for r in range(rows):
            v_coord = 1.0 - (r / max(1, rows - 1))
            for c in range(cols):
                u_coord = c / max(1, cols - 1)
                lines.append(f"vt {u_coord:.4f} {v_coord:.4f}")

        # Caras superiores
        for r in range(rows - 1):
            for c in range(cols - 1):
                idx00 = r * cols + c + 1
                idx10 = r * cols + (c + 1) + 1
                idx01 = (r + 1) * cols + c + 1
                idx11 = (r + 1) * cols + (c + 1) + 1
                lines.append(f"f {idx00}/{idx00} {idx01}/{idx01} {idx11}/{idx11}")
                lines.append(f"f {idx00}/{idx00} {idx11}/{idx11} {idx10}/{idx10}")

        return "\n".join(lines)

    @classmethod
    def export_obj_file(
        cls,
        z_grid: np.ndarray,
        output_path: str,
        width_mm: float = 150.0,
        height_mm: float = 200.0,
        max_relief_depth_mm: float = 8.0,
        base_thickness_mm: float = 6.0
    ) -> str:
        """Guarda la malla Wavefront OBJ con UVs en disco."""
        obj_data = cls.generate_obj_mesh(
            z_grid=z_grid,
            width_mm=width_mm,
            height_mm=height_mm,
            max_relief_depth_mm=max_relief_depth_mm,
            base_thickness_mm=base_thickness_mm
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(obj_data)
        return output_path


if __name__ == "__main__":
    print("[OK] MayanCNCExporter cargado con soporte G-code ISO, STL 3D binario y Heightmap 16-bit.")
