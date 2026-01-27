# Design System - CIS

## 1. Design Philosophy

### 1.1 Principes Directeurs

Le design system CIS est conçu pour un environnement **professionnel de santé et services sociaux** suisse. Il doit être:

| Principe | Application |
|----------|-------------|
| **Chaleureux** | Couleurs douces, accents orangés pour l'humain |
| **Professionnel** | Sobre, structuré, inspirant confiance |
| **Accessible** | WCAG AA, contraste élevé, navigation claire |
| **Efficace** | Réduction du temps administratif |

### 1.2 Style Sélectionné: Clean Professional + Soft Accents

Combinaison de:
- **Minimalism** - Interface épurée, espace blanc généreux
- **Soft UI** - Coins arrondis, ombres douces, transitions fluides
- **Dashboard Professional** - Grilles structurées, hiérarchie claire

**Anti-patterns à éviter:**
- Glassmorphism excessif (lisibilité réduite)
- Dark mode forcé (contexte professionnel diurne)
- Animations distractives (usage intensif)
- Emojis comme icônes (non professionnel)

---

## 2. Palette de Couleurs

### 2.1 Couleurs Principales

```css
:root {
  /* Primary - Bleu confiance (professionnel, suisse) */
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

  /* Secondary - Orange chaleureux (humain, social) */
  --secondary-50: #FFF7ED;
  --secondary-100: #FFEDD5;
  --secondary-200: #FED7AA;
  --secondary-300: #FDBA74;
  --secondary-400: #FB923C;
  --secondary-500: #F97316;  /* Accent */
  --secondary-600: #EA580C;
  --secondary-700: #C2410C;
  --secondary-800: #9A3412;
  --secondary-900: #7C2D12;
}
```

### 2.2 Couleurs Sémantiques

```css
:root {
  /* Statuts */
  --success-50: #F0FDF4;
  --success-500: #22C55E;
  --success-700: #15803D;

  --warning-50: #FFFBEB;
  --warning-500: #F59E0B;
  --warning-700: #B45309;

  --error-50: #FEF2F2;
  --error-500: #EF4444;
  --error-700: #B91C1C;

  --info-50: #EFF6FF;
  --info-500: #3B82F6;
  --info-700: #1D4ED8;
}
```

### 2.3 Couleurs Objectifs (Code couleurs visuels)

```css
:root {
  /* Statuts objectifs */
  --objective-pending: #9CA3AF;     /* Gris - À faire */
  --objective-in-progress: #3B82F6; /* Bleu - En cours */
  --objective-achieved: #22C55E;    /* Vert - Atteint */
  --objective-abandoned: #6B7280;   /* Gris foncé - Abandonné */
  --objective-overdue: #EF4444;     /* Rouge - En retard */

  /* Priorités */
  --priority-high: #EF4444;
  --priority-medium: #F59E0B;
  --priority-low: #22C55E;

  /* Termes */
  --term-short: #8B5CF6;   /* Violet - Court terme */
  --term-medium: #3B82F6;  /* Bleu - Moyen terme */
  --term-long: #06B6D4;    /* Cyan - Long terme */
}
```

### 2.4 Catégories Journal (avec icônes)

| Catégorie | Couleur | Code Hex | Icône Lucide |
|-----------|---------|----------|--------------|
| Santé | Émeraude | `#10B981` | `heart-pulse` |
| Comportement | Ambre | `#F59E0B` | `alert-triangle` |
| Conflit | Rouge | `#EF4444` | `zap` |
| Compétences | Bleu | `#3B82F6` | `book-open` |
| Vie privée | Violet | `#8B5CF6` | `user` |
| Inter-unités | Cyan | `#06B6D4` | `users` |
| Entretien | Indigo | `#6366F1` | `message-circle` |
| Incident | Rouge foncé | `#DC2626` | `alert-circle` |
| Progrès | Vert | `#22C55E` | `trending-up` |
| Autre | Gris | `#6B7280` | `file-text` |

### 2.5 Neutres

