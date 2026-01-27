# Spécifications UI/UX - CIS

## 1. Principes Directeurs

### 1.1 Philosophie
L'interface doit être **chaleureuse, dynamique et intuitive** selon les retours des utilisateurs. L'objectif est de réduire le temps passé sur les tâches administratives pour permettre aux MSP de se concentrer sur l'accompagnement humain.

### 1.2 Principes UX

| Principe | Application |
|----------|-------------|
| **Clarté** | Information hiérarchisée, pas de surcharge visuelle |
| **Efficacité** | Accès rapide aux actions fréquentes (2-3 clics max) |
| **Cohérence** | Patterns UI identiques dans toute l'application |
| **Feedback** | Confirmation des actions, états de chargement clairs |
| **Accessibilité** | WCAG AA, contraste suffisant, navigation clavier |

### 1.3 Cibles utilisateurs

| Profil | Caractéristiques | Besoins prioritaires |
|--------|------------------|---------------------|
| MSP | Usage quotidien, terrain + bureau | Rapidité, mobile-friendly, vue centrée bénéficiaire |
| RUA/RES | Usage hebdomadaire, bureau | Tableaux de bord, rapports, vue globale |
| ADMIN | Usage occasionnel | Configuration, gestion utilisateurs |

---

## 2. Identité Visuelle

### 2.1 Palette de Couleurs

```css
/* Couleurs principales */
--primary-50: #EFF6FF;
--primary-100: #DBEAFE;
--primary-200: #BFDBFE;
--primary-300: #93C5FD;
--primary-400: #60A5FA;
--primary-500: #3B82F6;  /* Principal */
--primary-600: #2563EB;
--primary-700: #1D4ED8;
--primary-800: #1E40AF;
--primary-900: #1E3A8A;

/* Couleurs secondaires (accent chaleureux) */
--secondary-400: #FB923C;
--secondary-500: #F97316;  /* Orange accent */
--secondary-600: #EA580C;

/* Couleurs sémantiques */
--success: #22C55E;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;

/* Neutres */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-400: #9CA3AF;
--gray-500: #6B7280;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;

/* Background */
--bg-primary: #FFFFFF;
--bg-secondary: #F9FAFB;
--bg-tertiary: #F3F4F6;
```

### 2.2 Codes Couleurs Objectifs

```css
/* Statuts objectifs */
--status-pending: #9CA3AF;     /* Gris - À faire */
--status-in-progress: #3B82F6; /* Bleu - En cours */
--status-achieved: #22C55E;    /* Vert - Atteint */
--status-abandoned: #6B7280;   /* Gris foncé - Abandonné */
--status-overdue: #EF4444;     /* Rouge - En retard */

/* Priorités */
--priority-high: #EF4444;
--priority-medium: #F59E0B;
--priority-low: #22C55E;
```

### 2.3 Typographie

```css
/* Police principale */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Tailles */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* Poids */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 2.4 Espacements

```css
/* Système 4px */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
```

### 2.5 Ombres et Bordures

```css
/* Ombres */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

