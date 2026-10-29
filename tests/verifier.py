#!/usr/bin/env python3
"""Vérifie le site généré sur un téléphone simulé (390 × 844) avec une fausse base Firestore.
Usage : python3 tests/verifier.py [chemin de xlsx.full.min.js]
Captures dans tests/out/."""
import json, re, subprocess, sys, time, pathlib, functools, http.server, threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE, OUT, FAKE = ROOT / 'site', ROOT / 'tests' / 'out', ROOT / 'tests' / 'fake'
OUT.mkdir(exist_ok=True)
XLSX = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
tpl = (ROOT / 'modeles' / 'caramel' / 'invitation.html').read_text()
FONT_CSS = '\n'.join(re.findall(r'@font-face \{.*?\}', tpl, re.S))

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle(self):
        try: super().handle()
        except (ConnectionResetError, BrokenPipeError): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), functools.partial(Quiet, directory=str(SITE)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:8765/'
ok, ko = [], []
def check(name, cond, info=''):
    (ok if cond else ko).append(name + ('' if cond else f' → {info}'))
    print(('  OK  ' if cond else '  ÉCHEC ') + name + ('' if cond else f' → {info}'))

def routes(ctx):
    def gstatic(route):
        name = route.request.url.split('/')[-1]
        route.fulfill(path=str(FAKE / name), content_type='application/javascript')
    ctx.route(re.compile(r'https://www\.gstatic\.com/firebasejs/.*'), gstatic)
    ctx.route(re.compile(r'https://fonts\.googleapis\.com/.*'), lambda r: r.fulfill(body=FONT_CSS, content_type='text/css'))
    ctx.route(re.compile(r'https://fonts\.gstatic\.com/.*'), lambda r: r.abort())
    if XLSX: ctx.route(re.compile(r'https://cdnjs\.cloudflare\.com/.*xlsx.*'), lambda r: r.fulfill(path=str(XLSX), content_type='application/javascript'))
    def admin(route):
        body = (SITE / 'admin' / 'index.html').read_text().replace('const FB = null', 'const FB = {"projectId":"test"}')
        route.fulfill(body=body, content_type='text/html')
    ctx.route(BASE + 'admin/', admin)

def page(b, user=None, admins=None, db=None, now=None):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale='fr-FR')
    routes(ctx)
    init = f"window.__FAKE_USER = {json.dumps(user)}; window.__FAKE_LOGIN = {json.dumps(user)}; window.__FAKE_ADMINS = {json.dumps(admins or [])};"
    if db is not None: init += f"if (!sessionStorage.getItem('seeded')) {{ localStorage.setItem('FAKEDB', {json.dumps(json.dumps(db))}); sessionStorage.setItem('seeded','1'); }}"
    if now: init += f"(() => {{ const T = {now}, D = Date, off = T - D.now(); class FD extends D {{ constructor(...a) {{ super(...(a.length ? a : [D.now() + off])); }} static now() {{ return D.now() + off; }} }} window.Date = FD; }})();"
    ctx.add_init_script(init)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    return ctx, p, errs

def skip_film(p):
    p.wait_for_timeout(800)
    p.click('#skipBtn')
    p.wait_for_timeout(2600)

EV = json.loads((SITE / 'admin' / 'evenements.json').read_text())[0]
SLUG = EV['slug']
CLIENT, STUDIO_MAIL, OTHER = 'client.test@gmail.com', 'oasismdg3434@gmail.com', 'inconnu@gmail.com'
DB0 = {'evenements': {SLUG: {'actif': True, 'clients': [CLIENT], 'depenses': CLIENT, 'dateLimite': EV['date_limite_ms'], 'titre': EV['titre']}}}

