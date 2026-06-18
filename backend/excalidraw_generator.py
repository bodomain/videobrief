"""Generiert EINE grosse Excalidraw-Canvas im Karpathy-Stil.

Alles auf einer Flaeche, Sektionen raeumlich angeordnet,
mit Pfeilen verbunden. Karpathy wandert dra rum.

Layout (auf grosser Canvas):
  +--------------------------+  +------------------------+
  |  [TITEL]                  |  |                        |
  |  Kernaussage              |  |  Charts                |
  |  [box]                    |->|  [box]                 |
  |                           |  |                        |
  |  Timeline                 |  |  Argumentation         |
  |  [1][2][3]...            |->|  [box]                 |
  |  [4][5]...               |  |                        |
  +--------------------------+  +------------------------+
                                 |  Offene Fragen         |
                                 |  [?][?]               |
                                 +------------------------+
                                          |
                                     [Fragen?]
"""

import json
import re
import random
from pathlib import Path

# --- Farben ---
COLOR_STROKE = "#1e1e1e"
COLOR_ACCENT = "#4263eb"
COLOR_TEXT = "#1e1e1e"
COLOR_BG = "transparent"
COLOR_HIGHLIGHT_BG = "#dbe4ff"
COLOR_DIM = "#868e96"
COLOR_GREEN = "#2b8a3e"

# --- Canvas ---
COL_W = 2200          # Spaltenbreite
GAP = 200             # Spalten-Abstand
SECTION_GAP = 100     # Vertikaler Abstand zwischen Sektionen
MARGIN = 120          # Aussenrand
CANVAS_W = COL_W * 2 + GAP + MARGIN * 2
CANVAS_H = 4200       # Gross genug fuer alles


def _uid() -> str:
    return f"el_{random.randint(10**10, 10**11 - 1)}"


def _text(text: str, x: int, y: int, font_size: int = 20,
          stroke: str = COLOR_TEXT, bold: bool = False,
          align: str = "left", width: int = 0) -> dict:
    lines = text.split("\n")
    if width == 0:
        width = max(int(max(len(l) for l in lines) * font_size * 0.62), 100)
    height = int(len(lines) * font_size * 1.3)
    return {
        "id": _uid(), "type": "text",
        "x": x, "y": y, "width": width, "height": height,
        "angle": 0,
        "strokeColor": stroke, "backgroundColor": COLOR_BG,
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100,
        "groupIds": [], "frameId": None, "index": None, "roundness": None,
        "seed": random.randint(1, 10**9), "version": 1,
        "versionNonce": random.randint(1, 10**9), "isDeleted": False,
        "boundElements": [], "updated": 1, "link": None, "locked": False,
        "text": text, "fontSize": font_size, "fontFamily": 1,
        "textAlign": align, "verticalAlign": "top",
        "containerId": None, "originalText": text,
        "autoResize": True, "lineHeight": 1.25,
    }


def _rect(x: int, y: int, w: int, h: int,
          stroke: str = COLOR_STROKE, bg: str = COLOR_BG,
          fill: str = "solid", stroke_w: int = 2) -> dict:
    return {
        "id": _uid(), "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": fill, "strokeWidth": stroke_w, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100,
        "groupIds": [], "frameId": None, "index": None,
        "roundness": {"type": 3},
        "seed": random.randint(1, 10**9), "version": 1,
        "versionNonce": random.randint(1, 10**9), "isDeleted": False,
        "boundElements": [], "updated": 1, "link": None, "locked": False,
    }


def _arrow(x1: int, y1: int, x2: int, y2: int,
           stroke: str = COLOR_DIM, width: int = 2) -> dict:
    return {
        "id": _uid(), "type": "arrow",
        "x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1,
        "angle": 0,
        "strokeColor": stroke, "backgroundColor": COLOR_BG,
        "fillStyle": "solid", "strokeWidth": width, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100,
        "groupIds": [], "frameId": None, "index": None,
        "roundness": {"type": 2},
        "seed": random.randint(1, 10**9), "version": 1,
        "versionNonce": random.randint(1, 10**9), "isDeleted": False,
        "boundElements": [], "updated": 1, "link": None, "locked": False,
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": "arrow",
        "elbowed": False,
    }


