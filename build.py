#!/usr/bin/env python3
"""Génère tout le site du studio dans docs/ :

  docs/index.html                    vitrine (catalogue des modèles, essai, commande)
  docs/modeles/<modèle>/             démonstration protégée de chaque modèle (filigrane, rien n'est enregistré)
  docs/e/<slug>/                     invitation d'un client
  docs/e/<slug>/gestion/             gestion des invités du client (connexion Google)
  docs/admin/                        admin du studio (accès des clients, paiement)

Usage : python3 build.py            (tout)
        python3 build.py <slug>     (un seul événement + vitrine + admin)
"""
import hashlib, html, json, re, shutil, subprocess, sys, unicodedata, pathlib
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / 'docs'
STUDIO = json.loads((ROOT / 'studio.json').read_text())

JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

# ---------- petites aides ----------
def h(v): return html.escape(str(v), quote=True)
def j(v):
    s = str(v).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    return s.replace('\n', '\\n').replace('\r', '').replace('</', '<\\/')
def safe_text(v):
    v = str(v)
    assert not re.search(r"[\\'\"`<>&$]", v), f'caractère interdit dans {v!r}'
    return v
def slugify(v):
    v = unicodedata.normalize('NFD', str(v)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', v).strip('-')
def jour_mois(d):
    return ('1er' if d.day == 1 else str(d.day)) + ' ' + MOIS[d.month - 1]
def tel_intl(t):
    d = re.sub(r'\D', '', str(t))
    if d.startswith('0'): d = STUDIO.get('indicatif', '261') + d[1:]
    return d
def version(p):
    return hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else '0'

def fill(tpl, vals):
    def sub(m):
        ctx, key = m.group(1), m.group(2)
        if key not in vals: raise KeyError(f'champ manquant : {key}')
        v = vals[key]
        return {'H': h, 'J': j, 'HJ': lambda x: j(h(x)), 'T': safe_text, 'R': str}[ctx](v)
    out = re.sub(r'⟦(HJ|H|J|T|R)\.(\w+)⟧', sub, tpl)
    assert '⟦' not in out, 'champ non rempli'
    return out

# ---------- blocs du modèle Caramel ----------
SVG_TEL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'
SVG_FB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07z"/></svg>'
SVG_PIN = '<svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg>'

def caramel_values(cfg, slug, folder, demo=False):
    tz = cfg.get('fuseau', STUDIO.get('fuseau', '+03:00'))
    if cfg.get('date') == 'auto':
        # démonstration : toujours un samedi dans environ 6 semaines, réponses ouvertes jusqu'à 1 semaine avant
        d0 = datetime.now() + timedelta(days=42)
        d0 += timedelta(days=(5 - d0.weekday()) % 7)
        cfg = {**cfg, 'date': d0.strftime('%Y-%m-%d') + 'T10:00:00' + tz, 'date_limite': (d0 - timedelta(days=7)).strftime('%Y-%m-%d')}
    jour =datetime.fromisoformat(cfg['date'] if len(cfg['date']) > 10 else cfg['date'] + 'T08:00:00' + tz)
    dl = cfg['date_limite']
    dl_day = datetime.fromisoformat(dl[:10])
    deadline = datetime.fromisoformat(dl if len(dl) > 10 else (dl_day + timedelta(days=1)).strftime('%Y-%m-%d') + 'T00:00:00' + tz)
    hotes = cfg['hotes']
    noms = [x['nom'] for x in hotes]
    lieux = cfg['lieux']
    fb = cfg.get('facebook') or {}
    first = hotes[0]
    gcon = ('<div class="gcon gx rv" style="--d:1.4s">\n        <div class="gc">'
            f'<a class="gtel" href="tel:+{tel_intl(first["tel"])}"><i class="gi">{SVG_TEL}</i><span class="num">{h(first["tel"])}</span></a>'
            + (f'<a class="gfb" href="{h(fb["url"])}" target="_blank" rel="noopener"><i class="gi fb">{SVG_FB}</i><span>{h(fb["nom"])}</span></a>' if fb.get('url') else '')
            + '</div>\n      </div>')
    contacts = ('<div class="contacts rv ngx" style="--d:1.4s;margin-top:50px">\n'
                + ''.join(f'        <a href="tel:+{tel_intl(x["tel"])}"><span class="script" style="font-size:72px">{h(x["nom"])}</span><span class="num">{h(x["tel"])}</span></a>\n' for x in hotes)
                + '      </div>')
    maps = ('<div class="maps rv" style="--d:1.6s">\n'
            + ''.join(f'        <a href="{h(l["maps"])}" target="_blank" rel="noopener">{SVG_PIN}{h(l.get("bouton") or "Map " + l["nom"])}</a>\n' for l in lieux)
            + '      </div>')
    cotes = [[slugify(n), n] for n in noms]
    def btn(file, label, title=''):
        p = folder / file
        if not p.exists(): return ''
        t = f' title="{h(title)}"' if title else ''
        return f'<a class="a-btn sec" href="{file}?v={version(p)}" target="_blank" rel="noopener"{t} style="text-decoration:none;display:inline-flex;align-items:center">{label}</a>'
    def vbtn(file):
        p = folder / file
        if not p.exists(): return ''
        return f'<a class="a-btn sm sec" style="text-decoration:none;display:inline-flex;align-items:center" target="_blank" rel="noopener" href="{file}?v={version(p)}">Vidéo</a>'
    et = ' et '.join([', '.join(noms[:-1]), noms[-1]]) if len(noms) > 1 else noms[0]
    ou = ' ou '.join([', '.join(noms[:-1]), noms[-1]]) if len(noms) > 1 else noms[0]
    amp = ' & '.join(noms)
    url = STUDIO['url_site'].rstrip('/') + (f'/modeles/{cfg["modele"]}/' if demo else f'/e/{slug}/')
    reply = cfg.get('whatsapp_reponse') or hotes[-1]['tel']
    return {
        'titre': cfg['titre'],
        'og_description': cfg.get('description') or f'{JOURS[jour.weekday()].capitalize()} {jour.day} {MOIS[jour.month-1]} {jour.year} · {lieux[0]["nom"]}',
        'phrase_partage': cfg.get('phrase_partage', 'pour partager ce bonheur avec nous'),
        'objet_confirmation': cfg.get('objet_confirmation', 'à votre ' + cfg['titre']),
        'texte_whatsapp': cfg.get('texte_whatsapp') or f"Nous avons la joie de vous inviter à notre {cfg['titre']}, le {JOURS[jour.weekday()]} {jour_mois(jour)} {jour.year} à {jour.hour}h.",
        'signature': cfg.get('signature', amp),
        'table_honneur': cfg.get('table_honneur', amp),
        'hotes_et': et, 'hotes_ou': ou, 'hotes_amp': amp, 'hote1_maj': noms[0].upper(),
        'lieu1': lieux[0]['nom'], 'lieu2': lieux[-1]['nom'],
        'url': url, 'slug': slug,
        'whatsapp': tel_intl(reply),
        'messenger': cfg.get('messenger') or f'https://wa.me/{tel_intl(reply)}',
        'Jour_date': f'{JOURS[jour.weekday()].capitalize()} {jour_mois(jour)} {jour.year}',
        'jour_date': f'{JOURS[jour.weekday()]} {jour_mois(jour)} {jour.year}',
        'date_texte': f'{jour_mois(jour)} {jour.year}',
        'date_points': jour.strftime('%d.%m.%Y'),
        'dl_texte': f'{jour_mois(dl_day)} {dl_day.year}',
        'dl_court': jour_mois(dl_day),
        'deadline_ms': int(deadline.timestamp() * 1000),
        'event_ms': int(jour.timestamp() * 1000),
        'bloc_gcon': gcon, 'bloc_contacts': contacts, 'bloc_maps': maps,
        'cotes_options': ''.join(f'<option value="{k}">Famille {h(n)}</option>' for k, n in cotes),
        'cotes_js': json.dumps(cotes, ensure_ascii=False),
        'btn_imprimer': btn('invitation-a-imprimer.pdf', 'Invitation à imprimer'),
        'btn_etiquette': btn('etiquette-bouteille-vin.pdf', 'Étiquette bouteille de vin', 'A4 portrait, 100 %, sans marges si possible, couper sur les pointillés'),
        'btn_video_generale': vbtn('video-generale.mp4'),
        'btn_video_invitation': vbtn('video-invitation.mp4'),
        'firebase': json.dumps(STUDIO.get('firebase') or {}),
        'v_film': version(folder / 'film.mp4'), 'v_poster': version(folder / 'film.jpg'), 'v_music': version(folder / 'music.mp3'),
    }, {'slug': slug, 'titre': cfg['titre'], 'date': jour.isoformat(), 'date_ms': int(jour.timestamp() * 1000),
        'date_limite_ms': int(deadline.timestamp() * 1000), 'date_texte': f'{jour_mois(jour)} {jour.year}',
        'hotes': amp, 'modele': cfg['modele'], 'url': url}

def copy_media(folder, dest, names):
    dest.mkdir(parents=True, exist_ok=True)
    for n in names:
        p = folder / n
        if p.exists(): shutil.copy2(p, dest / n)

# ---------- démonstration protégée ----------
def demo_film(folder, dest):
    """Film de démonstration : plus petit, filigrane incrusté dans l'image (reste visible même sur une capture d'écran)."""
    src = folder / 'film.mp4'
    cache = folder / '.cache-demo.mp4'
    stamp = folder / '.cache-demo.txt'
    key = version(src) + STUDIO['nom']
    if not (cache.exists() and stamp.exists() and stamp.read_text() == key):
        font = ROOT / 'studio-assets' / 'DejaVuSans-Bold.ttf'
        txt = f"MODÈLE DE DÉMONSTRATION · {STUDIO['nom']}".replace(':', r'\:').replace("'", '')
        dt = (f"drawtext=fontfile={font}:text='{txt}':fontcolor=white@0.55:fontsize=17:borderw=1:bordercolor=black@0.25:"
              "x=(w-text_w)/2:y=h*{y}")
        vf = 'scale=540:960,' + ','.join(dt.format(y=y) for y in ('0.12', '0.5', '0.88'))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-vf', vf, '-c:v', 'libx264', '-preset', 'veryfast',
                        '-crf', '27', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '96k', str(cache)], check=True)
        stamp.write_text(key)
    shutil.copy2(cache, dest / 'film.mp4')

