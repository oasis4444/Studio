"""Pages propres au studio : vitrine publique, admin du studio, règles Firestore."""
import html, json, re

def h(v): return html.escape(str(v), quote=True)
def tel_intl(t, ind='261'):
    d = re.sub(r'\D', '', str(t))
    return ind + d[1:] if d.startswith('0') else d

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Great+Vibes&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">'

BASE_CSS = """
:root{--linen:#d9c6a8;--paper:#f7f0e4;--card:#fbf6ee;--sand:#e6d4b8;--caramel:#a87c50;--brown:#6b4a2f;--espresso:#3d2a1b;
  --line:rgba(107,74,47,.18);--ok:#4f6b3a;--no:#9a4a34;
  --script:'Great Vibes',cursive;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Jost','Helvetica Neue',Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--espresso);font:400 16px/1.55 var(--sans);-webkit-text-size-adjust:100%}
a{color:inherit}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:500 15px/1 var(--sans);letter-spacing:.05em;border-radius:40px;
  padding:14px 22px;border:1.5px solid var(--brown);background:var(--brown);color:var(--paper);text-decoration:none;cursor:pointer;white-space:nowrap}
.btn.sec{background:transparent;color:var(--brown);border-color:rgba(107,74,47,.4)}
.btn.wa{background:#3f6b3f;border-color:#3f6b3f}
.btn.sm{padding:9px 14px;font-size:13.5px}
.btn:focus-visible{outline:3px solid var(--caramel);outline-offset:3px}
.kicker{font:500 12.5px/1.4 var(--sans);letter-spacing:.28em;text-transform:uppercase;color:var(--caramel)}
h2{font:600 clamp(30px,6vw,44px)/1.1 var(--serif);margin:6px 0 14px;color:var(--espresso)}
"""

