# Studio Fanasana — invitations numériques

Un seul dépôt GitHub (site sur GitHub Pages, dossier docs/ de la branche main) et un seul projet Firebase pour tous les clients.

| Adresse | Pour qui | Ce qu'on y fait |
|---|---|---|
| `/` | Prospects | Vitrine : modèles, essai, commande WhatsApp |
| `/modeles/caramel/` | Prospects | Démonstration : filigrane, film réduit avec filigrane incrusté, rien n'est enregistré |
| `/e/<slug>/` | Invités du client | L'invitation (lien général, ou lien personnel `?i=…`) |
| `/e/<slug>/gestion/` | Le client | Sa liste d'invités, ses réponses, ses tables (connexion Google) |
| `/admin/` | Le studio | Activer un client, ses adresses Gmail, le paiement, le message de livraison |

## Nouveau client

1. Créer `evenements/<slug>/config.json` (copier `evenements/exemple-client/config.json`). Le slug apparaît dans le lien : `noces-rakoto-2026`.
2. Mettre dans le même dossier : `film.mp4` (720 × 1280), `film.jpg` (première image), `music.mp3`.
   Facultatif : `invitation-a-imprimer.pdf`, `etiquette-bouteille-vin.pdf`, `video-generale.mp4`, `video-invitation.mp4` (les boutons apparaissent seuls).
3. `python3 build.py <slug>` puis `python3 tests/verifier.py <xlsx.full.min.js>`.
4. Commit et push sur `main`.
5. Dans `/admin/` : ajouter les adresses Gmail du client, cocher **Activé**, Enregistrer. Tant que ce n'est pas activé, les invités ne peuvent pas répondre (pratique pour attendre le paiement).
6. « Message de livraison » copie le texte à envoyer au client avec ses deux liens.

## Champs de `config.json`

`titre`, `date` (`2026-12-19T10:00:00+03:00`), `date_limite` (`2026-12-05` = jusqu'à minuit heure de Madagascar),
`hotes` (nom + téléphone), `lieux` (nom, bouton, lien Maps), `facebook`, `messenger`, `phrase_partage`,
`objet_confirmation` (« à votre mariage »), `texte_whatsapp`, `signature`, `table_honneur`. Les dates écrites en toutes lettres sont calculées.

## Un nouveau modèle

Un modèle = `modeles/<nom>/invitation.html` + `gestion.html` avec des champs `⟦H.titre⟧` (voir `outils/creer_modele_caramel.py`),
plus un dossier `evenements/_demo-<nom>/` avec `"demo": true` pour la vitrine.

## Firebase (une seule fois)

Firestore + connexion Google, domaine `<compte>.github.io` autorisé, configuration web dans `studio.json` → `firebase`.
Les règles sont générées dans `firestore.rules` : à coller dans la console (Firestore → Règles → Publier) après chaque changement de `admins`.

## Limites honnêtes

- Une démonstration ne peut pas empêcher une capture d'écran : c'est pour cela que le filigrane est incrusté dans le film et posé sur les pages.
- Le film de chaque client est un travail du studio (montage et rendu), il n'est pas généré par `build.py`.