/* Bordures */
--radius-sm: 0.25rem;  /* 4px */
--radius: 0.375rem;    /* 6px */
--radius-md: 0.5rem;   /* 8px */
--radius-lg: 0.75rem;  /* 12px */
--radius-xl: 1rem;     /* 16px */
--radius-full: 9999px;
```

---

## 3. Structure des Pages

### 3.1 Layout Principal

```
┌─────────────────────────────────────────────────────────────┐
│                         Header                               │
│  [Logo] [Recherche globale...] [Notifs] [User Menu]         │
├───────────┬─────────────────────────────────────────────────┤
│           │                                                  │
│  Sidebar  │              Zone de contenu                     │
│           │                                                  │
│  - Accueil│                                                  │
│  - CAI    │                                                  │
│  - Object.│                                                  │
│  - Journal│                                                  │
│  - Docs   │                                                  │
│  - Rapports                                                  │
│  ─────────│                                                  │
│  - Admin  │                                                  │
│           │                                                  │
└───────────┴─────────────────────────────────────────────────┘
```

### 3.2 Responsive Breakpoints

```css
/* Mobile first */
--breakpoint-sm: 640px;   /* Petit mobile → Grand mobile */
--breakpoint-md: 768px;   /* Mobile → Tablette */
--breakpoint-lg: 1024px;  /* Tablette → Desktop */
--breakpoint-xl: 1280px;  /* Desktop → Grand écran */
--breakpoint-2xl: 1536px; /* Grand écran */
```

### 3.3 Comportement Responsive

| Élément | Mobile (<768px) | Tablette (768-1024px) | Desktop (>1024px) |
|---------|-----------------|----------------------|-------------------|
| Sidebar | Menu hamburger | Icônes uniquement | Complète |
| Tableaux | Cards empilées | Scroll horizontal | Complet |
| Formulaires | 1 colonne | 2 colonnes | 2-3 colonnes |
| Dashboard | Cards empilées | Grid 2 cols | Grid 3-4 cols |

---

## 4. Composants UI

### 4.1 Navigation

#### Header
```
┌────────────────────────────────────────────────────────────┐
│ [≡]  [🔷 CIS]    [🔍 Rechercher...]        [🔔 3] [👤 JD ▼]│
└────────────────────────────────────────────────────────────┘
```

- Logo cliquable → Dashboard
- Recherche globale (bénéficiaires, objectifs, journal)
- Notification badge avec compteur
- Menu utilisateur avec déconnexion

#### Sidebar
```
┌──────────────────┐
│ 📊 Tableau de bord │ ← Active: fond bleu clair
├──────────────────┤
│ 👥 Bénéficiaires  │
│ 🎯 Objectifs      │
│ 📝 Journal        │
│ 📁 Documents      │
│ 📈 Rapports       │
├──────────────────┤
│ ⚙️ Administration │ ← Visible si admin/RUA
└──────────────────┘
```

### 4.2 Cards Bénéficiaires

```
┌─────────────────────────────────────────────┐
│ ┌─────┐                                     │
│ │ 📷  │  Pierre Martin                      │
│ │     │  Atelier Bois • MSP: Jean Dupont   │
│ └─────┘                                     │
├─────────────────────────────────────────────┤
│ Objectifs                                   │
│ [●●●○○] 3/5 en cours   [!] 1 en retard     │
├─────────────────────────────────────────────┤
│ Dernière note: 15 jan. 2024                 │
│ [Voir profil →]                             │
└─────────────────────────────────────────────┘
```

### 4.3 Cards Objectifs

```
┌─────────────────────────────────────────────┐
│ [●] PAI  [⚡ Haute]                     [⋮] │
├─────────────────────────────────────────────┤
│ Améliorer la gestion du stress              │
│                                             │
│ Pierre Martin                               │
├─────────────────────────────────────────────┤
│ ████████░░░░░░░░░░░░ 40%                   │
├─────────────────────────────────────────────┤
│ 📅 Échéance: 30 juin 2024                   │
│ [En cours ▼]                                │
└─────────────────────────────────────────────┘
```

### 4.4 Formulaires

#### Input standard
```
┌─────────────────────────────────────────────┐
│ Prénom *                                    │
│ ┌─────────────────────────────────────────┐ │
│ │ Pierre                                  │ │
│ └─────────────────────────────────────────┘ │
│ ✓ Champ valide                              │
└─────────────────────────────────────────────┘
```

#### Input avec erreur
```
┌─────────────────────────────────────────────┐
│ Email *                                     │
│ ┌─────────────────────────────────────────┐ │
│ │ pierre.martin                      [❌] │ │
│ └─────────────────────────────────────────┘ │
│ ⚠️ Format d'email invalide                  │
└─────────────────────────────────────────────┘
```

#### Select
```
┌─────────────────────────────────────────────┐
│ Unité / Atelier *                           │
│ ┌─────────────────────────────────────────┐ │
│ │ Atelier Bois                        [▼] │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 4.5 Tableaux