with sync_playwright() as pw:
    b = pw.chromium.launch()

    print('1. Vitrine')
    ctx, p, errs = page(b)
    p.goto(BASE); p.wait_for_timeout(600)
    p.screenshot(path=OUT / '01-vitrine.png')
    p.locator('#modeles').scroll_into_view_if_needed(); p.wait_for_timeout(300)
    p.screenshot(path=OUT / '02-vitrine-modeles.png')
    p.locator('#commander').scroll_into_view_if_needed(); p.wait_for_timeout(300)
    p.screenshot(path=OUT / '03-vitrine-commander.png')
    check('vitrine sans erreur', not errs, errs)
    check('vitrine : 1 modèle', p.locator('.model').count() == 1)
    ctx.close()

    print('2. Démo lien général')
    ctx, p, errs = page(b)
    p.goto(BASE + 'modeles/caramel/'); p.wait_for_timeout(700)
    p.screenshot(path=OUT / '04-demo-film.png')
    skip_film(p)
    p.screenshot(path=OUT / '05-demo-general-page1.png')
    check('démo : filigrane présent', p.locator('#wm span').count() > 3)
    check('démo : bandeau Commander', p.locator('#demoBar a').is_visible())
    check('démo : pas de Firebase', 'initializeApp' not in p.content())
    p.mouse.click(195, 300); p.wait_for_timeout(2600)
    p.screenshot(path=OUT / '06-demo-general-confirmation.png')
    check('démo générale : pas de formulaire', not p.locator('#yes').is_visible())
    check('démo sans erreur', not errs, errs)
    ctx.close()

    print('3. Démo lien personnel')
    ctx, p, errs = page(b)
    perso = re.search(r'href="(modeles/caramel/index.html\?i=[^"]+)"', (SITE / 'index.html').read_text()).group(1)
    p.goto(BASE + perso); skip_film(p)
    p.screenshot(path=OUT / '07-demo-perso-page1.png')
    check('démo perso : nom de la famille', 'Rakoto' in p.inner_text('#filmName') or p.locator('#seatsN').inner_text() == '4')
    p.mouse.click(195, 300); p.wait_for_timeout(2600)
    p.click('#yes'); p.wait_for_timeout(500)
    p.screenshot(path=OUT / '08-demo-perso-reponse.png')
    check('démo perso : réponse non enregistrée', 'Démonstration' in p.inner_text('#rsvpNote'), p.inner_text('#rsvpNote'))
    check('démo perso : aucune écriture', not p.evaluate('window.__WRITES || []'))
    ctx.close()

    print('4. Invitation client, lien personnel, avant la date limite')
    enc = lambda o: __import__('base64').urlsafe_b64encode(json.dumps(o, ensure_ascii=False).encode()).decode().rstrip('=')
    ctx, p, errs = page(b, db=DB0)
    p.goto(BASE + f'e/{SLUG}/?i=' + enc({'n': 'Famille Rabe', 's': 3, 'id': 'rabe', 'a': 2, 'e': 1}))
    skip_film(p); p.mouse.click(195, 300); p.wait_for_timeout(2600)
    p.screenshot(path=OUT / '09-client-perso-formulaire.png')
    p.click('#yes'); p.wait_for_timeout(800)
    w = p.evaluate('window.__WRITES || []')
    rep = [x for x in w if x['path'] == f'evenements/{SLUG}/reponses']
    check('client : réponse enregistrée dans son événement', len(rep) == 1 and rep[0]['data']['reponse'] == 'Vient' and rep[0]['data']['personnes'] == 3, w)
    check('client : champs autorisés seulement', rep and set(rep[0]['data']) <= {'familyId', 'famille', 'places', 'reponse', 'personnes', 'date'}, rep)
    p.screenshot(path=OUT / '10-client-perso-merci.png')
    check('client sans erreur', not errs, errs)
    ctx.close()

    print('5. Invitation client après la date limite')
    ctx, p, errs = page(b, db=DB0, now=EV['date_limite_ms'] + 3600_000)
    p.goto(BASE + f'e/{SLUG}/?i=' + enc({'n': 'Famille Rabe', 's': 3, 'id': 'rabe'}))
    skip_film(p); p.mouse.click(195, 300); p.wait_for_timeout(2600)
    p.screenshot(path=OUT / '11-client-apres-limite.png')
    note = p.inner_text('#rsvpNote') if p.locator('#rsvpNote').is_visible() else ''
    check('après limite : encadré « réponses closes »', 'closes depuis' in note, note)
    check('après limite : plus de bouton', not p.locator('#yes').is_visible())
    check('après limite : pas de « vous pouvez encore modifier »', not p.locator('#rsvpPre').is_visible())
    ctx.close()

    print('6. Gestion client')
    ctx, p, errs = page(b, user={'email': CLIENT}, db=DB0)
    p.goto(BASE + f'e/{SLUG}/gestion/'); p.wait_for_timeout(1500)
    p.screenshot(path=OUT / '12-gestion-client.png')
    check('gestion : ouverte pour le client', p.locator('#admin').is_visible() and not p.locator('#login').is_visible())
    if XLSX:
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Invités'
        ws.append(['Nom', 'Adultes', 'Enfants', 'Catégorie', 'Téléphone'])
        for r in [['RAKOTO Jean', 2, 1, 'FAMILLE HERY', '0340000011'], ['RABE Marie', 2, 0, 'FAMILLE FARA', '0340000012'],
                  ['ANDRIA Paul', 1, 2, 'AMIS', ''], ['RAKOTO Jean', 2, 0, 'FAMILLE HERY', '']]: ws.append(r)
        xp = OUT / 'liste-test.xlsx'; wb.save(xp)
        p.click('#aImport'); p.wait_for_timeout(300)
        inp = p.locator('input[type=file]').first
        inp.set_input_files(str(xp)); p.wait_for_timeout(1200)
        p.screenshot(path=OUT / '13-gestion-import.png')
        go = p.locator('#iGo')
        if go.is_visible(): go.click(); p.wait_for_timeout(2500)
        p.screenshot(path=OUT / '14-gestion-apres-import.png', full_page=True)
        fams = p.evaluate(f"Object.keys(JSON.parse(localStorage.getItem('FAKEDB'))['evenements/{SLUG}/families'] || {{}}).length")
        check('import Excel : familles dans son événement (avec doublon renommé)', fams == 4, fams)
    check('gestion sans erreur', not errs, errs)
    ctx.close()

    print('7. Gestion : compte non autorisé')
    ctx, p, errs = page(b, user={'email': OTHER}, db=DB0)
    p.goto(BASE + f'e/{SLUG}/gestion/'); p.wait_for_timeout(1200)
    p.screenshot(path=OUT / '15-gestion-refusee.png')
    check('gestion refusée à un inconnu', p.locator('#login').is_visible() and 'pas accès' in p.inner_text('#lErr'), p.inner_text('#lErr'))
    ctx.close()

    print('8. Admin studio')
    ctx, p, errs = page(b, user={'email': STUDIO_MAIL}, admins=[STUDIO_MAIL], db={'evenements': {}})
    p.goto(BASE + 'admin/'); p.wait_for_timeout(1500)
    check('admin : événement listé', p.locator('.ev').count() == len(json.loads((SITE / 'admin' / 'evenements.json').read_text())))
    p.fill('[data-f=clients]', 'Client.Test@gmail.com, mauvaise-adresse')
    p.check('[data-f=actif]'); p.click('[data-save]'); p.wait_for_timeout(600)
    p.screenshot(path=OUT / '16-admin.png', full_page=True)
    doc = p.evaluate(f"JSON.parse(localStorage.getItem('FAKEDB'))['evenements']['{SLUG}']")
    check('admin : client activé avec la date limite', doc and doc['clients'] == [CLIENT] and doc['actif'] and doc['dateLimite'] == EV['date_limite_ms'], doc)
    check('admin sans erreur', not errs, errs)
    ctx.close()
    b.close()

srv.shutdown()
print(f'\n{len(ok)} vérifications réussies, {len(ko)} échec(s)')
for k in ko: print(' -', k)
sys.exit(1 if ko else 0)