def vitrine(studio, catalogue):
    wa = tel_intl(studio.get('whatsapp', ''), studio.get('indicatif', '261'))
    msg = f"Bonjour {studio['nom']} ! Je voudrais une invitation numérique."
    import urllib.parse
    wa_link = f'https://wa.me/{wa}?text=' + urllib.parse.quote(msg) if wa else ''
    cards = []
    for m in catalogue:
        base = f"modeles/{m['modele']}/index.html"
        img = f"modeles/{m['modele']}/film.jpg"
        occ = ''.join(f'<li>{h(o)}</li>' for o in m.get('occasions', []))
        order = (f'<a class="btn wa sm" href="https://wa.me/{wa}?text=' + urllib.parse.quote(f"Bonjour {studio['nom']} ! Je voudrais le modèle {m.get('nom', m['modele'])}.") + '" target="_blank" rel="noopener">Commander ce modèle</a>') if wa else ''
        cards.append(f"""
    <article class="model">
      <a class="poster" href="{base}" aria-label="Essayer le modèle {h(m.get('nom', m['modele']))}">
        <img src="{img}" alt="Aperçu du modèle {h(m.get('nom', m['modele']))}" loading="lazy" draggable="false">
        <span class="play" aria-hidden="true">▶</span><span class="tag">Démo</span>
      </a>
      <div class="m-body">
        <h3>{h(m.get('nom', m['modele']))}</h3>
        <p>{h(m.get('accroche', ''))}</p>
        <ul class="occ">{occ}</ul>
        <div class="m-acts">
          <a class="btn sm" href="{base}">Essayer · lien général</a>
          <a class="btn sm sec" href="{base}{m['perso']}">Essayer · lien personnel</a>
        </div>
        <div class="m-acts">{order}</div>
      </div>
    </article>""")
    formules = studio.get('formules') or []
    if formules:
        prix = '<div class="prices">' + ''.join(
            f'<div class="price"><h3>{h(f["nom"])}</h3><div class="amt">{h(f["prix"])}</div><ul>' + ''.join(f'<li>{h(x)}</li>' for x in f.get('inclus', [])) + '</ul></div>'
            for f in formules) + '</div>'
    else:
        prix = '<p class="note">Tarifs sur demande, selon le modèle, la durée du film et les options choisies.</p>'
    steps = [('Choisissez', 'Essayez les modèles ci-dessus sur votre téléphone, comme vos invités les verront.'),
             ('Envoyez', 'Vos noms, la date, le programme, les lieux, vos photos, vidéos et la musique.'),
             ('Nous créons', 'Votre film d’ouverture et vos pages, avec vos textes. Vous validez chaque étape.'),
             ('Vous invitez', 'Vous recevez votre lien et votre espace Gestion pour la liste d’invités et les réponses.')]
    feats = [('Film d’ouverture', 'Vertical, avec votre musique, enveloppe qui s’ouvre et vos photos.'),
             ('Lien général', 'Un seul lien pour un groupe Messenger ou WhatsApp, sans formulaire.'),
             ('Lien personnel', 'Un lien par famille : son nom, ses places et un formulaire de réponse.'),
             ('Date limite', 'Après la date, le formulaire se ferme tout seul et affiche vos contacts.'),
             ('Compte à rebours', 'Jours, heures, minutes jusqu’au grand jour, et les cartes des lieux.'),
             ('Espace Gestion', 'Import de votre liste Excel, statistiques, réponses en direct, envoi WhatsApp.'),
             ('Plan de tables', 'Tables, places restantes, cartes de table à imprimer.'),
             ('Dépenses et check-list', 'Budget, acomptes, reste à payer, tâches à cocher, pour vous seul.')]
    send = ['Type d’événement, prénoms, date et programme avec les heures', 'Lieux et liens Google Maps', 'Date limite de réponse',
            'Téléphones et lien Facebook ou Messenger à afficher', 'Photos et vidéos, musique', 'Liste d’invités Excel (vous pouvez aussi l’ajouter plus tard)',
            'Adresses Gmail qui auront accès à la Gestion']
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{h(studio['nom'])} · Invitations numériques</title>
<meta name="description" content="{h(studio.get('slogan', ''))}">
<meta property="og:title" content="{h(studio['nom'])} · Invitations numériques"><meta property="og:description" content="{h(studio.get('slogan', ''))}">
{FONTS}
<style>{BASE_CSS}
header.hero{{position:relative;overflow:hidden;background:radial-gradient(ellipse at 50% 0%,#efe2cc,var(--linen) 70%);border-bottom:1px solid var(--line)}}
.hero .wrap{{padding-top:22px;padding-bottom:56px;text-align:center}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:46px}}
.brand{{font:400 30px/1 var(--script);color:var(--brown);text-decoration:none}}
.top nav{{display:flex;gap:16px;font:500 13px var(--sans);letter-spacing:.08em;text-transform:uppercase}}
.top nav a{{text-decoration:none;color:var(--brown)}}
.hero h1{{font:400 clamp(52px,13vw,96px)/1 var(--script);color:var(--brown);margin:14px 0 10px}}
.hero p.lead{{font:italic 400 clamp(20px,4.6vw,26px)/1.35 var(--serif);max-width:620px;margin:0 auto 26px}}
.hero .acts{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
.orn{{display:block;margin:0 auto;width:200px;height:18px}}
section{{padding:56px 0;border-bottom:1px solid var(--line)}}
.models{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px;margin-top:22px}}
.model{{background:var(--card);border:1px solid var(--line);border-radius:22px;overflow:hidden;display:flex;flex-direction:column}}
.poster{{position:relative;display:block;aspect-ratio:9/12;overflow:hidden;background:var(--sand)}}
.poster img{{width:100%;height:100%;object-fit:cover;object-position:50% 30%;display:block;-webkit-touch-callout:none;user-select:none}}
.poster .play{{position:absolute;left:50%;top:50%;width:68px;height:68px;margin:-34px 0 0 -34px;border-radius:50%;background:rgba(61,42,27,.78);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:26px;padding-left:5px}}
.poster .tag{{position:absolute;left:12px;top:12px;background:rgba(251,246,238,.92);color:var(--brown);border-radius:20px;padding:5px 11px;font:600 11px var(--sans);letter-spacing:.18em;text-transform:uppercase}}
.m-body{{padding:18px 18px 20px;display:flex;flex-direction:column;gap:10px}}
.m-body h3{{margin:0;font:400 40px/1 var(--script);color:var(--brown)}}
.m-body p{{margin:0;font:italic 19px/1.35 var(--serif)}}
.occ{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px}}
.occ li{{font-size:12.5px;border:1px solid var(--line);border-radius:20px;padding:3px 10px;background:#fff8ee}}
.m-acts{{display:flex;flex-wrap:wrap;gap:8px}}
.m-acts:empty{{display:none}}
.soon{{border:1.5px dashed rgba(107,74,47,.3);border-radius:22px;padding:26px;display:flex;flex-direction:column;justify-content:center;gap:8px;text-align:center;min-height:200px}}
.soon h3{{margin:0;font:400 36px/1 var(--script);color:var(--brown)}}
.steps{{list-style:none;padding:0;margin:22px 0 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;counter-reset:s}}
.steps li{{counter-increment:s;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}}
.steps li::before{{content:counter(s);display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--brown);color:var(--paper);align-items:center;justify-content:center;font:600 16px var(--sans);margin-bottom:8px}}
.steps b{{display:block;font:600 22px var(--serif)}}
.feats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px 26px;margin-top:20px}}
.feat{{border-top:1px solid var(--line);padding-top:12px}}
.feat b{{font:600 21px var(--serif);display:block}}
.feat span{{font-size:15px;opacity:.85}}
.order{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:26px;align-items:start}}
.order ul{{margin:0;padding-left:18px}}
.order li{{margin:4px 0}}
.cta{{background:var(--brown);color:var(--paper);border-radius:24px;padding:24px}}
.cta h3{{margin:0 0 6px;font:400 40px/1 var(--script)}}
.cta p{{margin:0 0 16px;opacity:.9}}
.cta .btn{{background:var(--paper);color:var(--brown);border-color:var(--paper)}}
.cta .btn.wa{{background:#4f8a4f;border-color:#4f8a4f;color:#fff}}
.cta .acts{{display:flex;gap:10px;flex-wrap:wrap}}
.prices{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:20px}}
.price{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}}
.price h3{{margin:0;font:600 24px var(--serif)}} .price .amt{{font:600 30px var(--sans);color:var(--brown);margin:4px 0 8px}}
.note{{font:italic 19px/1.4 var(--serif)}}
footer{{padding:30px 0 40px;text-align:center;font-size:13px;opacity:.75}}
@media (max-width:560px){{.top nav{{display:none}} section{{padding:44px 0}}}}
</style></head><body>
<header class="hero"><div class="wrap">
  <div class="top"><a class="brand" href="#">{h(studio['nom'])}</a>
    <nav><a href="#modeles">Modèles</a><a href="#inclus">Inclus</a><a href="#commander">Commander</a></nav></div>
  <div class="kicker">Mariage · Anniversaire de mariage · Baptême</div>
  <h1>Vos invitations,<br>en film</h1>
  <svg class="orn" viewBox="0 0 200 18" aria-hidden="true"><path d="M0 9H80M120 9H200" stroke="#a87c50" stroke-width="1.5"/><path d="M100 2 L107 9 L100 16 L93 9Z" fill="none" stroke="#a87c50" stroke-width="1.5"/></svg>
  <p class="lead">{h(studio.get('slogan', ''))}. Un film d’ouverture avec votre musique, un lien pour chaque famille et les réponses qui arrivent toutes seules.</p>
  <div class="acts"><a class="btn" href="#modeles">Voir les modèles</a>{f'<a class="btn wa" href="{h(wa_link)}" target="_blank" rel="noopener">Nous écrire sur WhatsApp</a>' if wa_link else ''}</div>