```css
:root {
  --gray-50: #F9FAFB;   /* Background secondaire */
  --gray-100: #F3F4F6;  /* Background tertiaire */
  --gray-200: #E5E7EB;  /* Bordures légères */
  --gray-300: #D1D5DB;  /* Bordures */
  --gray-400: #9CA3AF;  /* Texte placeholder */
  --gray-500: #6B7280;  /* Texte secondaire */
  --gray-600: #4B5563;  /* Texte muted */
  --gray-700: #374151;  /* Texte body */
  --gray-800: #1F2937;  /* Titres */
  --gray-900: #111827;  /* Texte principal */
}
```

---

## 3. Typographie

### 3.1 Font Pairing

**Combinaison recommandée: Inter + Inter**

```css
/* Une seule famille pour cohérence et performance */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  font-family: var(--font-sans);
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
}
```

**Alternative premium: Outfit (headings) + Inter (body)**

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --font-heading: 'Outfit', sans-serif;
  --font-body: 'Inter', sans-serif;
}
```

### 3.2 Échelle Typographique

```css
:root {
  /* Tailles */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */

  /* Line heights */
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 1.75;
}
```

### 3.3 Styles Texte

| Usage | Classe Tailwind | Specs |
|-------|-----------------|-------|
| H1 Page | `text-3xl font-bold text-gray-900` | 30px, 700, #111827 |
| H2 Section | `text-2xl font-semibold text-gray-800` | 24px, 600, #1F2937 |
| H3 Card | `text-lg font-semibold text-gray-800` | 18px, 600, #1F2937 |
| H4 Subsection | `text-base font-medium text-gray-700` | 16px, 500, #374151 |
| Body | `text-base text-gray-700` | 16px, 400, #374151 |
| Body small | `text-sm text-gray-600` | 14px, 400, #4B5563 |
| Caption | `text-xs text-gray-500` | 12px, 400, #6B7280 |
| Label | `text-sm font-medium text-gray-700` | 14px, 500, #374151 |

---

## 4. Espacements

### 4.1 Système Base 4px

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### 4.2 Application

| Élément | Padding | Gap/Margin |
|---------|---------|------------|
| Page | `px-4 md:px-6 lg:px-8` | - |
| Section | `py-8 md:py-12` | `space-y-8` |
| Card | `p-4 md:p-6` | `gap-4` |
| Form group | - | `space-y-4` |
| Button | `px-4 py-2` | - |
| Input | `px-3 py-2` | - |
| Badge | `px-2 py-0.5` | - |

---

## 5. Composants

### 5.1 Boutons

```html
<!-- Primary -->
<button class="
  inline-flex items-center justify-center gap-2
  px-4 py-2 rounded-lg
  bg-primary-600 text-white font-medium
  hover:bg-primary-700
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
  transition-colors duration-200
">
  <IconPlus class="w-4 h-4" />
  Nouveau
</button>

<!-- Secondary -->
<button class="
  inline-flex items-center justify-center gap-2
  px-4 py-2 rounded-lg
  bg-white text-gray-700 font-medium
  border border-gray-300
  hover:bg-gray-50
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  transition-colors duration-200
">
  Annuler
</button>

<!-- Danger -->
<button class="
  inline-flex items-center justify-center gap-2
  px-4 py-2 rounded-lg
  bg-error-600 text-white font-medium
  hover:bg-error-700
  focus:outline-none focus:ring-2 focus:ring-error-500 focus:ring-offset-2
  transition-colors duration-200
">
  <IconTrash class="w-4 h-4" />
  Supprimer
</button>

<!-- Ghost -->
<button class="
  inline-flex items-center justify-center gap-2
  px-4 py-2 rounded-lg
  text-gray-600 font-medium
  hover:bg-gray-100
  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
  transition-colors duration-200
">
  Plus d'options
</button>
```

### 5.2 Cards

```html
<!-- Card standard -->
<div class="
  bg-white rounded-xl
  border border-gray-200
  shadow-sm
  overflow-hidden
">
  <div class="p-6">
    <!-- Content -->
  </div>
</div>

<!-- Card interactive (clickable) -->
<div class="
  bg-white rounded-xl
  border border-gray-200
  shadow-sm
  overflow-hidden
  cursor-pointer
  hover:border-primary-300 hover:shadow-md
  transition-all duration-200
">
  <!-- Content -->
</div>

