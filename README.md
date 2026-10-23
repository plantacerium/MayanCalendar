

# Mayan Stele - Ultimate Calendar, Fractal Pattern Analyzer & MCP Server

A comprehensive, mathematically rigorous Mayan calendar application and **Model Context Protocol (MCP)** server built with Python and PySide6. Convert any Gregorian date to its exact Mayan equivalent, compute Kuramoto phase synchronization across planetary cycles, detect Dresden Codex eclipse windows, explore biocymatic/genetic resonances, and empower AI agents to interact with ancient mesoamerican chronometry.

<p align="center">
  <img src="./assets/screenshots/tab0_calendar.png" alt="Mayan Stele - Calendario, Estela & Ruedas Interlocking" width="100%" />
</p>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52?logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![MCP Protocol](https://img.shields.io/badge/MCP-JSON--RPC%202.0-8A2BE2)](https://modelcontextprotocol.io)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./LICENSE)

---

## Logo
<p align="center">
  <img src="./assets/logo_fusion_quantum_pyramid_calendar.svg" alt="Mayan Stele - Quantum Pyramid & Calendar Core" width="2032" />
</p>

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Model Context Protocol (MCP) Server for AI Agents](#model-context-protocol-mcp-server-for-ai-agents)
   - [Why MCP for Mayan Epigraphy?](#why-mcp-for-mayan-epigraphy)
   - [Client Setup (Antigravity IDE, Cursor, Claude Desktop)](#client-setup)
   - [Available MCP Tools Reference](#available-mcp-tools-reference)
   - [Example Agent Queries & Responses](#example-agent-queries--responses)
3. [Advanced Chronometry & Astronomical Engines](#advanced-chronometry--astronomical-engines)
   - [Kuramoto Coupled Oscillators Synchronization ($R, \Psi$)](#kuramoto-coupled-oscillators-synchronization)
   - [Dresden Codex Eclipse Warning Engine](#dresden-codex-eclipse-warning-engine)
   - [Dresden Codex Mars Table & The Celestial Beast (pp. 43b–45b)](#dresden-codex-mars-table--the-celestial-beast-pp-43b45b)
   - [Deep Time Eras (up to Alautun)](#deep-time-eras)
   - [Correlation Constants](#correlation-constants)
4. [Desktop GUI Application (`mayan-stele.py`)](#desktop-gui-application)
   - [Astronomical Calendar & Rotating Wheel](#astronomical-calendar--rotating-wheel)
   - [Fractal Pattern Analyzer & Soliton Wave Packets](#fractal-pattern-analyzer--soliton-wave-packets)
   - [⏳ Operaciones & Retornos (Distance Numbers & CRT)](#operaciones--retornos)
   - [🧬 Resonancia Biológica (Amino Acids, Codons & Kototama)](#resonancia-biológica)
   - [Encyclopedia & Basalt/Obsidian Styling](#encyclopedia--styling)
5. [Multi-Format Profile Exporter (`mayan_exporter.py`)](#multi-format-profile-exporter)
6. [Installation & Quickstart](#installation--quickstart)
7. [License & Acknowledgments](#license--acknowledgments)

---

## Architectural Overview

The repository consists of four core modular engines working seamlessly together:

```mermaid
graph TD
    A["MayanConverter (mayan-stele.py)"] --> B["FractalPatternAnalyzer (mayan-stele.py)"]
    A --> D["Operaciones & Distance Numbers (mayan-stele.py)"]
    A --> E["Resonancia Biológica & Kototama (resonaxers.py)"]
    B --> F["Kuramoto Dynamical Sync (R, Psi)"]
    B --> G["Dresden Codex 11,960d Eclipse Engine"]
    A --> H["MayanProfileExporter (mayan_exporter.py)"]
    B --> H
    E --> H
    A --> C["MCP Server stdio JSON-RPC 2.0 (mayan_mcp_server.py)"]
    B --> C
    D --> C
    E --> C
    H --> C
    C --> I["AI Agents (Antigravity IDE, Cursor, Claude, LLMs)"]
    A --> J["Desktop GUI (PySide6 Obsidian / Jade)"]
    B --> J
    D --> J
    E --> J
```

---

## Model Context Protocol (MCP) Server for AI Agents

The **Mayan Stele MCP Server** (`mayan_mcp_server.py`) implements the official **Model Context Protocol (MCP)** specification via standard input/output (`stdio`) using JSON-RPC 2.0. 

### Why MCP for Mayan Epigraphy?
Large Language Models frequently struggle with non-linear calendar arithmetic, modular residue calculations, and non-congruent orbital periods. The MCP server bridges LLMs directly to verified algorithmic engines:
- **Zero Shot**: Precise integer mathematics for Long Counts, Tzolk'in day signs, and Haab' dates.
- **Continuous Cosmic Coherence**: Computes the complex Kuramoto order parameter $R e^{i\Psi}$ and Dresden nodal eclipse warnings for any epoch.
- **Biomolecular Mapping**: Cross-references Tzolk'in solar seals with genetic codons, amino acids, and Kototama sound matrices.
- **Multiformat Generation**: Direct programmatic export to SVG, Markdown, ASCII, and JSON.

### Client Setup

#### 1. Google Antigravity IDE
Add the server configuration to your MCP settings or plugin directory:
```json
{
  "mcpServers": {
    "mayan-calendar": {
      "command": "python",
      "args": [
        "g:/GitHub/MayanCalendar-main/MayanCalendar-main/mayan_mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### 2. Cursor IDE (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "mayan-calendar": {
      "command": "python",
      "args": [
        "mayan_mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### 3. Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "mayan-calendar": {
      "command": "python",
      "args": [
        "g:\\GitHub\\MayanCalendar-main\\MayanCalendar-main\\mayan_mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

> **Note for Windows Users**: The server automatically forces UTF-8 encoding across `stdin`, `stdout`, and `stderr`, preventing character corruption with glyph symbols or mathematical markers.

---

### Available MCP Tools Reference

The server exposes **13 specialized tools**:

| Tool Name | Purpose | Key Arguments |
|-----------|---------|---------------|
| `mayan_convert_gregorian` | Gregorian date $\to$ complete Mayan calendar system | `year`, `month`, `day`, `correlation` |
| `mayan_convert_long_count` | Long Count (Baktun..Kin) $\to$ Gregorian date | `baktun`, `katun`, `tun`, `uinal`, `kin`, `correlation` |
| `mayan_add_distance_number` | Epigraphic Distance Number chronological vector addition | `base_year`, `base_month`, `base_day`, `direction`, `katun`, `tun`, `uinal`, `kin` |
| `mayan_calculate_resonance` | Harmonic score ($0-100\%$), Kuramoto order parameter ($R, \Psi$), Dresden eclipse alert | `year`, `month`, `day`, `natal_year`, `natal_month`, `natal_day`, `selected_cycles` |
| `mayan_find_convergences` | Range scanner detecting wave packets, solitons ($>60\%$) & harmonic bridges | `start_year`, `start_month`, `start_day`, `total_days`, `min_score`, `natal_year` |
| `mayan_exact_cycle_returns` | Chinese Remainder Theorem (CRT) modular solver for multi-cycle returns | `start_year`, `cycle1_name`, `cycle1_target`, `cycle2_name`, `cycle2_target` |
| `mayan_project_pattern` | Projects cyclic harmonic steps forward or backward | `base_year`, `base_month`, `base_day`, `interval_days`, `count` |
| `mayan_get_biomolecular_profile` | Maps Tzolk'in solar seal to amino acids, RNA codons & Kototama | `tzolkin_sign` (e.g. `Ahau`, `Imix`, `Cauac`) |
| `mayan_get_paris_zodiac` | Paris Codex (pp. 21-24) 13 Maya Ecliptic Constellations (Meeus solar algorithm) | `year`, `month`, `day` (optional: omit for full catalog) |
| `mayan_resolve_serpent_series` | Dresden Codex (pp. 61–69) Serpent Series & Ring Numbers Deep Time calculator (~33,000 yrs) | `serpent_index` (0–4) or `ring_days` + `serpent_distance_days`, `correlation` |
| `mayan_get_364_day_season` | Dresden Codex (pp. 65a–69b) 364-Day Seasonal Year & 4 Cardinal Quarters (Chac deities, 91d stations, 1,820d cycle) | `year`, `month`, `day`, `correlation` |
| `mayan_get_mars_table` | Dresden Codex (pp. 43b–45b) 780-day Mars Synodic Table & Celestial Beast Retrograde Loop (10x78d stations, 9,360d & 56,940d macro-cycles) | `year`, `month`, `day`, `correlation` |
| `mayan_export_profile` | Generates full profile in SVG, Markdown, ASCII, or JSON format | `year`, `month`, `day`, `format`, `correlation` |

---

### Example Agent Queries & Responses

#### Query: `mayan_calculate_resonance` for March 11, 2032
```json
{
  "name": "mayan_calculate_resonance",
  "arguments": {
    "year": 2032,
    "month": 3,
    "day": 11
  }
}
```
**Response Payload**:
```json
{
  "date": "2032-03-11",
  "long_count": "13.0.19.9.0",
  "tzolkin": "4 Ahau",
  "haab": "8 Cumku",
  "harmonic_score_percent": 78.3,
  "kuramoto_order_parameter": {
    "R_coherence_percent": 57.6,
    "psi_phase_deg": 35.8,
    "state": "Coherente (Phase-locked)"
  },
  "dresden_eclipse": {
    "active": true,
    "type": "Solar (Luna Nueva)",
    "days_to_node": 1.2,
    "window_description": "Ventana de Eclipse Dresden activa (Alerta Solar / Nodo cercano)"
  },
  "active_alignments": [
    "Tzolkin",
    "Haab",
    "Tun",
    "Venus",
    "Calendar Round",
    "Dresden Solar (Luna Nueva)"
  ]
}
```

#### Query: `mayan_get_biomolecular_profile` for "Ahau"
```json
{
  "name": "mayan_get_biomolecular_profile",
  "arguments": {
    "tzolkin_sign": "Ahau"
  }
}
```
**Response Payload**:
```json
{
  "sign": "Ahau",
  "kiche_name": "Junajpu",
  "meaning": "Sol, Iluminación, Maestría Universal",
  "amino_acid": "Triptófano (Trp / W)",
  "codons": ["UGG"],
  "polarity": "Apolar aromático hidrófobo",
  "biological_role": "Precursor de serotonina y melatonina, antena electromagnética",
  "kototama_vowel": "A",
  "kototama_consonant": "WA",
  "bija_mantra": "OM / RAM",
  "element": "Fuego / Luz Solar"
}
```

---

## Advanced Chronometry & Astronomical Engines

### Kuramoto Coupled Oscillators Synchronization

In addition to traditional modular returns (Day 0), the engine models the solar system and Mesoamerican cycles as a network of **$N=8$ coupled non-linear phase oscillators** governed by the Kuramoto order parameter:

$$r e^{i\psi} = \frac{1}{N} \sum_{j=1}^{N} e^{i \theta_j(t)}$$

Where:
- $\theta_j(t) = 2\pi \frac{(t - t_{0,j}) \pmod{T_j}}{T_j}$ is the instantaneous phase of cycle $j$.
- $R = |r| \in [0, 1]$ measures the **macroscopic phase coherence** ($0\%$ = complete dispersion, $100\%$ = perfect phase alignment).
- $\Psi \in [0, 360^\circ)$ represents the **collective cosmic phase angle**.

Coupled cycles include:
1. **Tzolk'in** ($260$ days)
2. **Haab'** ($365$ days)
3. **Tún** ($360$ days)
4. **Venus Synodic Period** ($584$ days)
5. **K'awiil Sacred Quadripartite Cycle** ($819$ days)
6. **Lunar Synodic Period** ($29.530588$ days)
7. **Draconic Eclipse Half-Year** ($173.31$ days)
8. **Dresden Great Eclipse Cycle** ($11,960$ days)

When $R > 50\%$, the cycles enter constructive resonance, forming **Soliton wave packets** in the time continuum.

---

### Dresden Codex Eclipse Warning Engine

Based on pages 51–58 of the **Dresden Codex**, the Maya tracked eclipses using a master cycle of **11,960 days** ($405$ lunations $= 46$ Tzolk'in $\approx 32.7$ tropical years). 

The engine evaluates syzygies against the lunar node passages:
- **Eclipse Node Period**: $T_{\text{node}} = 173.31$ days (the Draconic half-year).
- **Node Distance**: $\Delta t_{\text{node}} = \min(t \pmod{173.31}, 173.31 - (t \pmod{173.31}))$.
- If $\Delta t_{\text{node}} \le 15.0$ days, the date falls within an astronomical eclipse corridor:
  - **Solar Eclipse Warning**: If Moon Phase is near New Moon ($0^\circ \pm 30^\circ$ or $330^\circ-360^\circ$).
  - **Lunar Eclipse Warning**: If Moon Phase is near Full Moon ($180^\circ \pm 30^\circ$).

---

### Dresden Codex Mars Table & The Celestial Beast (pp. 43b–45b)

Pages 43b–45b of the **Dresden Codex** preserve the famous Maya synodic table of **Mars**, structured around a precise cycle of **780 days** ($3 \times 260\text{d}$ Tzolk'in):

- **Canonical Epigraphic Anchor**: Anchored to `9.19.7.15.8 3 Lamat` (Day 1,435,628 from 0.0.0.0.0).
- **Invariable Sacred Coefficient 3**: The 780-day cycle is divided into **10 stations of 78 days** ($6 \times 13$ trecenas). Because $78 \equiv 0 \pmod{13}$, the tonal numeral **3** never changes across the entire table:
  1. **3 Lamat** (Day 0 / 780d) — *Morning Heliacal Rising* (Act I)
  2. **3 Cimi** (Day 78 / 780d) — *Prograde Advance 1* (Act I)
  3. **3 Kan** (Day 156 / 780d) — *Prograde Advance 2* (Act I)
  4. **3 Ik** (Day 234 / 780d) — *Pre-Stationary Deceleration* (Act I)
  5. **3 Ahau** (Day 312 / 780d) — *1st Stationary Point: Entrance to Retrograde Loop* (Act II)
  6. **3 Etznab** (Day 390 / 780d) — *Solar Opposition & Retrograde Apex: The Celestial Beast* (Act II)
  7. **3 Cib** (Day 468 / 780d) — *2nd Stationary Point: Resumption of Direct Motion* (Act II)
  8. **3 Ix** (Day 546 / 780d) — *Evening Sky Advance* (Act III)
  9. **3 Eb** (Day 624 / 780d) — *Heliacal Setting & Solar Twilight Approach* (Act III)
  10. **3 Oc** (Day 702 / 780d) — *Solar Conjunction: Underworld Passage* (Act III)
- **The Celestial Beast Loop**: In Act II (days 312 to 468, centered on solar opposition at day 390 in 3 Etznab), Mars exhibits apparent retrograde motion. The Dresden scribes illustrated this terrifying sky phenomenon as a **Celestial Beast** (Mars Beast) hanging from the skyband with wide open jaws.
- **Cosmic Commensurabilities**:
  - **Super-Tun of 9,360 Days**: $12 \times 780\text{d} = 9,360\text{d} = 26\text{ Tuns} = 36\text{ Tzolk'in}$.
  - **Grand Return of 56,940 Days**: $73 \times 780\text{d} = 56,940\text{d} = 156\text{ Haab'} = 3\text{ Calendar Rounds}$ (exact solar-Martian-Tzolk'in synchronization).

---

### Deep Time Eras

The Maya Long Count extends far beyond the 13 Baktun creation era:

| Unit | Factor | Exact Days | Gregorian Span |
|------|--------|------------|----------------|
| **K'in** | 1 | 1 | 1 Day |
| **Uinal** | 20 K'in | 20 | 20 Days |
| **Tún** | 18 Uinal | 360 | ~0.986 Years |
| **Katún** | 20 Tún | 7,200 | ~19.71 Years |
| **Baktún** | 20 Katún | 144,000 | ~394.26 Years |
| **Piktún** | 20 Baktún | 2,880,000 | ~7,885 Years |
| **Kalabtún** | 20 Piktún | 57,600,000 | ~157,704 Years |
| **K'inchiltún** | 20 Kalabtún | 1,152,000,000 | ~3,154,079 Years |
| **Alautún** | 20 K'inchiltún | 23,040,000,000 | ~63,081,588 Years |

---

### Correlation Constants

Users and agents can switch instantly between recognized correlation constants:
- **GMT (584283)**: Standard archaeological consensus (Goodman-Martínez-Thompson).
- **GMT+2 (584285)**: Astronomical correlation aligning historical eclipses and radiocarbon dates.
- **Spinden (489384)**: Early 20th-century correlation (13.0.0.0.0 = 3373 BCE).

---

## Desktop GUI Application

Built with **PySide6** and styled with an authentic stone-carved, basalt obsidian, jade, and gold visual theme.

```
┌────────────────────────────────────────────────────────────────────────┐
│  MAYAN STELE - COSMIC CHRONOMETRY & FRACTAL ANALYZER                   │
├────────────────────────────────────────────────────────────────────────┤
│  [📅 Calendario & Estela]  [🌀 Analizador Fractal]                     │
│  [⏳ Operaciones & Retornos] [🧬 Resonancia Biológica] [📚 Enciclopedia]│
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Calendario & Estela

<p align="center">
  <img src="./assets/screenshots/tab0_calendar.png" alt="Mayan Stele - Calendario, Estela & Ruedas Interlocking" width="100%" />
</p>

- **Universal Historical Date Selector**: Completely removes the classic Qt year 100 limit (`QDateEdit` limitation). Custom `HistoricalDateSelector` and `ChronoDate` engine support proleptic Gregorian calculation across $-99,999$ BCE to $+99,999$ CE with dedicated **"🏛️ 3114 a.C. Creación"** instant jump (13.0.0.0.0 4 Ahau 8 Cumku) and bidirectional day-by-day navigation.
- **Interactive Rotary Wheel**: Concentric rings for the Paris Codex Zodiac (13 Ecliptic Constellations), Haab' civil months (19), Tzolk'in sacred days (20), and Lords of the Night (9).
- **Paris Codex Ecliptic Zodiac Panel**: Real-time astronomical calculation (Jean Meeus algorithm) of the apparent solar longitude $\lambda_{\odot}$ mapping the Sun's transit across the 13 indigenous Maya constellations (*Códice de París*, pp. 21-24: Tzab, Ak, K'ek'en, Chuen, Koh, K'uk'ul, Chitam, Zina'an, Balam, Sotz', Muan, Pez, Xoc).
- **364-Day Seasonal Computing Year Panel (Dresden pp. 65a-69b)**: Dedicated StonePanel and embedded `Season364Bar` tracking the 4 Cardinal Quarters ($4 \times 91 = 364\text{d}$) and 7 trecenas per quarter ($7 \times 13 = 91\text{d}$), directional Chac deities, and the 1,820-day Grand Return ($5 \times 364 = 7 \times 260\text{d}$).
- **Mars Table & Celestial Beast Panel (Dresden pp. 43b-45b)**: Dedicated StonePanel and custom visual `MarsPhaseBar` displaying the 780-day synodic cycle, active station of 78 days (with immutable sacred coefficient 3), Tzolk'in acts (1 to 3), Celestial Beast retrograde indicators, solar opposition windows, and the 9,360-day Super-Tun commensurability.
- **Glyph Cartouches**: Vectorized iconography for Day Signs and Glyphs A, C, X.
- **Live Clock & Deep Time Counter**: Real-time ticking odometer displaying cosmic coordinates.

### 2. Analizador Fractal

<p align="center">
  <img src="./assets/screenshots/tab1_fractal.png" alt="Mayan Stele - Analizador Fractal & Dinámica Kuramoto" width="100%" />
</p>

- **Continuous Kuramoto Gauge**: Visual indicator showing collective phase coherence $R$ and angle $\Psi$.
- **Dresden Codex Warning Banner**: Highlights active solar/lunar eclipse corridors.
- **Wave Packet & Soliton Table**: Identifies multi-day convergence clusters where multiple sacred periods coincide across deep history.
- **Personal Natal Resonance**: Computes individualized alignment scores with personal birth matrices.

### 3. ⏳ Operaciones & Retornos

<p align="center">
  <img src="./assets/screenshots/tab2_operations.png" alt="Mayan Stele - Operaciones & Retornos (Vista Superior)" width="100%" />
</p>

- **Distance Numbers**: Add or subtract historical vectors ($k$ Katún, $t$ Tún, $u$ Uinal, $k$ K'in) to any epoch with full BCE/CE support.
- **CRT Exact Cycle Solver**: Solves simultaneous modular congruences using the Chinese Remainder Theorem:
  - *Calendar Round Return* (Tzolk'in + Haab' = 18,980 days / ~52 years)
  - *Venus Great Cycle* (Tzolk'in + Venus = 37,960 days / ~104 years)
  - *Tzolk'in-Tún Grand Conjunction* (260 + 360 = 93,600 days / 260 Tún)
- **Harmonic Pattern Projector**: Projects forward/backward steps over arbitrary cycle frequencies into deep time.
- **Cuentas Serpentinas y Números de Anillo (Dresden Codex pp. 61–69)**: Explores Deep Time chronology (~12.3 to 12.5 million days / >33,000 years) using Ring Numbers tied with red ribbons to subtract intervals prior to the Creation date 13.0.0.0.0 4 Ahau 8 Cumku (3114 BCE) into primordial chaos, then projecting forward to historical arrival dates. Includes one-click stele synchronizers for both Primordial Base Dates and Terminal Arrival Dates.
- **Cómputo de 364 Días y Estaciones Cósmicas (Dresden Codex pp. 65a–69b)**: Solves the exact next seasonal transitions (Equinoccio de Primavera, Solsticio de Verano, Equinoccio de Otoño, Solsticio de Invierno) and the 1,820-day Grand Return alignment with Tzolk'in, featuring 1-click synchronization to the main calendar stele.
- **La Tabla de Marte y la Bestia Celeste (Dresden Codex pp. 43b–45b)**: Interactive section computing next station jumps for all 10 canonical stations of 78 days (3 Lamat, 3 Cimi, 3 Kan, 3 Ik, 3 Ahau, 3 Etznab, 3 Cib, 3 Ix, 3 Eb, 3 Oc), the 9,360-day Super-Tun ($12\text{ Marte} = 26\text{ Tuns} = 36\text{ Tzolk'in}$), and the 56,940-day Grand Return ($73\text{ Marte} = 156\text{ Haab'} = 3\text{ Ruedas Calendáricas}$) with direct 1-click stele alignment.

<p align="center">
  <img src="./assets/screenshots/tab2_operations_mars.png" alt="Mayan Stele - Operaciones & Retornos (Cómputo 364d y Tabla de Marte)" width="100%" />
</p>

### 4. 🧬 Resonancia Biológica

<p align="center">
  <img src="./assets/screenshots/tab3_biological.png" alt="Mayan Stele - Resonancia Biológica & Genética" width="100%" />
</p>

- **20 Solar Seals $\to$ 20 Amino Acids**: Symmetrical mapping grounded in molecular charge, hydropathy, and aromaticity.
- **RNA Genetic Triplets**: Direct codon assignments for every Tzolk'in sign.
- **Kototama Phonetics & Bīja Mantras**: Traditional vocalic frequencies associated with daily vibrational archetypes.

### 5. 📚 Enciclopedia & Basalt Obsidian Styling

<p align="center">
  <img src="./assets/screenshots/tab4_reference.png" alt="Mayan Stele - Enciclopedia & Referencia Epigráfica" width="100%" />
</p>
- Comprehensive scholarly reference for all 13 Galactic Tones, 9 Underworld Lords, Venus Helical Risings, and Lunar Patrons.
- **Quantum Insignia & Showcase**: Features the official *Quantum Pyramid & Calendar Core* vector emblem integrated into the application header, window icon, and reference codex. Explore all 5 design variants in [`assets/logos/showcase.html`](./assets/logos/showcase.html).
- Seamless Dark Obsidian and Basque Gold CSS palettes without white artifact bleeds.

---

## Multi-Format Profile Exporter (`mayan_exporter.py`)

Generate full chronological and epigraphic dossiers directly from the GUI or via the MCP server:

- **SVG Vector Stele (`.svg`)**: Hieroglyphic stone slab illustration containing Long Count glyphs, Tzolk'in/Haab' cartouches, Kuramoto synchronization wheel, and biocymatic glyphs.
- **Markdown Dossier (`.md`)**: Comprehensive research report with mathematical tables, alignments, and biological correspondences.
- **ASCII Monument (`.txt`)**: Terminal-rendered ancient monument banner suitable for text consoles.
- **JSON Payload (`.json`)**: Full structured machine-readable document for pipelines and LLM ingestion.

---

## Installation & Quickstart

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Setup
```bash
# Clone repository
git clone https://github.com/plantacerium/MayanCalendar.git
cd MayanCalendar

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install PySide6
```

### Launch the GUI
```bash
python mayan-stele.py
```

### Run the MCP Server Standalone
```bash
python mayan_mcp_server.py
```

---

## Historical & Significant Dates to Explore

| Gregorian Date | Long Count | Tzolk'in | Haab' | Cosmic Context |
|----------------|------------|----------|-------|----------------|
| **Aug 11, 3114 BCE** | 0.0.0.0.0 | 4 Ahau | 8 Cumku | Maya Creation Epoch |
| **Dec 21, 2012** | 13.0.0.0.0 | 4 Ahau | 3 Kankin | Completion of the 13th Baktún |
| **Dec 01, 0940** | 10.5.12.6.0 | 4 Ahau | 8 Cumku | Peak Wave Packet W13 (80.0% Harmonic Score) |
| **Mar 11, 2032** | 13.0.19.9.0 | 4 Ahau | 8 Cumku | Soliton W72, $R=57.6\%$, Dresden Solar Eclipse Window |
| **Jan 02, 2045** | 13.1.12.9.0 | 4 Ahau | 8 Cumku | Soliton W3, Dresden Lunar Eclipse Window |

---

## License & Citation

Distributed under the **GPL V3 License**. See [`LICENSE`](./LICENSE) for full details.

If you use this software or the MCP server in your research, computational chronometry, or agentic systems, please cite:

```bibtex
@software{mayan_stele_mcp_2026,
  author = {Plantacerium and Contributors},
  title = {Mayan Stele: Ultimate Calendar, Fractal Pattern Analyzer & MCP Server},
  year = {2026},
  url = {https://github.com/plantacerium/MayanCalendar}
}
```

---

*"Time is not an arrow, but a symphony of concentric spirals resonating across deep space."*
