#!/usr/bin/env python3
"""Transforme les pages de l'invitation MARIAGE (Tsidy & Njara) en modèle « Caramel » réutilisable.

Usage : python3 outils/creer_modele_caramel.py <dossier du dépôt MARIAGE>

Chaque texte propre à l'événement d'origine devient un champ ⟦CONTEXTE.nom⟧ que build.py remplit :
  H.  texte échappé pour le HTML
  J.  texte échappé pour une chaîne JavaScript
  HJ. texte échappé pour le HTML puis pour le JavaScript (HTML écrit dans un gabarit JS)
  T.  texte simple déjà sûr partout (dates)
  R.  valeur brute calculée par build.py (nombres, JSON, blocs HTML)
Le script s'arrête si un remplacement attendu ne trouve rien, puis vérifie qu'aucun nom d'origine ne reste.
"""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '../randnjara/mariage')
out = pathlib.Path(__file__).resolve().parent.parent / 'modeles' / 'caramel'

def block(s, start, end_marker, token):
    a = s.find(start)
    assert a >= 0, start
    b = s.find(end_marker, a)
    assert b >= 0, end_marker
    return s[:a] + token + s[b:]

def rep(s, old, new, n=None, regex=False, opt=False):
    if regex:
        s2, k = re.subn(old, new, s)
    else:
        k = s.count(old); s2 = s.replace(old, new)
    assert k > 0 or opt, f'introuvable : {old[:80]}'
    if n is not None:
        assert k == n, f'{k} au lieu de {n} : {old[:80]}'
    return s2

def common(s, gestion):
    pre = '../' if gestion else ''
    # en-tête
    s = rep(s, 'content="Vous êtes invités · Noces d\'Étain &amp; Baptême"', 'content="Vous êtes invités · ⟦H.titre⟧"', 1)
    s = rep(s, 'content="Samedi 7 novembre 2026 · Église Christ Roi Manjakaray"', 'content="⟦H.og_description⟧"', 1)
    if gestion:
        s = rep(s, "<title>Gestion · Noces d'Étain</title>", '<title>Gestion · ⟦H.titre⟧</title>', 1)
    else:
        s = rep(s, "<title>Invitation · Noces d'Étain T &amp; N</title>", '<title>Invitation · ⟦H.titre⟧</title>', 1)
    # fichiers lourds : numéro de version calculé à partir du contenu
    s = rep(s, f'poster="{pre}film.jpg?v=14"', f'poster="{pre}film.jpg?v=⟦R.v_poster⟧"', 1)
    s = rep(s, f'src="{pre}film.mp4?v=34"', f'src="{pre}film.mp4?v=⟦R.v_film⟧"', 1)
    s = rep(s, "'music.mp3?v=2'", "'music.mp3?v=⟦R.v_music⟧'", 1)
    # dates (ordre important : DEADLINE avant le remplacement des textes)
    s = rep(s, r'const DEADLINE = Date\.UTC\([^)]*\);[^\n]*', 'const DEADLINE = ⟦R.deadline_ms⟧; /* date limite des réponses */', 1, regex=True)
    s = rep(s, r"// compte à rebours jusqu'au [^\n]*\n\(function\(\)\{ const T=Date\.parse\('[^']+'\);",
            "// compte à rebours jusqu'au jour J\n(function(){ const T=⟦R.event_ms⟧;", 1, regex=True)
    s = rep(s, 'Samedi 7 novembre 2026', '⟦T.Jour_date⟧', opt=True)
    s = rep(s, 'samedi 7 novembre 2026', '⟦T.jour_date⟧')
    s = rep(s, '7 novembre 2026', '⟦T.date_texte⟧')
    s = rep(s, '31 octobre 2026', '⟦T.dl_texte⟧')
    s = rep(s, '07.11.2026', '⟦T.date_points⟧', 1)
    s = rep(s, "Noces d'Étain &amp; Baptême · ⟦T.date_points⟧", '⟦H.titre⟧ · ⟦T.date_points⟧', 1)
    # textes
    s = rep(s, 'pour partager ce double bonheur avec nous', '⟦H.phrase_partage⟧', 1)
    s = rep(s, "Nous confirmons notre présence à vos Noces d'Étain et au baptême de Mihaja Kael le ⟦T.jour_date⟧.",
            'Nous confirmons notre présence ⟦J.objet_confirmation⟧ le ⟦T.jour_date⟧.', 1)
    s = rep(s, 'Bonjour Tsidy et Njara', 'Bonjour ⟦J.hotes_et⟧', 2)
    s = rep(s, 'appelez Tsidy ou Njara', 'appelez ⟦J.hotes_ou⟧')
    # contacts, Facebook, cartes : blocs générés
    s = block(s, '<div class="gcon gx rv"', '<div class="contacts rv ngx"', '⟦R.bloc_gcon⟧\n      ')
    s = block(s, '<div class="contacts rv ngx"', '<div class="maps rv"', '⟦R.bloc_contacts⟧\n      ')
    a = s.find('<div class="maps rv"'); b = s.find('</div>', a) + len('</div>')
    s = s[:a] + '⟦R.bloc_maps⟧' + s[b:]
    # transport (désactivé dans le modèle, textes neutres)
    s = rep(s, 'Église → Espace Fenitra', '⟦H.lieu1⟧ → ⟦H.lieu2⟧', 1)
    s = rep(s, '<p>Aller : de l’Église Christ Roi Manjakaray vers l’Espace Fenitra.<br>', '<p>Aller : ⟦H.lieu1⟧ → ⟦H.lieu2⟧.<br>', 1)
    # adresses
    s = rep(s, "const GUEST_URL = 'https://randnjara.github.io/MARIAGE/';", "const GUEST_URL = '⟦J.url⟧';", 1)
    s = rep(s, "const REPLY_WA = '261342754147';", "const REPLY_WA = '⟦J.whatsapp⟧';", 1)
    s = rep(s, "const MSGR = 'https://m.me/njara.randria.583025';", "const MSGR = '⟦J.messenger⟧';", 1)
    # Firebase : un seul projet pour le studio, données rangées par événement
    s = rep(s, r'initializeApp\(\{"apiKey":[^}]*\}\)', 'initializeApp(⟦R.firebase⟧)', 1, regex=True)
    s = rep(s, r"(const (?:fs|app) = [^\n]*initializeApp\(⟦R\.firebase⟧\)[^\n]*)", r"\1\nconst EID = '⟦J.slug⟧';", 1, regex=True)
    s = rep(s, r"collection\(fs, (c|'\w+')\)", r"collection(fs, 'evenements', EID, \1)", regex=True)
    if gestion:
        s = rep(s, r"doc\(fs, (c|'\w+'), ", r"doc(fs, 'evenements', EID, \1, ", regex=True)
    return s

