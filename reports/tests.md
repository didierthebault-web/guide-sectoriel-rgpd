# Rapport de tests

Date : 16 novembre 2026. Manuscrit V3. Les résultats ci-dessous concernent le build local ; le contrôle de publication est consigné séparément dans `deployment.json` après déploiement.

| Contrôle demandé | Résultat et preuve |
| --- | --- |
| Sept parties intégrales | Vérification indépendante DOCX/HTML, 4 946 paragraphes dans le même ordre et avec le même texte |
| Vingt fiches métier | 20 numéros uniques ; seconde fiche 06 conservée comme complément |
| Tableaux | 60 tableaux ; texte de toutes les cellules comparé à la source |
| Listes | 721 éléments de liste conservés ; nombre et séquence contrôlés |
| Recherche plein texte | Pagefind : 433 pages de section indexées, langue française, filtre Partie ; recherche « conservation » testée avec extraits et liens |
| Liens permanents | 433 identifiants uniques, ancres présentes ; copie d’URL testée au navigateur |
| Navigation mobile | Pages accueil, fiches, outils, partie IV, fiche 01 à 390 × 844 ; aucun débordement global ; navigation repliable testée |
| Navigation clavier | Lien d’évitement, accès aux champs, fermeture Échap et retour du focus à l’appelant testés |
| Proposer une observation | Métadonnées de la section et de version vérifiées |
| Préremplissage GitHub | Domaine, dépôt, titre, corps et labels vérifiés ; aucune publication de test effectuée |
| Copier une observation | Presse-papiers testé ; refus simulé et sélection manuelle vérifiée ; contribution longue testée |
| Modèles d’issues | Cinq modèles présents avec avertissement public et statut initial |
| Labels | 18 labels métier créés et relus via l’API du dépôt |
| Synchronisation | Lecture réelle : 0 issue au premier instantané ; tests de pagination à 101 éléments, exclusion des PR, erreur API et conservation atomique |
| Date de synchronisation | Date réelle et ancienneté affichées, contrôlées au navigateur |
| Indicateurs et filtres | Compteurs testés avec fixtures ouvertes/clôturées ; filtres du tableau de bord testés sur l’instantané réel vide |
| Validation par version | État initial non examiné ; test de changement de hash → à réexaminer ; partie VI provisoire |
| Dix-huit outils | O01 à O18 et leurs liens vers le manuscrit vérifiés |
| Téléchargements | Word source réel ; aucun téléchargement d’annexe inventé ; futurs fichiers contrôlés au build |
| Chemin de base | Navigation et liens de recherche testés sous /guide-sectoriel-rgpd/ |
| Accessibilité automatique | axe WCAG A/AA et WCAG 2.1 AA : zéro violation sur accueil, fiches, outils, concertation, fiche 01 |
| Erreurs JavaScript | Aucune dans les parcours testés |
| Dépendances | Après mise à jour Astro : npm audit, zéro vulnérabilité connue |
| Logo FULBI | Fichier fourni intégré à l’en-tête et au pied de page ; dimensions proportionnelles, texte alternatif et affichage mobile contrôlés |

Neuf tests Node passent. Neuf groupes de tests navigateur passent, dont le réglage effectif de la taille du texte sur mobile. Le vérificateur de concordance indépendant passe. Les captures de l’accueil, de la recherche, du formulaire et de la lecture mobile ont été générées pour examen visuel.

Limites : pas d’audit RGAA exhaustif, pas de test avec une personne utilisatrice de lecteur d’écran, pas de revue juridique du fond, pas de publication d’issue de test et pas de simulation réelle d’une panne GitHub en production. Les tests de synchronisation couvrent les cas d’erreur avec des réponses simulées. La validation des textes et les décisions du comité restent humaines.
