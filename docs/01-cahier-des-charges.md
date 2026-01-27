# Cahier des Charges - Logiciel CIS (Suivi Accompagnement Socioprofessionnel)

## 1. Contexte et Objectifs

### 1.1 Contexte
L'organisation accompagne des personnes bénéficiaires de l'Assurance Invalidité (AI) dans leur parcours de réinsertion socioprofessionnelle. Actuellement, les informations sont dispersées entre plusieurs outils (Outlook, Abacus, plateforme PAI existante), ce qui nuit à l'efficacité du suivi.

### 1.2 Objectifs du projet
- **Centraliser** toutes les informations relatives aux bénéficiaires (CAI) sur une plateforme unique
- **Optimiser** le suivi des objectifs et plans d'accompagnement individualisés (PAI)
- **Faciliter** la collaboration entre les différentes unités et intervenants
- **Automatiser** les rappels et la génération de rapports
- **Sécuriser** les données conformément à la LPD suisse

### 1.3 Périmètre
Le logiciel CIS couvrira :
- Gestion des profils bénéficiaires
- Suivi des objectifs et plans d'action
- Journal de bord collaboratif
- Gestion documentaire
- Tableaux de bord et reporting
- Gestion du temps et des absences

---

## 2. Acteurs et Rôles

### 2.1 Rôles utilisateurs

| Rôle | Code | Description | Niveau d'accès |
|------|------|-------------|----------------|
| Administrateur système | ADMIN | Gestion technique et configuration | Total |
| Responsable d'unité | RUA | Direction d'une unité/atelier | Lecture/écriture sur son unité + lecture inter-unités |
| Responsable | RES | Encadrement d'équipe | Lecture/écriture sur son équipe |
| Maître socioprofessionnel | MSP | Accompagnement direct des CAI | Lecture/écriture sur ses références + lecture inter-unités |
| Consultation | CONSULT | Accès en lecture seule | Lecture uniquement |