```
┌──────────────────────────────────────────────────────────────────┐
│ [☐] Nom ↕        │ Unité      │ Référent    │ Statut │ Actions  │
├──────────────────────────────────────────────────────────────────┤
│ [☐] Martin Pierre│ Atelier Bois│ J. Dupont  │ [Actif]│ [👁] [✏️]│
│ [☐] Durand Jean  │ Atelier Métal│ M. Bernard │ [Pause]│ [👁] [✏️]│
│ [☐] Garcia Maria │ Atelier Bois│ J. Dupont  │ [Actif]│ [👁] [✏️]│
├──────────────────────────────────────────────────────────────────┤
│ Affichage 1-20 sur 45                    [< 1 2 3 ... 5 >]      │
└──────────────────────────────────────────────────────────────────┘
```

### 4.6 Badges et Tags

```
Statuts:
[● Actif]     → Vert, fond vert clair
[● En pause]  → Orange, fond orange clair
[● Sorti]     → Gris, fond gris clair

Priorités:
[⚡ Haute]    → Rouge
[● Moyenne]   → Orange
[○ Basse]     → Vert

Catégories journal:
[Santé]       → Vert émeraude
[Conflit]     → Rouge
[Entretien]   → Indigo
```

### 4.7 Modales

```
┌─────────────────────────────────────────────┐
│ Nouveau bénéficiaire                    [×] │
├─────────────────────────────────────────────┤
│                                             │
│  [Contenu du formulaire]                    │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│                    [Annuler] [Enregistrer]  │
└─────────────────────────────────────────────┘
```

### 4.8 Alertes et Toasts

```
Succès:
┌─────────────────────────────────────────────┐
│ ✓ Bénéficiaire créé avec succès        [×] │
└─────────────────────────────────────────────┘

Erreur:
┌─────────────────────────────────────────────┐
│ ❌ Erreur lors de l'enregistrement      [×] │
│    Veuillez réessayer                       │
└─────────────────────────────────────────────┘

Avertissement:
┌─────────────────────────────────────────────┐
│ ⚠️ 3 objectifs arrivent à échéance      [×] │
│    cette semaine                            │
└─────────────────────────────────────────────┘
```

---

## 5. Pages Principales

### 5.1 Dashboard MSP

```
┌─────────────────────────────────────────────────────────────────┐
│ Bonjour Jean 👋                              Lundi 15 janv. 2024│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────┐ ┌─────────────────────────────────────┐│
│ │ Mes bénéficiaires   │ │ Rappels du jour                     ││
│ │ 8 actifs            │ │                                     ││
│ │                     │ │ ⚠️ Objectif échéance: P. Martin     ││
│ │ [Card] [Card]       │ │ 📅 Entretien mensuel: M. Garcia     ││
│ │ [Card] [Card]       │ │ 📋 Valider absence: J. Durand       ││
│ │ ...                 │ │                                     ││
│ └─────────────────────┘ └─────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Dernières entrées journal                                   ││
│ │                                                             ││
│ │ 📝 Entretien mensuel - P. Martin        Il y a 2 heures    ││
│ │ 📝 Incident atelier - J. Durand         Hier               ││
│ │ 📝 Progrès formation - M. Garcia        Il y a 2 jours     ││
│ └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Liste Bénéficiaires

```
┌─────────────────────────────────────────────────────────────────┐
│ Bénéficiaires                              [+ Nouveau]          │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 🔍 Rechercher...  │ Unité: [Tous ▼] │ Statut: [Actif ▼]    ││
│ └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Vue: [☷ Grille] [≡ Liste]                     45 résultats ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ [Cards ou Tableau selon la vue sélectionnée]                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Profil Bénéficiaire

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Retour                                            [✏️ Modifier]│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────┐                                                     │
│ │  Photo  │  Pierre Martin                    [● Actif]         │
│ │         │  Atelier Bois • Référent: Jean Dupont              │
│ └─────────┘  Entrée: 01.06.2023 • Taux: 80%                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [Informations] [PAI & Objectifs] [Journal] [Temps] [Documents] │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ ┌──────────────────────────┐ ┌────────────────────────────────┐│
│ │ Données personnelles     │ │ Réseau / Contacts              ││
│ │                          │ │                                ││
│ │ Adresse: Rue Gare 10     │ │ 🚨 Marie Martin (urgence)     ││
│ │ 1000 Lausanne            │ │    +41 79 987 65 43           ││
│ │                          │ │                                ││
│ │ Tél: +41 79 123 45 67    │ │ 🏥 Dr. Müller (médecin)       ││
│ │ Email: p.martin@mail.ch  │ │    +41 21 123 45 67           ││
│ └──────────────────────────┘ └────────────────────────────────┘│
│                                                                 │
│ ┌──────────────────────────┐ ┌────────────────────────────────┐│
│ │ Données administratives  │ │ Statistiques                   ││
│ │                          │ │                                ││
│ │ N° AI: AI-12345          │ │ Objectifs:  ████░░ 4/6         ││
│ │ Rente: Demi-rente        │ │ Absentéisme 30j: 5.5%         ││
│ │ Curatelle: Aucune        │ │ Dernière note: 15.01.2024     ││
│ └──────────────────────────┘ └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Onglet PAI & Objectifs

