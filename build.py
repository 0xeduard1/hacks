"""Builds the Hack Library static site from data/ into docs/ (served by GitHub Pages).

Add a hack: drop a JSON file in data/hacks/ (same fields as the others), run `python3 build.py`, commit, push.
"""
import json, html, shutil, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
BASE = "/hacks"                       # GitHub Pages path; change to "" on a custom domain
SITE = "https://0xeduard1.github.io" + BASE
KIT = "https://0xeduard1.kit.com/d7db093bd4"
X = "https://x.com/0xeduard1"
e = html.escape

monsters = {m["slug"]: m for m in json.loads((ROOT / "data/monsters.json").read_text())}
hacks = sorted((json.loads(p.read_text()) for p in (ROOT / "data/hacks").glob("*.json")),
               key=lambda h: h["date"], reverse=True)
biggest = max(h["loss_usd"] for h in hacks)


def money(n):
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.0f}M"
    return f"${n/1e3:.0f}K"


def date_h(d):
    return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")


def page(title, desc, body, path, extra_head=""):
    url = SITE + path
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/static/code-mage.png"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary"><meta name="twitter:site" content="@0xeduard1">
<link rel="icon" href="{BASE}/static/favicon.png">
<link rel="alternate" type="application/rss+xml" title="Hack Library" href="{BASE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fredoka:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/static/style.css">
{extra_head}</head><body>
<div class="wrap"><header class="top">
<a class="brand" href="{BASE}/"><img src="{BASE}/static/mage-180.png" alt=""><span><b>Hack Library</b><small>by 0xeduard1</small></span></a>
<nav><a href="{BASE}/#monsters">Monsters</a><a href="{BASE}/#hacks">All hacks</a><a href="{KIT}">Newsletter</a></nav>
</header></div>
<main>{body}</main>
<footer><div class="wrap"><span>I'm Eduard, learning smart contract security from zero and writing down every hack I study. Facts are checked against the linked sources; amounts are approximate, in USD at the time.</span>
<span class="links"><a href="{X}">X</a>  <a href="https://github.com/0xeduard1">GitHub</a>  <a href="{KIT}">Newsletter</a>  <a href="{BASE}/feed.xml">RSS</a></span></div></footer>
</body></html>"""


def card(h):
    m = monsters[h["monster"]]
    pct = max(4, round(100 * h["loss_usd"] / biggest))
    ret = '<span class="tag ok">Funds returned</span>' if h.get("returned") else ""
    return f"""<a class="card" href="{BASE}/h/{h['slug']}/" data-monster="{m['slug']}" data-date="{h['date']}" data-loss="{h['loss_usd']}" data-text="{e((h['name']+' '+h['tldr']+' '+m['class']+' '+h['chain']).lower())}">
<span class="sticker" title="{e(m['name'])}" aria-hidden="true">{m['emoji']}</span>
<h3>{e(h['name'])}</h3>
<span class="meta">{date_h(h['date'])} on {e(h['chain'])}</span>
<span class="dmg">💥 {money(h['loss_usd'])}<span class="bar" aria-hidden="true"><i style="width:{pct}%"></i></span></span>
<p>{e(h['tldr'])}</p>
<span class="tag">{m['emoji']} {e(m['class'])}</span>{ret}
</a>"""


def cta():
    return f"""<section class="cta"><img src="{BASE}/static/mage-180.png" alt="">
<div><h2>Get the free cheat sheet</h2><p>10 crypto hacks, 3 lines each, plus one new hack explained every week by email.</p>
<a class="btn" href="{KIT}">Send me the cheat sheet</a></div></section>"""


def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "static").mkdir(parents=True)
    for f in (ROOT / "static").iterdir(): shutil.copy(f, OUT / "static" / f.name)
    (OUT / ".nojekyll").write_text("")
    counts = {s: sum(h["monster"] == s for h in hacks) for s in monsters}

    # home
    chips = "".join(f'<button class="mon" data-filter="{s}" aria-pressed="false"><span class="ico">{m["emoji"]}</span><span>{e(m["name"])}<br><small>{e(m["class"])}, {counts[s]} {"hack" if counts[s]==1 else "hacks"}</small></span></button>'
                    for s, m in monsters.items() if counts[s])
    total = sum(h["loss_usd"] for h in hacks)
    home = f"""<div class="wrap">