### 2.2 Bénéficiaires
- **CAI** (Collaborateur en Atelier d'Insertion) : personne accompagnée, sujet principal du suivi

---

## 3. Exigences Fonctionnelles

### 3.1 Module Profil Bénéficiaire (CAI)

#### 3.1.1 Données personnelles
| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Nom | Texte | Oui | Nom de famille |
| Prénom | Texte | Oui | Prénom(s) |
| Date de naissance | Date | Oui | |
| Photo | Image | Non | Portrait pour identification |
| Adresse | Texte | Oui | Adresse postale complète |
| Téléphone | Texte | Non | Numéro principal |
| Email | Email | Non | |
| Langue | Sélection | Oui | Langue de communication |

#### 3.1.2 Données administratives
| Champ | Type | Description |
|-------|------|-------------|
| Numéro AI | Texte | Identifiant assurance invalidité |
| Type de rente | Sélection | Quart, demi, trois-quarts, entière |
| Statut curatelle | Sélection | Type de mesure de protection |
| Curateur | Relation | Lien vers contact réseau |
| Date d'entrée | Date | Entrée dans la structure |
| Date de sortie | Date | Sortie (si applicable) |
| Statut | Sélection | Actif, en pause, sorti |

#### 3.1.3 Données contractuelles/RH
| Champ | Type | Description |
|-------|------|-------------|
| Type de contrat | Sélection | CDD, CDI, stage, mesure AI |
| Taux d'occupation | Pourcentage | Temps de travail |
| Salaire | Montant | Rémunération |
| Unité/Atelier | Relation | Affectation principale |
| MSP référent | Relation | Accompagnant principal |

#### 3.1.4 Données médicales (accès restreint)
| Champ | Type | Description |
|-------|------|-------------|
| Médication | Texte | Traitements impactant la sécurité |
| Restrictions | Texte | Limitations physiques/cognitives |
| Allergies | Texte | Pour urgences |
| Notes médicales | Texte riche | Informations confidentielles |

#### 3.1.5 Réseau et contacts
| Champ | Type | Description |
|-------|------|-------------|
| Personne d'urgence | Contact | Nom + téléphone |
| Médecin traitant | Contact | Coordonnées |
| Psychologue | Contact | Si applicable |
| Référent AI | Contact | Conseiller AI |
| Autres intervenants | Liste contacts | Réseau complet |

#### 3.1.6 Comportements à risque
| Champ | Type | Description |
|-------|------|-------------|
| Type de risque | Sélection multiple | Catégorisation |
| Description | Texte riche | Détail du comportement |
| Niveau de gravité | Sélection | Faible, moyen, élevé, critique |
| Mesures préventives | Texte | Actions à mettre en place |
| Date signalement | Date | |
| Signalé par | Utilisateur | |

---

### 3.2 Module Plan d'Accompagnement Individualisé (PAI)

#### 3.2.1 Structure du PAI
```
PAI
├── Informations générales
│   ├── Date de création
│   ├── Période de validité
│   ├── Statut (brouillon, actif, clôturé)
│   └── Créé par (MSP)
├── Bilan initial
│   ├── Forces identifiées
│   ├── Difficultés identifiées
│   └── Souhaits du bénéficiaire
├── Objectifs
│   ├── Objectifs long terme (> 1 an)
│   ├── Objectifs moyen terme (3-12 mois)
│   └── Objectifs court terme (< 3 mois)
└── Historique des révisions
```

#### 3.2.2 Objectifs
| Champ | Type | Description |
|-------|------|-------------|
| Titre | Texte | Intitulé court |
| Description | Texte riche | Détail de l'objectif |
| Type | Sélection | PAI, comportemental, opérationnel |
| Échéance | Date | Date cible |
| Priorité | Sélection | Haute, moyenne, basse |
| Statut | Sélection | À faire, en cours, atteint, abandonné |
| Progression | Pourcentage | 0-100% |
| Indicateurs | Liste | Critères de réussite mesurables |

#### 3.2.3 Actions (sous-tâches d'un objectif)
| Champ | Type | Description |
|-------|------|-------------|
| Description | Texte | Action à réaliser |
| Responsable | Sélection | Qui (CAI, MSP, autre) |
| Échéance | Date | |
| Statut | Sélection | À faire, fait |
| Notes | Texte | Commentaires |

#### 3.2.4 Rappels automatiques
- Rappel configurable (hebdomadaire, mensuel)
- Notification avant échéance (J-7, J-3, J-1)
- Alerte objectif en retard
- Intégration Outlook possible (export ICS)

---

### 3.3 Module Journal de Bord

#### 3.3.1 Entrée de journal
| Champ | Type | Description |
|-------|------|-------------|
| Date/Heure | DateTime | Automatique ou manuel |
| Auteur | Utilisateur | MSP qui rédige |
| CAI concerné | Relation | Bénéficiaire |
| Catégorie | Sélection multiple | Voir liste ci-dessous |
| Titre | Texte | Résumé court |
| Contenu | Texte riche | Description détaillée |
| Visibilité | Sélection | Équipe, unité, inter-unités |
| Pièces jointes | Fichiers | Documents liés |
| Tags | Liste | Mots-clés libres |

#### 3.3.2 Catégories de journal
- Santé
- Comportement
- Conflit
- Compétences / Formation
- Vie privée
- Échange inter-unités
- Entretien
- Incident
- Progrès / Réussite
- Autre

#### 3.3.3 Fonctionnalités de recherche
- Filtrage par catégorie, date, auteur, tags
- Recherche plein texte
- Export historique (PDF, Excel)
- Extraction multi-CAI (répertoire comportements à risque)

---

### 3.4 Module Gestion du Temps

#### 3.4.1 Suivi des timbrages
| Champ | Type | Description |
|-------|------|-------------|
| Date | Date | |
| Heure entrée | Time | |
| Heure sortie | Time | |
| Heures travaillées | Calculé | |
| Type | Sélection | Travail, formation, rendez-vous |

#### 3.4.2 Absences
| Champ | Type | Description |
|-------|------|-------------|
| Type | Sélection | Maladie, vacances, accident, autre |
| Date début | Date | |
| Date fin | Date | |
| Justificatif | Fichier | Certificat médical, etc. |
| Validé par | Utilisateur | |

#### 3.4.3 Indicateurs
- Taux d'absentéisme (calculé automatiquement)
- Solde vacances
- Historique des absences
- Alertes seuils (ex: > 20% absentéisme)

---

### 3.5 Module Compétences et Formations

#### 3.5.1 Matrice des compétences
| Champ | Type | Description |
|-------|------|-------------|
| Compétence | Relation | Référentiel compétences |
| Niveau | Sélection | Non acquis, en cours, acquis, maîtrisé |
| Date évaluation | Date | |
| Évalué par | Utilisateur | |
| Commentaire | Texte | |

#### 3.5.2 Formations internes
| Champ | Type | Description |
|-------|------|-------------|
| Intitulé | Texte | Nom de la formation |
| Date | Date | |
| Durée | Nombre | En heures |
| Formateur | Texte/Utilisateur | |
| Attestation | Fichier | |
| Commentaire | Texte | Appréciation |

#### 3.5.3 Suivi Alto (si applicable)
- Intégration ou saisie manuelle des données Alto
- Historique des évaluations

---

### 3.6 Module Documents (GED)

#### 3.6.1 Types de documents
- Contrats
- Certificats médicaux
- Évaluations
- Rapports
- Correspondance
- Photos / Justificatifs

#### 3.6.2 Métadonnées
| Champ | Type | Description |
|-------|------|-------------|
| Nom fichier | Texte | |
| Type document | Sélection | |
| Date document | Date | |
| Date upload | DateTime | Automatique |
| Uploadé par | Utilisateur | |
| CAI concerné | Relation | |
| Confidentialité | Sélection | Standard, confidentiel, très confidentiel |
| Description | Texte | |

#### 3.6.3 Fonctionnalités
- Upload multiple
- Prévisualisation (PDF, images)
- Versioning automatique
- Recherche par métadonnées
- Archivage automatique

---

### 3.7 Module Tableaux de Bord

#### 3.7.1 Dashboard MSP
- Liste des CAI référés avec statut visuel
- Objectifs en cours / en retard (code couleurs)
- Alertes et rappels du jour
- Dernières entrées journal
- Tâches à effectuer

#### 3.7.2 Dashboard Direction
- Vue globale tous CAI
- Statistiques : entrées/sorties, taux réinsertion
- Taux d'absentéisme global et par unité
- Objectifs en retard (toutes unités)
- Indicateurs de performance

#### 3.7.3 Vue Objectifs Globale
- Tableau de tous les CAI avec leurs objectifs
- Filtrage par unité, MSP, type d'objectif
- Code couleurs : vert (OK), orange (attention), rouge (retard)
- Export Excel

---

### 3.8 Module Rapports et Exports

#### 3.8.1 Rapports prédéfinis
- Synthèse individuelle CAI (PDF)
- Rapport d'activité mensuel/annuel
- Historique journal d'un CAI
- Liste des comportements à risque
- Statistiques d'absentéisme
- Bilan des objectifs

#### 3.8.2 Exports
- PDF (rapports formatés)
- Excel (données brutes, listes)
- ICS (calendrier objectifs/rappels)

#### 3.8.3 Partage
- Génération de liens temporaires sécurisés
- Envoi par email intégré
- Traçabilité des partages

---

## 4. Exigences Non Fonctionnelles

### 4.1 Performance
- Temps de chargement page < 2 secondes
- Recherche plein texte < 1 seconde
- Support 50 utilisateurs simultanés minimum
- Disponibilité 99.5% (heures ouvrées)

### 4.2 Sécurité
- Authentification forte (mot de passe + 2FA optionnel)
- Chiffrement des données sensibles (AES-256)
- HTTPS obligatoire
- Tokens JWT avec expiration
- Protection CSRF, XSS, injection SQL
- Audit trail complet (qui, quoi, quand)

### 4.3 Conformité LPD
- Consentement documenté pour données sensibles
- Droit d'accès et de rectification
- Durée de conservation configurable
- Anonymisation/suppression sur demande
- Registre des traitements

### 4.4 Accessibilité
- Interface responsive (desktop, tablette, mobile)
- Support navigateurs modernes (Chrome, Firefox, Safari, Edge)
- Contrastes suffisants (WCAG AA)

### 4.5 Maintenabilité
- Code documenté
- Tests automatisés (>80% couverture)
- Logs structurés
- Monitoring des erreurs

---

## 5. Contraintes Techniques

### 5.1 Hébergement
- **On-premise obligatoire** (serveurs internes)
- Pas de cloud public pour les données

### 5.2 Stack technique imposée
- **Conteneurisation** : Docker / Docker Compose
- **Frontend** : React (TypeScript recommandé)
- **Backend** : Python 3.11+ avec FastAPI
- **Base de données** : PostgreSQL 15+
- **Migrations** : Alembic
- **Cache** : Redis (optionnel)

### 5.3 Intégrations souhaitées
- Export calendrier Outlook (ICS)
- Import/export Abacus (à définir)
- API REST documentée (OpenAPI/Swagger)

---

## 6. Livrables Attendus

1. Code source complet (Git)
2. Documentation technique (architecture, API, déploiement)
3. Documentation utilisateur
4. Scripts de déploiement Docker
5. Jeu de données de test
6. Plan de tests et résultats

---

## 7. Planning Indicatif

| Phase | Durée estimée | Livrables |
|-------|---------------|-----------|
| Conception détaillée | 2 semaines | Maquettes, modèle de données |
| Développement MVP | 8 semaines | Modules profil, PAI, journal |
| Développement complet | 6 semaines | Modules temps, GED, dashboards |
| Tests et corrections | 2 semaines | Rapport de tests |
| Déploiement pilote | 2 semaines | Installation, formation |
| Mise en production | 1 semaine | Go-live |

---

## 8. Critères d'Acceptation

- Toutes les fonctionnalités décrites sont opérationnelles
- Performance conforme aux exigences
- Tests de sécurité passés (OWASP Top 10)
- Documentation complète
- Formation des utilisateurs clés effectuée
- Période de garantie de 3 mois
