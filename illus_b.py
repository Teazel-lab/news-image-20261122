"""Illustration registry B for 22 November 2026: story id -> (w, h) -> inline <svg> string.

Cards 9-13, 189x66 viewBox; the bottom 15 units sit under build.py's caption band.
"""
from illus_a import CARD, FONT, INK, _label, _lg, _person, _smoke, _svg


def nrol136(w, h):
    """Falcon-style rocket climbing off a coastal pad at dawn, booster-landing pad marked LZ-4."""
    d = _lg("nr", "#2c3f66", "#f0a878")
    b = ['<rect width="189" height="66" fill="url(#nr)"/>',
         '<rect y="44" width="189" height="22" fill="#33566e"/>',
         '<path d="M0 44 l40 -10 l40 6 l30 -4 v22 h-110z" fill="#6f6a55"/>',
         '<path d="M44 38 Q 70 30 96 22" stroke="#f4e6d0" stroke-width="5" fill="none" opacity="0.8"/>',
         _smoke([(40, 38, 6), (30, 40, 5), (52, 40, 5)], "#efe6da", 0.9),
         '<g transform="rotate(62 100 20)"><rect x="96" y="2" width="7" height="34" rx="1" fill="#f4f4f2"/>'
         '<path d="M96 2 l3.5 -7 l3.5 7z" fill="#f4f4f2"/><rect x="96" y="12" width="7" height="2" fill="#222"/>'
         '<path d="M97 36 l2.5 10 l2.5 -10z" fill="#ffcf4a"/></g>',
         '<rect x="132" y="38" width="34" height="13" rx="2" fill="#dcd4c4"/>'
         '<text x="149" y="48.5" text-anchor="middle" %s font-size="11" fill="%s">LZ-4</text>' % (FONT, INK),
         '<circle cx="168" cy="10" r="1" fill="#fff"/><circle cx="178" cy="20" r="0.8" fill="#fff"/>',
         _label(8, 13, "NROL-136", 11, INK, "#f2c14e")]
    return _svg(w, h, CARD, "".join(b), d)


def f1_vegas(w, h):
    """A dark-blue single-seater at night under a neon skyline, chequered flag waving."""
    b = ['<rect width="189" height="66" fill="#141a33"/>']
    for x, hh, c in ((6, 26, "#ff3fa4"), (26, 36, "#2ee6d6"), (48, 22, "#ffd23f"), (64, 40, "#b46bff"),
                     (88, 28, "#ff3fa4"), (110, 34, "#2ee6d6"), (134, 24, "#ffd23f"), (150, 38, "#ff7a3f")):
        b.append('<rect x="%d" y="%d" width="16" height="%d" fill="#232a4f" stroke="%s" stroke-width="1.2"/>'
                 % (x, 44 - hh, hh, c))
    b.append('<rect y="44" width="189" height="22" fill="#2b2b33"/>'
             '<rect y="50" width="189" height="1.5" fill="#f4f4f2" opacity="0.6"/>')
    # car
    b.append('<path d="M44 46 l8 -6 h40 l10 -4 h18 l4 6 h14 l2 4z" fill="#1c3a8a"/>'
             '<rect x="40" y="38" width="6" height="8" fill="#1c3a8a"/><rect x="136" y="41" width="8" height="4" fill="#1c3a8a"/>'
             '<path d="M88 40 q6 -6 12 0" fill="#222"/><rect x="62" y="42" width="30" height="2" fill="#e8c23a"/>'
             '<circle cx="60" cy="48" r="6" fill="#111"/><circle cx="124" cy="48" r="6" fill="#111"/>'
             '<circle cx="60" cy="48" r="2" fill="#777"/><circle cx="124" cy="48" r="2" fill="#777"/>')
    # chequered flag
    b.append('<line x1="172" y1="6" x2="172" y2="40" stroke="#ccc" stroke-width="1.5"/>')
    for i in range(4):
        for j in range(3):
            b.append('<rect x="%d" y="%d" width="4" height="4" fill="%s"/>'
                     % (173 + i * 4, 6 + j * 4, "#fff" if (i + j) % 2 else "#111"))
    b.append(_label(8, 13, "+0.639s", 11, INK, "#f2c14e"))
    return _svg(w, h, CARD, "".join(b))


