#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
MAYAN-LANG MCP SERVER (AH TS'IB ENGINE)
══════════════════════════════════════════════════════════════════════════════
Model Context Protocol (MCP) server for Mayan epigraphy, phonemic CV syllabification,
4-Layer Semantic Prism compilation (ES/EN ⟷ Maya VOS), 2D cartouche topological
packaging, and high-parity calligraphic vector rendering.

Compatible with Antigravity IDE, Cursor, Claude Desktop, and JSON-RPC 2.0 stdio clients.
══════════════════════════════════════════════════════════════════════════════
"""

import sys
import json
import traceback
from typing import Dict, Any, List, Optional

# Ensure UTF-8 I/O encoding across platforms, particularly Windows consoles
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

# Import core language and silhouette engines
try:
    import mayan_lang as ml
except ImportError:
    import importlib
    ml = importlib.import_module("mayan-lang")

from mayan_glyph_silhouette import (
    CalligraphicGeometry,
    CorpusPathExtractor,
    EllipticFourierEngine,
    MayanRadicalGrammar,
    render_syllable_svg,
    render_logogram_svg,
    render_numeral_svg as render_num_svg,
    morph_glyph_svg
)

MayanEpigraphyLexicon = ml.MayanEpigraphyLexicon
MayanLinguisticCompiler = ml.MayanLinguisticCompiler
MayanCalligraphicEngine = ml.MayanCalligraphicEngine
GlyphAffixSlot = ml.GlyphAffixSlot
GlyphCartoucheBlock = ml.GlyphCartoucheBlock
SemanticPrismTranslation = ml.SemanticPrismTranslation

EPIGRAPHY_TOOLS = [
    {
        "name": "mayan_translate_to_epigraphy",
        "description": "Traduce texto de entrada (Español, Inglés o Maya Directo) a una inscripción epigráfica maya completa en orden sintáctico VOS clásico (Verbo-Objeto-Sujeto), descomponiéndolo a través del Prisma Semántico de 4 Capas (Superficie, Glosa Morfo-Topológica, Acordes Homofónicos/Difrasismos Tz'ak, y Vector Biocimático/Kototama) y generando la estela vectorial SVG completa.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto a traducir o inscribir (ej. 'El jaguar contempla el cielo sagrado', 'The king dedicated the stone monument')."
                },
                "source_lang": {
                    "type": "string",
                    "enum": ["es", "en", "maya"],
                    "default": "es",
                    "description": "Idioma de origen: 'es' (Español), 'en' (Inglés), o 'maya' (Maya epigráfico directo)."
                },
                "orthography_mode": {
                    "type": "string",
                    "enum": ["logosyllabic", "logographic", "syllabic"],
                    "default": "logosyllabic",
                    "description": "Estilo ortográfico: 'logosyllabic' (estándar clásico con complementos fonéticos), 'logographic' (raíces puras), o 'syllabic' (fonético puro CV)."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian",
                    "description": "Paleta visual de la estela: 'obsidian' (basalto, oro y jade), 'codex' (papel amate, hematita y azul maya), o 'heightmap' (escala de grises para relieve 3D)."
                },
                "include_svg": {
                    "type": "boolean",
                    "default": True,
                    "description": "Si es True, incluye el documento SVG vectorial completo de la estela en la respuesta."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "mayan_syllabify_word",
        "description": "Descompone fonéticamente cualquier palabra, sustantivo o nombre propio (ej. 'Oliver', 'Pakal', 'Madrid', 'Kukulkan') en sílabas fonéticas CV mayas del silabario clásico (95 sílabas), aplicando reglas de sinarmonía/disarmonía vocálica, asociando códigos Thompson (T-codes) y frecuencias de resonancia Kototama.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "Palabra o nombre a silabificar fonéticamente en maya."
                },
                "harmony_mode": {
                    "type": "string",
                    "enum": ["synharmonic", "disharmonic"],
                    "default": "synharmonic",
                    "description": "Regla de armonía vocálica para la consonante final: 'synharmonic' (vocal idéntica = vocal corta) o 'disharmonic' (vocal contrastante = vocal larga/glotalizada)."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian",
                    "description": "Estilo de renderizado para los glifos silábicos resultantes."
                }
            },
            "required": ["word"]
        }
    },
    {
        "name": "mayan_compose_glyph_block",
        "description": "Construye y empaqueta topológicamente un Cartucho Jeroglífico Maya 2D individual a partir de sus ranuras epigráficas (Signo Principal, Superfijo, Prefijo, Infijo, Subfijo, Postfijo y Numeral vigesimal 0..19), aplicando deformación bilineal (FFD) para que los afijos abracen al núcleo, y devuelve el código SVG vectorial.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "main_sign": {
                    "type": "string",
                    "description": "Código o nombre del Signo Principal (ej. 'B'ALAM', 'AJAW', 'K'IN', 'CHAN', 'WITZ', 'ba', 'ka')."
                },
                "superfix": {
                    "type": "string",
                    "description": "Glifo o sílaba superior (ej. 'K'UH', 'u', 'ti'). Opcional."
                },
                "prefix": {
                    "type": "string",
                    "description": "Glifo o sílaba prefijo a la izquierda (ej. 'u', 'aj', 'ta'). Opcional."
                },
                "infix": {
                    "type": "string",
                    "description": "Glifo infijo incrustado en el interior del signo principal (ej. 'K'IN', 'IK''). Opcional."
                },
                "subfix": {
                    "type": "string",
                    "description": "Glifo o sílaba subfijo inferior (ej. 'ma', 'ja', 'la', 'li'). Opcional."
                },
                "postfix": {
                    "type": "string",
                    "description": "Glifo o sílaba postfijo a la derecha. Opcional."
                },
                "numeral": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 19,
                    "description": "Numeral vigesimal maya (0 a 19) a anteponer como coeficiente (opcional)."
                },
                "coord": {
                    "type": "string",
                    "default": "A1",
                    "description": "Coordenada epigráfica del bloque (ej. 'A1', 'B1', 'C2')."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian",
                    "description": "Tema visual del cartucho."
                }
            },
            "required": ["main_sign"]
        }
    },
    {
        "name": "mayan_search_epigraphic_lexicon",
        "description": "Busca dentro del Catálogo Epigráfico Maya nuclear: 95 sílabas fonéticas CV, más de 120 logogramas monumentales, raíces de verbos VOS y difrasismos sagrados (Tz'ak). Permite filtrar por texto en español, inglés, glosa maya o código Thompson.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término de búsqueda (ej. 'jaguar', 'sol', 'cielo', 'T751', 'k'in', 'escriba', 'morir')."
                },
                "category": {
                    "type": "string",
                    "enum": ["all", "logograms", "syllables", "diphrasisms"],
                    "default": "all",
                    "description": "Categoría epigráfica a consultar."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "mayan_export_stele_inscription",
        "description": "Genera y exporta una inscripción jeroglífica maya en multiformato de alta precisión: SVG vectorial, Informe Markdown estructurado, Arte ASCII/Unicode en columnas pareadas, o JSON semántico puro.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto a inscribir y exportar."
                },
                "source_lang": {
                    "type": "string",
                    "enum": ["es", "en", "maya"],
                    "default": "es"
                },
                "format": {
                    "type": "string",
                    "enum": ["svg", "markdown", "ascii", "json", "all"],
                    "default": "markdown",
                    "description": "Formato de salida deseado."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian"
                },
                "columns": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "default": 2,
                    "description": "Número de columnas pareadas de la estela (por defecto 2: A1-B1, A2-B2...)."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "mayan_get_syllabary_matrix",
        "description": "Devuelve la matriz completa del Silabario Fonético Maya (19 consonantes x 5 vocales = 95 sílabas CV) con sus códigos Thompson, arquetipos caligráficos y frecuencias resonantes Kototama en Hertz (Hz).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vowel_filter": {
                    "type": "string",
                    "enum": ["all", "a", "e", "i", "o", "u"],
                    "default": "all",
                    "description": "Filtrar por columna vocálica específica."
                },
                "consonant_filter": {
                    "type": "string",
                    "description": "Filtrar por consonante (ej. 'k', 'b\'', 'ch', 'tz\''). Dejar vacío para todas."
                }
            }
        }
    },
    {
        "name": "mayan_morph_cephalomorphic_glyph",
        "description": "Calcula la interpolación continua (Morphing) en el dominio de frecuencias mediante Descriptores Elípticos de Fourier (EFD) entre la silueta Geométrica Simple (alpha=0.0) y la variante Cefalomorfa sagrada / Cabeza de Perfil (alpha=1.0) para glifos como B'ALAM, AJAW, K'IN o CH'EN.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "glyph_name": {
                    "type": "string",
                    "enum": ["B'ALAM", "AJAW", "K'IN", "CH'EN"],
                    "default": "B'ALAM",
                    "description": "Glifo maya a interpolar armónicamente."
                },
                "alpha": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Factor de morphing: 0.0 (geometría abstracta), 0.5 (híbrido transicional), 1.0 (rostro cefalomorfo sagrado)."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian"
                }
            },
            "required": ["glyph_name"]
        }
    },
    {
        "name": "mayan_get_thompson_glyph",
        "description": "Obtiene la ficha arqueológica completa, código MHD Macri-Looper, valor fonémico, traducción en español/inglés, clasificación y el trazado SVG vectorial independiente de cualquiera de los +800 signos del Catálogo Thompson (T1 a T1066).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "t_code": {
                    "type": "string",
                    "description": "Número o código Thompson del glifo (ej. 'T751', 'T533', 'T1', 'T1017', '548')."
                },
                "theme": {
                    "type": "string",
                    "enum": ["obsidian", "codex", "heightmap"],
                    "default": "obsidian",
                    "description": "Estilo cromático del glifo: obsidiana/oro, códice (amate/azul maya) o heightmap (profundidad 16-bit)."
                },
                "size": {
                    "type": "number",
                    "default": 240.0,
                    "description": "Tamaño del lienzo cuadrado SVG en píxeles."
                }
            },
            "required": ["t_code"]
        }
    },
    {
        "name": "mayan_search_corpus_800",
        "description": "Busca signos jeroglíficos en el Corpus Arqueológico Maestro de Thompson (+800 glifos: T1–T1066) mediante consulta libre (español, inglés, lectura fonémica maya, código T o MHD) o filtrado por categoría.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "default": "",
                    "description": "Término de búsqueda (ej. 'jaguar', 'sol', 'water', 'king', 'T751', 'death', 'cueva')."
                },
                "category": {
                    "type": "string",
                    "enum": ["all", "affix", "zoomorphic", "deity", "astronomical", "anthropomorphic", "artifact", "vegetal", "geometric"],
                    "default": "all",
                    "description": "Categoría taxonómica de filtrado."
                },
                "limit": {
                    "type": "integer",
                    "default": 25,
                    "description": "Límite máximo de resultados devueltos."
                }
            }
        }
    },
    {
        "name": "mayan_list_thompson_categories",
        "description": "Lista todas las familias taxonómicas del Catálogo Thompson (+800 glifos) con sus descripciones arqueológicas y conteo de signos por categoría.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def execute_epigraphy_tool(name: str, args: Dict[str, Any]) -> str:
    """Ejecuta una herramienta epigráfica y devuelve un JSON estructurado."""
    if name == "mayan_translate_to_epigraphy":
        text = args.get("text", "")
        lang = args.get("source_lang", "es")
        ortho = args.get("orthography_mode", "logosyllabic")
        theme = args.get("theme", "obsidian")
        include_svg = args.get("include_svg", True)

        prism = MayanLinguisticCompiler.translate_and_compile(text, source_lang=lang, orthography_mode=ortho)
        svg_content = MayanCalligraphicEngine.render_stele_svg(prism, style=theme, columns=2) if include_svg else ""
        md_report = MayanCalligraphicEngine.render_stele_markdown(prism)

        res = {
            "status": "success",
            "input_text": text,
            "source_lang": lang,
            "orthography_mode": ortho,
            "epigraphic_transcription_vos": prism.epigraphic_transcription,
            "phonemic_reading": prism.phonemic_reading,
            "semantic_prism_4_layers": {
                "layer1_surface": {
                    "es": prism.layer1_surface_es,
                    "en": prism.layer1_surface_en
                },
                "layer2_morpho_topological": prism.layer2_morpho_topological,
                "layer3_harmonic_diphrasisms": prism.layer3_harmonic_diphrasisms,
                "layer4_biocymatic_kototama": prism.layer4_biocymatic_kototama
            },
            "cartouche_blocks_count": len(prism.blocks),
            "cartouche_blocks": [
                {
                    "coord": b.coord,
                    "epigraphic_translit": b.epigraphic_translit,
                    "phonemic_maya": b.phonemic_maya,
                    "main_sign": b.main_sign.code,
                    "prefix": b.prefix.code if b.prefix else None,
                    "superfix": b.superfix.code if b.superfix else None,
                    "subfix": b.subfix.code if b.subfix else None,
                    "postfix": b.postfix.code if b.postfix else None,
                    "infix": b.infix.code if b.infix else None,
                    "numeral": b.numeral
                }
                for b in prism.blocks
            ],
            "markdown_dossier": md_report,
            "svg_monument": svg_content
        }
        return json.dumps(res, ensure_ascii=False, indent=2)

    elif name == "mayan_syllabify_word":
        word = args.get("word", "")
        mode = args.get("harmony_mode", "synharmonic")
        theme = args.get("theme", "obsidian")

        res_syl = MayanLinguisticCompiler.syllabify_word(word, vowel_harmony=mode)
        slots = res_syl["slots"]

        # Generar bloques cartucho para cada sílaba
        cartouche_blocks = []
        for i, s in enumerate(slots):
            blk = GlyphCartoucheBlock(
                coord=f"A{i+1}",
                main_sign=GlyphAffixSlot(s["syllable"], False, s["thompson_id"], "main"),
                epigraphic_translit=s["syllable"],
                phonemic_maya=s["syllable"]
            )
            cartouche_blocks.append(blk)

        # SVG standalone para cada sílaba
        syllable_svgs = {
            s["syllable"]: render_syllable_svg(s["syllable"], size=160.0, theme=theme)
            for s in slots
        }

        output = {
            "status": "success",
            "word": word,
            "harmony_mode": mode,
            "syllables_cv": res_syl["syllables"],
            "epigraphic_hyphenated": res_syl["epigraphic_hyphenated"],
            "slots_detail": slots,
            "syllable_svg_vectors": syllable_svgs
        }
        return json.dumps(output, ensure_ascii=False, indent=2)

    elif name == "mayan_compose_glyph_block":
        main_sign = args.get("main_sign", "AJAW")
        superfix = args.get("superfix")
        prefix = args.get("prefix")
        infix = args.get("infix")
        subfix = args.get("subfix")
        postfix = args.get("postfix")
        numeral = args.get("numeral")
        coord = args.get("coord", "A1")
        theme = args.get("theme", "obsidian")

        def make_slot(code_str: Optional[str], role: str) -> Optional[GlyphAffixSlot]:
            if not code_str:
                return None
            code_clean = code_str.strip()
            is_logo = code_clean.isupper()
            return GlyphAffixSlot(code_clean, is_logo, "T000", role)

        main_slot = make_slot(main_sign, "main") or GlyphAffixSlot("AJAW", True, "T533", "main")
        sup_slot = make_slot(superfix, "superfix")
        pre_slot = make_slot(prefix, "prefix")
        inf_slot = make_slot(infix, "infix")
        sub_slot = make_slot(subfix, "subfix")
        post_slot = make_slot(postfix, "postfix")

        # Construir fórmula epigráfica
        parts = []
        if numeral is not None:
            parts.append(str(numeral))
        if pre_slot:
            parts.append(pre_slot.code)
        if sup_slot:
            parts.append(sup_slot.code)
        core = f"{main_slot.code}[{inf_slot.code}]" if inf_slot else main_slot.code
        parts.append(core)
        if sub_slot:
            parts.append(sub_slot.code)
        if post_slot:
            parts.append(post_slot.code)

        formula = " - ".join(parts)
        block = GlyphCartoucheBlock(
            coord=coord,
            main_sign=main_slot,
            superfix=sup_slot,
            prefix=pre_slot,
            infix=inf_slot,
            subfix=sub_slot,
            postfix=post_slot,
            numeral=numeral,
            epigraphic_translit=formula,
            phonemic_maya=formula.lower()
        )

        cartouche_svg = MayanCalligraphicEngine.render_cartouche_block_svg(block, 10, 10, size=240.0, style=theme)
        svg_doc = f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="260" height="260">{cartouche_svg}</svg>'

        output = {
            "status": "success",
            "coord": coord,
            "epigraphic_formula": formula,
            "phonemic_reading": formula.lower(),
            "slots": {
                "numeral": numeral,
                "prefix": pre_slot.code if pre_slot else None,
                "superfix": sup_slot.code if sup_slot else None,
                "main_sign": main_slot.code,
                "infix": inf_slot.code if inf_slot else None,
                "subfix": sub_slot.code if sub_slot else None,
                "postfix": post_slot.code if post_slot else None
            },
            "svg_cartouche": svg_doc
        }
        return json.dumps(output, ensure_ascii=False, indent=2)

    elif name == "mayan_search_epigraphic_lexicon":
        query = args.get("query", "").lower().strip()
        cat = args.get("category", "all")
        matches = []

        # 1. Buscar en Catálogo de Logogramas
        if cat in ("all", "logograms", "diphrasisms"):
            for logo_k, data in MayanEpigraphyLexicon.LOGOGRAM_CATALOG.items():
                match_score = 0
                if query in logo_k.lower():
                    match_score += 3
                if query in data.get("thompson", "").lower():
                    match_score += 3
                if query in data.get("maya_phonemic", "").lower():
                    match_score += 2
                for es_t in data.get("es", []):
                    if query in es_t.lower():
                        match_score += 2
                for en_t in data.get("en", []):
                    if query in en_t.lower():
                        match_score += 2
                if query in data.get("accord", "").lower():
                    match_score += 1

                if match_score > 0:
                    matches.append({
                        "type": "logogram",
                        "code": logo_k,
                        "thompson": data.get("thompson", ""),
                        "phonemic": data.get("maya_phonemic", ""),
                        "syllabic": data.get("syllabic", []),
                        "es": data.get("es", []),
                        "en": data.get("en", []),
                        "harmonic_accord": data.get("accord", ""),
                        "radical_assigned": MayanRadicalGrammar.LOGOGRAM_TO_RADICAL.get(logo_k, "R08_AJAW_ROYAL_FACE")
                    })

        # 2. Buscar en Silabario CV
        if cat in ("all", "syllables"):
            for cons in MayanEpigraphyLexicon.CONSONANTS:
                arch, t_code, desc = MayanEpigraphyLexicon.CONSONANT_GLYPH_ARCHETYPE[cons]
                for c_idx, v in enumerate(MayanEpigraphyLexicon.VOWELS):
                    syl = f"{cons}{v}"
                    t_full = f"{t_code}.{c_idx+1}"
                    v_info = MayanEpigraphyLexicon.VOWEL_KOTOTAMA.get(v, {"kototama": v, "freq_hz": 432.0, "element": "Luz"})
                    v_name = v_info["kototama"]
                    freq = v_info["freq_hz"]
                    el = v_info["element"]
                    if query in syl or query in t_full.lower() or query in desc.lower() or query in v_name.lower():
                        matches.append({
                            "type": "syllable_cv",
                            "code": syl,
                            "thompson": t_full,
                            "consonant": cons or "null (vowel onset)",
                            "archetype": arch,
                            "vowel": v,
                            "resonant_frequency_hz": freq,
                            "elemental_polarity": el
                        })

        return json.dumps({
            "status": "success",
            "query": query,
            "category": cat,
            "matches_count": len(matches),
            "results": matches
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_export_stele_inscription":
        text = args.get("text", "")
        lang = args.get("source_lang", "es")
        fmt = args.get("format", "markdown")
        theme = args.get("theme", "obsidian")
        cols = args.get("columns", 2)

        prism = MayanLinguisticCompiler.translate_and_compile(text, source_lang=lang, orthography_mode="logosyllabic")

        res_export: Dict[str, Any] = {
            "status": "success",
            "text": text,
            "phonemic_reading": prism.phonemic_reading,
            "epigraphic_transcription": prism.epigraphic_transcription
        }

        if fmt in ("svg", "all"):
            res_export["svg"] = MayanCalligraphicEngine.render_stele_svg(prism, style=theme, columns=cols)
        if fmt in ("markdown", "all"):
            res_export["markdown"] = MayanCalligraphicEngine.render_stele_markdown(prism)
        if fmt in ("ascii", "all"):
            res_export["ascii"] = MayanCalligraphicEngine.render_stele_ascii(prism)
        if fmt in ("json", "all"):
            res_export["json"] = json.loads(MayanCalligraphicEngine.render_stele_json(prism))

        return json.dumps(res_export, ensure_ascii=False, indent=2)

    elif name == "mayan_get_syllabary_matrix":
        v_filter = args.get("vowel_filter", "all")
        c_filter = args.get("consonant_filter", "").strip()

        vowels = [v_filter] if v_filter in ("a", "e", "i", "o", "u") else list(MayanEpigraphyLexicon.VOWELS)
        consonants = [c_filter] if c_filter and c_filter in MayanEpigraphyLexicon.CONSONANTS else list(MayanEpigraphyLexicon.CONSONANTS)

        grid = []
        for cons in consonants:
            arch, t_code, desc = MayanEpigraphyLexicon.CONSONANT_GLYPH_ARCHETYPE[cons]
            row_items = []
            for v in vowels:
                c_idx = MayanEpigraphyLexicon.VOWELS.index(v)
                syl = f"{cons}{v}"
                v_info = MayanEpigraphyLexicon.VOWEL_KOTOTAMA.get(v, {"kototama": v, "freq_hz": 432.0, "element": "Luz"})
                row_items.append({
                    "syllable": syl,
                    "thompson_id": f"{t_code}.{c_idx+1}",
                    "vowel": v,
                    "frequency_hz": v_info["freq_hz"],
                    "element": v_info["element"]
                })
            grid.append({
                "consonant": cons or "' (vowel onset)",
                "archetype": arch,
                "description": desc,
                "syllables": row_items
            })

        return json.dumps({
            "status": "success",
            "total_consonants": len(consonants),
            "total_vowels": len(vowels),
            "vowel_frequencies_hz": {v: MayanEpigraphyLexicon.VOWEL_KOTOTAMA[v]["freq_hz"] for v in MayanEpigraphyLexicon.VOWELS},
            "syllabary_grid": grid
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_morph_cephalomorphic_glyph":
        glyph_name = args.get("glyph_name", "B'ALAM")
        alpha = float(args.get("alpha", 0.5))
        theme = args.get("theme", "obsidian")

        svg_code = morph_glyph_svg(glyph_name, alpha=alpha, size=240.0, theme=theme)

        output = {
            "status": "success",
            "glyph_name": glyph_name,
            "alpha": alpha,
            "interpretation": (
                "Geometría abstracta pura" if alpha <= 0.05 else
                "Variante cefalomorfa sagrada (cabeza de perfil de deidad)" if alpha >= 0.95 else
                f"Híbrido morfológico transicional (armónicos de Fourier balanceados al {int(alpha*100)}%)"
            ),
            "theme": theme,
            "svg_morphed_contour": svg_code
        }
        return json.dumps(output, ensure_ascii=False, indent=2)

    elif name == "mayan_get_thompson_glyph":
        from mayan_thompson_catalog import MayanThompsonCatalog, render_thompson_glyph_svg
        t_code = args.get("t_code", "T533")
        theme = args.get("theme", "obsidian")
        size = float(args.get("size", 240.0))

        catalog = MayanThompsonCatalog()
        entry = catalog.get_entry(t_code)
        if not entry:
            m = re.search(r'\d+', t_code)
            t_num = int(m.group(0)) if m else 533
            entry = catalog.generate_systematic_vault_entry(t_num)

        svg_str = render_thompson_glyph_svg(entry.t_number, size=size, theme=theme)

        return json.dumps({
            "status": "success",
            "thompson_id": entry.t_number,
            "name": entry.name,
            "phonemic": entry.phonemic,
            "is_logogram": entry.is_logogram,
            "category": entry.category,
            "category_name": MayanThompsonCatalog.CATEGORIES.get(entry.category, entry.category),
            "mhd_code": entry.mhd_code,
            "es_meaning": entry.es_meaning,
            "en_meaning": entry.en_meaning,
            "radical_id": entry.radical_id,
            "archaeological_note": entry.archaeological_note,
            "svg": svg_str
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_search_corpus_800":
        from mayan_thompson_catalog import MayanThompsonCatalog
        query = args.get("query", "")
        category = args.get("category", "all")
        limit = int(args.get("limit", 25))

        matches = MayanThompsonCatalog.search_corpus(query=query, category=category)
        res_list = []
        for m in matches[:limit]:
            res_list.append({
                "thompson_id": m.t_number,
                "name": m.name,
                "phonemic": m.phonemic,
                "is_logogram": m.is_logogram,
                "category": m.category,
                "category_name": MayanThompsonCatalog.CATEGORIES.get(m.category, m.category),
                "mhd_code": m.mhd_code,
                "es_meaning": m.es_meaning,
                "en_meaning": m.en_meaning
            })

        return json.dumps({
            "status": "success",
            "query": query,
            "category_filter": category,
            "total_matches": len(matches),
            "returned_count": len(res_list),
            "results": res_list
        }, ensure_ascii=False, indent=2)

    elif name == "mayan_list_thompson_categories":
        from mayan_thompson_catalog import MayanThompsonCatalog
        stats = MayanThompsonCatalog.get_category_stats()
        cats = [
            {"id": k, "name": v, "glyph_count": stats.get(k, 0)}
            for k, v in MayanThompsonCatalog.CATEGORIES.items()
        ]
        return json.dumps({
            "status": "success",
            "total_glyphs_indexed": stats.get("all", 1066),
            "categories": cats
        }, ensure_ascii=False, indent=2)

    else:
        raise ValueError(f"Herramienta epigráfica desconocida: '{name}'")


def run_stdio_server():
    """Bucle stdio estándar JSON-RPC 2.0 para clientes MCP."""
    sys.stderr.write("[MayanLang MCP] Servidor de Epigrafía (Ah Ts'ib Engine) iniciado en stdio JSON-RPC 2.0...\n")
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
                        "name": "mayan-lang-epigraphy-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": EPIGRAPHY_TOOLS
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                output = execute_epigraphy_tool(tool_name, tool_args)
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
