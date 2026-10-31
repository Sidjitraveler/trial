"""Generate area landing pages, FAQ schema and sitemap.

Run from the repo root after editing index.html or AREAS:  python3 tools/build.py
"""
import html
from urllib.parse import quote
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://sukoonbysid.in"
PHONE = "919607227768"
TODAY = date.today().isoformat()

AREAS = {
    "hsr-layout": {
        "name": "HSR Layout",
        "intro": "Long week at your desk? Skip the drive to a spa on 27th Main. I come to your flat in any HSR sector with a padded table, fresh linens and oils, and I'm set up in about 10 minutes.",
        "localities": ["Sectors 1–7", "Agara", "Parangi Palya", "Somasundarapalya", "27th Main", "Silk Board side"],
        "nearby": ["koramangala", "btm-layout", "bellandur"],
    },
    "koramangala": {
        "name": "Koramangala",
        "intro": "Koramangala traffic is the last thing you need after a long week. Book a massage at home instead. I bring the table, fresh linens and oils to your place, in any block from 1st to 8th.",
        "localities": ["1st to 8th Block", "Ejipura", "ST Bed", "Venkatapura", "Adugodi"],
        "nearby": ["hsr-layout", "btm-layout", "indiranagar"],
    },
    "jayanagar": {
        "name": "Jayanagar",
        "intro": "Relax properly without leaving home. I come to your house or flat in any Jayanagar block with everything needed for an unhurried session, and leave the room as I found it.",
        "localities": ["1st to 9th Block", "4th T Block", "Tilak Nagar", "Jayanagar East", "South End Circle"],
        "nearby": ["jp-nagar", "btm-layout", "koramangala"],
    },
    "btm-layout": {
        "name": "BTM Layout",
        "intro": "Want a proper massage without fighting Silk Board traffic? I come to you in BTM on weekends with a table, fresh linens and oils. All you have to do is lie down.",
        "localities": ["BTM 1st Stage", "BTM 2nd Stage", "Madiwala", "Tavarekere", "Silk Board side"],
        "nearby": ["hsr-layout", "koramangala", "jp-nagar", "jayanagar"],
    },
    "jp-nagar": {
        "name": "JP Nagar",
        "intro": "Weekend massages at home anywhere in JP Nagar, from Phase 1 to Phase 9. No spa waiting room and no drive home afterwards. Just rest.",
        "localities": ["Phases 1–9", "Dollars Colony", "Puttenahalli", "Sarakki", "Bannerghatta Road side"],
        "nearby": ["jayanagar", "btm-layout"],
    },
    "indiranagar": {
        "name": "Indiranagar",
        "intro": "Swap the busy 100 Feet Road spas for a quiet session in your own space. I bring everything with me and pack it all away afterwards.",
        "localities": ["100 Feet Road", "HAL 2nd Stage", "Defence Colony", "Domlur", "Jeevan Bima Nagar"],
        "nearby": ["koramangala", "hsr-layout"],
    },
    "bellandur": {
        "name": "Bellandur",
        "intro": "Working near the Outer Ring Road all week? Unwind at home in Bellandur on the weekend. I come to you with a table, fresh linens and oils.",
        "localities": ["Outer Ring Road", "Green Glen Layout", "Kadubeesanahalli", "Sarjapur Road", "Ecospace side"],
        "nearby": ["hsr-layout", "koramangala"],
    },
}


def esc(s):
    return html.escape(s, quote=True)


def area_url(slug):
    return f"{SITE}/massage-at-home/{slug}/"


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"