DEMO_CSS = """
<style>
#wm{position:fixed;inset:0;z-index:60;pointer-events:none;overflow:hidden}
#wm span{position:absolute;left:50%;top:50%;width:200vmax;margin-left:-100vmax;transform:translateY(-50%) rotate(-28deg);
  font:600 13px/2.8 'Jost',sans-serif;letter-spacing:.32em;text-transform:uppercase;color:rgba(255,255,255,.34);
  text-shadow:0 0 2px rgba(61,42,27,.35);white-space:pre-wrap;text-align:center;word-spacing:.6em}
#demoBar{position:fixed;left:0;right:0;bottom:0;z-index:70;display:flex;align-items:center;justify-content:center;gap:10px;
  padding:8px 12px calc(8px + env(safe-area-inset-bottom));background:rgba(61,42,27,.88);color:#f5ecdd;font:500 13px/1.2 'Jost',sans-serif;letter-spacing:.04em}
#demoBar a{color:#3d2a1b;background:#f5ecdd;border-radius:30px;padding:8px 14px;text-decoration:none;font-weight:600;white-space:nowrap}
#demoBar span{opacity:.9}
img,video{-webkit-touch-callout:none;-webkit-user-drag:none}
</style>"""

def demo_html(page, studio_url):
    # aucun enregistrement : on retire Firebase, et le lien personnel s'affiche quand même en mode démonstration
    a = page.find('<script type="module">'); b = page.find('</script>', a) + len('</script>')
    assert 'initializeApp' in page[a:b]
    page = page[:a] + page[b:]
    page = page.replace("const demo = /[?&]demo\\b/.test(location.search);\nwindow.__gInfo = m && !demo ? dec(m[1]) : null;",
                        "const demo = true;\nwindow.__gInfo = m ? dec(m[1]) : null;")
    assert 'const demo = true;' in page
    page = page.replace('<video id="film" playsinline', '<video id="film" controlslist="nodownload noplaybackrate" disablepictureinpicture disableremoteplayback playsinline')
    wm = ('MODÈLE DE DÉMONSTRATION · ' + STUDIO['nom'] + '      ') * 6
    marks = '\n'.join(f'<span style="margin-top:{y}vh">{h(wm)}</span>' for y in range(-90, 100, 16))
    extra = (DEMO_CSS + f'\n<div id="wm" aria-hidden="true">{marks}</div>'
             + f'\n<div id="demoBar"><span>Modèle de démonstration</span><a href="../../index.html#commander" target="_top">Commander ce modèle</a></div>'
             + "\n<script>window.__saveRsvp = () => Promise.resolve(); /* démonstration : rien n'est envoyé */"
             + "document.addEventListener('contextmenu',e=>e.preventDefault());document.addEventListener('dragstart',e=>e.preventDefault());</script>\n")
    page = page.replace('</body></html>', extra + '</body></html>')
    page = page.replace('<meta name="robots" content="noindex">', '<meta name="robots" content="noindex">')
    return page

