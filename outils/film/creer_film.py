#!/usr/bin/env python3
"""Crée le film d'ouverture vertical d'un événement à partir de ses photos, de ses textes et de sa musique.

Usage :
  python3 outils/film/creer_film.py <slug> --apercu      images test (une par scène, au moment le plus chargé)
  python3 outils/film/creer_film.py <slug>               film complet → evenements/<slug>/film.mp4 + film.jpg

Entrées dans evenements/<slug>/ :
  config.json   titre, date, hôtes, lieux (déjà utilisés par le site)
  film.json     facultatif : scènes, textes, programme, verset (voir FILM_DEFAUT plus bas)
  photo*.jpg    photos du couple / de la famille (dans l'ordre des noms)
  lieu1.jpg …   photo de chaque lieu (facultatif)
  music.mp3     musique (facultatif)
Chaque scène est filmée image par image dans Chromium (animations CSS figées à l'instant voulu), encodée dans son
propre fichier, puis les fichiers sont joints sans réencodage et la musique est ajoutée.
"""
import html, json, os, pathlib, shutil, subprocess, sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
W, H, FPS = 720, 1280, 30
JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
def e(v): return html.escape(str(v))

# ---------- habillage commun (papier, cadre, pétales) ----------
CSS = """
*{box-sizing:border-box}html,body{margin:0;width:720px;height:1280px;overflow:hidden;background:#f5ecdd}
:root{--paper:#f5ecdd;--caramel:#a87c50;--brown:#6b4a2f;--espresso:#3d2a1b;--script:'Great Vibes',cursive;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Jost',Arial,sans-serif}
.sc{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse at 50% 42%,#fbf5ea 0%,#f3e7d4 60%,#e6d4b8 100%)}
.frame{position:absolute;inset:34px;border:1.5px solid rgba(139,100,64,.5)}.frame::after{content:"";position:absolute;inset:8px;border:1px solid rgba(139,100,64,.28)}
.col{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 80px}
.kicker{font:500 19px/1.5 var(--sans);letter-spacing:.34em;text-transform:uppercase;color:var(--caramel)}
.script{font:400 96px/1.02 var(--script);color:var(--brown)}
.serif{font-family:var(--serif);color:var(--espresso)}
.rule{width:220px;height:1.5px;background:var(--caramel);opacity:.6;margin:22px auto}
.in{opacity:0;animation:in 1.3s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}
@keyframes in{from{opacity:0;transform:translateY(26px);filter:blur(7px)}to{opacity:1;transform:none;filter:none}}
.pop{opacity:0;animation:pop 1.1s cubic-bezier(.2,.8,.25,1.15) var(--d,0s) both}
@keyframes pop{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}
.fade{position:absolute;inset:0;background:#f5ecdd;pointer-events:none;animation:fio var(--dur) linear both;z-index:50}
@keyframes fio{0%{opacity:1}9%{opacity:0}91%{opacity:0}100%{opacity:1}}
.petal{position:absolute;top:-40px;width:var(--w);height:calc(var(--w)*.55);left:var(--x);animation:fall var(--t) linear var(--dl) infinite;z-index:30}
.petal::before{content:"";position:absolute;inset:0;background:var(--c);border-radius:0 100% 0 100%;transform:rotate(25deg);opacity:.85}
@keyframes fall{0%{transform:translate(0,0) rotate(0)}100%{transform:translate(var(--dx),1360px) rotate(520deg)}}
.dove{position:absolute;z-index:60!important;width:110px;height:69px;filter:drop-shadow(0 3px 4px rgba(61,42,27,.25));z-index:31;animation:fly var(--t) linear var(--dl) infinite}
@keyframes fly{0%{transform:translate(-120px,var(--y)) scale(var(--s))}100%{transform:translate(860px,calc(var(--y) - 160px)) scale(var(--s))}}
.dove svg{width:100%;height:100%;overflow:visible}.dove .wing{transform-origin:30px 22px;animation:flap .5s ease-in-out infinite alternate}
@keyframes flap{from{transform:scaleY(1)}to{transform:scaleY(-.55)}}
/* photo dans une arche */
.arch{position:absolute;left:96px;right:96px;top:250px;height:760px;border-radius:264px 264px 18px 18px;overflow:hidden;box-shadow:0 22px 44px rgba(61,42,27,.3);background:#e6d4b8}
.arch::after{content:"";position:absolute;inset:0;border-radius:inherit;box-shadow:inset 0 0 0 8px rgba(245,236,221,.92),inset 0 0 0 9.5px rgba(168,124,80,.6)}
.arch img{position:absolute;inset:-4%;width:108%;height:108%;object-fit:cover;animation:kb var(--dur) linear both}
@keyframes kb{from{transform:scale(1.12) translate(var(--kx,1%),var(--ky,1%))}to{transform:scale(1) translate(0,0)}}
.cap{position:absolute;left:60px;right:60px;top:1040px;text-align:center}
.prog{display:flex;flex-direction:column;gap:30px;margin-top:40px;align-self:stretch;text-align:left;padding-left:30px}
.prog .it{display:grid;grid-template-columns:150px 1fr;align-items:baseline;border-bottom:1px solid rgba(139,100,64,.25);padding-bottom:18px}
.prog .h{font:600 52px/1 var(--serif);color:var(--espresso);font-variant-numeric:lining-nums}
.prog .t{font:italic 38px/1.2 var(--serif);color:var(--brown)}
.verse{font:italic 44px/1.35 var(--serif);color:var(--espresso);max-width:560px}
.flw{position:absolute;pointer-events:none;z-index:20}.flw svg{width:100%;height:100%;overflow:visible}
.flw .sw{transform-box:fill-box;transform-origin:50% 100%;animation:flsway 4s ease-in-out infinite alternate}
@keyframes flsway{from{transform:rotate(-2deg)}to{transform:rotate(2deg)}}
.flw.top{left:50%;top:44px;width:480px;height:168px;margin-left:-240px}
.flw.bot{left:50%;bottom:44px;width:420px;height:138px;margin-left:-210px;transform:rotate(180deg)}
.flw.c1{left:-4px;top:-4px;width:150px;height:150px;transform:scaleX(-1)}.flw.c2{right:-4px;top:-4px;width:150px;height:150px}
"""