def gestion_only(s):
    s = rep(s, "<h1>Noces d'Étain &amp; Baptême</h1><div class=\"sub\">⟦T.Jour_date⟧ · Gestion des invités</div>",
            '<h1>⟦H.titre⟧</h1><div class="sub">⟦T.Jour_date⟧ · Gestion des invités</div>', 1)
    s = block(s, '<a class="a-btn sec" href="invitation-a-imprimer.pdf', '<a class="a-btn sec" href="etiquette-bouteille-vin.pdf', '⟦R.btn_imprimer⟧')
    a = s.find('<a class="a-btn sec" href="etiquette-bouteille-vin.pdf'); b = s.find('</a>', a) + 4
    s = s[:a] + '⟦R.btn_etiquette⟧' + s[b:]
    for f, tok in (('video-generale.mp4', 'btn_video_generale'), ('video-invitation.mp4', 'btn_video_invitation')):
        a = s.find(f); a = s.rfind('<a ', 0, a); b = s.find('</a>', a) + 4
        s = s[:a] + f'⟦R.{tok}⟧' + s[b:]
    s = rep(s, '(famille de Neny Tsidy, groupe Messenger)', '(famille, groupe Messenger)', 1)
    s = rep(s, 'avant le 31 octobre.', 'avant le ⟦T.dl_court⟧.')
    s = rep(s, "const u = 'https://randnjara.github.io/MARIAGE/';", "const u = GUEST_URL;", 1)
    s = rep(s, r"const invText = f => `Bonjour \$\{f\.name\},\\n[^`]*?Votre invitation : \$\{invLink\(f\)\}\\nMerci de confirmer avant le [^`]*?\\nTsidy & Njara`;",
            "const invText = f => `Bonjour ${f.name},\\n⟦J.texte_whatsapp⟧\\nVotre invitation : ${invLink(f)}\\nMerci de confirmer avant le ⟦T.dl_court⟧.\\n⟦J.signature⟧`;", 1, regex=True)
    s = rep(s, 'Table d’honneur · Tsidy &amp; Njara · Mihaja Kaël', 'Table d’honneur · ⟦HJ.table_honneur⟧', 1)
    s = rep(s, '<b>Tsidy &amp; Njara</b>Noces d’Étain · Baptême de Mihaja Kaël<br>⟦T.date_texte⟧', '<b>⟦HJ.hotes_amp⟧</b>⟦HJ.titre⟧<br>⟦T.date_texte⟧', 1)
    s = rep(s, 'placeholder="ex. Espace Fenitra, 034 00 000 00"', 'placeholder="ex. Salle des fêtes, 034 00 000 00"', 1)
    s = rep(s, 'Aller : église → Espace Fenitra.', 'Aller : ⟦HJ.lieu1⟧ → ⟦HJ.lieu2⟧.', 1)
    # côtés (famille de l'un ou l'autre hôte)
    s = rep(s, '<option value="njara">Famille Njara</option><option value="tsidy">Famille Tsidy</option>', '⟦R.cotes_options⟧', 3)
    s = rep(s, "[['njara','Njara'],['tsidy','Tsidy']]", '⟦R.cotes_js⟧', 1)
    s = rep(s, "/tsidy/i.test(name) && !/njara/i.test(name) ? 'tsidy' : /njara/i.test(name) && !/tsidy/i.test(name) ? 'njara' : (", '(window.__side(name) || ', 1)
    s = rep(s, "/njara/i.test(x.cat) && !/tsidy/i.test(x.cat) ? 'njara' : /tsidy/i.test(x.cat) && !/njara/i.test(x.cat) ? 'tsidy' : ''", 'window.__side(x.cat)', 1)
    s = rep(s, "const CATS = ['FAMILLE TSIDY DADA','FAMILLE TSIDY NENY','FAMILLE NJARA','AMIE NJARA','MPIASA NJARA TSIDY','AMI TSIDY','BASKET'];",
            "const CATS = []; /* catégories prises dans la liste importée */", 1)
    s = rep(s, "filename:'invites-noces-etain.xlsx'", "filename:'invites-⟦J.slug⟧.xlsx'", 1)
    s = rep(s, "filename: 'depenses-noces-bapteme.xlsx'", "filename: 'depenses-⟦J.slug⟧.xlsx'", 1)
    # un encadré vide (aucune réponse, aucune ouverture) reste caché
    s = rep(s, '<main id="admin" hidden>', '<style>#admin section[hidden]{display:none!important}</style>\n<main id="admin" hidden>', 1)
    s = rep(s, 'placeholder="ex. FAMILLE NJARA"','placeholder="ex. FAMILLE ⟦H.hote1_maj⟧"', 1)
    s = rep(s, "const GUEST_URL = '⟦J.url⟧';", "const GUEST_URL = '⟦J.url⟧';\nwindow.__side = t => { const h = ⟦R.cotes_js⟧.filter(([k, l]) => new RegExp(k, 'i').test(String(t || ''))); return h.length === 1 ? h[0][0] : ''; };", 1)
    # comptes : l'adresse des dépenses vient de la fiche, la liste d'invités de départ est vide
    # accès par événement : la fiche evenements/<slug> (créée dans l'admin studio) liste les clients autorisés
    # et l'adresse qui voit les dépenses ; un compte non autorisé voit un message clair au lieu d'une page vide
    s = rep(s, "import { getFirestore, collection, doc, onSnapshot, addDoc, updateDoc, deleteDoc, setDoc }",
            "import { getFirestore, collection, doc, getDoc, onSnapshot, addDoc, updateDoc, deleteDoc, setDoc }", 1)
    s = rep(s, """  $('#login').hidden = true;
  window.__owner = String(u.email || '').toLowerCase() === 'randnjara@gmail.com';
  if (!started) { started = true; window.__startAdmin(); watchResponses(); watchViews(); }
});""", """  const mail = String(u.email || '').toLowerCase();
  getDoc(doc(fs, 'evenements', EID)).then(ev => {
    const e = ev.exists() ? ev.data() : null;
    if (!e) throw new Error('absent');
    $('#login').hidden = true;
    window.__owner = mail === String(e.depenses || '').toLowerCase();
    if (!started) { started = true; window.__startAdmin(); watchResponses(); watchViews(); }
  }).catch(() => {
    $('#login').hidden = false;
    $('#lErr').innerHTML = 'Le compte <b>' + esc(mail) + '</b> n’a pas accès à cet événement. Demandez au studio de l’ajouter, ou <a href="#" id="lOut">changez de compte</a>.';
    const o = document.getElementById('lOut'); if (o) o.onclick = ev => { ev.preventDefault(); signOut(auth); $('#lErr').textContent = ''; };
  });
});""", 1)
    s = rep(s, r'const SEED = \[.*?\];\n', 'const SEED = [];\n', 1, regex=True)
    return s

FORBIDDEN = ['Tsidy', 'Njara', 'njara', 'tsidy', 'Mihaja', 'Fenitra', 'Christ Roi', 'randnjara', 'Étain', 'novembre', 'octobre',
             '261342', 'mariage-e5de1', 'Andria', 'Manjakaray']

def check(name, s):
    s2 = re.sub(r'data:[a-z0-9/+.-]+;base64,[A-Za-z0-9+/=]{200,}', '', s)
    low = s2.lower()
    left = [w for w in FORBIDDEN + ['neny', 'dada', 'kael', 'kaël', 'noces', 'bapteme'] if w.lower() in low]
    assert not left, f'{name} : restent {left} ' + str([s2[max(0, s2.find(w) - 60):s2.find(w) + 40] for w in left])

out.mkdir(parents=True, exist_ok=True)
inv = common((src / 'index.html').read_text(), False)
check('invitation', inv)
(out / 'invitation.html').write_text(inv)
ges = gestion_only(common((src / 'gestion' / 'index.html').read_text(), True))
check('gestion', ges)
(out / 'gestion.html').write_text(ges)
toks = sorted(set(re.findall(r'⟦([A-Z]+\.\w+)⟧', inv + ges)))
print('Modèle Caramel créé :', ', '.join(toks))
