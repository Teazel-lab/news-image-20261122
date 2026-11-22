"""Illustration registry A for 22 November 2026: story id -> (w, h) -> inline <svg> string.

Leads use a 325x132 viewBox, cards 189x66; build.py lays a caption band over the
bottom 16 (lead) / 15 (card) units, so the scene sits above that.
"""

INK = "#1d1a16"
FONT = 'font-family="Barlow Condensed, Arial Narrow, sans-serif" font-weight="700"'
LEAD, CARD = (325, 132), (189, 66)


def _svg(w, h, vb, body, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'preserveAspectRatio="xMidYMid slice"><defs>%s</defs>%s</svg>' % (w, h, vb[0], vb[1], defs, body))


def _lg(gid, *stops):
    s = "".join('<stop offset="%s" stop-color="%s"/>' % (i / (len(stops) - 1), c) for i, c in enumerate(stops))
    return '<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1">%s</linearGradient>' % (gid, s)


def _label(x, y, text, size=13, fill="#fff", bg=INK):
    """Caps tag, left edge x, baseline y."""
    w = len(text) * size * 0.5 + 8
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
            '<text x="%.1f" y="%.1f" %s font-size="%s" fill="%s" letter-spacing="0.4">%s</text>'
            % (x - 4, y - size + 1, w, size + 3, bg, x, y, FONT, size, fill, text))


def _person(x, y, s=1.0, body="#3b4a63", head="#c99a6e", hat=None):
    """Standing figure, feet at (x, y), about 22*s tall."""
    out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
           '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
           '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
           % (x - 4 * s, y - 16 * s, 8 * s, 10 * s, 2.5 * s, body,
              x - 3.2 * s, y - 7 * s, 6.4 * s, 7 * s, "#2a2a2e",
              x, y - 19 * s, 3.2 * s, head))
    if hat:
        out += '<path d="M%.1f %.1f a3.6 3.2 0 0 1 %.1f 0z" fill="%s"/>' % (x - 3.6 * s, y - 19.6 * s, 7.2 * s, hat)
    return out


def _smoke(pts, fill="#6d6a68", op=0.85):
    return "".join('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>' % (x, y, r, fill, op) for x, y, r in pts)


def _flame(x, y, s=1.0):
    return ('<path d="M%.1f %.1f q%.1f %.1f %.1f %.1f q%.1f %.1f %.1f %.1f q%.1f %.1f %.1f %.1fz" fill="#f07a1a"/>'
            '<path d="M%.1f %.1f q%.1f %.1f %.1f %.1f q%.1f %.1f %.1f %.1fz" fill="#ffd23f"/>'
            % (x - 6 * s, y, -2 * s, -9 * s, 4 * s, -16 * s, 1 * s, 6 * s, 4 * s, 5 * s, 3 * s, 6 * s, 4 * s, 11 * s,
               x - 3 * s, y, -1 * s, -6 * s, 3 * s, -9 * s, 3 * s, 4 * s, 3 * s, 9 * s))


# ------------------------------------------------------------------ leads
def kyiv_dymer(w, h):
    """Dawn rescuers at a five-storey block with its middle stairwell collapsed; drones overhead."""
    d = _lg("kd", "#f3b58a", "#c9d6e6")
    b = ['<rect width="325" height="132" fill="url(#kd)"/>',
         '<rect y="108" width="325" height="24" fill="#8b857a"/>']
    # the block: left and right wings standing, middle gone
    for x0, x1 in ((70, 140), (186, 256)):
        b.append('<rect x="%d" y="30" width="%d" height="80" fill="#d8d0c0" stroke="#7b7366"/>' % (x0, x1 - x0))
        for fl in range(5):
            for c in range(x0 + 7, x1 - 8, 15):
                b.append('<rect x="%d" y="%d" width="8" height="9" fill="#5d6778"/>' % (c, 36 + fl * 15))
    b.append('<path d="M140 30 L148 44 L144 58 L152 70 L146 84 L150 110 L140 110z" fill="#bdb3a0"/>'
             '<path d="M186 30 L178 46 L183 60 L175 74 L181 88 L176 110 L186 110z" fill="#bdb3a0"/>')
    b.append('<path d="M128 110 L140 92 L152 98 L163 84 L176 95 L190 90 L200 110z" fill="#6f665a"/>'
             '<path d="M146 104 l14 -8 M160 101 l16 2 M170 92 l10 9" stroke="#3d3730" stroke-width="2"/>')
    b.append(_smoke([(160, 70, 12), (170, 56, 10), (154, 48, 8), (166, 38, 7)], "#8a8580", 0.7))
    # ladder truck and rescuers
    b.append('<rect x="262" y="94" width="46" height="16" rx="2" fill="#c0392b"/>'
             '<line x1="270" y1="94" x2="226" y2="52" stroke="#d9d4cc" stroke-width="4"/>'
             '<circle cx="272" cy="111" r="4" fill="#222"/><circle cx="298" cy="111" r="4" fill="#222"/>')
    for x in (110, 122, 204, 216, 234):
        b.append(_person(x, 116, 0.75, "#f2a20c", hat="#f6e33a"))
    # drones (delta wings) in the sky
    for x, y in ((24, 22), (44, 12), (292, 18)):
        b.append('<path d="M%d %d l10 4 l-10 4 l3 -4z" fill="%s"/>' % (x, y, INK))
    b.append(_label(10, 104, "14 MISSING", 13, bg="#8e1b1b"))
    return _svg(w, h, LEAD, "".join(b), d)