```
┌─────────────────────────────────────────────────────────────────┐
│ PAI actif: 01.01.2024 - 31.12.2024                [Voir PAI]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Objectifs (6)                               [+ Nouvel objectif] │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Filtrer: [Tous ▼]  Trier: [Échéance ▼]                     ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ [●] PAI  [⚡]  Améliorer gestion du stress                  ││
│ │ ████████░░░░░░░░░░ 40%           Échéance: 30.06.2024     ││
│ │ [En cours ▼]                                         [→]   ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ [●] Opérationnel     Maîtriser la scie circulaire          ││
│ │ ████████████████████ 100%        Atteint: 10.01.2024      ││
│ │ [Atteint ✓]                                          [→]   ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ [Charger plus...]                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 Vue Objectifs Globale

```
┌─────────────────────────────────────────────────────────────────┐
│ Vue globale des objectifs                      [📥 Export Excel]│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Unité: [Toutes ▼] │ MSP: [Tous ▼] │ Statut: [En cours ▼]  ││
│ │ Type: [Tous ▼]    │ [Échéances uniquement ☐]              ││
│ └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Résumé: 120 objectifs │ 🟢 35 atteints │ 🔵 50 en cours    ││
│ │         🟠 30 à faire │ 🔴 12 en retard                    ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌──────────────────────────────────────────────────────────────┐
│ │ Bénéficiaire    │ Objectif              │ Prog. │ Échéance  │
│ ├──────────────────────────────────────────────────────────────┤
│ │ P. Martin       │ Gestion stress        │ 40%   │ 🔴 30.06  │
│ │ P. Martin       │ Communication groupe  │ 20%   │ 30.09     │
│ │ J. Durand       │ Ponctualité           │ 60%   │ 🟠 15.02  │
│ │ M. Garcia       │ Autonomie poste       │ 80%   │ 28.02     │
│ └──────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### 5.6 Journal de Bord

