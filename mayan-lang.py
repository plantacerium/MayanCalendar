#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
MAYAN-LANG (AH TS'IB) • EPIGRAPHIC COMPILER, SYLLABARY & 4-LAYER SEMANTIC PRISM
══════════════════════════════════════════════════════════════════════════════
Motor epigráfico logosilábico, silabario fonético CV (95 sílabas), traductor
multidimensional (Español / Inglés ⟷ Maya Clásico VOS), generador caligráfico
vectorial paramétrico (Obsidiana/Jade, Códice Amate y Mapa de Profundidad 3D)
e interfaz de escritorio en PySide6.

Licencia: GPL v3 • Autor: Plantacerium
══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import re
import math
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any

# Integración del Motor de Siluetas y Radicales Arqueológicos (Puntos 1 y 2)
try:
    from mayan_glyph_silhouette import (
        CalligraphicGeometry,
        CorpusPathExtractor,
        EllipticFourierEngine,
        MayanRadicalGrammar,
        render_syllable_svg,
        render_logogram_svg,
        render_numeral_svg as render_numeral_silhouette_svg,
        morph_glyph_svg
    )
except ImportError:
    import importlib
    _mg = importlib.import_module("mayan_glyph_silhouette")
    CalligraphicGeometry = _mg.CalligraphicGeometry
    CorpusPathExtractor = _mg.CorpusPathExtractor
    EllipticFourierEngine = _mg.EllipticFourierEngine
    MayanRadicalGrammar = _mg.MayanRadicalGrammar
    render_syllable_svg = _mg.render_syllable_svg
    render_logogram_svg = _mg.render_logogram_svg
    render_numeral_silhouette_svg = _mg.render_numeral_svg
    morph_glyph_svg = _mg.morph_glyph_svg

try:
    from mayan_thompson_catalog import MayanThompsonCatalog, ThompsonGlyphEntry, render_thompson_glyph_svg
except ImportError:
    import importlib
    _mt = importlib.import_module("mayan_thompson_catalog")
    MayanThompsonCatalog = _mt.MayanThompsonCatalog
    ThompsonGlyphEntry = _mt.ThompsonGlyphEntry
    render_thompson_glyph_svg = _mt.render_thompson_glyph_svg


# ══════════════════════════════════════════════════════════════════════════════
# 1. ESTRUCTURAS DE DATOS EPIGRÁFICAS Y DEL PRISMA SEMÁNTICO DE 4 CAPAS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GlyphAffixSlot:
    """Representa un signo individual (logograma o silabograma) dentro de un cartucho."""
    code: str                   # ej. 'TS'IB', 'u', 'b'a', 'K'IN'
    is_logogram: bool = False   # True = MAYÚSCULAS (raíz), False = minúsculas (sílaba CV)
    thompson_id: str = "T000"   # Catálogo Thompson (ej. 'T1', 'T544', 'T751')
    role: str = "main"          # 'superfix', 'prefix', 'main', 'infix', 'subfix', 'postfix'
    meaning_es: str = ""
    meaning_en: str = ""


@dataclass
class GlyphCartoucheBlock:
    """
    Bloque cuadrangular de estela (Cartucho 2D) con empaquetado topológico Maya.
    Coordenadas epigráficas clásicas en columnas pareadas: A1, B1, A2, B2...
    """
    coord: str = "A1"
    main_sign: GlyphAffixSlot = field(default_factory=lambda: GlyphAffixSlot("AJAW", True, "T533", "main"))
    superfix: Optional[GlyphAffixSlot] = None
    prefix: Optional[GlyphAffixSlot] = None
    infix: Optional[GlyphAffixSlot] = None
    subfix: Optional[GlyphAffixSlot] = None
    postfix: Optional[GlyphAffixSlot] = None
    numeral: Optional[int] = None  # Numeral vigesimal de barras y puntos (0 a 19)

    # Metadatos lingüísticos del bloque
    epigraphic_translit: str = ""  # ej. "u-TS'IB-b'a-ja"
    phonemic_maya: str = ""        # ej. "uts'ib'aj"
    linear_es: str = ""            # Capa 1 ES
    linear_en: str = ""            # Capa 1 EN
    morpho_gloss: str = ""         # Capa 2: Glosa morfo-topológica
    harmonic_accord: str = ""      # Capa 3: Resonancia homofónica / Difrasismo (Tz'ak)
    biocymatic_vector: str = ""    # Capa 4: Cadencia vocálica Kototama / Pulso somático

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SemanticPrismTranslation:
    """Resultado completo del Prisma Semántico de 4 Capas para una inscripción."""
    source_text: str
    source_lang: str
    orthography_mode: str
    blocks: List[GlyphCartoucheBlock]
    layer1_surface_es: str
    layer1_surface_en: str
    layer2_morpho_topological: List[str]
    layer3_harmonic_diphrasisms: List[str]
    layer4_biocymatic_kototama: Dict[str, Any]
    epigraphic_transcription: str
    phonemic_reading: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_text": self.source_text,
            "source_lang": self.source_lang,
            "orthography_mode": self.orthography_mode,
            "epigraphic_transcription": self.epigraphic_transcription,
            "phonemic_reading": self.phonemic_reading,
            "layer1_surface_es": self.layer1_surface_es,
            "layer1_surface_en": self.layer1_surface_en,
            "layer2_morpho_topological": self.layer2_morpho_topological,
            "layer3_harmonic_diphrasisms": self.layer3_harmonic_diphrasisms,
            "layer4_biocymatic_kototama": self.layer4_biocymatic_kototama,
            "blocks": [b.to_dict() for b in self.blocks]
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2. CATÁLOGO DEL SILABARIO CV (19x5 = 95 SÍLABAS) Y LÉXICO EPIGRÁFICO
# ══════════════════════════════════════════════════════════════════════════════

class MayanEpigraphyLexicon:
    """
    Base de conocimiento determinista del Silabario Maya Clásico (Ch'olti' / Yucateco)
    y diccionario de raíces logográficas, posicionales y difrasismos (Tz'ak).
    """

    VOWELS = ["a", "e", "i", "o", "u"]

    # 19 Consonantes canónicas de la rejilla epigráfica maya ('' representa vocal pura / glotal)
    CONSONANTS = [
        "", "b'", "ch", "ch'", "h", "j", "k", "k'", "l",
        "m", "n", "p", "s", "t", "t'", "tz", "tz'", "w", "x", "y"
    ]

    # Familias morfológicas para el trazado caligráfico paramétrico de cada consonante
    CONSONANT_GLYPH_ARCHETYPE = {
        "":    ("vocalic_scroll",   "T1",   "Núcleo vocálico puro / Cuentas de jade"),
        "b'":  ("footprint_stone",  "T501", "Piedra / Huella de camino con puntos de jade"),
        "ch":  ("hatched_medallion","T520", "Medallón achurado en obsidiana"),
        "ch'": ("clenched_jaw",     "T671", "Garra / Mandíbula de pedernal"),
        "h":   ("knotted_reed",     "T684", "Atadura de junco / Aliento solar"),
        "j":   ("spiral_shell",     "T181", "Caracola lunar / Voluta de exhalación"),
        "k":   ("comb_teeth",       "T25",  "Peine acústico de resonancia (ka/ke/ki/ko/ku)"),
        "k'":  ("flame_hand",       "T669", "Puño de fuego / Chispa divina"),
        "l":   ("twin_feather",     "T534", "Doble pluma / Hoja lanceolada invertida"),
        "m":   ("cleft_scroll",     "T74",  "Hendidura terrestre / Labio de cueva"),
        "n":   ("earth_wave",       "T116", "Onda telúrica / Cola de serpiente"),
        "p":   ("woven_band",       "T586", "Banda tejida de estera (Pop)"),
        "s":   ("partitioned_arch", "T110", "Arco segmentado / Escama brillante"),
        "t":   ("crossed_torch",    "T59",  "Antorcha atada / Haz de luz"),
        "t'":  ("rabbit_ear",       "T513", "Hoja plegada / Gota hendida"),
        "tz":  ("stepped_fret",     "T507", "Greca escalonada mesoamericana"),
        "tz'": ("bat_wing_drop",    "T563", "Ala estriada / Gota de savia"),
        "w":   ("trefoil_foliage",  "T130", "Trébol de maíz / Brote tripartito"),
        "x":   ("obsidian_cross",   "T114", "Aspa de obsidiana y gotas"),
        "y":   ("jade_blossom",     "T126", "Flor de cuatro pétalos con estambre"),
    }

    # Mapeo Kototama y elemental de las 5 vocales mayas
    VOWEL_KOTOTAMA = {
        "a": {"kototama": "A (Origen / Apertura Solar)", "freq_hz": 432.0, "element": "Fuego / Luz"},
        "e": {"kototama": "E (Rama / Discernimiento)",   "freq_hz": 528.0, "element": "Viento / Éter"},
        "i": {"kototama": "I (Eje Vertical / Vida)",     "freq_hz": 639.0, "element": "Árbol Cósmico"},
        "o": {"kototama": "O (Cavidad / Armonía)",       "freq_hz": 396.0, "element": "Tierra / Piedra"},
        "u": {"kototama": "U (Semilla / Profundidad)",   "freq_hz": 285.0, "element": "Agua / Abismo"},
    }

    # Catálogo de Logogramas Epigráficos Nucleares con las 4 Capas del Prisma Semántico
    LOGOGRAM_CATALOG: Dict[str, Dict[str, Any]] = {
        "K'IN": {
            "thompson": "T544",
            "pos": "NOUN",
            "maya_phonemic": "k'in",
            "syllabic": ["k'i", "ni"],
            "es": ["sol", "día", "tiempo", "luz", "pulso"],
            "en": ["sun", "day", "time", "light", "pulse"],
            "morpho": "Sustantivo raíz absoluto (K'IN-ni): Flor solar de cuatro pétalos orientados a los rumbos cósmicos.",
            "accord": "Acorde Homofónico quíntuple: Sol + Día + Tiempo + Calor vital + Adivinación sacerdotal.",
            "biocymatic": "Frecuencia central I-A • Triptófano (Ahau) • Antena fotónica pineal."
        },
        "CHAN": {
            "thompson": "T561",
            "pos": "NOUN",
            "maya_phonemic": "chan",
            "syllabic": ["cha", "na"],
            "es": ["cielo", "serpiente", "cuatro", "cosmos", "firmamento"],
            "en": ["sky", "heaven", "serpent", "four", "cosmos"],
            "morpho": "Raíz celeste (CHAN-na): Banda planetaria con bandas cruzadas de la eclíptica.",
            "accord": "Tríada Homofónica Maya Clásica: CHAN = 'Cielo' + 'Serpiente Celeste' + 'Número 4' (los 4 pilares del espacio).",
            "biocymatic": "Frecuencia A-A • Resonancia de onda sinusoidal serpentina."
        },
        "KAB'": {
            "thompson": "T526",
            "pos": "NOUN",
            "maya_phonemic": "kab'",
            "syllabic": ["ka", "b'a"],
            "es": ["tierra", "mundo", "miel", "suelo", "territorio"],
            "en": ["earth", "world", "honey", "land", "ground"],
            "morpho": "Sustantivo telúrico (KAB'-b'a): Voluta sísmica de Caban con germinación subterránea.",
            "accord": "Doble Resonancia: KAB' = 'Tierra firme' y 'Miel/Colmena' (la tierra concebida como panal hexagonal vivo).",
            "biocymatic": "Frecuencia telúrica Schumann • Anclaje gravitatorio."
        },
        "CH'EN": {
            "thompson": "T598",
            "pos": "NOUN",
            "maya_phonemic": "ch'een",
            "syllabic": ["ch'e", "ne"],
            "es": ["cueva", "pozo", "santuario", "ciudad", "interior"],
            "en": ["cave", "well", "sanctuary", "city", "depths"],
            "morpho": "Raíz de cavidad sagrada (CH'EN-na): Boca de roca con achurado de oscuridad matricial.",
            "accord": "Portal de Xibalbá y manantial de agua subterránea (cenote); núcleo fundacional de toda ciudad maya.",
            "biocymatic": "Frecuencia E-E • Cámara de resonancia acústica pétrea."
        },
        "B'ALAM": {
            "thompson": "T751",
            "pos": "NOUN",
            "maya_phonemic": "b'alam",
            "syllabic": ["b'a", "la", "ma"],
            "es": ["jaguar", "guardián", "sol nocturno", "oculto"],
            "en": ["jaguar", "guardian", "night sun", "hidden"],
            "morpho": "Logograma zoomorfo (B'ALAM-ma): Cabeza de jaguar con manchas de obsidiana que reflejan el cielo estrellado.",
            "accord": "Arquetipo del Sol Nocturno que viaja por el inframundo; 'b'alam' significa también lo oculto y protegido.",
            "biocymatic": "Pulso infrasónico felino • Fuerza tendinosa y sigilo."
        },
        "AJAW": {
            "thompson": "T533",
            "pos": "NOUN",
            "maya_phonemic": "ajaw",
            "syllabic": ["a", "ja", "wa"],
            "es": ["señor", "gobernante", "rey", "maestro", "soberano"],
            "en": ["lord", "ruler", "king", "master", "sovereign"],
            "morpho": "Título real (AJAW-wa): Rostro frontal coronado con la diadema de jade (huunal).",
            "accord": "Etimológicamente derivado de 'aj-aw' ('aquel que proclama con voz resonante / quien sostiene el mando').",
            "biocymatic": "Vocal A-A-U • Emisión laríngea de decreto."
        },
        "K'UH": {
            "thompson": "T36",
            "pos": "ADJ",
            "maya_phonemic": "k'uhul",
            "syllabic": ["k'u", "hu", "lu"],
            "es": ["sagrado", "divino", "santo", "eterno", "luminoso"],
            "en": ["sacred", "divine", "holy", "eternal", "luminous"],
            "morpho": "Prefijo de sacralidad (K'UH-ul): Torrente de gotas preciosas (ch'ulel / fuerza vital en la sangre y el copal).",
            "accord": "No es 'sagrado' pasivo, sino carga electro-vital activa (*k'uh*) que habita en los rayos, la sangre y el jade.",
            "biocymatic": "Frecuencia U-U • Coherencia de campo cuántico-biológico."
        },
        "TS'IB": {
            "thompson": "T501v",
            "pos": "VERB",
            "maya_phonemic": "uts'ib'aj",
            "syllabic": ["u", "ts'i", "b'a", "ja"],
            "es": ["escribió", "escribir", "pintó", "talló", "codificó", "escribe", "diseñó"],
            "en": ["wrote", "write", "painted", "carved", "encoded", "writes", "designed"],
            "morpho": "Verbo transitivo ergativo (u-ts'ib'-aj): 3SG.ERG + raíz 'ts'ib' (trazar signos/pintar) + sufijo completivo.",
            "accord": "En el pensamiento maya, escribir, pintar, programar geometría e iluminar un códice son un único acto (*ts'ib*).",
            "biocymatic": "Cadencia U-I-A • Coordinación óculo-manual fina."
        },
        "TZUTZ": {
            "thompson": "T713",
            "pos": "VERB",
            "maya_phonemic": "tzutzuy",
            "syllabic": ["tzu", "tzu", "yi"],
            "es": ["completó", "completar", "cerró", "terminó", "culminó"],
            "en": ["completed", "complete", "closed", "finished", "culminated"],
            "morpho": "Verbo completivo de periodo (TZUTZ-yi): Mano que anuda y cierra un haz de tiempo.",
            "accord": "Indica que una espiral temporal (Katún o Baktún) ha cerrado su fase sin dejar residuo abierto.",
            "biocymatic": "Frecuencia U-U-I • Cierre de fase de Kuramoto (R → 1.0)."
        },
        "CHUM": {
            "thompson": "T644",
            "pos": "POS",
            "maya_phonemic": "chumlaj",
            "syllabic": ["chu", "mu", "la", "ja"],
            "es": ["sentó", "asentó", "entronizó", "estableció", "inició"],
            "en": ["sat", "seated", "enthroned", "established", "initiated"],
            "morpho": "Raíz Posicional Esférica (CHUM-laj): Cuerpo con centro de gravedad recogido que se acopla establemente a una base.",
            "accord": "Geometría física incrustada en el verbo: no es solo 'empezar a gobernar', sino tomar masa y raíz sobre el trono de piedra.",
            "biocymatic": "Frecuencia U-A • Enraizamiento pélvico y gravedad."
        },
        "UTIY": {
            "thompson": "T679",
            "pos": "VERB",
            "maya_phonemic": "utiy",
            "syllabic": ["u", "ti", "ya"],
            "es": ["ocurrió", "sucedió", "aconteció", "fue"],
            "en": ["happened", "occurred", "came to pass", "was"],
            "morpho": "Verbo intransitivo de evento (u-ti-ya): Marca el tránsito de la potencia al hecho consumado en el espacio-tiempo.",
            "accord": "Conector cronológico maestro de las estelas: enlaza Números de Distancia con manifestaciones materiales.",
            "biocymatic": "Cadencia U-I-A • Pulso de manifestación."
        },
        "IL": {
            "thompson": "T670",
            "pos": "VERB",
            "maya_phonemic": "yilaaj",
            "syllabic": ["yi", "la", "ja"],
            "es": ["vio", "ver", "atestiguó", "contempló", "observó", "mira"],
            "en": ["saw", "see", "witnessed", "beheld", "observed", "watches"],
            "morpho": "Verbo de percepción activa (y-il-aaj): Ojo abierto con voluta de proyección óptica.",
            "accord": "Para los mayas, la visión (*ich / il*) no es recepción pasiva de fotones, sino un rayo de conciencia que toca el objeto.",
            "biocymatic": "Frecuencia I-A • Resonancia óptica directa con Oculavera."
        },
        "PAT": {
            "thompson": "T590",
            "pos": "VERB",
            "maya_phonemic": "upatb'uuj",
            "syllabic": ["u", "pa", "ta", "ja"],
            "es": ["construyó", "formó", "creó", "forjó", "modeló", "erigió"],
            "en": ["built", "formed", "created", "forged", "modeled", "erected"],
            "morpho": "Verbo morfogenético (u-PAT-wa): Dar forma tridimensional a la arcilla, la piedra o la arquitectura.",
            "accord": "Conecta la alfarería sagrada con la arquitectura de templos y la geometría corporal.",
            "biocymatic": "Frecuencia A-A • Estructuración cristalina."
        },
        "LAKAM-TUN": {
            "thompson": "T767:T528",
            "pos": "NOUN",
            "maya_phonemic": "lakamtun",
            "syllabic": ["la", "ka", "ma", "tu", "ni"],
            "es": ["estela", "monumento", "gran piedra", "piedra"],
            "en": ["stele", "stela", "monument", "great stone", "stone"],
            "morpho": "Compuesto sustantivo (LAKAM-TUN-ni): 'Lakam' (estandarte/inmenso) + 'Tun' (piedra viva / año de 360 días).",
            "accord": "Al clavar una estela física (*Lakam-Tun*), el escriba está anclando literalmente un ciclo de tiempo (*Tun*) en la tierra.",
            "biocymatic": "Frecuencia A-A-U • Memoria lítica perenne (Codex Lithoma)."
        },
        "WITZ": {
            "thompson": "T529",
            "pos": "NOUN",
            "maya_phonemic": "witz",
            "syllabic": ["wi", "tzi"],
            "es": ["montaña", "pirámide", "templo", "cumbre", "monte"],
            "en": ["mountain", "pyramid", "temple", "summit", "hill"],
            "morpho": "Logograma topográfico (WITZ): Mascarón escalonado de roca viva con racimos de uva silvestre (tierra fértil).",
            "accord": "Toda pirámide maya es un *Witz* (Montaña Sagrada artificial) que contiene en su interior la cueva primordial (*Ch'en*).",
            "biocymatic": "Frecuencia I-I • Elevación tectónica (Sylva Tectónica)."
        },
        "HA'": {
            "thompson": "T501",
            "pos": "NOUN",
            "maya_phonemic": "ha'",
            "syllabic": ["ha", "a"],
            "es": ["agua", "río", "mar", "lluvia", "manantial"],
            "en": ["water", "river", "sea", "rain", "spring"],
            "morpho": "Sustantivo elemental (HA'): Lirio acuático y corriente con cuentas de jade en suspensión.",
            "accord": "Sustrato espejo de los observatorios astronómicos y sangre de la montaña (*Witz*).",
            "biocymatic": "Frecuencia A • Fluidez hidro-acústica."
        },
        "K'AK'": {
            "thompson": "T122",
            "pos": "NOUN",
            "maya_phonemic": "k'ak'",
            "syllabic": ["k'a", "k'a"],
            "es": ["fuego", "llama", "incendio", "antorcha", "energía"],
            "en": ["fire", "flame", "torch", "energy", "blaze"],
            "morpho": "Logograma ígneo (K'AK'): Volutas gemelas ascendentes de humo y brasa solar.",
            "accord": "El Fuego Nuevo (*K'ak'*) que purifica e inaugura los templos y los 4 ciclos de Quemadores del Códice Tro-Cortesiano.",
            "biocymatic": "Frecuencia A-A glotalizada • Termodinámica de plasma."
        },
        "IK'": {
            "thompson": "T503",
            "pos": "NOUN",
            "maya_phonemic": "ik'",
            "syllabic": ["i", "k'i"],
            "es": ["viento", "aliento", "espíritu", "aire", "vida"],
            "en": ["wind", "breath", "spirit", "air", "life"],
            "morpho": "Signo en forma de 'T' (IK'): Ventana arquitectónica por donde entra el viento y resuena como flauta.",
            "accord": "Identidad entre el viento atmosférico, la respiración pulmonar y el aliento anímico inmortal.",
            "biocymatic": "Frecuencia I • Modulación neumática y voz."
        },
        "WAY": {
            "thompson": "T539",
            "pos": "NOUN",
            "maya_phonemic": "way",
            "syllabic": ["wa", "ya"],
            "es": ["espíritu", "nahual", "sueño", "sombra", "co-esencia"],
            "en": ["spirit", "nagual", "dream", "shadow", "co-essence"],
            "morpho": "Rostro mitad humano y mitad recubierto por piel de jaguar achurada (T539).",
            "accord": "Como verbo ('way') significa soñar y transmutar; como sustantivo es el compañero animal / dimensión onírica.",
            "biocymatic": "Frecuencia A-I • Oscilación theta onírica."
        },
        "OTOT": {
            "thompson": "T614",
            "pos": "NOUN",
            "maya_phonemic": "yotot",
            "syllabic": ["yo", "to", "ti"],
            "es": ["casa", "hogar", "morada", "recinto", "habitación"],
            "en": ["house", "home", "dwelling", "sanctuary", "room"],
            "morpho": "Estructura arquitectónica con techo de palma tejida y dintel de piedra (y-OTOT-ti).",
            "accord": "Un templo no es un edificio inerte, sino la 'morada vestida' (*yotot*) de una fuerza cósmica o linaje.",
            "biocymatic": "Frecuencia O-O • Geometría de proyección espacial (OculaDomus)."
        },
        "AK'B'AL": {
            "thompson": "T504",
            "pos": "NOUN",
            "maya_phonemic": "ak'b'al",
            "syllabic": ["a", "k'a", "b'a", "la"],
            "es": ["noche", "oscuridad", "obsidiana", "misterio", "abismo"],
            "en": ["night", "darkness", "obsidian", "mystery", "abyss"],
            "morpho": "Escudo nocturno con fauces de serpiente y triángulo de obsidiana pulida (T504).",
            "accord": "La oscuridad primordial antes del primer amanecer; el espejo negro donde se contempla el cosmos sin deslumbramiento.",
            "biocymatic": "Frecuencia A-A • Silencio isotrópico y reposo celular."
        },
        "POP": {
            "thompson": "T551",
            "pos": "NOUN",
            "maya_phonemic": "pop",
            "syllabic": ["po", "po"],
            "es": ["estera", "trono", "consejo", "autoridad", "tejido"],
            "en": ["mat", "throne", "council", "authority", "weave"],
            "morpho": "Trenzado geométrico de junco entrelazado en diagonal (T551).",
            "accord": "Símbolo supremo de soberanía compartida y orden entrelazado; da nombre al primer mes del año solar Haab'.",
            "biocymatic": "Frecuencia O • Red tejida de nodos interconectados."
        },
    }

    # Catálogo de Difrasismos Mesoamericanos (Tz'ak — Álgebra Binaria de Conceptos)
    DIPHRASISMS: List[Dict[str, Any]] = [
        {
            "id": "CHAN-CH'EN",
            "pair": ("CHAN", "CH'EN"),
            "triggers_es": [("cielo", "cueva"), ("cielo", "pozo"), ("cosmos", "cueva"), ("mundo", "territorio")],
            "triggers_en": [("sky", "cave"), ("heaven", "cave"), ("sky", "well"), ("world", "realm")],
            "literal": "Cielo - Cueva (Chan - Ch'en)",
            "emergent_meaning_es": "El Mundo Habitado Completo / La Ciudad-Estado Soberana en su totalidad vertical (de la bóveda celeste al inframundo).",
            "emergent_meaning_en": "The Complete Inhabited World / The Sovereign Polity across its full vertical axis (from celestial vault to underworld)."
        },
        {
            "id": "K'IN-AK'B'AL",
            "pair": ("K'IN", "AK'B'AL"),
            "triggers_es": [("sol", "noche"), ("día", "noche"), ("luz", "oscuridad"), ("eternidad", "tiempo")],
            "triggers_en": [("sun", "night"), ("day", "night"), ("light", "darkness"), ("eternity", "time")],
            "literal": "Sol/Día - Oscuridad/Noche (K'in - Ak'b'al)",
            "emergent_meaning_es": "El Continuo Infinito del Tiempo / La Totalidad Dual de la Existencia.",
            "emergent_meaning_en": "The Infinite Continuum of Time / The Dual Totality of Existence."
        },
        {
            "id": "POP-TZ'AM",
            "pair": ("POP", "AJAW"),
            "triggers_es": [("estera", "trono"), ("autoridad", "soberanía"), ("ley", "gobierno")],
            "triggers_en": [("mat", "throne"), ("authority", "sovereignty"), ("law", "government")],
            "literal": "Estera - Trono (Pop - Tz'am)",
            "emergent_meaning_es": "La Magistratura Suprema y el Orden Constitucional Legítimo.",
            "emergent_meaning_en": "Supreme Magistracy and Legitimate Constitutional Order."
        },
        {
            "id": "WITZ-HA'",
            "pair": ("WITZ", "HA'"),
            "triggers_es": [("montaña", "agua"), ("monte", "agua"), ("comunidad", "tierra")],
            "triggers_en": [("mountain", "water"), ("hill", "water"), ("community", "ecosystem")],
            "literal": "Agua - Montaña (Ha' - Witz / Altepetl)",
            "emergent_meaning_es": "La Matriz Eco-Territorial Viva y Autónoma (Manantial + Cumbre).",
            "emergent_meaning_en": "The Living Autonomous Eco-Territorial Matrix (Spring + Summit)."
        },
        {
            "id": "CHAN-KAB'",
            "pair": ("CHAN", "KAB'"),
            "triggers_es": [("cielo", "tierra"), ("universo", "creación")],
            "triggers_en": [("sky", "earth"), ("heaven", "earth"), ("universe", "creation")],
            "literal": "Cielo - Tierra (Chan - Kab')",
            "emergent_meaning_es": "La Totalidad de la Creación Manifestada (El Telar Cósmico Cuadripartito).",
            "emergent_meaning_en": "The Totality of Manifested Creation (The Quadripartite Cosmic Loom)."
        },
    ]

    @classmethod
    def get_all_syllables(cls) -> List[Dict[str, str]]:
        """Devuelve la matriz completa de 100 posiciones (20 filas x 5 vocales) del silabario."""
        grid = []
        for cons in cls.CONSONANTS:
            arch_name, t_base, desc = cls.CONSONANT_GLYPH_ARCHETYPE[cons]
            for idx, v in enumerate(cls.VOWELS):
                syl = f"{cons}{v}"
                t_num = f"{t_base}.{idx + 1}"
                grid.append({
                    "syllable": syl,
                    "consonant": cons if cons else "' (Glotal)",
                    "vowel": v,
                    "archetype": arch_name,
                    "thompson_id": t_num,
                    "description": f"Sílaba fonética CV '{syl}' • {desc} + núcleo vocálico '{v.upper()}'"
                })
        return grid


# ══════════════════════════════════════════════════════════════════════════════
# 3. COMPILADOR LINGÜÍSTICO: SILABIFICADOR CV, REORDENADOR VOS Y PRISMA 4 CAPAS
# ══════════════════════════════════════════════════════════════════════════════

class MayanLinguisticCompiler:
    """
    Motor de traducción trilingüe (ES / EN ⟷ Maya Clásico), silabificador fonético
    con reglas de sinarmonía/disarmonía de Houston-Stuart-Robertson y empaquetador de cartuchos.
    """

    STOPWORDS_ES = {"el", "la", "los", "las", "un", "una", "en", "de", "del", "al", "con", "por", "para", "y", "e", "que", "su"}
    STOPWORDS_EN = {"the", "a", "an", "in", "of", "from", "to", "with", "by", "for", "and", "that", "his", "her", "its"}

    @classmethod
    def syllabify_word(cls, word: str, vowel_harmony: str = "synharmonic") -> Dict[str, Any]:
        """
        Convierte cualquier palabra (raíz maya o nombre propio moderno como 'Oliver', 'Oculavera')
        en una secuencia de silabogramas CV mayas aplicando reglas de sinarmonía vocálica.
        """
        clean = word.strip().lower()
        # Normalización de tildes a vocales base
        for acc, base in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u")]:
            clean = clean.replace(acc, base)

        # Sustitución fonológica de consonantes externas al maya clásico
        phonetic = clean
        phonetic = phonetic.replace("qu", "k").replace("c", "k").replace("z", "s")
        phonetic = phonetic.replace("v", "w").replace("f", "p").replace("r", "l")
        phonetic = phonetic.replace("d", "t").replace("g", "k").replace("ñ", "ny")
        phonetic = re.sub(r"[^a-z']", "", phonetic)

        if not phonetic:
            return {"input": word, "syllables": ["a"], "epigraphic_hyphenated": "a", "slots": []}

        # Tokenización en fonemas mayas (reconociendo dígrafos ch', tz', ch, tz, b', k', t')
        tokens: List[str] = []
        i = 0
        n = len(phonetic)
        digraphs_3 = {"ch'", "tz'"}
        digraphs_2 = {"ch", "tz", "b'", "k'", "t'"}

        while i < n:
            if i + 3 <= n and phonetic[i:i+3] in digraphs_3:
                tokens.append(phonetic[i:i+3])
                i += 3
            elif i + 2 <= n and phonetic[i:i+2] in digraphs_2:
                tokens.append(phonetic[i:i+2])
                i += 2
            else:
                tokens.append(phonetic[i])
                i += 1

        vowels = set(MayanEpigraphyLexicon.VOWELS)
        syllables: List[str] = []
        last_vowel = "a"

        idx = 0
        while idx < len(tokens):
            tok = tokens[idx]
            if tok in vowels:
                # Vocal inicial o en hiato -> sílaba de vocal pura
                syllables.append(tok)
                last_vowel = tok
                idx += 1
            else:
                # Consonante: mirar si le sigue una vocal
                if idx + 1 < len(tokens) and tokens[idx + 1] in vowels:
                    v = tokens[idx + 1]
                    syllables.append(f"{tok}{v}")
                    last_vowel = v
                    idx += 2
                else:
                    # Consonante final o en grupo consonántico -> insertar vocal sinarmónica o disarmónica muda
                    if vowel_harmony == "disharmonic":
                        echo_v = "i" if last_vowel != "i" else "a"
                    else:
                        echo_v = last_vowel
                    conn_c = tok if tok in MayanEpigraphyLexicon.CONSONANTS else "l"
                    syllables.append(f"{conn_c}{echo_v}")
                    idx += 1

        # Construir ranuras de empaquetado para un cartucho silábico puro
        slots = []
        for s_idx, syl in enumerate(syllables):
            role = "main" if s_idx == 0 else ("superfix" if s_idx == 1 and len(syllables) > 2 else "subfix")
            slots.append({
                "syllable": syl,
                "role": role,
                "thompson_id": cls._get_syllable_thompson(syl)
            })

        return {
            "input": word,
            "normalized_phonetic": phonetic,
            "vowel_harmony_rule": vowel_harmony,
            "syllables": syllables,
            "epigraphic_hyphenated": "-".join(syllables),
            "phonemic_reconstruction": clean,
            "slots": slots
        }

    @staticmethod
    def _get_syllable_thompson(syl: str) -> str:
        if not syl:
            return "T1.1"
        v = syl[-1]
        c = syl[:-1]
        arch = MayanEpigraphyLexicon.CONSONANT_GLYPH_ARCHETYPE.get(c, ("vocalic_scroll", "T1", ""))
        v_idx = MayanEpigraphyLexicon.VOWELS.index(v) + 1 if v in MayanEpigraphyLexicon.VOWELS else 1
        return f"{arch[1]}.{v_idx}"

    @classmethod
    def pack_cartouche_from_lexeme(
        cls,
        lex_key: str,
        coord: str = "A1",
        orthography: str = "logosyllabic",
        numeral: Optional[int] = None
    ) -> GlyphCartoucheBlock:
        """
        Empaqueta una entrada del léxico o una palabra fonética en un bloque cuadrangular
        aplicando el modo ortográfico elegido: 'logographic', 'logosyllabic' o 'syllabic'.
        """
        cat = MayanEpigraphyLexicon.LOGOGRAM_CATALOG.get(lex_key.upper())
        if cat:
            syls = cat["syllabic"]
            is_verb = cat["pos"] in ("VERB", "POS")

            if orthography == "logographic":
                main_s = GlyphAffixSlot(lex_key.upper(), True, cat["thompson"], "main", cat["es"][0], cat["en"][0])
                sup_s = GlyphAffixSlot("u", False, "T1.5", "superfix", "3SG.ERG", "3SG.ERG") if is_verb else None
                sub_s = None
                post_s = None
                translit = f"u-{lex_key.upper()}" if is_verb else lex_key.upper()

            elif orthography == "syllabic":
                # 100% Silábico fonético sin logograma
                s0 = syls[0]
                main_s = GlyphAffixSlot(s0, False, cls._get_syllable_thompson(s0), "main", cat["es"][0], cat["en"][0])
                sup_s = GlyphAffixSlot("u", False, "T1.5", "superfix") if is_verb and s0 != "u" else None
                sub_s = GlyphAffixSlot(syls[1], False, cls._get_syllable_thompson(syls[1]), "subfix") if len(syls) > 1 else None
                post_s = GlyphAffixSlot(syls[-1], False, cls._get_syllable_thompson(syls[-1]), "postfix") if len(syls) > 2 else None
                translit = "-".join(syls)

            else:
                # Modo Clásico Reina: Logosílabico (Logograma + Complemento fonético subfijo/superfijo)
                main_s = GlyphAffixSlot(lex_key.upper(), True, cat["thompson"], "main", cat["es"][0], cat["en"][0])
                sup_s = GlyphAffixSlot("u", False, "T1.5", "superfix", "3SG.ERG", "3SG.ERG") if is_verb else None
                last_syl = syls[-1]
                sub_s = GlyphAffixSlot(last_syl, False, cls._get_syllable_thompson(last_syl), "subfix", "Comp. fonético", "Phonetic comp.")
                post_s = None
                prefix_str = "u-" if is_verb else ""
                translit = f"{prefix_str}{lex_key.upper()}-{last_syl}"

            return GlyphCartoucheBlock(
                coord=coord,
                main_sign=main_s,
                superfix=sup_s,
                subfix=sub_s,
                postfix=post_s,
                numeral=numeral,
                epigraphic_translit=translit,
                phonemic_maya=cat["maya_phonemic"],
                linear_es=cat["es"][0].capitalize(),
                linear_en=cat["en"][0].capitalize(),
                morpho_gloss=cat["morpho"],
                harmonic_accord=cat["accord"],
                biocymatic_vector=cat["biocymatic"]
            )

        # Si es un nombre propio o término libre no catalogado -> Transliteración Fonética CV
        syl_data = cls.syllabify_word(lex_key)
        syls = syl_data["syllables"]
        s_main = syls[0] if syls else "a"
        main_slot = GlyphAffixSlot(s_main, False, cls._get_syllable_thompson(s_main), "main", lex_key, lex_key)
        sup_slot = GlyphAffixSlot(syls[1], False, cls._get_syllable_thompson(syls[1]), "superfix") if len(syls) > 1 else None
        sub_slot = GlyphAffixSlot(syls[2], False, cls._get_syllable_thompson(syls[2]), "subfix") if len(syls) > 2 else None
        post_slot = GlyphAffixSlot(syls[3], False, cls._get_syllable_thompson(syls[3]), "postfix") if len(syls) > 3 else None

        dom_vowel = s_main[-1] if s_main[-1] in MayanEpigraphyLexicon.VOWEL_KOTOTAMA else "a"
        koto = MayanEpigraphyLexicon.VOWEL_KOTOTAMA[dom_vowel]

        return GlyphCartoucheBlock(
            coord=coord,
            main_sign=main_slot,
            superfix=sup_slot,
            subfix=sub_slot,
            postfix=post_slot,
            numeral=numeral,
            epigraphic_translit=syl_data["epigraphic_hyphenated"],
            phonemic_maya=syl_data["phonemic_reconstruction"],
            linear_es=f"{lex_key} (Nombre/Término fonético)",
            linear_en=f"{lex_key} (Phonetic proper noun/term)",
            morpho_gloss=f"Transliteración silábica CV ({syl_data['epigraphic_hyphenated']}) con regla sinarmónica.",
            harmonic_accord=f"Adaptación fonológica al canon maya clásico ({len(syls)} sílabas acopladas).",
            biocymatic_vector=f"Kototama {koto['kototama']} • {koto['freq_hz']} Hz • {koto['element']}"
        )

    @classmethod
    def translate_and_compile(
        cls,
        text: str,
        source_lang: str = "es",
        orthography_mode: str = "logosyllabic"
    ) -> SemanticPrismTranslation:
        """
        Traduce un texto en Español, Inglés o Maya Clásico, detecta difrasismos (Tz'ak),
        reordena sintácticamente al canon epigráfico VOS (Verbo -> Objeto -> Sujeto)
        y construye el Prisma Semántico de 4 Capas.
        """
        raw_words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+", text)
        stopwords = cls.STOPWORDS_ES if source_lang == "es" else cls.STOPWORDS_EN

        # 1. Detectar Difrasismos activos en el texto
        lower_set = {w.lower() for w in raw_words}
        detected_diphrasisms: List[str] = []
        for diph in MayanEpigraphyLexicon.DIPHRASISMS:
            triggers = diph["triggers_es"] if source_lang == "es" else diph["triggers_en"]
            for t1, t2 in triggers:
                if t1 in lower_set and t2 in lower_set:
                    meaning = diph["emergent_meaning_es"] if source_lang == "es" else diph["emergent_meaning_en"]
                    detected_diphrasisms.append(f"✦ Difrasismo [{diph['id']}] ({diph['literal']}): {meaning}")
                    break

        # 2. Emparejar cada palabra con el catálogo epigráfico o silabificarla
        matched_tokens: List[Tuple[str, str, Optional[int]]] = []  # (lex_key, pos, numeral)
        pending_numeral: Optional[int] = None

        for w in raw_words:
            w_low = w.lower()
            if w_low in stopwords:
                continue
            if w_low.isdigit():
                pending_numeral = int(w_low) % 20
                continue

            found_key = None
            found_pos = "NOUN"

            # Comprobar si el usuario escribió directamente el código Maya (ej. B'ALAM, K'IN, TS'IB)
            if w.upper() in MayanEpigraphyLexicon.LOGOGRAM_CATALOG:
                found_key = w.upper()
                found_pos = MayanEpigraphyLexicon.LOGOGRAM_CATALOG[found_key]["pos"]
            else:
                for k_logo, data in MayanEpigraphyLexicon.LOGOGRAM_CATALOG.items():
                    lang_list = data["es"] if source_lang == "es" else data["en"]
                    if w_low in lang_list or any(w_low.startswith(stem[:4]) and len(w_low) >= 4 for stem in lang_list if len(stem) >= 4):
                        found_key = k_logo
                        found_pos = data["pos"]
                        break
                    if w_low == data["maya_phonemic"]:
                        found_key = k_logo
                        found_pos = data["pos"]
                        break

            if found_key:
                matched_tokens.append((found_key, found_pos, pending_numeral))
            else:
                matched_tokens.append((w, "PROPER", pending_numeral))
            pending_numeral = None

        if not matched_tokens:
            matched_tokens = [("K'IN", "NOUN", 4), ("AJAW", "NOUN", None)]

        # 3. Reordenamiento Sintáctico Epigráfico Maya Clásico:
        #    [VERB / POS] -> [ADJ + Objeto] -> [Sujeto / Títulos]
        verbs = [t for t in matched_tokens if t[1] in ("VERB", "POS")]
        others = [t for t in matched_tokens if t[1] not in ("VERB", "POS")]
        vos_ordered = verbs + others

        # 4. Construir los Cartuchos en coordenadas pareadas (A1, B1, A2, B2...)
        blocks: List[GlyphCartoucheBlock] = []
        for idx, (lex_key, _pos, num) in enumerate(vos_ordered):
            col = "A" if idx % 2 == 0 else "B"
            row = (idx // 2) + 1
            coord = f"{col}{row}"
            blk = cls.pack_cartouche_from_lexeme(lex_key, coord=coord, orthography=orthography_mode, numeral=num)
            blocks.append(blk)

        # 5. Ensamblar las 4 Capas del Prisma Semántico
        epigraphic_str = "  ".join(f"[{b.coord}] {b.epigraphic_translit}" for b in blocks)
        phonemic_str = " ".join(b.phonemic_maya for b in blocks)

        surface_es_parts = [b.linear_es for b in blocks]
        surface_en_parts = [b.linear_en for b in blocks]

        layer2_morpho = [f"[{b.coord} • {b.epigraphic_translit}] → {b.morpho_gloss}" for b in blocks]
        layer3_harmonics = [f"[{b.coord} • {b.main_sign.code}] → {b.harmonic_accord}" for b in blocks]
        if detected_diphrasisms:
            layer3_harmonics = detected_diphrasisms + layer3_harmonics

        # Calcular cadencia vocálica Kototama global de la inscripción
        all_vowels = [ch for ch in phonemic_str.lower() if ch in MayanEpigraphyLexicon.VOWEL_KOTOTAMA]
        if not all_vowels:
            all_vowels = ["a"]
        dominant_v = max(set(all_vowels), key=all_vowels.count)
        koto_info = MayanEpigraphyLexicon.VOWEL_KOTOTAMA[dominant_v]

        layer4_bio = {
            "vowel_cadence": " - ".join(v.upper() for v in all_vowels[:16]),
            "dominant_kototama": koto_info["kototama"],
            "resonant_frequency_hz": koto_info["freq_hz"],
            "elemental_polarity": koto_info["element"],
            "block_vectors": [f"[{b.coord}] {b.biocymatic_vector}" for b in blocks]
        }

        return SemanticPrismTranslation(
            source_text=text,
            source_lang=source_lang,
            orthography_mode=orthography_mode,
            blocks=blocks,
            layer1_surface_es=" • ".join(surface_es_parts),
            layer1_surface_en=" • ".join(surface_en_parts),
            layer2_morpho_topological=layer2_morpho,
            layer3_harmonic_diphrasisms=layer3_harmonics,
            layer4_biocymatic_kototama=layer4_bio,
            epigraphic_transcription=epigraphic_str,
            phonemic_reading=phonemic_str
        )


# ══════════════════════════════════════════════════════════════════════════════
# 4. MOTOR CALIGRÁFICO VECTORIAL PARAMÉTRICO (SVG + QPAINTER + HEIGHTMAP 3D)
# ══════════════════════════════════════════════════════════════════════════════

class MayanCalligraphicEngine:
    """
    Generador caligráfico vectorial sin dependencias externas.
    Dibuja los 95 silabogramas CV, los logogramas monumentales, numerales vigesimales
    y cartuchos completos en formato SVG puro o directamente sobre un QPainter.
    """

    THEMES = {
        "obsidian": {
            "bg": "#080B11",
            "slab_bg": "#0F1522",
            "slab_border": "#F59E0B",
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
            "slab_bg": "#F4ECD8",
            "slab_border": "#8B1E0F",
            "cartouche_fill": "#FAF3E3",
            "cartouche_rim": "#1C1917",
            "inner_rim": "#8B1E0F",
            "glyph_fill": "#EFE4CE",
            "glyph_stroke": "#1C1917",
            "jade_accent": "#2E6F95",     # Azul Maya clásico
            "crimson_accent": "#991B1B",  # Rojo Hematita
            "text_primary": "#1C1917",
            "text_secondary": "#57534E",
        },
        "heightmap": {
            "bg": "#000000",
            "slab_bg": "#181818",
            "slab_border": "#505050",
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

    @classmethod
    def render_sign_svg_primitives(
        cls,
        code: str,
        x: float,
        y: float,
        w: float,
        h: float,
        palette: Dict[str, str],
        is_logogram: bool = False,
        role: str = "main",
        thompson_id: str = ""
    ) -> str:
        """
        PUNTO 1 Y 2: Genera los trazos vectoriales de alta paridad arqueológica para cualquier
        logograma o sílaba CV (con los 24+ radicales, cintas Bézier de presión variable,
        inflexión vocálica y deformación anamórfica en jaula bilineal).
        """
        return MayanRadicalGrammar.render_high_parity_slot_svg(
            code=code,
            x=x,
            y=y,
            w=w,
            h=h,
            role=role,
            palette=palette,
            is_logogram=is_logogram,
            thompson_id=thompson_id,
            show_label=True
        )

    @classmethod
    def render_numeral_svg(cls, number: int, x: float, y: float, w: float, h: float, palette: Dict[str, str]) -> str:
        """Dibuja un numeral vigesimal maya de barras (5) y puntos (1) o concha sagrada Mih (0)."""
        return MayanRadicalGrammar.render_numeral_high_parity_svg(
            number=number,
            x=x,
            y=y,
            w=w,
            h=h,
            palette=palette,
            vertical=True
        )

    @classmethod
    def render_cartouche_block_svg(
        cls,
        block: GlyphCartoucheBlock,
        x: float,
        y: float,
        size: float = 210.0,
        style: str = "obsidian"
    ) -> str:
        """
        Empaqueta topológicamente un Cartucho completo (Numeral + Prefijo + Superfijo +
        Principal + Infijo + Subfijo + Postfijo) en el cuadrado (x, y, size, size)
        usando deformación en jaula bilineal para que los afijos abracen orgánicamente al signo principal.
        """
        pal = cls.THEMES.get(style, cls.THEMES["obsidian"])
        svg = []

        # 1. Marco exterior monumental del cartucho (Squircle doble)
        outer_r = size * 0.16
        svg.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{outer_r:.1f}" '
            f'fill="{pal["cartouche_fill"]}" stroke="{pal["cartouche_rim"]}" stroke-width="3.2"/>'
        )
        svg.append(
            f'<rect x="{x+5:.1f}" y="{y+5:.1f}" width="{size-10:.1f}" height="{size-10:.1f}" rx="{outer_r-3:.1f}" '
            f'fill="none" stroke="{pal["inner_rim"]}" stroke-width="1.3" stroke-dasharray="6,3"/>'
        )

        # Cuentas de jade en las 4 esquinas del cartucho
        for cx_off, cy_off in [(12, 12), (size - 12, 12), (12, size - 12), (size - 12, size - 12)]:
            svg.append(f'<circle cx="{x+cx_off:.1f}" cy="{y+cy_off:.1f}" r="3.2" fill="{pal["jade_accent"]}"/>')

        # Coordenada epigráfica (ej. A1, B1)
        svg.append(
            f'<text x="{x+14:.1f}" y="{y+20:.1f}" fill="{pal["jade_accent"]}" '
            f'font-family="Consolas, monospace" font-size="11px" font-weight="bold">{block.coord}</text>'
        )

        # 2. Cálculo de la geometría interior según qué afijos están activos
        ix = x + 12.0
        iy = y + 24.0
        iw = size - 24.0
        ih = size - 48.0

        # Si hay numeral vigesimal a la izquierda
        if block.numeral is not None:
            num_w = iw * 0.24
            svg.append(cls.render_numeral_svg(block.numeral, ix, iy, num_w, ih, pal))
            ix += num_w + 4
            iw -= (num_w + 4)

        # Si hay prefijo a la izquierda
        if block.prefix is not None:
            pre_w = iw * 0.26
            svg.append(cls.render_sign_svg_primitives(
                block.prefix.code, ix, iy, pre_w, ih, pal,
                is_logogram=block.prefix.is_logogram, role="prefix", thompson_id=block.prefix.thompson_id
            ))
            ix += pre_w + 3
            iw -= (pre_w + 3)

        # Si hay postfijo a la derecha
        if block.postfix is not None:
            post_w = iw * 0.26
            svg.append(cls.render_sign_svg_primitives(
                block.postfix.code, ix + iw - post_w, iy, post_w, ih, pal,
                is_logogram=block.postfix.is_logogram, role="postfix", thompson_id=block.postfix.thompson_id
            ))
            iw -= (post_w + 3)

        # Si hay superfijo arriba (se arquea hacia abajo abrazando la bóveda del signo central)
        if block.superfix is not None:
            sup_h = ih * 0.26
            svg.append(cls.render_sign_svg_primitives(
                block.superfix.code, ix, iy, iw, sup_h, pal,
                is_logogram=block.superfix.is_logogram, role="superfix", thompson_id=block.superfix.thompson_id
            ))
            iy += sup_h + 3
            ih -= (sup_h + 3)

        # Si hay subfijo abajo (se curva hacia arriba acunando la base del signo central)
        if block.subfix is not None:
            sub_h = ih * 0.26
            svg.append(cls.render_sign_svg_primitives(
                block.subfix.code, ix, iy + ih - sub_h, iw, sub_h, pal,
                is_logogram=block.subfix.is_logogram, role="subfix", thompson_id=block.subfix.thompson_id
            ))
            ih -= (sub_h + 3)

        # 3. Signo Principal en el núcleo restante
        svg.append(cls.render_sign_svg_primitives(
            block.main_sign.code, ix, iy, iw, ih, pal,
            is_logogram=block.main_sign.is_logogram, role="main", thompson_id=block.main_sign.thompson_id
        ))

        # 4. Si hay Infijo incrustado en el corazón del Signo Principal
        if block.infix is not None:
            inf_w = iw * 0.42
            inf_h = ih * 0.42
            inf_x = ix + (iw - inf_w) * 0.5
            inf_y = iy + (ih - inf_h) * 0.5
            svg.append(cls.render_sign_svg_primitives(
                block.infix.code, inf_x, inf_y, inf_w, inf_h, pal,
                is_logogram=block.infix.is_logogram, role="infix", thompson_id=block.infix.thompson_id
            ))

        # 5. Pie del cartucho con transliteración y lectura fonémica
        caption = f"{block.epigraphic_translit} ({block.phonemic_maya})"
        svg.append(
            f'<text x="{x + size*0.5:.1f}" y="{y + size - 8:.1f}" fill="{pal["text_secondary"]}" '
            f'font-family="Consolas, monospace" font-size="10.5px" text-anchor="middle">{caption[:28]}</text>'
        )

        return "\n".join(svg)

        # 4. Si hay Infijo incrustado en el corazón del Signo Principal
        if block.infix is not None:
            inf_w = iw * 0.42
            inf_h = ih * 0.42
            inf_x = ix + (iw - inf_w) * 0.5
            inf_y = iy + (ih - inf_h) * 0.5
            svg.append(cls.render_sign_svg_primitives(
                block.infix.code, inf_x, inf_y, inf_w, inf_h, pal, block.infix.is_logogram
            ))

        # 5. Pie del cartucho con transliteración y lectura fonémica
        caption = f"{block.epigraphic_translit} ({block.phonemic_maya})"
        svg.append(
            f'<text x="{x + size*0.5:.1f}" y="{y + size - 8:.1f}" fill="{pal["text_secondary"]}" '
            f'font-family="Consolas, monospace" font-size="10.5px" text-anchor="middle">{caption[:28]}</text>'
        )

        return "\n".join(svg)

    @classmethod
    def render_stele_svg(
        cls,
        prism: SemanticPrismTranslation,
        style: str = "obsidian",
        columns: int = 2
    ) -> str:
        """
        Renderiza una Estela Maya completa en formato SVG vectorial con lectura
        boustrophedon en columnas pareadas (A1-B1, A2-B2...) y cabecera epigráfica.
        """
        pal = cls.THEMES.get(style, cls.THEMES["obsidian"])
        cols = max(1, min(4, columns))
        blocks = prism.blocks
        rows = math.ceil(len(blocks) / cols)

        cell_size = 220.0
        pad = 24.0
        header_h = 95.0
        footer_h = 85.0

        total_w = pad * 2 + cols * cell_size + (cols - 1) * 18.0
        total_h = header_h + rows * (cell_size + 18.0) + footer_h

        svg = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="{total_w:.0f}" height="{total_h:.0f}">',
            f'<rect width="100%" height="100%" fill="{pal["bg"]}"/>',
            f'<rect x="10" y="10" width="{total_w-20:.0f}" height="{total_h-20:.0f}" rx="18" '
            f'fill="{pal["slab_bg"]}" stroke="{pal["slab_border"]}" stroke-width="3"/>',
            f'<text x="{total_w*0.5:.1f}" y="42" fill="{pal["cartouche_rim"]}" font-family="Consolas, monospace" '
            f'font-size="16px" font-weight="bold" text-anchor="middle">MAYAN STELE • AH TS\'IB EPIGRAPHIC MONUMENT</text>',
            f'<text x="{total_w*0.5:.1f}" y="66" fill="{pal["jade_accent"]}" font-family="Consolas, monospace" '
            f'font-size="12px" text-anchor="middle">{prism.phonemic_reading.upper()}</text>'
        ]

        for idx, blk in enumerate(blocks):
            r = idx // cols
            c = idx % cols
            bx = pad + c * (cell_size + 18.0)
            by = header_h + r * (cell_size + 18.0)
            svg.append(cls.render_cartouche_block_svg(blk, bx, by, size=cell_size, style=style))

        # Pie con el resumen de Kototama y traducción lineal
        fy = total_h - footer_h + 25
        koto_str = f"Kototama: {prism.layer4_biocymatic_kototama['dominant_kototama']} ({prism.layer4_biocymatic_kototama['resonant_frequency_hz']} Hz)"
        svg.append(
            f'<text x="{total_w*0.5:.1f}" y="{fy:.1f}" fill="{pal["text_primary"]}" '
            f'font-family="Segoe UI, sans-serif" font-size="12px" text-anchor="middle">{prism.layer1_surface_es[:72]}</text>'
        )
        svg.append(
            f'<text x="{total_w*0.5:.1f}" y="{fy+22:.1f}" fill="{pal["text_secondary"]}" '
            f'font-family="Consolas, monospace" font-size="11px" text-anchor="middle">{koto_str}</text>'
        )
        svg.append("</svg>")
        return "\n".join(svg)

    @classmethod
    def render_stele_markdown(cls, prism: SemanticPrismTranslation) -> str:
        """Exporta la inscripción epigráfica y el Prisma Semántico a un informe Markdown estructurado."""
        koto = prism.layer4_biocymatic_kototama
        lines = [
            f"# 📜 INSCRIPIÓN EPIGRÁFICA MAYA • ESTELA AH TS'IB",
            f"",
            f"**Lectura Fonémica:** *{prism.phonemic_reading}*",
            f"**Transcripción Epigráfica (Orden VOS):** `{prism.epigraphic_transcription}`",
            f"",
            f"---",
            f"",
            f"## 🧱 Matriz de Cartuchos (Columnas Pareadas A1-B1, A2-B2...)",
            f"",
            f"| Coord | Transliteración Epigráfica | Maya Fonémico | Ranuras Topológicas Activas |",
            f"| :---: | :--- | :--- | :--- |"
        ]

        for blk in prism.blocks:
            slots_desc = []
            if blk.numeral is not None:
                slots_desc.append(f"Num: {blk.numeral}")
            if blk.prefix:
                slots_desc.append(f"Pref: {blk.prefix.code} ({blk.prefix.thompson_id})")
            if blk.superfix:
                slots_desc.append(f"Sup: {blk.superfix.code} ({blk.superfix.thompson_id})")
            main_str = f"Main: {blk.main_sign.code} ({blk.main_sign.thompson_id})"
            if blk.infix:
                main_str += f" [Inf: {blk.infix.code}]"
            slots_desc.append(main_str)
            if blk.subfix:
                slots_desc.append(f"Sub: {blk.subfix.code} ({blk.subfix.thompson_id})")
            if blk.postfix:
                slots_desc.append(f"Post: {blk.postfix.code} ({blk.postfix.thompson_id})")

            lines.append(f"| **{blk.coord}** | `{blk.epigraphic_translit}` | *{blk.phonemic_maya}* | {', '.join(slots_desc)} |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 🔮 Análisis del Prisma Semántico de 4 Capas",
            f"",
            f"### 🔹 Capa 1: Superficie Lineal",
            f"- **Español:** {prism.layer1_surface_es}",
            f"- **Inglés:** {prism.layer1_surface_en}",
            f"",
            f"### 🔹 Capa 2: Glosa Morfo-Topológica y Geometría Sintáctica",
        ])
        for m in prism.layer2_morpho_topological:
            lines.append(f"- {m}")

        lines.extend([
            f"",
            f"### 🔹 Capa 3: Acordes de Resonancia Homofónica y Difrasismos (Tz'ak)",
        ])
        for h in prism.layer3_harmonic_diphrasisms:
            lines.append(f"- {h}")

        lines.extend([
            f"",
            f"### 🔹 Capa 4: Vector Biocimático y Kototama",
            f"- **Cadencia de Vocales:** `{koto.get('vowel_cadence', '')}`",
            f"- **Kototama Dominante:** `{koto.get('dominant_kototama', '')}` ({koto.get('resonant_frequency_hz', 0)} Hz)",
            f"- **Polaridad Elemental:** {koto.get('elemental_polarity', '')}",
            f"- **Perfil Resonante:** {', '.join(koto.get('vowel_resonance_profile', []))}",
            f"",
            f"---",
            f"*Generado por Ah Ts'ib Engine • MayanCalendar Project (GPL v3)*"
        ])
        return "\n".join(lines)

    @classmethod
    def render_stele_ascii(cls, prism: SemanticPrismTranslation) -> str:
        """Exporta una visualización en arte ASCII/Unicode de los cartuchos pareados."""
        blocks = prism.blocks
        lines = [
            "╔══════════════════════════════════════════════════════════════════╗",
            "║             ESTELA MAYA EPIGRÁFICA • LECTURA EN PAREJAS          ║",
            "╚══════════════════════════════════════════════════════════════════╝",
            ""
        ]
        for i in range(0, len(blocks), 2):
            b1 = blocks[i]
            b2 = blocks[i+1] if i+1 < len(blocks) else None

            t1 = f"[{b1.coord}] {b1.epigraphic_translit}"[:30].ljust(30)
            t2 = f"[{b2.coord}] {b2.epigraphic_translit}"[:30].ljust(30) if b2 else "".ljust(30)

            p1 = f"/{b1.phonemic_maya}/"[:30].ljust(30)
            p2 = f"/{b2.phonemic_maya}/"[:30].ljust(30) if b2 else "".ljust(30)

            lines.append(f"┌─{'─'*32}─┐  ┌─{'─'*32}─┐")
            lines.append(f"│  {t1}  │  │  {t2}  │")
            lines.append(f"│  {p1}  │  │  {p2}  │")
            lines.append(f"└─{'─'*32}─┘  └─{'─'*32}─┘")
            lines.append("")

        lines.append(f"Lectura Fonémica Global: \"{prism.phonemic_reading}\"")
        return "\n".join(lines)

    @classmethod
    def render_stele_json(cls, prism: SemanticPrismTranslation, indent: int = 2) -> str:
        """Serializa la estela completa y el prisma semántico a JSON estructurado."""
        data = {
            "epigraphic_transcription": prism.epigraphic_transcription,
            "phonemic_reading": prism.phonemic_reading,
            "layer1_surface": {
                "es": prism.layer1_surface_es,
                "en": prism.layer1_surface_en
            },
            "layer2_morpho_topological": prism.layer2_morpho_topological,
            "layer3_harmonic_diphrasisms": prism.layer3_harmonic_diphrasisms,
            "layer4_biocymatic_kototama": prism.layer4_biocymatic_kototama,
            "blocks": [asdict(b) for b in prism.blocks]
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)


# ══════════════════════════════════════════════════════════════════════════════
# 5. INTERFAZ GRÁFICA DE ESCRITORIO EN PYSIDE6 (ESTÉTICA OBSIDIANA, JADE Y ORO)
# ══════════════════════════════════════════════════════════════════════════════

try:
    from PySide6.QtCore import Qt, QRectF, QPointF
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
        QComboBox, QTextEdit, QScrollArea, QFrame, QSpinBox, QCheckBox,
        QFileDialog, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
        QSlider, QAbstractItemView
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


DARK_OBSIDIAN_QSS = """
QMainWindow, QWidget {
    background-color: #080B11;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #0B0F17;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #1E293B;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #131C2E;
    color: #F59E0B;
    border-bottom: 2px solid #10B981;
}
QFrame#CardFrame {
    background-color: #0F1522;
    border: 1px solid #1E293B;
    border-radius: 8px;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #131C2E;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 6px 10px;
    selection-background-color: #10B981;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #F59E0B;
}
QPushButton {
    background-color: #1E293B;
    color: #FCD34D;
    border: 1px solid #F59E0B;
    border-radius: 5px;
    padding: 7px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #064E3B;
    color: #34D399;
    border: 1px solid #10B981;
}
QTableWidget {
    background-color: #0B0F17;
    gridline-color: #1E293B;
    border: 1px solid #1E293B;
}
QHeaderView::section {
    background-color: #131C2E;
    color: #F59E0B;
    padding: 6px;
    border: 1px solid #1E293B;
    font-weight: bold;
}
"""

class SteleCanvasWidget(QWidget):
    """Lienzo nativo en QPainter para renderizar estelas y cartuchos con nitidez infinita."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocks: List[GlyphCartoucheBlock] = []
        self.style_mode: str = "obsidian"
        self.columns: int = 2
        self.setMinimumSize(460, 520)

    def set_blocks(self, blocks: List[GlyphCartoucheBlock], style: str = "obsidian", cols: int = 2):
        self.blocks = blocks
        self.style_mode = style
        self.columns = max(1, cols)
        rows = max(1, math.ceil(len(self.blocks) / self.columns))
        self.setMinimumHeight(max(500, rows * 235 + 90))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pal = MayanCalligraphicEngine.THEMES.get(self.style_mode, MayanCalligraphicEngine.THEMES["obsidian"])

        painter.fillRect(self.rect(), QColor(pal["bg"]))
        if not self.blocks:
            return

        w = self.width()
        h = self.height()

        if len(self.blocks) == 1:
            # En modo bloque individual (ej. Taller del Escriba o Inspector de Glifo),
            # escalar de forma monumental centrada para aprovechar el panel
            cell_sz = min(360.0, min(w - 48.0, h - 50.0))
            cell_sz = max(180.0, cell_sz)
            start_x = (w - cell_sz) * 0.5
            start_y = max(16.0, (h - cell_sz) * 0.5)
            self._draw_cartouche(painter, self.blocks[0], start_x, start_y, cell_sz, pal)
            return

        cell_sz = min(215.0, (w - 48.0) / self.columns - 12.0)
        cell_sz = max(140.0, cell_sz)
        total_grid_w = self.columns * cell_sz + (self.columns - 1) * 14.0
        start_x = max(16.0, (w - total_grid_w) * 0.5)
        start_y = 24.0

        for idx, blk in enumerate(self.blocks):
            r = idx // self.columns
            c = idx % self.columns
            bx = start_x + c * (cell_sz + 14.0)
            by = start_y + r * (cell_sz + 18.0)
            self._draw_cartouche(painter, blk, bx, by, cell_sz, pal)

    def _draw_cartouche(self, p: QPainter, blk: GlyphCartoucheBlock, x: float, y: float, sz: float, pal: Dict[str, str]):
        # Renderizado de alta fidelidad arqueológica mediante QSvgRenderer
        try:
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtCore import QByteArray, QRectF
            cartouche_svg = MayanCalligraphicEngine.render_cartouche_block_svg(blk, 0, 0, sz, self.style_mode)
            svg_doc = f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="{sz:.1f}" height="{sz:.1f}">{cartouche_svg}</svg>'
            renderer = QSvgRenderer(QByteArray(svg_doc.encode("utf-8")))
            if renderer.isValid():
                renderer.render(p, QRectF(x, y, sz, sz))
                return
        except Exception:
            pass

        # Fallback nativo directo sobre QPainter si QSvgRenderer no estuviese disponible
        p.setPen(QPen(QColor(pal["cartouche_rim"]), 2.8))
        p.setBrush(QBrush(QColor(pal["cartouche_fill"])))
        p.drawRoundedRect(QRectF(x, y, sz, sz), sz * 0.15, sz * 0.15)

        # Marco interior punteado en jade
        pen_in = QPen(QColor(pal["inner_rim"]), 1.2, Qt.DashLine)
        p.setPen(pen_in)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(x + 5, y + 5, sz - 10, sz - 10), sz * 0.13, sz * 0.13)

        # Coordenada (A1, B1...)
        p.setPen(QColor(pal["jade_accent"]))
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        p.drawText(QPointF(x + 12, y + 18), blk.coord)

        ix, iy = x + 11.0, y + 23.0
        iw, ih = sz - 22.0, sz - 44.0

        # Numeral vigesimal
        if blk.numeral is not None:
            nw = iw * 0.23
            self._draw_numeral(p, blk.numeral, ix, iy, nw, ih, pal)
            ix += nw + 4
            iw -= (nw + 4)

        if blk.prefix is not None:
            pw = iw * 0.26
            self._draw_sign(p, blk.prefix.code, ix, iy, pw, ih, pal, blk.prefix.is_logogram)
            ix += pw + 3
            iw -= (pw + 3)

        if blk.postfix is not None:
            pow_w = iw * 0.26
            self._draw_sign(p, blk.postfix.code, ix + iw - pow_w, iy, pow_w, ih, pal, blk.postfix.is_logogram)
            iw -= (pow_w + 3)

        if blk.superfix is not None:
            sh = ih * 0.26
            self._draw_sign(p, blk.superfix.code, ix, iy, iw, sh, pal, blk.superfix.is_logogram)
            iy += sh + 3
            ih -= (sh + 3)

        if blk.subfix is not None:
            sub_h = ih * 0.26
            self._draw_sign(p, blk.subfix.code, ix, iy + ih - sub_h, iw, sub_h, pal, blk.subfix.is_logogram)
            ih -= (sub_h + 3)

        # Signo principal
        self._draw_sign(p, blk.main_sign.code, ix, iy, iw, ih, pal, blk.main_sign.is_logogram)

        # Infijo
        if blk.infix is not None:
            inf_w, inf_h = iw * 0.44, ih * 0.44
            self._draw_sign(p, blk.infix.code, ix + (iw - inf_w) * 0.5, iy + (ih - inf_h) * 0.5, inf_w, inf_h, pal, blk.infix.is_logogram)

        # Pie epigráfico
        p.setPen(QColor(pal["text_secondary"]))
        p.setFont(QFont("Consolas", 8))
        caption = f"{blk.epigraphic_translit} ({blk.phonemic_maya})"
        p.drawText(QRectF(x + 4, y + sz - 18, sz - 8, 16), Qt.AlignCenter, caption[:26])

    def _draw_numeral(self, p: QPainter, num: int, x: float, y: float, w: float, h: float, pal: Dict[str, str]):
        n = max(0, min(19, num))
        bars, dots = n // 5, n % 5
        if n == 0:
            p.setPen(QPen(QColor(pal["glyph_stroke"]), 1.8))
            p.setBrush(QColor(pal["crimson_accent"]))
            p.drawEllipse(QPointF(x + w * 0.5, y + h * 0.5), w * 0.32, h * 0.36)
            return
        cx_cur = x + 4
        if dots > 0:
            p.setPen(QPen(QColor(pal["glyph_stroke"]), 1.4))
            p.setBrush(QColor(pal["jade_accent"]))
            step = h / (dots + 1)
            for d in range(dots):
                p.drawEllipse(QPointF(cx_cur + 5, y + step * (d + 1)), 4.5, 4.5)
            cx_cur += 14
        p.setBrush(QColor(pal["cartouche_rim"]))
        for b in range(bars):
            p.drawRoundedRect(QRectF(cx_cur + b * 8, y + h * 0.12, 5.5, h * 0.76), 2.5, 2.5)

    def _draw_sign(self, p: QPainter, code: str, x: float, y: float, w: float, h: float, pal: Dict[str, str], is_logo: bool):
        p.setPen(QPen(QColor(pal["glyph_stroke"]), 2.0))
        p.setBrush(QColor(pal["glyph_fill"]))
        r = min(w, h) * 0.25
        p.drawRoundedRect(QRectF(x + 2, y + 2, w - 4, h - 4), r, r)

        cx, cy = x + w * 0.5, y + h * 0.5
        rx, ry = w * 0.36, h * 0.36

        # Motivo geométrico interno en jade y carmesí
        p.setPen(QPen(QColor(pal["jade_accent"]), 1.7))
        p.setBrush(Qt.NoBrush)
        if is_logo:
            p.drawEllipse(QPointF(cx, cy), rx * 0.85, ry * 0.85)
            p.setPen(QPen(QColor(pal["crimson_accent"]), 1.6))
            p.drawLine(QPointF(cx - rx * 0.6, cy), QPointF(cx + rx * 0.6, cy))
            p.drawLine(QPointF(cx, cy - ry * 0.6), QPointF(cx, cy + ry * 0.6))
        else:
            p.drawRoundedRect(QRectF(cx - rx * 0.7, cy - ry * 0.5, rx * 1.4, ry), 4, 4)

        p.setPen(QColor(pal["text_primary"]))
        f_sz = max(7, min(12, int(min(w, h) * 0.22)))
        p.setFont(QFont("Consolas", f_sz, QFont.Bold))
        p.drawText(QRectF(x, y, w, h), Qt.AlignCenter, code)

class MayanLangWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAYAN-LANG (AH TS'IB) • Epigraphic Compiler, Syllabary & 4-Layer Semantic Prism")
        self.resize(1340, 860)
        self.setStyleSheet(DARK_OBSIDIAN_QSS)

        self.current_prism: Optional[SemanticPrismTranslation] = None
        self._build_ui()
        self._run_translation()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(14, 14, 14, 14)

        # Cabecera Monumental
        hdr = QLabel("✒️ MAYAN-LANG (AH TS'IB) • COMPILADOR EPIGRÁFICO, SILABARIO CV & PRISMA SEMÁNTICO")
        hdr.setStyleSheet("font-size: 18px; font-weight: bold; color: #F59E0B; padding: 6px;")
        main_lay.addWidget(hdr)

        self.tabs = QTabWidget()
        main_lay.addWidget(self.tabs)

        self._build_tab_composer()
        self._build_tab_scribe_workshop()
        self._build_tab_syllabary_grid()
        self._build_tab_lexicon()

    # ── PESTAÑA 1: COMPOSITOR ES/EN ⟷ MAYA & PRISMA DE 4 CAPAS ──
    def _build_tab_composer(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)

        left_panel = QFrame()
        left_panel.setObjectName("CardFrame")
        left_lay = QVBoxLayout(left_panel)

        # Selector de Preajustes Monumentales
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("📜 Preajustes Clásicos:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "(Escribir texto personalizado...)",
            "El sagrado señor jaguar escribió la estela en el cielo y la cueva",
            "Pakal se sentó en el trono sagrado de la montaña",
            "Kukulkán descendió de la pirámide al amanecer",
            "El sol ilumina el templo sagrado y el agua viva",
            "The divine king carved the holy stela for the gods"
        ])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_row.addWidget(self.preset_combo)
        left_lay.addLayout(preset_row)

        left_lay.addWidget(QLabel("🌐 ENTRADA MULTILINGÜE (Español / Inglés / Maya Directo):"))
        self.input_text = QLineEdit("El sagrado señor jaguar escribió la estela en el cielo y la cueva")
        left_lay.addWidget(self.input_text)

        ctrl_row = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["es (Español ➔ Maya VOS)", "en (English ➔ Maya VOS)"])
        ctrl_row.addWidget(QLabel("Idioma:"))
        ctrl_row.addWidget(self.lang_combo)

        self.ortho_combo = QComboBox()
        self.ortho_combo.addItems(["logosyllabic (Clásico)", "logographic (Puro)", "syllabic (100% Fonético)"])
        ctrl_row.addWidget(QLabel("Ortografía:"))
        ctrl_row.addWidget(self.ortho_combo)

        self.style_combo = QComboBox()
        self.style_combo.addItems(["obsidian (Basalto/Jade/Oro)", "codex (Amate/Azul Maya)", "heightmap (Relieve 3D OculaDomus)"])
        ctrl_row.addWidget(QLabel("Paleta:"))
        ctrl_row.addWidget(self.style_combo)
        left_lay.addLayout(ctrl_row)

        btn_row = QHBoxLayout()
        btn_compile = QPushButton("⚡ Compilar Estela VOS")
        btn_compile.clicked.connect(self._run_translation)
        btn_export_svg = QPushButton("💾 SVG")
        btn_export_svg.clicked.connect(self._export_current_svg)
        btn_export_md = QPushButton("📋 Markdown")
        btn_export_md.clicked.connect(self._export_current_markdown)
        btn_export_ascii = QPushButton("🔲 ASCII")
        btn_export_ascii.clicked.connect(self._export_current_ascii)
        btn_export_json = QPushButton("📦 JSON")
        btn_export_json.clicked.connect(self._export_current_json)

        btn_row.addWidget(btn_compile)
        btn_row.addWidget(btn_export_svg)
        btn_row.addWidget(btn_export_md)
        btn_row.addWidget(btn_export_ascii)
        btn_row.addWidget(btn_export_json)
        left_lay.addLayout(btn_row)

        left_lay.addWidget(QLabel("🔮 PRISMA SEMÁNTICO DE 4 CAPAS (Trascendiendo la Traducción Lineal):"))
        self.prism_output = QTextEdit()
        self.prism_output.setReadOnly(True)
        left_lay.addWidget(self.prism_output, stretch=1)

        # Lienzo derecho con la Estela en Vivo
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        self.stele_canvas = SteleCanvasWidget()
        right_scroll.setWidget(self.stele_canvas)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_scroll)
        splitter.setSizes([680, 600])
        lay.addWidget(splitter)

        self.tabs.addTab(tab, "✒️ Compositor ES/EN ⟷ Maya & Prisma")

    # ── PESTAÑA 2: TALLER DEL ESCRIBA (ARMADOR MANUAL DE CARTUCHOS 2D) ──
    def _build_tab_scribe_workshop(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)

        form_card = QFrame()
        form_card.setObjectName("CardFrame")
        f_lay = QVBoxLayout(form_card)

        f_lay.addWidget(QLabel("🧱 CONSTRUCTOR TOPOLÓGICO DE CARTUCHO 2D (Ranuras Epigráficas):"))

        grid = QGridLayout()
        all_codes = list(MayanEpigraphyLexicon.LOGOGRAM_CATALOG.keys()) + [
            s["syllable"] for s in MayanEpigraphyLexicon.get_all_syllables()
        ]

        self.slot_main = QComboBox(); self.slot_main.addItems(all_codes); self.slot_main.setCurrentText("B'ALAM")
        self.slot_sup = QComboBox(); self.slot_sup.addItems(["(Ninguno)"] + all_codes); self.slot_sup.setCurrentText("K'UH")
        self.slot_pre = QComboBox(); self.slot_pre.addItems(["(Ninguno)"] + all_codes); self.slot_pre.setCurrentText("u")
        self.slot_inf = QComboBox(); self.slot_inf.addItems(["(Ninguno)"] + all_codes); self.slot_inf.setCurrentText("K'IN")
        self.slot_sub = QComboBox(); self.slot_sub.addItems(["(Ninguno)"] + all_codes); self.slot_sub.setCurrentText("ma")
        self.slot_post = QComboBox(); self.slot_post.addItems(["(Ninguno)"] + all_codes)

        self.use_num_chk = QCheckBox("Incluir Numeral Vigesimal (0..19):")
        self.use_num_chk.setChecked(True)
        self.num_spin = QSpinBox(); self.num_spin.setRange(0, 19); self.num_spin.setValue(4)

        grid.addWidget(QLabel("Signo Principal (Centro):"), 0, 0); grid.addWidget(self.slot_main, 0, 1)
        grid.addWidget(QLabel("Superfijo (Arriba):"), 1, 0); grid.addWidget(self.slot_sup, 1, 1)
        grid.addWidget(QLabel("Prefijo (Izquierda):"), 2, 0); grid.addWidget(self.slot_pre, 2, 1)
        grid.addWidget(QLabel("Infijo (Incrustado):"), 3, 0); grid.addWidget(self.slot_inf, 3, 1)
        grid.addWidget(QLabel("Subfijo (Abajo):"), 4, 0); grid.addWidget(self.slot_sub, 4, 1)
        grid.addWidget(QLabel("Postfijo (Derecha):"), 5, 0); grid.addWidget(self.slot_post, 5, 1)
        grid.addWidget(self.use_num_chk, 6, 0); grid.addWidget(self.num_spin, 6, 1)
        f_lay.addLayout(grid)

        btn_row_work = QHBoxLayout()
        btn_update_blk = QPushButton("🔨 Tallar Cartucho")
        btn_update_blk.clicked.connect(self._update_custom_cartouche)
        btn_export_blk = QPushButton("💾 Exportar SVG")
        btn_export_blk.clicked.connect(self._export_workshop_cartouche_svg)
        btn_row_work.addWidget(btn_update_blk)
        btn_row_work.addWidget(btn_export_blk)
        f_lay.addLayout(btn_row_work)

        self.custom_formula_lbl = QLabel("")
        self.custom_formula_lbl.setStyleSheet("color: #10B981; font-family: Consolas; font-size: 14px; padding: 6px;")
        f_lay.addWidget(self.custom_formula_lbl)

        self.workshop_info_lbl = QLabel("")
        self.workshop_info_lbl.setStyleSheet("color: #94A3B8; font-family: Consolas; font-size: 11.5px; padding: 6px;")
        f_lay.addWidget(self.workshop_info_lbl)
        f_lay.addStretch()

        self.workshop_canvas = SteleCanvasWidget()
        lay.addWidget(form_card, stretch=1)
        lay.addWidget(self.workshop_canvas, stretch=1)

        self.tabs.addTab(tab, "🧱 Taller del Escriba (Cartucho 2D)")
        self._update_custom_cartouche()

    # ── PESTAÑA 3: MATRIZ DEL SILABARIO CV (19x5) & SILABIFICADOR ──
    def _build_tab_syllabary_grid(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)

        left_box = QWidget()
        left_lay = QVBoxLayout(left_box)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("🔤 Silabificador Fonético de Nombres y Palabras:"))
        self.syl_word_input = QLineEdit("Oculavera")
        top_bar.addWidget(self.syl_word_input)
        self.harmony_combo = QComboBox()
        self.harmony_combo.addItems(["synharmonic (Vocal corta)", "disharmonic (Vocal larga/glotal)"])
        top_bar.addWidget(self.harmony_combo)
        btn_syl = QPushButton("Silabificar y Trazar")
        btn_syl.clicked.connect(self._run_syllabifier)
        top_bar.addWidget(btn_syl)
        left_lay.addLayout(top_bar)

        self.syl_result_lbl = QLabel("")
        self.syl_result_lbl.setStyleSheet("color: #FCD34D; font-family: Consolas; font-size: 14px; padding: 4px;")
        left_lay.addWidget(self.syl_result_lbl)

        # Tabla 20x5 del Silabario Maya
        self.syl_table = QTableWidget(len(MayanEpigraphyLexicon.CONSONANTS), 5)
        self.syl_table.setHorizontalHeaderLabels(["A (Fuego/432Hz)", "E (Viento/528Hz)", "I (Eje/639Hz)", "O (Tierra/396Hz)", "U (Agua/285Hz)"])
        v_labels = [c if c else "' (Vocal)" for c in MayanEpigraphyLexicon.CONSONANTS]
        self.syl_table.setVerticalHeaderLabels(v_labels)
        self.syl_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for r_idx, cons in enumerate(MayanEpigraphyLexicon.CONSONANTS):
            arch, t_code, _desc = MayanEpigraphyLexicon.CONSONANT_GLYPH_ARCHETYPE[cons]
            for c_idx, v in enumerate(MayanEpigraphyLexicon.VOWELS):
                syl = f"{cons}{v}"
                item = QTableWidgetItem(f"{syl}  [{t_code}.{c_idx+1}]")
                item.setTextAlignment(Qt.AlignCenter)
                self.syl_table.setItem(r_idx, c_idx, item)

        self.syl_table.cellClicked.connect(self._on_syllable_cell_clicked)
        left_lay.addWidget(self.syl_table)

        # Panel Derecho: Visualizador Caligráfico en Vivo de Sílabas (Puntos 1 y 2)
        right_box = QFrame()
        right_box.setObjectName("CardFrame")
        right_lay = QVBoxLayout(right_box)
        right_lay.addWidget(QLabel("✒️ TRAZADO DE SÍLABAS Y GLIFOS (ALTA PARIDAD):"))

        self.syllable_detail_lbl = QLabel("Selecciona cualquier celda para ver el radical anatómico e inflexión vocálica:")
        self.syllable_detail_lbl.setStyleSheet("color: #38BDF8; font-family: Consolas; font-size: 12px;")
        right_lay.addWidget(self.syllable_detail_lbl)

        self.syllabary_canvas = SteleCanvasWidget()
        right_lay.addWidget(self.syllabary_canvas, stretch=1)

        self.syllable_koto_card = QLabel("")
        self.syllable_koto_card.setStyleSheet("color: #FCD34D; font-family: Consolas; font-size: 11.5px; padding: 4px;")
        right_lay.addWidget(self.syllable_koto_card)

        btn_export_syl_svg = QPushButton("💾 Exportar Sílabas SVG")
        btn_export_syl_svg.clicked.connect(self._export_syllable_svg)
        right_lay.addWidget(btn_export_syl_svg)

        lay.addWidget(left_box, stretch=3)
        lay.addWidget(right_box, stretch=2)
        self.tabs.addTab(tab, "🔣 Matriz del Silabario (95 Sílabas CV)")
        self._run_syllabifier()

    # ── PESTAÑA 4: CORPUS THOMPSON (+860 GLIFOS MAYAS) & CÓDICE ──
    def _build_tab_lexicon(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)

        left_box = QWidget()
        left_lay = QVBoxLayout(left_box)

        # Barra superior con buscador en tiempo real y selector de familias arqueológicas
        filter_panel = QFrame()
        filter_panel.setObjectName("CardFrame")
        filter_lay = QVBoxLayout(filter_panel)
        filter_lay.setContentsMargins(8, 8, 8, 8)

        lbl_head = QLabel("🏛️ CORPUS THOMPSON (+860 GLIFOS: T1–T1066) & ARQUEOLOGÍA CLÁSICA:")
        lbl_head.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 13px;")
        filter_lay.addWidget(lbl_head)

        search_row = QHBoxLayout()
        self.thompson_search_input = QLineEdit()
        self.thompson_search_input.setPlaceholderText("🔍 Buscar por nombre, T-code (ej. T751, 533), MHD, maya, español o inglés...")
        self.thompson_search_input.textChanged.connect(self._on_thompson_filter_changed)
        search_row.addWidget(self.thompson_search_input, stretch=3)

        self.thompson_cat_combo = QComboBox()
        self.thompson_cat_combo.addItem("Todas las Familias (Corpus Completo)", "all")
        for cat_k, cat_lbl in MayanThompsonCatalog.CATEGORIES.items():
            self.thompson_cat_combo.addItem(cat_lbl, cat_k)
        self.thompson_cat_combo.currentIndexChanged.connect(self._on_thompson_filter_changed)
        search_row.addWidget(self.thompson_cat_combo, stretch=2)
        filter_lay.addLayout(search_row)

        self.thompson_status_lbl = QLabel("Mostrando 1066 de 1066 signos arqueológicos indexados")
        self.thompson_status_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        filter_lay.addWidget(self.thompson_status_lbl)
        left_lay.addWidget(filter_panel)

        # Tabla del Corpus Thompson
        self.thompson_table = QTableWidget(0, 6)
        self.thompson_table.setHorizontalHeaderLabels(["Thompson", "Nombre Glífico", "Categoría", "MHD", "Lectura Maya", "Significado ES / EN"])
        self.thompson_table.setColumnWidth(0, 80)
        self.thompson_table.setColumnWidth(1, 110)
        self.thompson_table.setColumnWidth(2, 130)
        self.thompson_table.setColumnWidth(3, 70)
        self.thompson_table.setColumnWidth(4, 105)
        self.thompson_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.thompson_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.thompson_table.cellClicked.connect(self._on_thompson_row_clicked)
        left_lay.addWidget(self.thompson_table)

        # Panel Derecho: Inspector Arqueológico, Morphing y Ensamblador Dinámico
        right_box = QFrame()
        right_box.setObjectName("CardFrame")
        right_lay = QVBoxLayout(right_box)
        right_lay.addWidget(QLabel("🏛️ INSPECTOR EPIGRÁFICO & MORPHING CEFALOMORFO:"))

        self.lex_detail_title = QLabel("Glifo: B'ALAM [T751]")
        self.lex_detail_title.setStyleSheet("color: #F59E0B; font-family: Consolas; font-size: 15px; font-weight: bold;")
        right_lay.addWidget(self.lex_detail_title)

        self.lex_mhd_lbl = QLabel("MHD 2N18 • /b'alam/ • Fauna Sagrada")
        self.lex_mhd_lbl.setStyleSheet("color: #10B981; font-family: Consolas; font-size: 11.5px;")
        right_lay.addWidget(self.lex_mhd_lbl)

        self.lexicon_canvas = SteleCanvasWidget()
        right_lay.addWidget(self.lexicon_canvas, stretch=1)

        # Control de Morphing Fourier
        morph_row = QHBoxLayout()
        morph_row.addWidget(QLabel("Morphing EFD:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(50)
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        morph_row.addWidget(self.morph_slider)
        right_lay.addLayout(morph_row)

        self.morph_lbl = QLabel("α = 0.50 (Híbrido morfológico balanceado)")
        self.morph_lbl.setStyleSheet("color: #38BDF8; font-family: Consolas; font-size: 11px;")
        right_lay.addWidget(self.morph_lbl)

        self.lex_desc_lbl = QLabel("Jaguar sagrado, guardián nocturno, sol que viaja por el inframundo.")
        self.lex_desc_lbl.setStyleSheet("color: #94A3B8; font-size: 11.5px; padding: 4px;")
        self.lex_desc_lbl.setWordWrap(True)
        right_lay.addWidget(self.lex_desc_lbl)

        # Herramienta de Inserción directa en el Taller del Escriba (Cartucho 2D)
        insert_box = QFrame()
        insert_box.setStyleSheet("background-color: #0E1626; border-radius: 6px; padding: 6px;")
        insert_lay = QVBoxLayout(insert_box)
        lbl_ins = QLabel("📥 ENSAMBLAR EN CARTUCHO 2D (TALLER DEL ESCRIBA):")
        lbl_ins.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 11px;")
        insert_lay.addWidget(lbl_ins)
        insert_row = QHBoxLayout()
        self.target_slot_combo = QComboBox()
        self.target_slot_combo.addItems([
            "Signo Principal (Centro)",
            "Superfijo (Arriba)",
            "Prefijo (Izquierda)",
            "Infijo (Incrustado)",
            "Subfijo (Abajo)",
            "Postfijo (Derecha)"
        ])
        insert_row.addWidget(self.target_slot_combo, stretch=2)
        btn_insert = QPushButton("Insertar en Cartucho ➔")
        btn_insert.clicked.connect(self._on_insert_into_workshop_clicked)
        insert_row.addWidget(btn_insert, stretch=2)
        insert_lay.addLayout(insert_row)
        right_lay.addWidget(insert_box)

        btn_export_logo_svg = QPushButton("💾 Exportar Glifo Thompson SVG")
        btn_export_logo_svg.clicked.connect(self._export_lexicon_svg)
        right_lay.addWidget(btn_export_logo_svg)

        split_lex = QSplitter(Qt.Horizontal)
        split_lex.addWidget(left_box)
        split_lex.addWidget(right_box)
        split_lex.setSizes([860, 500])
        lay.addWidget(split_lex)
        self.tabs.addTab(tab, "🏛️ Corpus Thompson (+860 Glifos) & Códice")

        # Cargar datos iniciales del Corpus
        self.current_filtered_entries: List[ThompsonGlyphEntry] = []
        self._populate_thompson_table()

    # ── SLOTS Y ACCIONES INTERACTIVAS ──
    def _on_preset_selected(self, idx: int):
        if idx <= 0:
            return
        preset_txt = self.preset_combo.currentText()
        self.input_text.setText(preset_txt)
        if "The divine" in preset_txt:
            self.lang_combo.setCurrentIndex(1)
        else:
            self.lang_combo.setCurrentIndex(0)
        self._run_translation()

    def _run_translation(self):
        txt = self.input_text.text().strip()
        lang = "es" if self.lang_combo.currentIndex() == 0 else "en"
        ortho = ["logosyllabic", "logographic", "syllabic"][self.ortho_combo.currentIndex()]
        style = ["obsidian", "codex", "heightmap"][self.style_combo.currentIndex()]

        prism = MayanLinguisticCompiler.translate_and_compile(txt, source_lang=lang, orthography_mode=ortho)
        self.current_prism = prism
        self.stele_canvas.set_blocks(prism.blocks, style=style, cols=2)

        # Formatear el reporte del Prisma Semántico de 4 Capas
        koto = prism.layer4_biocymatic_kototama
        html = [
            f"<h3 style='color:#F59E0B; margin-bottom:4px;'>📜 Transcripción Epigráfica (Orden VOS):</h3>",
            f"<p style='font-family:Consolas; font-size:14px; color:#34D399;'><b>{prism.epigraphic_transcription}</b><br>"
            f"<i>Lectura fonémica: \"{prism.phonemic_reading}\"</i></p>",
            f"<hr style='border:1px solid #1E293B;'>",
            f"<h4 style='color:#38BDF8;'>🔹 CAPA 1: Superficie Lineal (ES / EN)</h4>",
            f"<p><b>ES:</b> {prism.layer1_surface_es}<br><b>EN:</b> {prism.layer1_surface_en}</p>",
            f"<h4 style='color:#FCD34D;'>🔹 CAPA 2: Glosa Morfo-Topológica y Geometría Posicional</h4>",
            "<ul>" + "".join(f"<li>{m}</li>" for m in prism.layer2_morpho_topological) + "</ul>",
            f"<h4 style='color:#A78BFA;'>🔹 CAPA 3: Acorde de Resonancia Homofónica y Difrasismos (Tz'ak)</h4>",
            "<ul>" + "".join(f"<li>{h}</li>" for h in prism.layer3_harmonic_diphrasisms) + "</ul>",
            f"<h4 style='color:#10B981;'>🔹 CAPA 4: Vector Biocimático & Kototama</h4>",
            f"<p><b>Cadencia Vocálica:</b> <code>{koto['vowel_cadence']}</code><br>"
            f"<b>Kototama Dominante:</b> {koto['dominant_kototama']} ({koto['resonant_frequency_hz']} Hz) • {koto['elemental_polarity']}</p>"
        ]
        self.prism_output.setHtml("\n".join(html))

    def _update_custom_cartouche(self):
        def make_slot(combo: QComboBox, role: str) -> Optional[GlyphAffixSlot]:
            val = combo.currentText()
            if val == "(Ninguno)":
                return None
            is_logo = val.isupper()
            return GlyphAffixSlot(val, is_logo, "T000", role)

        main_s = make_slot(self.slot_main, "main") or GlyphAffixSlot("AJAW", True, "T533", "main")
        sup_s = make_slot(self.slot_sup, "superfix")
        pre_s = make_slot(self.slot_pre, "prefix")
        inf_s = make_slot(self.slot_inf, "infix")
        sub_s = make_slot(self.slot_sub, "subfix")
        post_s = make_slot(self.slot_post, "postfix")
        num_val = self.num_spin.value() if self.use_num_chk.isChecked() else None

        parts = []
        if num_val is not None:
            parts.append(str(num_val))
        if pre_s:
            parts.append(pre_s.code)
        if sup_s:
            parts.append(sup_s.code)
        core_str = f"{main_s.code}[{inf_s.code}]" if inf_s else main_s.code
        parts.append(core_str)
        if sub_s:
            parts.append(sub_s.code)
        if post_s:
            parts.append(post_s.code)

        formula = " - ".join(parts)
        blk = GlyphCartoucheBlock(
            coord="A1",
            main_sign=main_s,
            superfix=sup_s,
            prefix=pre_s,
            infix=inf_s,
            subfix=sub_s,
            postfix=post_s,
            numeral=num_val,
            epigraphic_translit=formula,
            phonemic_maya=formula.lower()
        )
        self.custom_formula_lbl.setText(f"Fórmula Topológica:  {formula}")
        
        info_lines = [
            f"Núcleo: {main_s.code} ({'Logograma' if main_s.is_logogram else 'Sílaba'})"
        ]
        if num_val is not None:
            info_lines.append(f"Coeficiente: {num_val}")
        if sup_s:
            info_lines.append(f"Superfijo: {sup_s.code}")
        if pre_s:
            info_lines.append(f"Prefijo: {pre_s.code}")
        if inf_s:
            info_lines.append(f"Infijo: {inf_s.code}")
        if sub_s:
            info_lines.append(f"Subfijo: {sub_s.code}")
        self.workshop_info_lbl.setText(" • ".join(info_lines))
        self.workshop_canvas.set_blocks([blk], style="obsidian", cols=1)

    def _on_syllable_cell_clicked(self, row: int, col: int):
        cons = MayanEpigraphyLexicon.CONSONANTS[row]
        v = MayanEpigraphyLexicon.VOWELS[col]
        syl = f"{cons}{v}"
        arch, t_code, desc = MayanEpigraphyLexicon.CONSONANT_GLYPH_ARCHETYPE[cons]
        v_info = MayanEpigraphyLexicon.VOWEL_KOTOTAMA.get(v, {"kototama": v, "freq_hz": 432.0, "element": "Luz"})
        v_name = v_info["kototama"]
        freq_hz = v_info["freq_hz"]
        el = v_info["element"]
        self.syllable_detail_lbl.setText(
            f"Sílaba: '{syl}' • Thompson: {t_code}.{col+1} • Radical: {arch}\n"
            f"Inflexión: {v.upper()} ({v_name}) • Frecuencia: {freq_hz} Hz ({el})"
        )
        self.syllable_koto_card.setText(
            f"Kototama: {v_name} | {freq_hz} Hz | Polaridad: {el} | Arquetipo: {desc[:40]}"
        )
        slot = GlyphAffixSlot(syl, False, f"{t_code}.{col+1}", "main")
        blk = GlyphCartoucheBlock(
            coord="A1",
            main_sign=slot,
            epigraphic_translit=syl,
            phonemic_maya=syl
        )
        if hasattr(self, "syllabary_canvas"):
            self.syllabary_canvas.set_blocks([blk], style="obsidian", cols=1)

    def _run_syllabifier(self):
        word = self.syl_word_input.text().strip() or "Pakal"
        mode = "synharmonic" if self.harmony_combo.currentIndex() == 0 else "disharmonic"
        res = MayanLinguisticCompiler.syllabify_word(word, vowel_harmony=mode)
        self.syl_result_lbl.setText(
            f"Entrada: '{word}'  ➔  Sílabas CV: [ {res['epigraphic_hyphenated']} ]  "
            f"➔  Thompson: {', '.join(s['thompson_id'] for s in res['slots'])}"
        )
        blocks = []
        for i, slot in enumerate(res["slots"]):
            b = GlyphCartoucheBlock(
                coord=f"A{i+1}",
                main_sign=GlyphAffixSlot(slot["syllable"], False, slot["thompson_id"], "main"),
                epigraphic_translit=slot["syllable"],
                phonemic_maya=slot["syllable"]
            )
            blocks.append(b)

        # Calcular frecuencia promedio Kototama
        vowels_in_word = [s["syllable"][-1] for s in res["slots"] if s["syllable"][-1] in MayanEpigraphyLexicon.VOWEL_KOTOTAMA]
        if vowels_in_word:
            freqs = [MayanEpigraphyLexicon.VOWEL_KOTOTAMA[v]["freq_hz"] for v in vowels_in_word]
            avg_freq = sum(freqs) / len(freqs)
            cadence = " - ".join(v.upper() for v in vowels_in_word)
            self.syllable_koto_card.setText(
                f"Resonancia Acústica: Cadencia [{cadence}] • Promedio: {avg_freq:.1f} Hz • {len(res['slots'])} Cartuchos CV"
            )

        if hasattr(self, "syllabary_canvas") and blocks:
            self.syllabary_canvas.set_blocks(blocks, style="obsidian", cols=min(3, max(1, len(blocks))))

    def _on_thompson_filter_changed(self):
        self._populate_thompson_table()

    def _populate_thompson_table(self):
        query = self.thompson_search_input.text().strip()
        cat = self.thompson_cat_combo.currentData() or "all"
        entries = MayanThompsonCatalog.search_corpus(query=query, category=cat)
        self.current_filtered_entries = entries

        total_all = 1066
        cat_name = self.thompson_cat_combo.currentText().split("(")[0].strip()
        self.thompson_status_lbl.setText(
            f"Mostrando {len(entries)} de {total_all} signos arqueológicos indexados • Filtro activo: {cat_name}"
        )

        self.thompson_table.setRowCount(len(entries))
        for row, e in enumerate(entries):
            cat_label = MayanThompsonCatalog.CATEGORIES.get(e.category, e.category).split("(")[0].strip()
            self.thompson_table.setItem(row, 0, QTableWidgetItem(e.t_number))
            self.thompson_table.setItem(row, 1, QTableWidgetItem(e.name))
            self.thompson_table.setItem(row, 2, QTableWidgetItem(cat_label))
            self.thompson_table.setItem(row, 3, QTableWidgetItem(e.mhd_code))
            self.thompson_table.setItem(row, 4, QTableWidgetItem(e.phonemic))
            self.thompson_table.setItem(row, 5, QTableWidgetItem(f"{e.es_meaning} / {e.en_meaning}"))

        if entries and self.thompson_table.currentRow() < 0:
            self.thompson_table.selectRow(0)
            self._display_thompson_entry(entries[0])

    def _on_thompson_row_clicked(self, row: int, _col: int):
        if row < 0 or row >= len(self.current_filtered_entries):
            return
        entry = self.current_filtered_entries[row]
        self._display_thompson_entry(entry)

    def _display_thompson_entry(self, entry: ThompsonGlyphEntry):
        self.current_inspected_entry = entry
        self.current_inspected_logogram = entry.name
        self.lex_detail_title.setText(f"Glifo: {entry.name} [{entry.t_number}]")
        cat_badge = MayanThompsonCatalog.CATEGORIES.get(entry.category, entry.category).split("(")[0].strip()
        self.lex_mhd_lbl.setText(f"MHD {entry.mhd_code} • /{entry.phonemic}/ • {cat_badge}")
        self.lex_desc_lbl.setText(f"{entry.es_meaning}\n\nNota Arqueológica: {entry.archaeological_note}")

        # Renderizar en el lienzo vectorial
        role = "superfix" if entry.category == "affix" else "main"
        slot = GlyphAffixSlot(entry.name, entry.is_logogram, entry.t_number, role)
        blk = GlyphCartoucheBlock(
            coord="A1",
            main_sign=slot,
            epigraphic_translit=entry.name,
            phonemic_maya=entry.phonemic
        )
        if hasattr(self, "lexicon_canvas"):
            self.lexicon_canvas.set_blocks([blk], style="obsidian", cols=1)

    def _on_insert_into_workshop_clicked(self):
        if not hasattr(self, "current_inspected_entry") or not self.current_inspected_entry:
            return
        entry = self.current_inspected_entry
        slot_idx = self.target_slot_combo.currentIndex()
        slot_combos = [
            self.slot_main,  # 0
            self.slot_sup,   # 1
            self.slot_pre,   # 2
            self.slot_inf,   # 3
            self.slot_sub,   # 4
            self.slot_post   # 5
        ]
        target_combo = slot_combos[slot_idx]
        val_to_insert = entry.name

        idx = target_combo.findText(val_to_insert)
        if idx < 0:
            target_combo.addItem(val_to_insert)
            idx = target_combo.count() - 1
        target_combo.setCurrentIndex(idx)

        self._update_custom_cartouche()
        self.tabs.setCurrentIndex(1)

    def _on_morph_slider_changed(self, val: int):
        alpha = val / 100.0
        interp = "Geométrica abstracta" if alpha <= 0.05 else "Cefalomorfa sagrada (cabeza)" if alpha >= 0.95 else "Híbrido armónico de Fourier"
        self.morph_lbl.setText(f"α = {alpha:.2f} ({interp})")
        entry = getattr(self, "current_inspected_entry", None)
        logo_k = entry.name if entry else getattr(self, "current_inspected_logogram", "B'ALAM")
        t_id = entry.t_number if entry else "T751"
        is_logo = entry.is_logogram if entry else True
        role = "superfix" if (entry and entry.category == "affix") else "main"
        slot = GlyphAffixSlot(logo_k, is_logo, t_id, role)
        blk = GlyphCartoucheBlock(
            coord="A1",
            main_sign=slot,
            epigraphic_translit=f"{logo_k} [α={alpha:.2f}]",
            phonemic_maya=entry.phonemic if entry else logo_k.lower()
        )
        if hasattr(self, "lexicon_canvas"):
            self.lexicon_canvas.set_blocks([blk], style="obsidian", cols=1)

    def _export_current_svg(self):
        if not self.current_prism:
            return
        style = ["obsidian", "codex", "heightmap"][self.style_combo.currentIndex()]
        svg_str = MayanCalligraphicEngine.render_stele_svg(self.current_prism, style=style, columns=2)
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Estela SVG", f"mayan_stele_{style}.svg", "SVG Files (*.svg)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg_str)

    def _export_current_markdown(self):
        if not self.current_prism:
            return
        md_str = MayanCalligraphicEngine.render_stele_markdown(self.current_prism)
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Informe Markdown", "mayan_stele_dossier.md", "Markdown Files (*.md)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(md_str)

    def _export_current_ascii(self):
        if not self.current_prism:
            return
        ascii_str = MayanCalligraphicEngine.render_stele_ascii(self.current_prism)
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Cartuchos ASCII", "mayan_stele_ascii.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(ascii_str)

    def _export_current_json(self):
        if not self.current_prism:
            return
        json_str = MayanCalligraphicEngine.render_stele_json(self.current_prism)
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Estela JSON", "mayan_stele_epigraphy.json", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)

    def _export_workshop_cartouche_svg(self):
        if not hasattr(self, "workshop_canvas") or not self.workshop_canvas.blocks:
            return
        blk = self.workshop_canvas.blocks[0]
        svg_str = MayanCalligraphicEngine.render_cartouche_block_svg(blk, 10, 10, size=260.0, style="obsidian")
        full_svg = f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="280" height="280">{svg_str}</svg>'
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Cartucho SVG", "mayan_cartouche_custom.svg", "SVG Files (*.svg)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(full_svg)

    def _export_syllable_svg(self):
        word = self.syl_word_input.text().strip() or "Pakal"
        mode = "synharmonic" if self.harmony_combo.currentIndex() == 0 else "disharmonic"
        res = MayanLinguisticCompiler.syllabify_word(word, vowel_harmony=mode)
        svg_parts = [render_syllable_svg(s["syllable"], size=160.0, theme="obsidian") for s in res["slots"]]
        full_svg = "\n<!-- SLIDE -->\n".join(svg_parts)
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Sílabas SVG", f"mayan_syllables_{word}.svg", "SVG Files (*.svg)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg_parts[0] if svg_parts else "")

    def _export_lexicon_svg(self):
        entry = getattr(self, "current_inspected_entry", None)
        t_id = entry.t_number if entry else "T751"
        svg_str = render_thompson_glyph_svg(t_id, size=240.0, theme="obsidian")
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Glifo Thompson SVG", f"mayan_glyph_{t_id}.svg", "SVG Files (*.svg)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg_str)


def launch_gui():
    if not PYSIDE6_AVAILABLE:
        print('PySide6 no est? disponible.')
        return
    app = QApplication.instance() or QApplication(sys.argv)
    win = MayanLangWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    launch_gui()