<!-- Card bénéficiaire -->
<div class="
  bg-white rounded-xl
  border border-gray-200
  shadow-sm
  overflow-hidden
  cursor-pointer
  hover:border-primary-300 hover:shadow-md
  transition-all duration-200
">
  <div class="p-4 flex items-start gap-4">
    <img
      src="/photos/1.jpg"
      alt="Pierre Martin"
      class="w-12 h-12 rounded-full object-cover"
    />
    <div class="flex-1 min-w-0">
      <h3 class="text-base font-semibold text-gray-900 truncate">
        Pierre Martin
      </h3>
      <p class="text-sm text-gray-500">
        Atelier Bois • J. Dupont
      </p>
    </div>
    <span class="
      inline-flex items-center
      px-2 py-0.5 rounded-full
      text-xs font-medium
      bg-success-50 text-success-700
    ">
      Actif
    </span>
  </div>
  <div class="px-4 pb-4">
    <div class="flex items-center gap-2 text-sm">
      <span class="text-gray-500">Objectifs:</span>
      <div class="flex gap-1">
        <span class="w-2 h-2 rounded-full bg-success-500"></span>
        <span class="w-2 h-2 rounded-full bg-success-500"></span>
        <span class="w-2 h-2 rounded-full bg-primary-500"></span>
        <span class="w-2 h-2 rounded-full bg-gray-300"></span>
        <span class="w-2 h-2 rounded-full bg-gray-300"></span>
      </div>
      <span class="text-gray-600">3/5</span>
      <span class="text-error-600 text-xs ml-2">1 en retard</span>
    </div>
  </div>
</div>
```

### 5.3 Inputs

```html
<!-- Text input -->
<div class="space-y-1">
  <label for="name" class="block text-sm font-medium text-gray-700">
    Prénom <span class="text-error-500">*</span>
  </label>
  <input
    type="text"
    id="name"
    class="
      w-full px-3 py-2 rounded-lg
      border border-gray-300
      text-gray-900 placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      transition-colors duration-200
    "
    placeholder="Ex: Pierre"
  />
</div>

<!-- Input avec erreur -->
<div class="space-y-1">
  <label for="email" class="block text-sm font-medium text-gray-700">
    Email
  </label>
  <input
    type="email"
    id="email"
    class="
      w-full px-3 py-2 rounded-lg
      border border-error-500
      text-gray-900 placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-error-500
      transition-colors duration-200
    "
    value="invalid-email"
  />
  <p class="text-sm text-error-600 flex items-center gap-1">
    <IconAlertCircle class="w-4 h-4" />
    Format d'email invalide
  </p>
</div>

<!-- Select -->
<div class="space-y-1">
  <label for="unit" class="block text-sm font-medium text-gray-700">
    Unité / Atelier
  </label>
  <select
    id="unit"
    class="
      w-full px-3 py-2 rounded-lg
      border border-gray-300
      text-gray-900 bg-white
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      transition-colors duration-200
    "
  >
    <option value="">Sélectionner...</option>
    <option value="1">Atelier Bois</option>
    <option value="2">Atelier Métal</option>
  </select>
</div>

<!-- Textarea -->
<div class="space-y-1">
  <label for="notes" class="block text-sm font-medium text-gray-700">
    Notes
  </label>
  <textarea
    id="notes"
    rows="4"
    class="
      w-full px-3 py-2 rounded-lg
      border border-gray-300
      text-gray-900 placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      resize-y
      transition-colors duration-200
    "
    placeholder="Ajouter des notes..."
  ></textarea>
</div>
```

### 5.4 Badges et Tags

```html
<!-- Status badges -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-50 text-success-700">
  Actif
</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-50 text-warning-700">
  En pause
</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
  Sorti
</span>

<!-- Priority badges -->
<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-error-50 text-error-700">
  <IconZap class="w-3 h-3" />
  Haute
</span>

<!-- Category tags -->
<span class="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
  <IconHeartPulse class="w-3 h-3" />
  Santé
</span>

<!-- Keyword tags -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600 hover:bg-gray-200 cursor-pointer transition-colors">
  entretien-mensuel