DOVE = '<svg viewBox="0 0 64 40"><path d="M6 24c10-2 18 0 26 4 6-6 14-8 24-6-6 2-10 6-12 10-8 4-22 4-38-8z" fill="#fffaf2" stroke="#c9b393" stroke-width="1"/><path class="wing" d="M28 22c-2-10 4-18 16-20-4 6-4 12-2 18z" fill="#fffaf2" stroke="#c9b393" stroke-width="1"/><circle cx="54" cy="22" r="1.4" fill="#6b4a2f"/></svg>'

def decor(seed, dur, petals=9, doves=2, t0=0.0):
    import random
    rnd = random.Random(seed)
    cols = ['#a87c50', '#c9a67a', '#8a6240', '#d8c09b', '#b58d62']
    out = ''.join(f'<i class="petal" style="--x:{rnd.randint(10, 700)}px;--w:{rnd.randint(16, 26)}px;--t:{rnd.uniform(7, 11):.1f}s;--dl:-{rnd.uniform(0, 10):.1f}s;--dx:{rnd.randint(-60, 60)}px;--c:{rnd.choice(cols)}"></i>' for _ in range(petals))
    # colombes : vol continu, toutes à la même hauteur de départ, jamais d'arrêt
    out += ''.join(f'<div class="dove" style="--t:{9 + k * 1.5:.1f}s;--dl:-{(k * 4.3 + 1 + t0):.2f}s;--y:{300 + k * 30}px;--s:{.9 - k * .15:.2f}">{DOVE}</div>' for k in range(doves))
    return out

def page(body, dur, seed, fleurs_mode='plein', t0=0.0):
    fleurs = {'plein': '<div class="flw in top" data-g="top" style="--d:.2s"></div><div class="flw in bot" data-g="bottom" style="--d:.5s"></div>',
              'coins': '<div class="flw in c1" data-g="small" style="--d:.2s"></div><div class="flw in c2" data-g="small" style="--d:.3s"></div>'}[fleurs_mode]
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{(HERE / "polices.css").read_text()}{CSS}</style></head><body>'
            f'<div class="sc" style="--dur:{dur}s"><div class="frame"></div>{fleurs}{body}{decor(seed, dur, t0=t0)}<div class="fade"></div></div>'
            f'<script>{(HERE / "fleurs.js").read_text()}</script></body></html>')