def cop31(w, h):
    """Plenary hall: a gavel over a draft whose fossil-fuel line is blank, stamped REJECTED."""
    d = _lg("cp", "#2c4a6e", "#18304c")
    b = ['<rect width="325" height="132" fill="url(#cp)"/>']
    # tiered delegate desks
    for i, (y, c) in enumerate(((96, "#5c7896"), (82, "#4d6886"), (68, "#405a77"))):
        b.append('<rect x="0" y="%d" width="325" height="9" fill="%s"/>' % (y, c))
        for x in range(8 + i * 6, 325, 18):
            b.append('<circle cx="%d" cy="%d" r="3.3" fill="#c49a73"/>' % (x, y - 2))
    b.append('<rect y="105" width="325" height="27" fill="#2a3240"/>')
    # draft document
    b.append('<g transform="rotate(-4 120 60)"><rect x="74" y="10" width="96" height="102" fill="#fbf8f0" stroke="#999"/>'
             '<text x="122" y="24" text-anchor="middle" %s font-size="11" fill="%s">COP31 DRAFT</text>' % (FONT, INK))
    for y in (32, 40, 48, 72, 80, 88, 96):
        b.append('<rect x="84" y="%d" width="%d" height="3" fill="#a9a39a"/>' % (y, 76 if y % 16 else 62))
    b.append('<rect x="80" y="54" width="84" height="14" fill="none" stroke="#c0392b" stroke-dasharray="3 2"/>'
             '<text x="122" y="65" text-anchor="middle" %s font-size="11" fill="#c0392b">FOSSIL FUELS: ?</text></g>' % FONT)
    # stamp
    b.append('<g transform="rotate(-14 200 50)"><rect x="164" y="38" width="98" height="26" rx="3" fill="none" '
             'stroke="#e04a3a" stroke-width="3"/><text x="213" y="58" text-anchor="middle" %s font-size="19" '
             'fill="#e04a3a" letter-spacing="1.5">REJECTED</text></g>' % FONT)
    # gavel
    b.append('<g transform="rotate(30 278 70)"><rect x="262" y="58" width="32" height="15" rx="3" fill="#8a5a2b"/>'
             '<rect x="275" y="73" width="6" height="34" fill="#6d4520"/></g>'
             '<rect x="252" y="100" width="44" height="6" rx="2" fill="#6d4520"/>')
    b.append(_label(10, 100, "EU + UK OBJECT", 13, INK, "#f2c14e"))
    return _svg(w, h, LEAD, "".join(b), d)