</div></header>

<section id="modeles"><div class="wrap">
  <div class="kicker">Catalogue</div><h2>Essayez nos modèles</h2>
  <p>Ouvrez un modèle sur votre téléphone : vous voyez exactement ce que vos invités verront. Les démonstrations portent un filigrane et rien n’y est enregistré ni téléchargeable : nous créons ensuite votre invitation avec vos textes, photos et musique.</p>
  <div class="models">{''.join(cards)}
    <div class="soon"><h3>Sur mesure</h3><p>Couleurs, fleurs, écriture, scènes du film : nous pouvons créer un modèle à votre image.</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="kicker">Comment ça marche</div><h2>De votre idée à vos invités</h2>
  <ol class="steps">{''.join(f'<li><b>{h(a)}</b>{h(b)}</li>' for a, b in steps)}</ol>
</div></section>

<section id="inclus"><div class="wrap">
  <div class="kicker">Inclus</div><h2>Tout pour recevoir sereinement</h2>
  <div class="feats">{''.join(f'<div class="feat"><b>{h(a)}</b><span>{h(b)}</span></div>' for a, b in feats)}</div>
  <h2 style="margin-top:40px;font-size:32px">Tarifs</h2>{prix}
</div></section>

<section id="commander"><div class="wrap order">
  <div><div class="kicker">Commander</div><h2>Ce qu’il nous faut</h2><ul>{''.join(f'<li>{h(x)}</li>' for x in send)}</ul>
    <p class="note" style="margin-top:16px">Les photos, vidéos et la musique doivent vous appartenir ou être libres de droits.</p></div>
  <div class="cta"><h3>Parlons de votre fête</h3><p>Dites-nous la date et le modèle qui vous plaît, nous vous répondons avec un devis.</p>
    <div class="acts">{f'<a class="btn wa" href="{h(wa_link)}" target="_blank" rel="noopener">WhatsApp</a>' if wa_link else ''}{f'<a class="btn" href="{h(studio["facebook"])}" target="_blank" rel="noopener">Facebook</a>' if studio.get('facebook') else ''}{f'<a class="btn" href="tel:+{wa}">Appeler</a>' if wa else ''}</div></div>