# ---------- scènes ----------
def sc_titre(f):
    return f"""<div class="col">
  <div class="kicker in" style="--d:.4s">Vous êtes invités</div>
  <div class="serif in" style="--d:.9s;font-size:32px;font-style:italic;margin-top:10px">à la célébration du</div>
  <div class="script in" style="--d:1.5s;margin-top:22px">{e(f['titre'])}</div>
  <div class="serif in" style="--d:2.4s;font:600 60px/1.1 var(--serif);margin-top:26px">{e(f['h1'])} <span style="font-family:var(--script);font-weight:400;color:var(--caramel);font-size:52px">&amp;</span> {e(f['h2'])}</div>
  {f'<div class="serif in" style="--d:3s;font:600 30px var(--sans);letter-spacing:.2em;margin-top:22px">{e(f["sous_titre"])}</div>' if f.get('sous_titre') else ''}
  <div class="rule in" style="--d:3.4s"></div>
  <div class="serif in" style="--d:3.8s;font:500 30px var(--sans);letter-spacing:.06em">{e(f['date_longue'])}</div>
</div>"""

def sc_photo(p, cap, k):
    kx, ky = [('2%', '1%'), ('-2%', '2%'), ('1%', '-2%'), ('-1%', '-1%')][k % 4]
    return f"""<div class="kicker in" style="--d:.3s;position:absolute;left:0;right:0;top:150px;text-align:center">{e(cap.get('haut', ''))}</div>
<div class="arch in" style="--d:.1s"><img src="{p.as_uri()}" style="--kx:{kx};--ky:{ky}"></div>
<div class="cap"><div class="script in" style="--d:.9s;font-size:{cap.get('taille', 78)}px">{e(cap.get('texte', ''))}</div></div>"""

def sc_programme(f):
    items = ''.join(f'<div class="it in" style="--d:{1.2 + i * .6:.1f}s"><span class="h">{e(x["heure"])}</span><span class="t">{e(x["texte"])}</span></div>' for i, x in enumerate(f['programme']))
    return f"""<div class="col"><div class="kicker in" style="--d:.3s">{e(f['date_longue'])}</div>
<div class="script in" style="--d:.7s;margin-top:16px">Au programme</div><div class="prog">{items}</div></div>"""

def sc_lieu(l, p, i):
    img = f'<div class="arch in" style="--d:.1s;top:330px;height:640px"><img src="{p.as_uri()}"></div>' if p else ''
    top = 'top:150px' if p else 'top:0;bottom:0;display:flex;flex-direction:column;justify-content:center'
    return f"""<div style="position:absolute;left:60px;right:60px;{top};text-align:center">
  <div class="kicker in" style="--d:.3s">{e(l.get('moment', ''))}</div>
  <div class="serif in" style="--d:.6s;font:600 46px/1.15 var(--serif);margin-top:12px">{e(l['nom'])}</div></div>
{img}<div class="cap" style="top:{1010 if p else 900}px"><div class="serif in" style="--d:1s;font:italic 32px var(--serif)">{e(l.get('adresse', ''))}</div></div>"""

def sc_verset(f):
    return f"""<div class="col"><div class="verse in" style="--d:.6s">« {e(f['verset']['texte'])} »</div>
<div class="kicker in" style="--d:1.6s;margin-top:34px">{e(f['verset'].get('ref', ''))}</div></div>"""

def sc_fin(f):
    return f"""<div class="col"><div class="script in" style="--d:.5s;font-size:84px">Votre présence sera pour nous un grand honneur</div>
<div class="rule in" style="--d:1.4s"></div><div class="kicker pop" style="--d:1.9s">{e(f['titre'])} · {e(f['date_points'])}</div></div>"""

