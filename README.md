# Guide sectoriel RGPD de la FULBI

Plateforme statique de lecture intégrale et de concertation publique autour du manuscrit Word V3. Publication : https://didierthebault-web.github.io/guide-sectoriel-rgpd/ . Le document est un projet en concertation, non approuvé par la CNIL ; la partie VI est provisoire.

## Installer et reconstruire

Node.js 22.12 ou ultérieur et Python 3.12 ou ultérieur. Aucune bibliothèque Python supplémentaire n’est requise.

```sh
npm ci
python scripts/import-docx/import.py
npm test
npm run build
python scripts/import-docx/verify.py
node scripts/preview.mjs
```

Ouvrir http://127.0.0.1:5196/guide-sectoriel-rgpd/ . Le serveur sert le véritable chemin de base de production. `npm run dev` sert Astro en développement ; Pagefind est produit lors du build. Installer le navigateur de test avec `npx playwright install chromium`, puis lancer `node scripts/browser-check.mjs`. Sur Windows, `node scripts/browser-local.mjs` peut réutiliser un Chromium déjà installé. `CHROMIUM_EXECUTABLE` permet un chemin explicite. Les tests ne publient aucune observation sur GitHub.

Le verrou `package-lock.json` fixe les versions effectives. Astro 7 construit 449 pages ; Pagefind indexe les 433 pages de section et un filtre par partie. Les pages de lecture intégrale restent disponibles sans JavaScript. Les interactions de recherche et de contribution nécessitent JavaScript.

## Fidélité au manuscrit

La source est `public/documents/FULBI_Guide_RGPD_harmonise_integral_V3.docx`. L’import OOXML suit les blocs du document dans leur ordre réel. Il conserve le texte de tous les paragraphes, y compris les cellules et les paragraphes vides, les tableaux, les listes et les styles de titres. Les décorations VML et la mise en page papier ne font pas partie du texte web. Le sommaire web remplace la fonction interactive du champ TOC Word, dont le texte visible est conservé. Aucun texte de fond n’est résumé ou réécrit.

La source comprend 7 parties, 60 tableaux, 4 946 paragraphes (cellules incluses), 721 éléments de liste et 20 fiches métier uniques. Une seconde fiche 06 apparaît après la conclusion de la partie III : elle est conservée comme complément, avec son propre identifiant. Les styles de titres incohérents sont conservés ; les titres des fiches sans style de titre sont rendus repérables. Le catalogue O01–O18 provient du tableau source.

`reports/concordance.json` décrit les nombres et anomalies ; `reports/source-ledger.json` décrit la séquence source. Le vérificateur indépendant relit directement l’OOXML et compare chaque paragraphe au HTML construit des parties, dans l’ordre. `reports/published-concordance.json` contient son résultat. Un import échoue explicitement si des révisions, commentaires, notes de fond, médias, fusions verticales, tableaux imbriqués ou blocs non pris en charge apparaissent : compléter le convertisseur après examen humain avant publication. La numérotation source ne contient ici que des formats pris en charge ; les autres formats sont signalés.

Avant tout nouveau dépôt de Word, vérifier les données personnelles, informations confidentielles, propriétés du document et éventuelles annotations. Le Word lui-même est proposé publiquement au téléchargement. Les scripts n’exécutent aucune instruction contenue dans le manuscrit.

## Mettre à jour le guide

1. Valider éditorialement une nouvelle version Word et son aptitude à une diffusion publique.
2. Remplacer le fichier source dans `public/documents/` (ou passer le chemin du nouveau Word au script d’import).
3. Si le nom, la version ou la date changent, adapter les métadonnées dans le script et les mentions de version de l’interface. Elles restent explicites pour éviter d’inventer une date de décision.
4. Lancer l’import, lire les anomalies et comparer le diff. Les identifiants de section s’appuient sur les `paraId` Word, indépendamment du titre. Les fiches utilisent leur numéro. Conserver ces identifiants dans Word ; si une réécriture les remplace, maintenir une redirection explicite avant publication. Les collisions sont signalées ou distinguées.
5. Lancer tests, build, vérification et tests navigateur. Examiner les validations marquées « À réexaminer ».
6. Commit, revue par les personnes habilitées et push sur `main`. GitHub Actions reconstruit et publie le site.

Le DOCX reste la référence. Une correction de texte doit être faite dans le manuscrit, puis réimportée, sans édition manuelle du JSON généré.

## Ajouter ou mettre à jour une annexe

Les fichiers modifiables sont séparés du manuscrit. Placer le fichier validé dans `public/outils/`, puis ajouter une entrée à `src/data/tool-files.json` :

```json
[{"code":"O01","file":"O01-registre-v1.xlsx","format":"XLSX","version":"1.0","date":"2026-11-16"}]
```

L’entrée ne doit être ajoutée qu’après réception réelle du fichier. Le build refuse un téléchargement pointant vers un fichier absent ou un chemin extérieur au répertoire. Rebuild et redéploiement techniques suffisent ; aucun réimport ni nouvelle validation du texte doctrinal n’est requis. Le catalogue doctrinal du Word et les métadonnées des fichiers ont des cycles séparés. Aucun fichier annexe modifiable n’était fourni dans la V3 initiale.