</div></section>
<footer>{h(studio['nom'])} · Invitations numériques</footer>
</body></html>"""


def admin(studio):
    fb = json.dumps(studio.get('firebase') or None)
    admins = json.dumps([a.lower() for a in studio.get('admins', [])])
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Admin · {h(studio['nom'])}</title>
{FONTS}
<style>{BASE_CSS}
body{{background:var(--paper)}}
header{{border-bottom:1px solid var(--line);background:var(--card)}}
header .wrap{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-top:14px;padding-bottom:14px}}
header b{{font:400 30px/1 var(--script);color:var(--brown)}}
#who{{font-size:13px;opacity:.75;text-align:right}}
main{{padding:22px 0 60px}}
.msg{{background:#fff8ee;border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:14px 0}}
.msg.err{{border-color:rgba(154,74,52,.4);color:var(--no)}}
.ev{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;margin:14px 0}}
.ev-h{{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline}}
.ev-h h3{{margin:0;font:600 24px/1.15 var(--serif)}}
.pill{{display:inline-block;border-radius:20px;padding:3px 10px;font-size:12px;font-weight:600;letter-spacing:.04em;background:#efe4d3}}
.pill.on{{background:#e3efdc;color:var(--ok)}} .pill.off{{background:#f4e1da;color:var(--no)}}
.meta{{font-size:13.5px;opacity:.8;margin:4px 0 10px}}
.links{{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px 14px}}
label{{display:flex;flex-direction:column;gap:4px;font-size:13px;font-weight:500;letter-spacing:.03em}}
input,select,textarea{{font:15px var(--sans);padding:10px 12px;border:1.5px solid rgba(107,74,47,.3);border-radius:12px;background:#fffdf9;color:var(--espresso);width:100%}}
textarea{{min-height:64px;resize:vertical}}
.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:12px}}
.chk{{flex-direction:row;align-items:center;gap:8px;font-size:14px}}
.chk input{{width:auto}}
.st{{font-size:13px;opacity:.85}}
.toast{{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:var(--espresso);color:var(--paper);padding:10px 16px;border-radius:30px;font-size:14px;z-index:9}}
.toast[hidden]{{display:none}}
</style></head><body>
<header><div class="wrap"><b>{h(studio['nom'])} · Admin</b><div id="who"></div></div></header>
<main class="wrap">
  <div id="login" class="msg" hidden><p style="margin-top:0">Connectez-vous avec un compte Google du studio.</p><button class="btn" id="gLogin" type="button">Se connecter avec Google</button><p id="lErr" class="st"></p></div>
  <div id="noFb" class="msg err" hidden>La configuration Firebase n’est pas encore dans <b>studio.json</b>. Ajoutez-la puis reconstruisez le site.</div>
  <div id="intro" class="msg" hidden>Chaque événement doit être <b>activé</b> ici pour que les invités puissent répondre. Ajoutez les adresses Gmail du client : lui seul (et le studio) verra sa Gestion. L’adresse « dépenses » voit en plus les dépenses et la check-list.</div>
  <div id="list"></div>
</main>
<div class="toast" id="toast" hidden></div>
<script type="module">
const FB = {fb}, ADMINS = {admins};
const $ = s => document.querySelector(s);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
let tt; const toast = t => {{ const e = $('#toast'); e.textContent = t; e.hidden = false; clearTimeout(tt); tt = setTimeout(() => e.hidden = true, 3200); }};
if (!FB) {{ $('#noFb').hidden = false; throw new Error('firebase'); }}
const {{ initializeApp }} = await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js');
const {{ getFirestore, collection, doc, getDocs, setDoc, getCountFromServer }} = await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');
const {{ getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut }} = await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js');
const app = initializeApp(FB), fs = getFirestore(app), auth = getAuth(app);
const fmt = ms => new Date(ms).toLocaleDateString('fr-FR', {{ weekday: 'short', day: 'numeric', month: 'long', year: 'numeric' }});
const mails = t => [...new Set(String(t || '').toLowerCase().split(/[\\s,;]+/).filter(x => /^[^@\\s]+@[^@\\s]+\\.[a-z]{{2,}}$/.test(x)))];
const abs = u => new URL(u, location.href).href;
async function load() {{
  const evs = await (await fetch('evenements.json?t=' + Date.now())).json();
  let docs = {{}};
  try {{ (await getDocs(collection(fs, 'evenements'))).forEach(d => docs[d.id] = d.data()); }}
  catch (e) {{ $('#list').innerHTML = '<div class="msg err">Lecture refusée (' + esc(e.code) + '). Vérifiez que les règles Firestore du studio sont publiées.</div>'; return; }}
  $('#intro').hidden = false;
  evs.sort((a, b) => a.date_ms - b.date_ms);
  $('#list').innerHTML = evs.map(e => {{ const d = docs[e.slug] || {{}}; const inv = abs('../e/' + e.slug + '/'), ges = inv + 'gestion/';
    const passe = Date.now() > e.date_ms;
    return `<article class="ev" data-slug="${{esc(e.slug)}}">
      <div class="ev-h"><h3>${{esc(e.titre)}}</h3><span class="pill ${{d.actif ? 'on' : 'off'}}">${{d.actif ? 'Actif' : 'Pas encore activé'}}</span></div>
      <div class="meta">${{esc(fmt(e.date_ms))}} · réponses jusqu’au ${{esc(fmt(e.date_limite_ms - 1))}} · modèle ${{esc(e.modele)}}${{passe ? ' · terminé' : ''}} · <span class="cnt">…</span></div>
      <div class="links"><a class="btn sm sec" href="${{inv}}" target="_blank" rel="noopener">Invitation</a><a class="btn sm sec" href="${{ges}}" target="_blank" rel="noopener">Gestion</a><button class="btn sm sec" type="button" data-copy>Message de livraison</button></div>
      <div class="grid">
        <label>Adresses Gmail du client (Gestion)<textarea data-f="clients" placeholder="client@gmail.com, conjoint@gmail.com">${{esc((d.clients || []).join(', '))}}</textarea></label>
        <label>Adresse qui voit dépenses et check-list<input data-f="depenses" value="${{esc(d.depenses || '')}}" placeholder="une seule adresse"></label>
        <label>Paiement<select data-f="statut">${{['Devis envoyé','Acompte reçu','Payé','Offert'].map(s => `<option${{(d.statut || 'Devis envoyé') === s ? ' selected' : ''}}>${{s}}</option>`).join('')}}</select></label>
        <label>Montant (Ar)<input data-f="montant" inputmode="numeric" value="${{esc(d.montant || '')}}"></label>
        <label>Note<input data-f="note" value="${{esc(d.note || '')}}"></label>
      </div>
      <div class="row"><label class="chk"><input type="checkbox" data-f="actif" ${{d.actif ? 'checked' : ''}}> Activé (les invités peuvent répondre)</label>
        <button class="btn sm" type="button" data-save>Enregistrer</button><span class="st"></span></div>
    </article>`; }}).join('') || '<div class="msg">Aucun événement client pour l’instant.</div>';
  for (const e of evs) {{
    const el = document.querySelector(`[data-slug="${{CSS.escape(e.slug)}}"]`);
    Promise.all(['families', 'reponses'].map(c => getCountFromServer(collection(fs, 'evenements', e.slug, c)).then(r => r.data().count).catch(() => '?')))
      .then(([f, r]) => el.querySelector('.cnt').textContent = `${{f}} famille${{f > 1 ? 's' : ''}} · ${{r}} réponse${{r > 1 ? 's' : ''}}`);
    el.querySelector('[data-save]').onclick = async () => {{
      const v = k => el.querySelector(`[data-f="${{k}}"]`);
      const clients = mails(v('clients').value), dep = mails(v('depenses').value)[0] || '';
      if (v('actif').checked && !clients.length) {{ toast('Ajoutez au moins une adresse Gmail du client'); return; }}
      const data = {{ titre: e.titre, dateLimite: e.date_limite_ms, dateJ: e.date_ms, clients, depenses: dep, statut: v('statut').value,
        montant: v('montant').value.trim().slice(0, 30), note: v('note').value.trim().slice(0, 300), actif: v('actif').checked, maj: Date.now() }};
      try {{ await setDoc(doc(fs, 'evenements', e.slug), data, {{ merge: true }}); toast('Enregistré'); el.querySelector('.pill').className = 'pill ' + (data.actif ? 'on' : 'off'); el.querySelector('.pill').textContent = data.actif ? 'Actif' : 'Pas encore activé'; v('clients').value = clients.join(', '); v('depenses').value = dep; }}
      catch (err) {{ toast('Refusé : ' + (err.code || err.message)); }}
    }};
    el.querySelector('[data-copy]').onclick = async () => {{
      const inv = abs('../e/' + e.slug + '/');
      const t = `Bonjour ! Votre invitation « ${{e.titre}} » est prête.\\n\\nLien à envoyer à vos invités (lien général) :\\n${{inv}}\\n\\nVotre Gestion (liste d’invités, liens personnels, réponses) :\\n${{inv}}gestion/\\nConnectez-vous avec votre compte Google. Importez votre liste Excel, puis envoyez à chaque famille son lien personnel avec « Envoyer sur WhatsApp ».\\n\\nLes réponses se ferment automatiquement le ${{fmt(e.date_limite_ms - 1)}} à minuit.\\n— {{j_studio}}`;
      try {{ await navigator.clipboard.writeText(t); toast('Message copié'); }} catch (err) {{ prompt('Copiez ce message :', t); }}
    }};
  }}
}}
onAuthStateChanged(auth, u => {{
  if (!u) {{ $('#login').hidden = false; $('#who').textContent = ''; return; }}
  const m = String(u.email || '').toLowerCase();
  $('#who').innerHTML = esc(m) + ' · <a href="#" id="out">changer</a>'; $('#out').onclick = ev => {{ ev.preventDefault(); signOut(auth); }};
  if (!ADMINS.includes(m)) {{ $('#login').hidden = false; $('#lErr').textContent = 'Ce compte n’est pas un compte du studio.'; $('#list').innerHTML = ''; return; }}
  $('#login').hidden = true; load();
}});
$('#gLogin').onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch(e => $('#lErr').textContent = 'Connexion impossible (' + e.code + ').');
</script></body></html>""".replace('{j_studio}', studio['nom'].replace('`', '').replace('\\', ''))