def motogp(w, h):
    """A rider knee-down through a corner and a trophy marked 8."""
    b = ['<rect width="189" height="66" fill="#cfe3d2"/>',
         '<path d="M0 52 Q 80 28 189 40 V66 H0z" fill="#55595e"/>',
         '<path d="M0 52 Q 80 28 189 40" stroke="#e33" stroke-width="2.5" stroke-dasharray="6 6" fill="none"/>',
         '<g transform="rotate(-30 70 40)"><ellipse cx="70" cy="40" rx="20" ry="6" fill="#c0392b"/>'
         '<circle cx="54" cy="46" r="6" fill="#111"/><circle cx="86" cy="46" r="6" fill="#111"/>'
         '<rect x="62" y="28" width="12" height="9" rx="3" fill="#f4f4f2"/><circle cx="76" cy="27" r="4.5" fill="#f2c14e"/></g>',
         '<path d="M136 10 h28 v6 q0 14 -14 16 q-14 -2 -14 -16z" fill="#e2b33a" stroke="#a37a1a"/>'
         '<rect x="147" y="32" width="6" height="8" fill="#c9a032"/><rect x="140" y="40" width="20" height="6" fill="#8a6a1a"/>'
         '<text x="150" y="27" text-anchor="middle" %s font-size="16" fill="#7a5410">8</text>' % FONT,
         _label(8, 13, "8TH TITLE", 11)]
    return _svg(w, h, CARD, "".join(b))


def il_talks(w, h):
    """Two negotiating teams across a hotel meeting table by a sea-view window."""
    b = ['<rect width="189" height="66" fill="#efe7d8"/>',
         '<rect x="120" y="4" width="62" height="28" fill="#9fd0e6" stroke="#b9ad96" stroke-width="2"/>'
         '<rect x="120" y="22" width="62" height="10" fill="#3d86b0"/>'
         '<line x1="151" y1="4" x2="151" y2="32" stroke="#b9ad96" stroke-width="2"/>']
    for x in (36, 54, 72):
        b.append(_person(x, 46, 1.0, "#2f5fa8"))
    for x in (112, 130, 148):
        b.append(_person(x, 46, 1.0, "#5e6670"))
    b.append('<rect x="22" y="38" width="144" height="8" rx="2" fill="#6b4a2e"/>'
             '<rect x="80" y="35" width="14" height="3" fill="#fbf8f0"/><rect x="98" y="35" width="10" height="3" fill="#fbf8f0"/>'
             '<rect y="46" width="189" height="20" fill="#a89a80"/>')
    b.append(_label(8, 13, "COALITION TALKS", 11))
    return _svg(w, h, CARD, "".join(b))


def np_visit(w, h):
    """Two officials shake hands in a columned hall between simplified Nepal and India flags."""
    b = ['<rect width="189" height="66" fill="#f1e8d6"/>']
    for x in (12, 44, 140, 172):
        b.append('<rect x="%d" y="6" width="8" height="42" fill="#ded2b8" stroke="#b9ad96"/>' % x)
    b.append('<rect y="0" width="189" height="6" fill="#b9ad96"/><rect y="48" width="189" height="18" fill="#a5413a"/>')
    # Nepal: double pennant, crimson with blue edge
    b.append('<line x1="64" y1="8" x2="64" y2="48" stroke="#777" stroke-width="1.5"/>'
             '<path d="M65 8 l14 9 h-9 l11 11 h-16z" fill="#c8102e" stroke="#003893" stroke-width="1.5"/>')
    # India: tricolour with wheel
    b.append('<line x1="124" y1="8" x2="124" y2="48" stroke="#777" stroke-width="1.5"/>'
             '<rect x="104" y="8" width="20" height="5" fill="#ff9933"/><rect x="104" y="13" width="20" height="5" fill="#fff"/>'
             '<rect x="104" y="18" width="20" height="5" fill="#138808"/><circle cx="114" cy="15.5" r="1.8" fill="none" stroke="#000080" stroke-width="0.7"/>')
    b.append(_person(84, 50, 1.25, "#2b2f3a"))
    b.append(_person(104, 50, 1.25, "#e8e2d4"))
    b.append('<rect x="88" y="34" width="12" height="3" rx="1.5" fill="#c99a6e"/>')
    return _svg(w, h, CARD, "".join(b))


ILLUS_B = {
    "wo-nrol136": nrol136,
    "am-f1-lv": f1_vegas,
    "eu-motogp": motogp,
    "me-il-talks": il_talks,
    "as-np-visit": np_visit,
}