```
┌─────────────────────────────────────────────────────────────────┐
│ Journal de bord                               [+ Nouvelle entrée]│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 🔍 Rechercher...                                           ││
│ │ Bénéficiaire: [Tous ▼] │ Catégorie: [Toutes ▼]            ││
│ │ Période: [7 derniers jours ▼]     │ Tags: [________]      ││
│ └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 📅 Aujourd'hui                                              ││
│ ├─────────────────────────────────────────────────────────────┤│
│ │ ┌─────────────────────────────────────────────────────────┐││
│ │ │ 14:30 │ Entretien mensuel - janvier          [Entretien]│││
│ │ │       │ Pierre Martin • Par: Jean Dupont                │││
│ │ │       │ Discussion sur les progrès réalisés en matière..│││
│ │ │       │ [entretien-mensuel] [bilan]              [→]   │││
│ │ └─────────────────────────────────────────────────────────┘││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 📅 Hier                                                     ││
│ ├─────────────────────────────────────────────────────────────┤│
│ │ [Entrées...]                                                ││
│ └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Interactions et Animations

### 6.1 Transitions

```css
/* Transition standard */
transition: all 150ms ease-in-out;

/* Hover cards */
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Apparition éléments */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 6.2 États des éléments

| État | Style |
|------|-------|
| Default | Fond blanc, bordure grise |
| Hover | Légère élévation, ombre |
| Focus | Ring bleu 2px |
| Active | Fond bleu clair |
| Disabled | Opacité 50%, curseur not-allowed |
| Loading | Skeleton ou spinner |

### 6.3 Feedback utilisateur

- **Chargement**: Skeleton screens pour les listes, spinner pour les actions
- **Succès**: Toast vert en haut à droite, disparition auto après 3s
- **Erreur**: Toast rouge persistant jusqu'à fermeture manuelle
- **Confirmation**: Modal de confirmation pour actions destructrices

---

## 7. Accessibilité

### 7.1 Navigation clavier

| Touche | Action |
|--------|--------|
| Tab | Navigation entre éléments focusables |
| Enter | Activation bouton/lien |
| Escape | Fermeture modal/dropdown |
| Flèches | Navigation dans les listes/menus |

### 7.2 ARIA

```html
<!-- Exemple modal -->
<div role="dialog" aria-labelledby="modal-title" aria-modal="true">
  <h2 id="modal-title">Titre modal</h2>
  ...
</div>

<!-- Exemple alerte -->
<div role="alert" aria-live="polite">
  Bénéficiaire créé avec succès
</div>
```

### 7.3 Contraste

- Texte normal: ratio minimum 4.5:1
- Texte large (>18px): ratio minimum 3:1
- Éléments interactifs: ratio minimum 3:1

---

## 8. Mobile et Tablette

### 8.1 Adaptations Mobile

- Sidebar → Menu hamburger
- Tableaux → Cards empilées
- Actions groupées → Menu contextuel (⋮)
- Filtres → Panneau coulissant
- Navigation onglets → Scroll horizontal

### 8.2 Touch Targets

- Taille minimum: 44x44px
- Espacement minimum entre cibles: 8px

### 8.3 Gestes

- Swipe gauche sur card: Actions rapides
- Pull to refresh: Rafraîchissement liste
- Long press: Menu contextuel

---

## 9. États Vides et Erreurs

### 9.1 État Vide

```
┌─────────────────────────────────────────────┐
│                                             │
│              [Illustration]                 │
│                                             │
│         Aucun bénéficiaire trouvé           │
│                                             │
│   Modifiez vos filtres ou créez un         │
│   nouveau bénéficiaire.                     │
│                                             │
│           [+ Créer un bénéficiaire]         │
│                                             │
└─────────────────────────────────────────────┘
```

### 9.2 État Erreur

```
┌─────────────────────────────────────────────┐
│                                             │
│              [Illustration erreur]          │
│                                             │
│       Une erreur est survenue               │
│                                             │
│   Impossible de charger les données.        │
│   Veuillez réessayer.                       │
│                                             │
│              [Réessayer]                    │
│                                             │
└─────────────────────────────────────────────┘
```

### 9.3 Page 404

```
┌─────────────────────────────────────────────┐
│                                             │
│                   404                       │
│                                             │
│         Page non trouvée                    │
│                                             │
│   La page que vous recherchez n'existe      │
│   pas ou a été déplacée.                    │
│                                             │
│        [Retour à l'accueil]                 │
│                                             │
└─────────────────────────────────────────────┘
```