</span>
```

### 5.5 Progress Bar

```html
<!-- Objectif progress -->
<div class="space-y-1">
  <div class="flex justify-between text-sm">
    <span class="text-gray-600">Progression</span>
    <span class="font-medium text-gray-900">40%</span>
  </div>
  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
    <div
      class="h-full bg-primary-500 rounded-full transition-all duration-500"
      style="width: 40%"
    ></div>
  </div>
</div>

<!-- Progress avec statut -->
<div class="h-2 bg-gray-200 rounded-full overflow-hidden">
  <div
    class="h-full bg-error-500 rounded-full"  <!-- Rouge si en retard -->
    style="width: 40%"
  ></div>
</div>
```

### 5.6 Tables

```html
<div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          <input type="checkbox" class="rounded border-gray-300" />
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Nom
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Unité
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Statut
        </th>
        <th scope="col" class="relative px-6 py-3">
          <span class="sr-only">Actions</span>
        </th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      <tr class="hover:bg-gray-50 transition-colors">
        <td class="px-6 py-4 whitespace-nowrap">
          <input type="checkbox" class="rounded border-gray-300" />
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="flex items-center gap-3">
            <img class="w-8 h-8 rounded-full" src="/photos/1.jpg" alt="" />
            <div>
              <div class="text-sm font-medium text-gray-900">Pierre Martin</div>
              <div class="text-sm text-gray-500">Réf: J. Dupont</div>
            </div>
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
          Atelier Bois
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-50 text-success-700">
            Actif
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
          <button class="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 transition-colors">
            <IconEye class="w-4 h-4" />
          </button>
          <button class="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 transition-colors">
            <IconPencil class="w-4 h-4" />
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### 5.7 Modales

```html
<!-- Overlay -->
<div class="fixed inset-0 bg-black/50 z-40"></div>

<!-- Modal -->
<div class="
  fixed inset-0 z-50
  flex items-center justify-center
  p-4
">
  <div class="
    w-full max-w-lg
    bg-white rounded-xl
    shadow-xl
    overflow-hidden
  ">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">
        Nouveau bénéficiaire
      </h2>
      <button class="
        p-1 rounded-lg
        text-gray-400 hover:text-gray-600 hover:bg-gray-100
        transition-colors
      ">
        <IconX class="w-5 h-5" />
      </button>
    </div>

    <!-- Body -->
    <div class="px-6 py-4 max-h-[60vh] overflow-y-auto">
      <!-- Form content -->
    </div>

    <!-- Footer -->
    <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
      <button class="px-4 py-2 text-gray-700 font-medium hover:bg-gray-100 rounded-lg transition-colors">
        Annuler
      </button>
      <button class="px-4 py-2 bg-primary-600 text-white font-medium hover:bg-primary-700 rounded-lg transition-colors">
        Enregistrer
      </button>
    </div>
  </div>
</div>
```

### 5.8 Toasts / Notifications

```html
<!-- Toast container (fixed en haut à droite) -->
<div class="fixed top-4 right-4 z-50 space-y-2">

  <!-- Success -->
  <div class="
    flex items-center gap-3
    px-4 py-3 rounded-lg
    bg-white border border-gray-200 shadow-lg
    animate-slide-in
  ">
    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-success-100 flex items-center justify-center">
      <IconCheck class="w-4 h-4 text-success-600" />
    </div>
    <p class="text-sm text-gray-700">Bénéficiaire créé avec succès</p>
    <button class="text-gray-400 hover:text-gray-600">
      <IconX class="w-4 h-4" />
    </button>
  </div>

  <!-- Error -->
  <div class="
    flex items-center gap-3
    px-4 py-3 rounded-lg
    bg-white border border-error-200 shadow-lg
  ">
    <div class="flex-shrink-0 w-8 h-8 rounded-full bg-error-100 flex items-center justify-center">
      <IconAlertCircle class="w-4 h-4 text-error-600" />
    </div>
    <div>
      <p class="text-sm font-medium text-gray-900">Erreur</p>
      <p class="text-sm text-gray-600">Veuillez réessayer</p>
    </div>
    <button class="text-gray-400 hover:text-gray-600">
      <IconX class="w-4 h-4" />
    </button>
  </div>

</div>
```

---

## 6. Layout

### 6.1 Structure Principale