def faq_schema(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ---------------------------------------------------------------- home page FAQ schema
index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")
pairs = [
    (strip_tags(q)[0].upper() + strip_tags(q)[1:], strip_tags(a))
    for q, a in re.findall(r'<details class="card">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>', index, re.S)
]
block = "<!-- faq-schema:start -->\n  " + ld(faq_schema(pairs)).replace("\n", "\n  ") + "\n  <!-- faq-schema:end -->"
index = re.sub(r"<!-- faq-schema:start -->.*?<!-- faq-schema:end -->", lambda _: block, index, flags=re.S)
index_path.write_text(index, encoding="utf-8")

sprite = re.search(r"  <!-- Doodle sprite -->\n.*?</svg>\n", index, re.S).group(0)
squiggle = '<svg viewBox="0 0 200 16" preserveAspectRatio="none"><use href="#d-squiggle"/></svg>'


# ---------------------------------------------------------------- area pages
def area_page(slug, a):
    name = a["name"]
    url = area_url(slug)
    title = f"Massage at Home in {name}, Bengaluru | ₹2,500 · Sukoon by Sid"
    desc = (f"Relaxing massage at home in {name}, Bengaluru. Sid brings the table, fresh linens and oils to you. "
            f"₹2,500 per massage plus travel, weekends only. Book on WhatsApp.")
    wa_text = f"Hi Sid, I'd like to book a massage at home in {name}."
    wa = f"https://wa.me/{PHONE}?text={quote(wa_text)}"

    faqs = [
        (f"Do you come to all of {name}?",
         f"Yes. I cover {', '.join(a['localities'][:-1])} and {a['localities'][-1]}. If you're just outside, message me anyway and I'll usually make it work."),
        (f"How much does a massage at home in {name} cost?",
         "₹2,500 per massage (about an hour), plus a travel charge that depends on exactly where you are. I'll confirm the total before you book. A ₹500 UPI advance confirms the slot and comes off the total."),
        ("When are you available?",
         "Saturdays and Sundays, between 7 am and 10 pm. Please book at least 3 days ahead."),
        ("Are you a certified therapist?",
         "No. I'm not certified or medically trained, and I offer relaxation massage only. For injuries or medical conditions, please see a physiotherapist."),
    ]

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "Massage at home",
            "name": f"Massage at home in {name}",
            "url": url,
            "provider": {"@type": "HealthAndBeautyBusiness", "name": "Sukoon by Sid", "url": SITE + "/", "telephone": "+91-96072-27768"},
            "areaServed": {"@type": "Place", "name": f"{name}, Bengaluru"},
            "offers": {"@type": "Offer", "price": "2500", "priceCurrency": "INR", "description": "Per massage, about 60 minutes. Travel extra."},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": f"Massage at home in {name}", "item": url},
            ],
        },
        faq_schema(faqs),
    ]

    loc_items = "\n".join(f"            <li>{esc(l)}</li>" for l in a["localities"])
    near_items = "\n".join(
        f'            <li><a href="/massage-at-home/{n}/">{esc(AREAS[n]["name"])}</a></li>' for n in a["nearby"]
    )
    other_items = "\n".join(
        f'          <li><a href="/massage-at-home/{s}/">{esc(o["name"])}</a></li>' for s, o in AREAS.items() if s != slug
    )
    faq_html = "\n".join(
        f'          <details class="card">\n            <summary>{esc(q[0].lower() + q[1:])}</summary>\n            <p>{esc(ans)}</p>\n          </details>'
        for q, ans in faqs
    )

    return f"""<!doctype html>
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="theme-color" content="#FBF8F1">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Massage at home in {esc(name)} · Sukoon by Sid">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/og-image.png">
  <meta property="og:locale" content="en_IN">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Caveat:wght@500;700&family=DM+Sans:opsz,wght@9..40,400..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  {"".join(ld(s) for s in schema).replace("</script><script", "</script>\n  <script")}
</head>
<body>
{sprite}
  <a class="skip" href="#main">Skip to content</a>

  <header class="site-header" id="top">
    <div class="wrap header-inner">
      <a href="/" class="brand" aria-label="Sukoon home">
        <svg class="brand-mark"><use href="#d-sparkle"/></svg>
        <span>sukoon</span>
      </a>
      <nav class="nav" id="nav" aria-label="Primary">
        <a href="/#menu">menu</a>
        <a href="/#how">how it works</a>
        <a href="/#areas">areas</a>
        <a href="/#faq">faq</a>
        <a href="/#book" class="btn btn-small">book now</a>
      </nav>
      <button class="nav-toggle" aria-controls="nav" aria-expanded="false" aria-label="Open menu">
        <span></span><span></span>
      </button>
    </div>
  </header>

  <main id="main">
    <section class="hero">
      <div class="wrap">
        <nav class="crumbs" aria-label="Breadcrumb"><a href="/">home</a> / <span>{esc(name.lower())}</span></nav>
      </div>
      <div class="wrap hero-grid">
        <div class="hero-copy reveal">
          <p class="sticker sticker-lime">✶ massage at home · {esc(name.lower())}</p>
          <h1>massage at home in <span class="scribble">{esc(name)}.{squiggle}</span></h1>
          <p class="lede">{esc(a["intro"])}</p>
          <div class="hero-cta">
            <a class="btn" data-wa href="{wa}">
              <svg class="i"><use href="#d-chat"/></svg> book on whatsapp
            </a>
            <a class="link" href="/#book">or use the booking form →</a>
          </div>
        </div>
        <aside class="card quick reveal" aria-label="Quick details">
          <p class="kicker">the quick version</p>
          <ul>
            <li><svg><use href="#d-heart"/></svg><span><strong>₹2,500</strong> per massage, about an hour</span></li>
            <li><svg><use href="#d-pin"/></svg><span><strong>Travel extra</strong>, quoted before you book</span></li>
            <li><svg><use href="#d-cal"/></svg><span><strong>Sat &amp; Sun</strong>, 7 am – 10 pm</span></li>
            <li><svg><use href="#d-moon"/></svg><span>Book <strong>3+ days ahead</strong></span></li>
            <li><svg><use href="#d-lock"/></svg><span><strong>Pay nothing</strong> until I confirm, then a ₹500 UPI advance</span></li>
            <li><svg><use href="#d-shh"/></svg><span><strong>Video call</strong> before your first booking, if you'd like</span></li>
          </ul>
          <a class="link" href="/#how">see exactly how a session works →</a>
        </aside>
      </div>
    </section>

    <section class="section section-tint">
      <div class="wrap areas-grid">
        <div class="reveal">
          <p class="kicker">where in {esc(name)}</p>
          <h2>all over {esc(name)}, <span class="scribble">door to door.{squiggle}</span></h2>
          <ul class="area-cloud">
{loc_items}
          </ul>
          <p class="muted">Close by? I also come to:</p>
          <ul class="area-cloud">
{near_items}
          </ul>
        </div>
        <div class="reveal">
          <p class="kicker">what you get</p>
          <h2>one price. <span class="scribble">four styles.{squiggle}</span></h2>
          <ul class="style-list">
            <li><span class="icon bg-lilac"><svg><use href="#d-waves"/></svg></span><div><h3>Relaxing</h3><p>Long, flowing strokes with gentle to medium pressure.</p></div></li>
            <li><span class="icon bg-peach"><svg><use href="#d-stones"/></svg></span><div><h3>Firm pressure</h3><p>Slower and firmer, focused on the neck, back and shoulders.</p></div></li>
            <li><span class="icon bg-sky"><svg><use href="#d-drop"/></svg></span><div><h3>Aromatherapy</h3><p>A relaxing massage with scented oils chosen for you.</p></div></li>
            <li><span class="icon bg-mint"><svg><use href="#d-face"/></svg></span><div><h3>Head, neck &amp; shoulders</h3><p>For screen fatigue. Can be done seated.</p></div></li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section dark">
      <div class="wrap privacy-grid">
        <div class="reveal">
          <p class="kicker">the important bit</p>
          <h2>chill vibes.<br><span class="hl">clear boundaries.</span></h2>
          <p class="muted-light">I'm not a certified therapist. This is relaxation massage, done respectfully.</p>
        </div>
        <ul class="principles">
          <li class="reveal"><svg><use href="#d-lock"/></svg><div><h3>strictly non-sexual</h3><p>Relaxation massage only. Any request for anything else ends the booking.</p></div></li>
          <li class="reveal"><svg><use href="#d-sheet"/></svg><div><h3>always draped</h3><p>A fresh sheet covers you the whole time.</p></div></li>
          <li class="reveal"><svg><use href="#d-shh"/></svg><div><h3>discreet by default</h3><p>Plain clothes, unbranded bags, and your details stay private.</p></div></li>
          <li class="reveal"><svg><use href="#d-heart"/></svg><div><h3>you're in charge</h3><p>Ask for more or less pressure, or stop at any time.</p></div></li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap faq-grid">
        <div class="reveal">
          <p class="kicker">faq</p>
          <h2>{esc(name)} <span class="scribble">questions.{squiggle}</span></h2>
        </div>
        <div class="faq-list reveal">
{faq_html}
        </div>
      </div>
    </section>

    <section class="section section-tint cta-band">
      <div class="wrap reveal">
        <h2>ready to unwind in <span class="scribble">{esc(name)}?{squiggle}</span></h2>
        <p class="muted">Message me with your locality and a weekend slot. I usually reply within an hour.</p>
        <div class="hero-cta">
          <a class="btn" data-wa href="{wa}"><svg class="i"><use href="#d-chat"/></svg> book on whatsapp</a>
          <a class="link" href="tel:+{PHONE}">or call +91 96072 27768</a>
        </div>
        <p class="kicker">other areas</p>
        <ul class="area-cloud">
{other_items}
        </ul>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p class="footer-word">sukoon<svg><use href="#d-sparkle"/></svg></p>
      <div class="footer-row">
        <p>At-home relaxation massage by Sid · Bengaluru<br>Not a certified therapist. Non-medical, non-sexual massage only.</p>
        <p><a href="tel:+{PHONE}">+91 96072 27768</a><br>© <span id="year">{date.today().year}</span> Sukoon</p>
      </div>
    </div>
  </footer>

  <a class="wa-float" data-wa href="https://wa.me/{PHONE}" aria-label="Chat with Sid on WhatsApp">
    <svg><use href="#d-chat"/></svg>
  </a>

  <script src="/script.js" defer></script>
</body>
</html>
"""


for slug, a in AREAS.items():
    out = ROOT / "massage-at-home" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(area_page(slug, a), encoding="utf-8")


# ---------------------------------------------------------------- sitemap
urls = [(SITE + "/", "1.0")] + [(area_url(s), "0.8") for s in AREAS]
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>\n" for u, p in urls)
    + "</urlset>\n",
    encoding="utf-8",
)

print(f"FAQ schema: {len(pairs)} questions · area pages: {len(AREAS)} · sitemap: {len(urls)} urls")