Le logo officiel fourni est conservé dans `public/fulbi-logo.png` et affiché dans l’en-tête et le pied de page. Aucun service externe de polices ou de statistiques n’est appelé par le site.

## GitHub Issues et décisions

Le bouton de chaque section prépare titre, corps, passage, URL, partie, type et version. La page officielle `/issues/new` s’ouvre préremplie ; l’auteur se connecte et confirme sur GitHub. Aucun jeton n’est présent côté client. Une URL de plus de 7 500 caractères est remplacée par une issue vide et une copie intégrale. En cas de refus du presse-papiers, la zone de texte reste sélectionnable et une consigne de copie apparaît.

Les cinq modèles sont dans `.github/ISSUE_TEMPLATE/` (syntaxe JSON, sous-ensemble valide de YAML). Les 18 labels métier sont décrits dans `src/utils/issues.mjs` : 6 types, 5 statuts et 7 parties. Ils ont été créés sur le dépôt. En cas de recréation du dépôt, les créer dans Settings → Issues → Labels avec ces noms exacts. Le workflow de triage pose uniquement `statut:a-instruire`, et retire une éventuelle décision de l’état initial. Les permissions d’écriture GitHub réservent les changements de labels et de fichiers aux collaborateurs habilités.

Cycle : à instruire → à compléter si nécessaire → décision motivée retenue/non retenue → correction du Word → vérification → intégrée → clôture justifiée avec lien vers le commit et la version. La non-rétention doit également être expliquée. Une issue ne modifie jamais le guide automatiquement. Seuls les mainteneurs habilités consignent les décisions faisant foi, après examen du comité. Les contributeurs publics ne disposent pas d’un bouton de validation.

Modération : utiliser les signalements GitHub ; masquer/supprimer les publications inappropriées et demander à GitHub Support une purge d’historique lorsque nécessaire. Ne pas citer à nouveau une donnée retirée. Documenter la mesure sans reproduire le contenu confidentiel. Fermer ou verrouiller une discussion abusive avec un motif. Pour une donnée sensible, ne pas demander à son auteur de la déposer dans une nouvelle issue publique.

## Synchronisation et indicateurs

`scripts/sync-issues/index.mjs` lit toutes les pages de l’API REST GitHub (`state=all`, `per_page=100`), exclut les pull requests et écrit atomiquement `src/data/issues.json` après validation complète. `GITHUB_TOKEN` n’est utilisé que dans Actions, avec `issues:read` et `contents:read`. Une lecture publique locale peut se faire avec `npm run sync` sans jeton.

Le workflow se déclenche sur création, édition, labels, suppression, transfert, clôture/réouverture, après triage, manuellement et toutes les six heures en secours. Le workflow de publication restaure l’instantané du dernier site publié avant de synchroniser. En cas d’échec API, il conserve cet instantané, ou à défaut celui versionné dans le dépôt. Une absence d’instantané affiche « indisponible », jamais un zéro inventé. L’ancienneté est affichée dans le navigateur ; après 48 heures un avertissement invite à consulter GitHub. Les compteurs sont dérivés des issues et labels réellement présents ; les groupes peuvent se recouper. Aucun corps de contribution n’est injecté dans du HTML non échappé.

## Suivi des validations

`src/data/validations.json` contient, pour chaque section : `id`, `version`, `contentHash`, `status`, `date`, `decision`, `outstanding`. États autorisés : « Non examinée », « En relecture », « Corrections demandées », « Validée pour une version précise », « À réexaminer ».

Après décision habilitée, mettre à jour le fichier dans un commit relu, avec la date ISO, la référence précise de décision et les numéros d’observations restantes. Une validation doit correspondre au hash actuel. Toute modification de contenu, même mineure par prudence, remet l’état à « À réexaminer » ; l’ancienne décision est gardée dans `previousDecision`. L’interface vérifie également le hash au build. La partie VI demeure présentée comme provisoire tant qu’une décision éditoriale n’a pas explicitement modifié cette mention.

## Déployer et administrer

Settings → Pages → Source : **GitHub Actions**. Le workflow construit le site, compare la publication au DOCX, téléverse l’artifact puis déploie avec `pages:write` et `id-token:write` uniquement dans le job de déploiement. Le chemin Astro est `/guide-sectoriel-rgpd`. Aucun serveur applicatif ni base de données ne sont nécessaires.

Ne pas ajouter de secret au navigateur, au dépôt ou au manuscrit. La configuration de dépôt peut être revue via Settings ; les permissions des collaborateurs doivent suivre la composition réelle du comité et des mainteneurs. Aucun rôle éditorial nominatif n’a été inventé.

## Tests et limites

Voir `reports/tests.md`, `reports/published-concordance.json` et `reports/browser-tests.json`. Les contrôles axe sont automatiques et ne constituent ni un audit complet ni une déclaration de conformité RGAA. Aucun test ne confirme la validité juridique du manuscrit. Les captures sont des éléments de vérification visuelle locale.

Références techniques : [déploiement Astro](https://docs.astro.build/en/guides/deploy/github/), [indexation Pagefind](https://pagefind.app/docs/indexing/), [configuration navigateur Pagefind](https://pagefind.app/docs/search-config/), [paramètres de création d’issue GitHub](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue).