def _section_label(text: str, x: int, y: int) -> list:
    """Kleine Sektions-Ueberschrift mit Akzent-Linie."""
    elems = []
    elems.append(_text(text, x, y, font_size=28, stroke=COLOR_ACCENT, bold=True))
    elems.append(_rect(x, y + 40, 60, 3,
                       stroke=COLOR_ACCENT, bg=COLOR_ACCENT, fill="solid"))
    return elems


def _wrap_text(text: str, max_chars: int) -> list:
    """Text in Zeilen umbrechen."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        if current and len(current) + len(w) + 1 > max_chars:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}" if current else w
    if current:
        lines.append(current)
    return lines


def layout_title(title: str, source_url: str, cx: int, cy: int) -> tuple:
    """Titel-Bereich oben links."""
    elems = []
    # Akzent-Balken
    elems.append(_rect(cx, cy, COL_W, 6,
                       stroke=COLOR_ACCENT, bg=COLOR_ACCENT, fill="solid"))
    # Titel (mehrzeilig wenn noetig)
    lines = _wrap_text(title, 50)
    y = cy + 40
    for line in lines[:2]:
        elems.append(_text(line, cx, y, font_size=42, stroke=COLOR_TEXT, bold=True,
                           width=COL_W, align="left"))
        y += 55
    # URL
    if source_url:
        elems.append(_text(source_url, cx, y + 10, font_size=14, stroke=COLOR_DIM))
        y += 30
    # Trennlinie
    elems.append(_rect(cx, y + 20, COL_W, 2,
                       stroke=COLOR_DIM, bg=COLOR_DIM, fill="solid"))
    return elems, y + 60  # elems + naechste Y-Position


def layout_kernaussage(summary: str, cx: int, cy: int) -> tuple:
    """Kernaussage-Box."""
    elems = []
    elems.extend(_section_label("Kernaussage", cx, cy))
    cy += 60
    box_h = 280
    elems.append(_rect(cx, cy, COL_W, box_h,
                       stroke=COLOR_STROKE, bg=COLOR_HIGHLIGHT_BG, fill="solid"))
    lines = _wrap_text(summary, 65)
    ty = cy + 20
    for line in lines[:8]:
        elems.append(_text(line, cx + 25, ty, font_size=18, stroke=COLOR_TEXT,
                           width=COL_W - 50))
        ty += 28
    return elems, cy + box_h


def layout_timeline(points: list, cx: int, cy: int) -> tuple:
    """Timeline als nummerierte Boxen in 2 Spalten."""
    elems = []
    elems.extend(_section_label("Timeline", cx, cy))
    cy += 60

    col_w = (COL_W - 60) # 2
    box_h = 100
    gap = 20

    for i, point in enumerate(points):
        col, row = i % 2, i # 2
        x = cx + col * (col_w + 60)
        y = cy + row * (box_h + gap)

        # Box
        elems.append(_rect(x, y, col_w, box_h,
                           stroke=COLOR_STROKE, bg=COLOR_BG))
        # Nummer-Badge
        elems.append(_rect(x + 8, y + 8, 36, 36,
                           stroke=COLOR_ACCENT, bg=COLOR_ACCENT, fill="solid"))
        elems.append(_text(str(i + 1), x + 12, y + 12,
                           font_size=18, stroke="#ffffff", bold=True,
                           align="center", width=28))

        # Text (Bold extrahieren)
        display = point
        m = re.match(r'\*\*(.+?)\*\*(.*)', point)
        if m:
            bold_part, rest = m.group(1), m.group(2).strip()
            display = f"{bold_part}\n{rest}" if rest else bold_part
        lines = _wrap_text(display, 30)
        ty = y + 12
        for line in lines[:4]:
            elems.append(_text(line, x + 52, ty, font_size=15, stroke=COLOR_TEXT,
                               width=col_w - 60))
            ty += 22

    rows = (len(points) + 1) # 2
    return elems, cy + rows * (box_h + gap)


def layout_charts(descriptions: list, cx: int, cy: int) -> tuple:
    """Charts-Bereich."""
    elems = []
    elems.extend(_section_label("Charts & Visualisierungen", cx, cy))
    cy += 60

    for i, desc in enumerate(descriptions):
        row_h = 70
        y = cy + i * (row_h + 12)
        # Frame-Badge
        elems.append(_rect(cx, y, 44, 44,
                           stroke=COLOR_DIM, bg=COLOR_HIGHLIGHT_BG, fill="solid"))
        elems.append(_text(f"F{i+1}", cx + 4, y + 10,
                           font_size=13, stroke=COLOR_DIM, bold=True,
                           align="center", width=36))
        # Beschreibung
        lines = _wrap_text(desc, 55)
        ty = y + 2
        for line in lines[:2]:
            elems.append(_text(line, cx + 55, ty, font_size=15, stroke=COLOR_TEXT,
                               width=COL_W - 70))
            ty += 22

    return elems, cy + len(descriptions) * (70 + 12)


def layout_argumentation(argument: str, cx: int, cy: int) -> tuple:
    """Argumentationsgang-Box."""
    elems = []
    elems.extend(_section_label("Argumentationsgang", cx, cy))
    cy += 60
    box_h = 350
    elems.append(_rect(cx, cy, COL_W, box_h,
                       stroke=COLOR_STROKE, bg=COLOR_BG))
    lines = _wrap_text(argument, 60)
    ty = cy + 20
    for line in lines[:12]:
        elems.append(_text(line, cx + 25, ty, font_size=17, stroke=COLOR_TEXT,
                           width=COL_W - 50))
        ty += 26
    # Akzent-Punkte
    for i in range(3):
        elems.append(_rect(cx + 25 + i * 16, cy + box_h - 30, 8, 8,
                           stroke=COLOR_ACCENT, bg=COLOR_ACCENT, fill="solid"))
    return elems, cy + box_h


def layout_fragen(questions: list, cx: int, cy: int) -> tuple:
    """Offene Fragen."""
    elems = []
    elems.extend(_section_label("Offene Fragen", cx, cy))
    cy += 60
    card_h, gap = 110, 20

    for i, q in enumerate(questions):
        y = cy + i * (card_h + gap)
        elems.append(_rect(cx, y, COL_W, card_h,
                           stroke=COLOR_DIM, bg=COLOR_BG))
        elems.append(_rect(cx + 12, y + 12, 44, 44,
                           stroke=COLOR_ACCENT, bg=COLOR_HIGHLIGHT_BG, fill="solid"))
        elems.append(_text("?", cx + 20, y + 18,
                           font_size=24, stroke=COLOR_ACCENT, bold=True,
                           align="center", width=28))
        lines = _wrap_text(q, 55)
        ty = y + 18
        for line in lines[:3]:
            elems.append(_text(line, cx + 65, ty, font_size=16, stroke=COLOR_TEXT,
                               width=COL_W - 80))
            ty += 24

    return elems, cy + len(questions) * (card_h + gap)


def layout_abschluss(title: str, cx: int, cy: int) -> tuple:
    """Abschluss-Bereich."""
    elems = []
    elems.append(_rect(cx, cy, COL_W, 200,
                       stroke=COLOR_ACCENT, bg=COLOR_HIGHLIGHT_BG, fill="solid"))
    elems.append(_text("Fragen?", cx, cy + 40, font_size=56,
                       stroke=COLOR_ACCENT, bold=True,
                       align="center", width=COL_W))
    elems.append(_text("VideoBrief - auto-generated from YouTube",
                       cx, cy + 130, font_size=14, stroke=COLOR_DIM,
                       align="center", width=COL_W))
    return elems, cy + 200


def _connect_arrows(right_y: int) -> list:
    """Pfeile zwischen linker und rechter Spalte."""
    elems = []
    # Horizontaler Pfeil von links nach rechts (Mitte der Canvas)
    mid_x = MARGIN + COL_W
    right_x = mid_x + GAP
    # Mehrere Pfeile auf verschiedenen Hoehen
    for y in [600, 1500, 2600]:
        elems.append(_arrow(mid_x - 20, y, right_x + 20, y,
                           stroke=COLOR_ACCENT, width=2))
    return elems


def generate_presentation(report_path: Path, output_dir: Path = None) -> Path:
    """Generiert EINE grosse Excalidraw-Datei aus einem Report.

    Gibt den Pfad zur erzeugten .excalidraw-Datei zurueck.
    """
    if output_dir is None:
        output_dir = report_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    data = parse_report(report_path)

    all_elements = []

    # === LINKE SPALTE ===
    lx = MARGIN
    y = 60  # Start-Y

    # Titel
    elems, y = layout_title(data["title"], data["source_url"], lx, y)
    all_elements.extend(elems)
    y += SECTION_GAP

    # Kernaussage
    if data["summary"]:
        elems, y = layout_kernaussage(data["summary"], lx, y)
        all_elements.extend(elems)
        y += SECTION_GAP

    # Timeline
    if data["timeline"]:
        elems, y = layout_timeline(data["timeline"], lx, y)
        all_elements.extend(elems)

    # === RECHTE SPALTE ===
    rx = MARGIN + COL_W + GAP
    y = 60

    # Charts
    if data["charts"]:
        elems, y = layout_charts(data["charts"], rx, y)
        all_elements.extend(elems)
        y += SECTION_GAP

    # Argumentation
    if data["argument"]:
        elems, y = layout_argumentation(data["argument"], rx, y)
        all_elements.extend(elems)
        y += SECTION_GAP

    # Offene Fragen
    if data["questions"]:
        elems, y = layout_fragen(data["questions"], rx, y)
        all_elements.extend(elems)
        y += SECTION_GAP

    # Abschluss (zentriert unten)
    abschluss_y = max(y, 3400)
    center_x = (CANVAS_W - COL_W) # 2
    elems, _ = layout_abschluss(data["title"], center_x, abschluss_y)
    all_elements.extend(elems)

    # Verbindungspfeile zwischen Spalten
    all_elements.extend(_connect_arrows(0))

    # === Datei schreiben ===
    doc = {
        "type": "excalidraw", "version": 2,
        "source": "https://excalidraw.com",
        "elements": all_elements,
        "appState": {"gridSize": 20, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }

    output_path = output_dir / "praesentation.excalidraw"
    output_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    return output_path


# --- Parser (unveraendert) ---

def parse_report(report_path: Path) -> dict:
    text = report_path.read_text(encoding="utf-8")
    data = {
        "title": "", "source_url": "", "summary": "",
        "timeline": [], "charts": [], "argument": "", "questions": [],
    }
    section = None

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not data["title"]:
            data["title"] = stripped[2:].strip()
            continue
        if stripped.startswith("**Quelle:**"):
            m = re.search(r'\[.*?\]\((.+?)\)', stripped)
            if m:
                data["source_url"] = m.group(1)
            continue
        # Sections: ### Heading  oder  **Heading Zusammenfassung:**
        if re.match(r'^#{1,3}\s*Kernaussage', stripped) or \
           re.match(r'^\*\*Kernaussage', stripped):
            section = "summary"; continue
        elif re.match(r'^#{1,3}\s*Timeline', stripped) or \
             re.match(r'^\*\*Timeline', stripped):
            section = "timeline"; continue
        elif re.match(r'^#{1,3}\s*(Charts|Beschreibung der Frames)', stripped) or \
             re.match(r'^\*\*Charts', stripped):
            section = "charts"; continue
        elif re.match(r'^#{1,3}\s*Argumentationsgang', stripped) or \
             re.match(r'^\*\*Argumentationsgang', stripped):
            section = "argument"; continue
        elif re.match(r'^#{1,3}\s*Offene Fragen', stripped) or \
             re.match(r'^\*\*Offene Fragen', stripped):
            section = "questions"; continue
        elif stripped.startswith("---") or stripped.startswith("## Verwendete"):
            section = None; continue

        # Content: Header-Zeilen (mit :) ueberspringen
        if stripped.endswith(":") and section and len(stripped) < 60:
            continue

        if section == "summary" and stripped and not stripped.startswith("**"):
            data["summary"] += stripped + " "
        elif section == "timeline" and stripped:
            cleaned = re.sub(r'^[\d\.\-\s]+', '', stripped).strip()
            if cleaned:
                data["timeline"].append(cleaned)
        elif section == "charts" and stripped.startswith("-"):
            cleaned = stripped.lstrip("- ").strip()
            if cleaned:
                data["charts"].append(cleaned)
        elif section == "argument" and stripped and not stripped.startswith("**"):
            data["argument"] += stripped + " "
        elif section == "questions" and stripped.startswith("- "):
            cleaned = stripped[2:].strip()
            if cleaned:
                data["questions"].append(cleaned)

    data["summary"] = data["summary"].strip()
    data["argument"] = data["argument"].strip()
    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m backend.excalidraw_generator <report.md> [output_dir]")
        sys.exit(1)
    report = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    path = generate_presentation(report, out)
    print(f"Generiert: {path}")
    print(f"  {len(json.loads(path.read_text())['elements'])} Elemente")