def rules(studio):
    admins = ', '.join(json.dumps(a.lower()) for a in studio.get('admins', []))
    return f"""rules_version = '2';
// Règles du studio : un seul projet Firebase, chaque client ne voit que son événement.
// À coller dans la console Firebase → Firestore Database → Règles → Publier.
service cloud.firestore {{
  match /databases/{{database}}/documents {{
    function mail() {{ return request.auth != null && request.auth.token.email_verified == true ? request.auth.token.email.lower() : ''; }}
    function isStudio() {{ return mail() in [{admins}]; }}

    match /evenements/{{eid}} {{
      function ev() {{ return get(/databases/$(database)/documents/evenements/$(eid)).data; }}
      function isClient() {{ return mail() != '' && mail() in ev().get('clients', []); }}
      function canManage() {{ return isStudio() || isClient(); }}
      function isDep() {{ return isStudio() || (mail() != '' && mail() == ev().get('depenses', '')); }}
      function open() {{ return ev().get('actif', false) == true; }}

      allow get: if isStudio() || (mail() != '' && mail() in resource.data.get('clients', []));
      allow list, create, update, delete: if isStudio();

      match /families/{{d}} {{ allow read, write: if canManage(); }}
      match /tables/{{d}} {{ allow read, write: if canManage(); }}
      match /depenses/{{d}} {{ allow read, write: if isDep(); }}
      match /taches/{{d}} {{ allow read, write: if isDep(); }}

      match /reponses/{{d}} {{
        allow create: if open()
          && (request.time.toMillis() < ev().dateLimite || canManage())
          && request.resource.data.keys().hasOnly(['familyId', 'famille', 'places', 'reponse', 'personnes', 'date'])
          && request.resource.data.familyId is string && request.resource.data.familyId.size() <= 60
          && request.resource.data.famille is string && request.resource.data.famille.size() < 120
          && request.resource.data.reponse in ['Vient', 'Ne vient pas']
          && request.resource.data.personnes is int && request.resource.data.personnes >= 0 && request.resource.data.personnes <= 30
          && request.resource.data.places is int && request.resource.data.places <= 200
          && request.resource.data.date is int;
        allow read, update, delete: if canManage();
      }}

      match /vues/{{d}} {{
        allow create: if open()
          && request.resource.data.keys().hasOnly(['fid', 'famille', 'date'])
          && request.resource.data.fid is string && request.resource.data.fid.size() <= 60
          && request.resource.data.famille is string && request.resource.data.famille.size() <= 120
          && request.resource.data.date is int;
        allow read, delete: if canManage();
      }}
    }}
  }}
}}
"""