# ---------- construction ----------
def build_event(folder, catalogue, admin_rows):
    cfg = json.loads((folder / 'config.json').read_text())
    demo = bool(cfg.get('demo'))
    slug = folder.name
    tpl_dir = ROOT / 'modeles' / cfg['modele']
    vals, row = caramel_values(cfg, slug, folder, demo)
    inv = fill((tpl_dir / 'invitation.html').read_text(), vals)
    if demo:
        dest = SITE / 'modeles' / cfg['modele']
        if dest.exists(): shutil.rmtree(dest)
        dest.mkdir(parents=True)
        (dest / 'index.html').write_text(demo_html(inv, STUDIO['url_site'].rstrip('/') + '/'))
        copy_media(folder, dest, ['film.jpg', 'music.mp3'])
        demo_film(folder, dest)
        meta = cfg.get('vitrine', {})
        catalogue.append({**meta, 'modele': cfg['modele'], 'titre_demo': cfg['titre'],
                          'perso': '?i=' + __import__('base64').urlsafe_b64encode(json.dumps(
                              {'n': meta.get('famille_exemple', 'Famille Rakoto'), 's': 4, 'id': 'demo', 'a': 2, 'e': 2}, ensure_ascii=False).encode()).decode().rstrip('=')})
        print(f'  démo  modeles/{cfg["modele"]}/')
        return
    dest = SITE / 'e' / slug
    if dest.exists(): shutil.rmtree(dest)
    (dest / 'gestion').mkdir(parents=True)
    (dest / 'index.html').write_text(inv)
    (dest / 'gestion' / 'index.html').write_text(fill((tpl_dir / 'gestion.html').read_text(), vals))
    copy_media(folder, dest, ['film.mp4', 'film.jpg', 'music.mp3'])
    copy_media(folder, dest / 'gestion', ['invitation-a-imprimer.pdf', 'etiquette-bouteille-vin.pdf', 'video-generale.mp4', 'video-invitation.mp4'])
    admin_rows.append(row)
    print(f'  client e/{slug}/')

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    SITE.mkdir(exist_ok=True)
    (SITE / '.nojekyll').write_text('')
    catalogue, admin_rows = [], []
    for folder in sorted((ROOT / 'evenements').iterdir()):
        if not (folder / 'config.json').exists(): continue
        cfg = json.loads((folder / 'config.json').read_text())
        if only and folder.name != only and not cfg.get('demo'):
            # garder la ligne admin des événements non reconstruits
            admin_rows.append(caramel_values(cfg, folder.name, folder)[1]); continue
        build_event(folder, catalogue, admin_rows)
    sys.path.insert(0, str(ROOT / 'outils'))
    import pages_studio
    (SITE / 'index.html').write_text(pages_studio.vitrine(STUDIO, catalogue))
    (SITE / 'admin').mkdir(exist_ok=True)
    (SITE / 'admin' / 'index.html').write_text(pages_studio.admin(STUDIO))
    (SITE / 'admin' / 'evenements.json').write_text(json.dumps(admin_rows, ensure_ascii=False, indent=1))
    (ROOT / 'firestore.rules').write_text(pages_studio.rules(STUDIO))
    print('  vitrine, admin, firestore.rules')

if __name__ == '__main__':
    main()