```html
<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="
    fixed top-0 left-0 right-0 z-30
    h-16 bg-white border-b border-gray-200
  ">
    <!-- Header content -->
  </header>

  <div class="flex pt-16">
    <!-- Sidebar -->
    <aside class="
      fixed top-16 left-0 bottom-0 z-20
      w-64 bg-white border-r border-gray-200
      overflow-y-auto
      hidden lg:block
    ">
      <!-- Sidebar content -->
    </aside>

    <!-- Main content -->
    <main class="flex-1 lg:ml-64">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Page content -->
      </div>
    </main>
  </div>
</div>
```

### 6.2 Header

```html
<header class="fixed top-0 left-0 right-0 z-30 h-16 bg-white border-b border-gray-200">
  <div class="h-full px-4 flex items-center justify-between">
    <!-- Left: Menu + Logo -->
    <div class="flex items-center gap-4">
      <button class="lg:hidden p-2 rounded-lg hover:bg-gray-100">
        <IconMenu class="w-5 h-5 text-gray-600" />
      </button>
      <a href="/" class="flex items-center gap-2">
        <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-sm">CIS</span>
        </div>
        <span class="hidden sm:block font-semibold text-gray-900">CIS</span>
      </a>
    </div>

    <!-- Center: Search -->
    <div class="flex-1 max-w-xl mx-4 hidden md:block">
      <div class="relative">
        <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="search"
          placeholder="Rechercher..."
          class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-2">
      <button class="relative p-2 rounded-lg hover:bg-gray-100">
        <IconBell class="w-5 h-5 text-gray-600" />
        <span class="absolute top-1 right-1 w-2 h-2 bg-error-500 rounded-full"></span>
      </button>
      <button class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100">
        <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
          <span class="text-sm font-medium text-primary-700">JD</span>
        </div>
        <IconChevronDown class="w-4 h-4 text-gray-400 hidden sm:block" />
      </button>
    </div>
  </div>
</header>
```

### 6.3 Sidebar

```html
<aside class="fixed top-16 left-0 bottom-0 z-20 w-64 bg-white border-r border-gray-200 overflow-y-auto">
  <nav class="p-4 space-y-1">
    <!-- Active item -->
    <a href="/dashboard" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      bg-primary-50 text-primary-700
      font-medium
    ">
      <IconLayoutDashboard class="w-5 h-5" />
      Tableau de bord
    </a>

    <!-- Normal items -->
    <a href="/beneficiaries" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconUsers class="w-5 h-5" />
      Bénéficiaires
    </a>

    <a href="/objectives" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconTarget class="w-5 h-5" />
      Objectifs
    </a>

    <a href="/journal" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconFileText class="w-5 h-5" />
      Journal
    </a>

    <a href="/documents" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconFolder class="w-5 h-5" />
      Documents
    </a>

    <a href="/reports" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconChartBar class="w-5 h-5" />
      Rapports
    </a>

    <!-- Separator -->
    <div class="h-px bg-gray-200 my-4"></div>

    <!-- Admin section -->
    <a href="/admin" class="
      flex items-center gap-3 px-3 py-2 rounded-lg
      text-gray-600 hover:bg-gray-100
      transition-colors
    ">
      <IconSettings class="w-5 h-5" />
      Administration
    </a>
  </nav>
</aside>
```

---

## 7. Iconographie

### 7.1 Bibliothèque: Lucide React

```bash
npm install lucide-react
```

### 7.2 Icônes Principales

| Usage | Icône | Import |
|-------|-------|--------|
| Dashboard | `LayoutDashboard` | `lucide-react` |
| Bénéficiaires | `Users` | `lucide-react` |
| Objectifs | `Target` | `lucide-react` |
| Journal | `FileText` | `lucide-react` |
| Documents | `Folder` | `lucide-react` |
| Rapports | `BarChart3` | `lucide-react` |
| Paramètres | `Settings` | `lucide-react` |
| Recherche | `Search` | `lucide-react` |
| Notifications | `Bell` | `lucide-react` |
| Ajouter | `Plus` | `lucide-react` |
| Modifier | `Pencil` | `lucide-react` |
| Supprimer | `Trash2` | `lucide-react` |
| Voir | `Eye` | `lucide-react` |
| Fermer | `X` | `lucide-react` |
| Menu | `Menu` | `lucide-react` |
| Chevron | `ChevronDown`, `ChevronRight` | `lucide-react` |
| Check | `Check` | `lucide-react` |
| Alerte | `AlertCircle`, `AlertTriangle` | `lucide-react` |