def id_fire(w, h):
    """Smoking sawtooth-roof candy factory, a fire engine spraying, rescuers searching."""
    d = _lg("if", "#d9cbb5", "#ecdcc4")
    b = ['<rect width="325" height="132" fill="url(#if)"/>',
         _smoke([(150, 24, 18), (176, 16, 16), (128, 18, 14), (200, 28, 14), (108, 30, 11)], "#55524f", 0.9),
         '<rect y="106" width="325" height="26" fill="#7f7a70"/>',
         '<path d="M70 50 l22 -14 v14 l22 -14 v14 l22 -14 v14 l22 -14 v14 l22 -14 v14 l22 -14 v14 v56 h-132z" '
         'fill="#c9bfae" stroke="#6f6758"/>']
    for x in range(80, 200, 22):
        b.append('<rect x="%d" y="64" width="13" height="16" fill="#3a2a22"/>' % x)
    for x in (90, 134, 178):
        b.append(_flame(x + 2, 80, 1.1))
    # candy sign
    b.append('<rect x="88" y="88" width="60" height="14" fill="#fbf3e6" stroke="#6f6758"/>'
             '<ellipse cx="118" cy="95" rx="7" ry="4.5" fill="#e0457b"/>'
             '<path d="M111 95 l-6 -4 v8z M125 95 l6 -4 v8z" fill="#e0457b"/>')
    # fire engine with water arc
    b.append('<rect x="230" y="88" width="62" height="20" rx="3" fill="#c0392b"/>'
             '<rect x="276" y="80" width="16" height="12" fill="#c0392b"/><rect x="279" y="83" width="10" height="6" fill="#bcd"/>'
             '<circle cx="242" cy="108" r="5" fill="#222"/><circle cx="282" cy="108" r="5" fill="#222"/>'
             '<path d="M236 86 Q 214 40 176 62" stroke="#7fc4ea" stroke-width="4" fill="none"/>')
    for x in (208, 220, 304):
        b.append(_person(x, 114, 0.8, "#2d3a4f", hat="#f6e33a"))
    b.append(_label(10, 104, "36 MISSING", 13, bg="#8e1b1b"))
    return _svg(w, h, LEAD, "".join(b), d)


# ------------------------------------------------------------------ cards 4-8
def ly_ship(w, h):
    """A grey warship burning at a Benghazi quay, a small drone overhead."""
    d = _lg("ls", "#e8b07a", "#b9cfd8")
    b = ['<rect width="189" height="66" fill="url(#ls)"/>',
         '<rect y="44" width="189" height="22" fill="#4f7b93"/>',
         '<rect x="0" y="40" width="40" height="26" fill="#9a8f7c"/>',
         _smoke([(104, 16, 9), (116, 10, 8), (94, 8, 6)], "#4a4744"),
         '<path d="M40 38 h112 l-10 10 h-94z" fill="#6c737b"/>'
         '<rect x="70" y="27" width="34" height="11" fill="#7d858e"/><rect x="82" y="17" width="9" height="10" fill="#7d858e"/>'
         '<line x1="86" y1="17" x2="86" y2="8" stroke="#555" stroke-width="1.5"/>',
         _flame(108, 38, 0.9),
         '<path d="M150 9 l10 3.5 l-10 3.5 l2.5 -3.5z" fill="%s"/>' % INK,
         _label(147, 33, "LIBYA", 11)]
    return _svg(w, h, CARD, "".join(b), d)


def wb_arson(w, h):
    """Village street at morning: a burnt-out car and scrawled graffiti on a stone wall."""
    b = ['<rect width="189" height="66" fill="#cfe0ea"/>',
         '<path d="M0 30 q30 -14 60 -4 q40 -16 80 0 q30 -8 49 -2 v42 h-189z" fill="#b6b27c"/>',
         '<rect x="8" y="16" width="44" height="34" fill="#e3d6b8" stroke="#a89978"/>'
         '<rect x="62" y="22" width="60" height="28" fill="#dccfae" stroke="#a89978"/>'
         '<rect x="16" y="24" width="8" height="9" fill="#4b4c50"/><rect x="34" y="24" width="8" height="9" fill="#4b4c50"/>'
         '<path d="M68 30 q6 -6 10 0 t10 0 t10 0 M70 40 l8 -6 l6 6 l8 -6" stroke="#c0392b" stroke-width="2" fill="none"/>',
         '<rect y="50" width="189" height="16" fill="#9b9384"/>',
         '<path d="M120 50 l6 -10 h28 l8 10 h6 v6 h-54 v-6z" fill="#2b2826"/>'
         '<circle cx="130" cy="56" r="4.5" fill="#111"/><circle cx="158" cy="56" r="4.5" fill="#111"/>'
         '<circle cx="138" cy="47" r="1.6" fill="#f07a1a"/><circle cx="150" cy="45" r="1.4" fill="#ffb03a"/>',
         _smoke([(140, 32, 5), (146, 24, 4), (150, 17, 3)], "#6d6a68", 0.6),
         _label(130, 13, "4 VILLAGES", 11)]
    return _svg(w, h, CARD, "".join(b))