<section class="hero"><div>
<h1>Every crypto hack is a lesson.</h1>
<p>I'm learning to find bugs before hackers do. This is my library of real hacks, each one explained simply: what broke, why, and how to stop it.</p>
<p class="count">{len(hacks)} hacks studied so far, {money(total)} lost.</p>
<a class="btn" href="#hacks">Start reading</a> <a class="btn ghost" href="{KIT}">Free cheat sheet</a>
</div><div class="mage"><span class="bubble">Pick a monster to see its hacks!</span><img src="{BASE}/static/code-mage.png" alt="Code Mage, the 0xeduard1 mascot"></div></section>

<h2 class="section-title" id="monsters">Bug monsters</h2>
<p class="section-sub">Every hack belongs to a family of bugs. Learn the monsters and you'll spot them in new code.</p>
<div class="bestiary" role="group" aria-label="Filter by bug monster">
<button class="mon" data-filter="all" aria-pressed="true"><span class="ico">🧙</span><span>All monsters<br><small>{len(hacks)} hacks</small></span></button>{chips}</div>

<h2 class="section-title" id="hacks">The library</h2>
<div class="tools"><label class="sr" hidden for="q">Search</label>
<input id="q" type="search" placeholder="Search a protocol or a bug, e.g. bridge" aria-label="Search hacks">
<select id="sort" aria-label="Sort hacks"><option value="new">Newest first</option><option value="old">Oldest first</option><option value="big">Biggest loss</option></select></div>
<div class="grid" id="grid">{''.join(card(h) for h in hacks)}</div>
<p class="empty" id="empty">No hack matches that yet. Try another word, or pick "All monsters".</p>
{cta()}
</div>
<script>
const grid=document.getElementById('grid'),cards=[...grid.children],q=document.getElementById('q'),sort=document.getElementById('sort'),empty=document.getElementById('empty');
let mon='all';
function apply(){{const t=q.value.trim().toLowerCase();let n=0;
 const s=[...cards].sort((a,b)=>sort.value==='big'?b.dataset.loss-a.dataset.loss:sort.value==='old'?a.dataset.date.localeCompare(b.dataset.date):b.dataset.date.localeCompare(a.dataset.date));
 s.forEach(c=>{{const ok=(mon==='all'||c.dataset.monster===mon)&&(!t||c.dataset.text.includes(t));c.hidden=!ok;if(ok)n++;grid.appendChild(c)}});
 empty.style.display=n?'none':'block'}}
document.querySelectorAll('.mon').forEach(b=>b.addEventListener('click',()=>{{mon=b.dataset.filter;
 document.querySelectorAll('.mon').forEach(x=>x.setAttribute('aria-pressed',x===b));apply();document.getElementById('hacks').scrollIntoView()}}));
q.addEventListener('input',apply);sort.addEventListener('change',apply);
</script>"""
    (OUT / "index.html").write_text(page("Hack Library: real crypto hacks, explained simply", "A growing library of real crypto and DeFi hacks, each explained for beginners: what broke, why, how to prevent it, and the lesson for auditors.", home, "/"))

    # hack pages
    for i, h in enumerate(hacks):
        m = monsters[h["monster"]]
        newer, older = (hacks[i - 1] if i else None), (hacks[i + 1] if i + 1 < len(hacks) else None)
        steps = [("🏰", "What was it?", h["what"]), ("💥", "What happened", h["happened"]),
                 (m["emoji"], "The bug, in plain words", h["bug"]), ("🛡️", "How it could have been stopped", h["prevent"]),
                 ("🧙", "The lesson for an auditor", h["lesson"])]
        path = "".join(f'<li><span class="step" aria-hidden="true">{ic}</span><h2>{t}</h2><p>{e(x)}</p></li>' for ic, t, x in steps)
        srcs = "".join(f'<li><a href="{e(s["url"])}" rel="nofollow noopener">{e(s["title"])}</a></li>' for s in h["sources"])
        level = "🟢 easy" if h["level"] == 1 else "🟡 medium" if h["level"] == 2 else "🔴 tricky"
        nav = (f'<a class="btn ghost" href="{BASE}/h/{older["slug"]}/">Older: {e(older["name"])}</a>' if older else "<span></span>") + \
              (f'<a class="btn ghost" href="{BASE}/h/{newer["slug"]}/">Newer: {e(newer["name"])}</a>' if newer else "")
        body = f"""<div class="wrap"><div class="read">