### 7.3 Usage

```tsx
import { Users, Target, FileText } from 'lucide-react';

// Taille standard
<Users className="w-5 h-5" />

// Avec couleur
<Target className="w-5 h-5 text-primary-600" />

// Dans bouton
<button className="flex items-center gap-2">
  <Plus className="w-4 h-4" />
  Nouveau
</button>
```

---

## 8. Animations

### 8.1 Transitions CSS

```css
/* Durées */
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;

/* Easing */
--ease-out: cubic-bezier(0.33, 1, 0.68, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
```

### 8.2 Classes Tailwind

```html
<!-- Hover standard -->
<div class="transition-colors duration-200 hover:bg-gray-100">

<!-- Card hover -->
<div class="transition-all duration-200 hover:shadow-md hover:border-primary-300">

<!-- Scale (éviter si possible - peut causer des shifts) -->
<div class="transition-transform duration-200 hover:scale-[1.02]">
```

### 8.3 Keyframes Personnalisés

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-in': 'slide-in 0.2s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
      },
    },
  },
}
```

### 8.4 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 9. Responsive Breakpoints

### 9.1 Configuration Tailwind

```js
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px',  // Large desktop
      '2xl': '1536px', // Extra large
    },
  },
}
```

### 9.2 Patterns Responsive

```html
<!-- Grid responsive -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">

<!-- Sidebar visible sur desktop -->
<aside class="hidden lg:block">

<!-- Stack sur mobile, row sur desktop -->
<div class="flex flex-col md:flex-row gap-4">

<!-- Texte adaptatif -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">

<!-- Padding adaptatif -->
<div class="px-4 md:px-6 lg:px-8">
```

---

## 10. Accessibilité

### 10.1 Checklist WCAG AA

- [x] Contraste texte: 4.5:1 minimum (normal), 3:1 (grand)
- [x] Contraste éléments UI: 3:1 minimum
- [x] Touch targets: 44x44px minimum
- [x] Focus visible: ring 2px primary
- [x] Alt text sur images significatives
- [x] Labels sur tous les inputs
- [x] Aria-labels sur boutons icônes
- [x] Navigation clavier fonctionnelle
- [x] Respect prefers-reduced-motion

### 10.2 Exemples

```html
<!-- Bouton icône avec aria-label -->
<button
  aria-label="Supprimer le bénéficiaire"
  class="p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
>
  <Trash2 className="w-5 h-5" />
</button>

<!-- Image avec alt -->
<img
  src="/photos/1.jpg"
  alt="Photo de profil de Pierre Martin"
  class="w-12 h-12 rounded-full object-cover"
/>

<!-- Input avec label associé -->
<label htmlFor="email" className="block text-sm font-medium text-gray-700">
  Email
</label>
<input
  type="email"
  id="email"
  name="email"
  aria-describedby="email-error"
/>
<p id="email-error" className="text-sm text-error-600" role="alert">
  Format invalide
</p>
```

---

## 11. Tailwind Config Complète

```js
// tailwind.config.js
const colors = require('tailwindcss/colors')

module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        secondary: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12',
        },
        success: colors.green,
        warning: colors.amber,
        error: colors.red,
        info: colors.blue,
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-in': 'slide-in 0.2s ease-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

---

## 12. Résumé Design System

| Aspect | Choix |
|--------|-------|
| **Style** | Clean Professional + Soft UI |
| **Primary** | Bleu #3B82F6 (confiance) |
| **Accent** | Orange #F97316 (chaleur humaine) |
| **Font** | Inter (400, 500, 600, 700) |
| **Icônes** | Lucide React |
| **Radius** | lg (8px) pour cards, md (6px) pour inputs |
| **Shadows** | Subtiles (sm, DEFAULT) |
| **Transitions** | 200ms ease-out |
| **Focus** | Ring 2px primary |