def aukus(w, h):
    """A submarine at the surface beside a report crossed out in red."""
    b = ['<rect width="189" height="66" fill="#d7e4ec"/>',
         '<rect y="34" width="189" height="32" fill="#2f5d7a"/>',
         '<path d="M10 38 q4 -8 18 -8 h76 q14 0 16 8z" fill="#22262b"/>'
         '<path d="M50 30 v-10 h18 l4 10z" fill="#22262b"/><line x1="58" y1="20" x2="58" y2="12" stroke="#22262b" stroke-width="2"/>'
         '<path d="M0 41 q8 -3 16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0" stroke="#bcd" stroke-width="1.2" fill="none"/>',
         '<g transform="rotate(6 154 26)"><rect x="132" y="4" width="44" height="44" fill="#fbf8f0" stroke="#888"/>'
         '<text x="154" y="17" text-anchor="middle" %s font-size="11" fill="%s">CBO</text>' % (FONT, INK),
         '<rect x="138" y="22" width="32" height="2.5" fill="#aaa"/><rect x="138" y="28" width="28" height="2.5" fill="#aaa"/>'
         '<rect x="138" y="34" width="32" height="2.5" fill="#aaa"/>'
         '<path d="M134 8 l40 36 M174 8 l-40 36" stroke="#d0342c" stroke-width="3.5"/></g>',
         _label(8, 13, "A$368BN PACT ON", 11)]
    return _svg(w, h, CARD, "".join(b))


def ss_tonj(w, h):
    """Dusk over a cattle camp: long-horned cattle and grass huts, smoke rising."""
    d = _lg("st", "#e9874a", "#f4c27a")
    b = ['<rect width="189" height="66" fill="url(#st)"/>',
         '<circle cx="150" cy="30" r="10" fill="#fbe0a0"/>',
         '<rect y="44" width="189" height="22" fill="#8a6a3a"/>',
         _smoke([(30, 26, 5), (34, 18, 4), (38, 11, 3)], "#5a4a40", 0.6)]
    for x in (14, 40):
        b.append('<rect x="%d" y="34" width="18" height="12" fill="#5a3f22"/><path d="M%d 35 l12 -12 l12 12z" fill="#b48a4a"/>'
                 % (x, x - 3))
    for x in (78, 108, 136, 164):
        b.append('<ellipse cx="%d" cy="42" rx="10" ry="5" fill="#2a1d14"/>'
                 '<rect x="%d" y="44" width="2" height="6" fill="#2a1d14"/><rect x="%d" y="44" width="2" height="6" fill="#2a1d14"/>'
                 '<circle cx="%d" cy="38" r="3" fill="#2a1d14"/>'
                 '<path d="M%d 36 q-4 -6 -1 -9 M%d 36 q4 -6 7 -7" stroke="#2a1d14" stroke-width="1.4" fill="none"/>'
                 % (x, x - 7, x + 5, x + 10, x + 9, x + 11))
    b.append(_label(8, 13, "15 KILLED", 11, bg="#8e1b1b"))
    return _svg(w, h, CARD, "".join(b), d)


def kr_edu(w, h):
    """A minister bowing at a podium beside stacked exam papers and a tiny camera."""
    b = ['<rect width="189" height="66" fill="#e9e3d6"/>',
         '<rect y="0" width="189" height="10" fill="#3b4f7a"/>',
         '<rect x="40" y="34" width="34" height="18" fill="#6b4a2e"/>'
         '<circle cx="57" cy="34" r="2" fill="#333"/>',
         # bowing figure: torso tilted forward
         '<g transform="rotate(38 92 44)"><rect x="88" y="22" width="9" height="22" rx="3" fill="#24283a"/>'
         '<circle cx="92.5" cy="18" r="4" fill="#c99a6e"/></g>'
         '<rect x="88" y="44" width="7" height="8" fill="#24283a"/>',
         '<rect x="118" y="34" width="36" height="18" fill="#fbf8f0" stroke="#999"/>'
         '<rect x="121" y="30" width="36" height="18" fill="#fbf8f0" stroke="#999"/>'
         '<text x="139" y="43" text-anchor="middle" %s font-size="11" fill="%s">CSAT</text>' % (FONT, INK),
         '<rect x="162" y="22" width="14" height="10" rx="2" fill="#333"/><circle cx="169" cy="27" r="3" fill="#7fc4ea"/>'
         '<text x="169" y="19" text-anchor="middle" %s font-size="11" fill="#c0392b">AI</text>' % FONT,
         '<rect y="52" width="189" height="14" fill="#8f877a"/>',
         _label(8, 25, "RESIGNS", 11)]
    return _svg(w, h, CARD, "".join(b))


ILLUS_A = {
    "kyiv-dymer-drones": kyiv_dymer,
    "cop31-reject": cop31,
    "as-id-fire": id_fire,
    "af-ly-ship": ly_ship,
    "me-wb-arson": wb_arson,
    "oc-aukus": aukus,
    "af-ss-tonj": ss_tonj,
    "as-kr-edu": kr_edu,
}
