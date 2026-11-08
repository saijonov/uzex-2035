import sys
from pathlib import Path

COLORS = {
    "K": "#111111",
    "W": "#FFFFFF",
    "S": "#F0BE94",
    "s": "#D9A07A",
    "Y": "#FFDD2D",
    "P": "#3D3A2A",
    "G": "#F4F4F1",
    "L": "#8A8980",
}

BASE = [
    ".......KKKKKKKKKK.......",
    "......KKWKKKKKKWKK......",
    ".....KKKKKWKKWKKKKK.....",
    ".....KWKKKKWWKKKKWK.....",
    ".....KKKKKKKKKKKKKK.....",
    ".....KKSSSSSSSSSSKK.....",
    ".....KSKKKSSSSKKKSK.....",
    ".....KSSSSSSSSSSSSK.....",
    "....sKSSKSSSSSSKSSKs....",
    "....sKSSKSSSSSSKSSKs....",
    ".....KSSSSSssSSSSSK.....",
    ".....KSSSKKKKKKSSSK.....",
    ".....KSSKKSSSSKKSSK.....",
    "......KSSSSSSSSSSK......",
    ".......KKSSSSSSKK.......",
    "........KWWSSWWK........",
    "...KYYYYYYWSSWYYYYYYK...",
    "..KYYYYYYYYWWYYYYYYYYK..",
    "..KYYKYYYYYKYYYYYYKYYK..",
    "..KYYKYYYYYYYYYYYYKYYK..",
    "..KYYKYYYYYKYYYYYYKYYK..",
    "..KYYKYYYYYYYYYYYYKYYK..",
    "..KSSKYYYYYKYYYYYYKSSK..",
    "..KKKKPPPPPPPPPPPPKKKK..",
    ".....KPPPPPPPPPPPPK.....",
    ".....KPPPPPKKPPPPPK.....",
    ".....KPPPPPKKPPPPPK.....",
    ".....KPPPPPKKPPPPPK.....",
    "....KKKKKKK..KKKKKKK....",
    "....KKKKKKK..KKKKKKK....",
]


def grid():
    return [list(row) for row in BASE]


def put(g, row, col, text):
    for i, ch in enumerate(text):
        g[row][col + i] = ch


def wave():
    g = grid()
    for row in range(17, 23):
        put(g, row, 18, "K...")
    put(g, 23, 18, "K...")
    put(g, 16, 18, "YYYK")
    put(g, 6, 20, "KKK")
    for row in (7, 8, 9):
        put(g, row, 20, "KSK")
    for row in range(10, 16):
        put(g, row, 20, "KYK")
    put(g, 16, 20, "YYK")
    put(g, 17, 18, "YKK.")
    put(g, 12, 6, "SSKKSWWSKKSS")
    return g


def worried():
    g = grid()
    put(g, 6, 6, "SSKKSSSSKKSS")
    put(g, 5, 9, "K")
    put(g, 5, 14, "K")
    put(g, 12, 6, "SSKKSSSSKKSS")
    put(g, 13, 10, "KK")
    return g


def happy():
    g = grid()
    put(g, 8, 6, "SSKSSSSSSKSS")
    put(g, 9, 6, "SKSKSSSSKSKS")
    put(g, 12, 6, "SSKKSWWSKKSS")
    put(g, 18, 14, "KKKK")
    put(g, 19, 14, "KYYK")
    put(g, 20, 14, "KYYK")
    put(g, 21, 14, "KKKK")
    put(g, 20, 18, "SS")
    put(g, 21, 18, "SS")
    return g


def svg(g, scale, label):
    rects = []
    for y, row in enumerate(g):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            end = x
            while end < len(row) and row[end] == ch:
                end += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{end - x}" height="1" fill="{COLORS[ch]}"/>')
            x = end
    w, h = len(g[0]), len(g)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="said" width="{w * scale}" height="{h * scale}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}">' + "".join(rects) + "</svg>"
    )


PAPERS = [
    "...KKKKKKKKKK..",
    "..KWWWWWWWWWWK.",
    ".KKKKKKKKKKKWK.",
    ".KWWWWWWWWWKWK.",
    "KKKKKKKKKKKWKK.",
    "KWWWWWWWWWKWK..",
    "KWLLLLLLWWKKK..",
    "KWWWWWWWWWK....",
    "KWLLLLLWWWK....",
    "KWWWWWWWWWK....",
    "KWLLLLLLLWK....",
    "KWWWWWWWWWK....",
    "KWLLLLWWWWK....",
    "KWWWWWWWWWK....",
    "KKKKKKKKKKK....",
]

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, g in (("said-wave", wave()), ("said-worried", worried()), ("said-happy", happy())):
        (out / f"{name}.svg").write_text(svg(g, 12, "Пиксельный Саид") + "\n")
    (out / "papers.svg").write_text(svg([list(r) for r in PAPERS], 12, "Документы") + "\n")