# ---------- plan du film ----------
def plan(slug):
    folder = ROOT / 'evenements' / slug
    cfg = json.loads((folder / 'config.json').read_text())
    fj = json.loads((folder / 'film.json').read_text()) if (folder / 'film.json').exists() else {}
    d = datetime.fromisoformat(cfg['date'])
    hs = cfg['hotes']
    f = {'titre': fj.get('titre', cfg['titre']), 'h1': hs[0]['nom'], 'h2': hs[-1]['nom'], 'sous_titre': fj.get('sous_titre', ''),
         'date_longue': f"{JOURS[d.weekday()].capitalize()} {d.day if d.day > 1 else '1er'} {MOIS[d.month - 1]} {d.year}",
         'date_points': d.strftime('%d.%m.%Y'),
         'programme': fj.get('programme') or [{'heure': d.strftime('%-Hh%M').replace('h00', ' h'), 'texte': cfg['lieux'][0]['nom']}],
         'verset': fj.get('verset')}
    photos = sorted(folder.glob('photo*.jpg'))
    caps = fj.get('legendes', [])
    scenes = [('titre', 7, sc_titre(f))]
    for k, p in enumerate(photos):
        scenes.append((f'photo{k + 1}', 4.5, sc_photo(p, caps[k] if k < len(caps) else {'texte': f"{f['h1']} & {f['h2']}" if k == 0 else ''}, k)))
    scenes.append(('programme', 2.5 + .7 * len(f['programme']) + 2.5, sc_programme(f)))
    for i, l in enumerate(cfg['lieux']):
        p = folder / f'lieu{i + 1}.jpg'
        info = {**l, **(fj.get('lieux', [{}] * 9)[i] if i < len(fj.get('lieux', [])) else {})}
        scenes.append((f'lieu{i + 1}', 4.5, sc_lieu(info, p if p.exists() else None, i)))
    if f['verset']: scenes.append(('verset', 6, sc_verset(f)))
    scenes.append(('fin', 6, sc_fin(f)))
    return folder, scenes

def busiest(dur):  # moment où presque tout est apparu
    return min(dur - 0.8, 4.2)

def render(slug, apercu=False):
    from playwright.sync_api import sync_playwright
    folder, scenes = plan(slug)
    work = folder / '.film'
    work.mkdir(exist_ok=True)
    out_files = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H})
        t0 = 0.0
        for k, (name, dur, body) in enumerate(scenes):
            hp = work / f'{name}.html'
            hp.write_text(page(body, dur, k, 'coins' if name.startswith(('photo', 'lieu')) and '<img' in body else 'plein', t0))
            t0 += round(dur * FPS) / FPS  # les colombes continuent leur vol d'une scène à l'autre
            pg.goto(hp.as_uri()); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(150)
            pg.evaluate("document.getAnimations().forEach(a => a.pause())")
            seek = lambda t: pg.evaluate(f"document.getAnimations().forEach(a => a.currentTime = {t * 1000})")
            if apercu:
                seek(busiest(dur)); pg.screenshot(path=str(work / f'apercu-{k:02d}-{name}.jpg'), type='jpeg', quality=88)
                print(f'  aperçu {name}'); continue
            n = int(round(dur * FPS))
            tmp = work / f'{k:02d}-{name}.part.mp4'
            enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(tmp)],
                                   stdin=subprocess.PIPE)
            for i in range(n):
                seek(i / FPS)
                enc.stdin.write(pg.screenshot(type='jpeg', quality=92))
            enc.stdin.close()
            assert enc.wait() == 0, f'ffmpeg a échoué ({name})'
            final = work / f'{k:02d}-{name}.mp4'; tmp.rename(final); out_files.append(final)
            print(f'  scène {name} : {dur:.1f} s')
        b.close()
    if apercu:
        return sorted(work.glob('apercu-*.jpg'))
    lst = work / 'liste.txt'
    lst.write_text(''.join(f"file '{p.name}'\n" for p in out_files))
    video = work / 'video.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(video)], check=True)
    total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)]))
    music = folder / 'music.mp3'
    tmp = folder / 'film.part.mp4'
    if music.exists():
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(video), '-i', str(music), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', f'afade=t=in:d=1,afade=t=out:st={total - 3:.2f}:d=3', '-c:a', 'aac', '-b:a', '160k', '-t', f'{total:.2f}',
                        '-movflags', '+faststart', str(tmp)], check=True)
    else:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(video), '-c', 'copy', '-movflags', '+faststart', str(tmp)], check=True)
    tmp.rename(folder / 'film.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '3.5', '-i', str(folder / 'film.mp4'), '-frames:v', '1', '-q:v', '3', str(folder / 'film.jpg')], check=True)
    print(f'  film.mp4 : {total:.1f} s')
    return folder / 'film.mp4'

if __name__ == '__main__':
    r = render(sys.argv[1], '--apercu' in sys.argv)
    print(r)