<p class="crumbs"><a href="{BASE}/">Hack Library</a> / <a href="{BASE}/monsters/{m['slug']}/">{e(m['name'])}</a></p>
<div class="hack-head"><span class="big-sticker" aria-hidden="true">{m['emoji']}</span>
<div><h1>{e(h['name'])}</h1><span class="tag">{m['emoji']} {e(m['class'])}</span>{' <span class="tag ok">Funds returned</span>' if h.get('returned') else ''}</div></div>
<div class="facts"><span class="fact money"><b>💥 {money(h['loss_usd'])}</b>{e(h['loss_note'])}</span>
<span class="fact"><b>{date_h(h['date'])}</b>date</span><span class="fact"><b>{e(h['chain'])}</b>chain</span><span class="fact"><b>{level}</b>to understand</span></div>
<p class="tldr">{e(h['tldr'])}</p>
<ol class="path">{path}</ol>
<section class="box"><h2>Meet the monster: {m['emoji']} {e(m['name'])}</h2><p>{e(m['explain'])}</p><p><a href="{BASE}/monsters/{m['slug']}/">See every {e(m['class'].lower())} hack</a></p></section>
<section class="box"><h2>Sources</h2><ul>{srcs}</ul></section>
{cta()}
<nav class="next" aria-label="More hacks">{nav}</nav>
</div></div>"""
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": f"{h['name']} hack explained",
                         "datePublished": h["added"], "author": {"@type": "Person", "name": "Eduard (0xeduard1)"},
                         "about": m["class"], "description": h["tldr"]})
        d = OUT / "h" / h["slug"]; d.mkdir(parents=True)
        (d / "index.html").write_text(page(f"{h['name']} hack ({h['date'][:4]}) explained simply · Hack Library", h["tldr"], body,
                                            f"/h/{h['slug']}/", f'<script type="application/ld+json">{ld}</script>'))

    # monster pages
    for s, m in monsters.items():
        mine = [h for h in hacks if h["monster"] == s]
        if not mine: continue
        body = f"""<div class="wrap"><section class="mon-hero"><span class="big-sticker" aria-hidden="true">{m['emoji']}</span>
<h1>{e(m['name'])}</h1><p>{e(m['class'])}: {e(m['short'])}</p></section>
<div class="read" style="margin:0 auto"><section class="box"><h2>How it attacks</h2><p>{e(m['explain'])}</p></section>
<section class="box"><h2>How to defend</h2><p>{e(m['defend'])}</p></section></div>
<h2 class="section-title">Hacks by {e(m['name'])}</h2><div class="grid">{''.join(card(h) for h in mine)}</div>{cta()}</div>"""
        d = OUT / "monsters" / s; d.mkdir(parents=True)
        (d / "index.html").write_text(page(f"{m['class']} hacks explained · Hack Library", f"{m['class']} in smart contracts: how it works, how to defend, and real hacks it caused.", body, f"/monsters/{s}/"))

    # 404, sitemap, robots, feed
    (OUT / "404.html").write_text(page("Page not found · Hack Library", "Page not found", f'<div class="wrap"><section class="mon-hero"><span class="big-sticker">🫥</span><h1>This page vanished.</h1><p>Like a self-destructed contract. <a href="{BASE}/">Back to the library</a></p></section></div>', "/404.html"))
    urls = ["/"] + [f"/h/{h['slug']}/" for h in hacks] + [f"/monsters/{s}/" for s in monsters if counts[s]]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                                     "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls) + "</urlset>")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    items = "".join(f"<item><title>{e(h['name'])} hack explained</title><link>{SITE}/h/{h['slug']}/</link><guid>{SITE}/h/{h['slug']}/</guid><pubDate>{datetime.date.fromisoformat(h['added']).strftime('%a, %d %b %Y 08:00:00 +0000')}</pubDate><description>{e(h['tldr'])}</description></item>"
                    for h in sorted(hacks, key=lambda h: h["added"], reverse=True)[:30])
    (OUT / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Hack Library by 0xeduard1</title><link>{SITE}/</link><description>Real crypto hacks, explained simply.</description>{items}</channel></rss>')
    print(f"built {len(hacks)} hacks, {sum(1 for c in counts.values() if c)} monsters -> {OUT}")


if __name__ == "__main__":
    build()
