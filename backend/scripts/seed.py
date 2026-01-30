"""
Seed script pour l'application CIS.

Crée des données de test réalistes pour le développement et les démonstrations.
Idempotent : vérifie l'existence avant chaque création.

Usage:
    cd backend
    python -m scripts.seed
"""

import asyncio
import sys
from datetime import UTC, date, datetime, time
from decimal import Decimal

sys.path.insert(0, ".")

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import (
    PAI,
    Absence,
    Action,
    Beneficiary,
    BeneficiaryMedicalData,
    BeneficiarySkill,
    Contact,
    JournalCategory,
    JournalEntry,
    JournalEntryCategory,
    JournalEntryTag,
    Notification,
    Objective,
    ObjectiveIndicator,
    Skill,
    TimeEntry,
    Unit,
    User,
    VacationBalance,
)
from app.utils.encryption import encrypt_data
from app.utils.security import get_password_hash

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def get_or_create(session, model, defaults=None, **filter_kwargs):
    """
    Recherche un enregistrement par filter_kwargs.
    S'il n'existe pas, le crée avec filter_kwargs + defaults.
    Retourne (instance, created: bool).
    """
    stmt = select(model).filter_by(**filter_kwargs)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance is not None:
        return instance, False
    params = {**filter_kwargs, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    await session.flush()
    return instance, True


def _dt(year, month, day, hour=10, minute=0):
    """Crée un datetime timezone-aware (UTC)."""
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


# ---------------------------------------------------------------------------
# 1. Units
# ---------------------------------------------------------------------------

async def seed_units(session):
    """Crée les 3 unités/ateliers."""
    print("\n--- Unités ---")

    units_data = [
        {
            "name": "Atelier Bois",
            "description": "Atelier de menuiserie et ébénisterie – "
            "travaux de découpe, assemblage, finition et restauration de meubles.",
        },
        {
            "name": "Atelier Cuisine",
            "description": "Atelier de restauration collective – "
            "préparation de repas, hygiène alimentaire, gestion des stocks.",
        },
        {
            "name": "Atelier Bureautique",
            "description": "Atelier de compétences administratives – "
            "traitement de texte, tableur, classement, accueil téléphonique.",
        },
    ]

    units = {}
    for data in units_data:
        unit, created = await get_or_create(
            session, Unit, name=data["name"], defaults={"description": data["description"]}
        )
        units[data["name"]] = unit
        print(f"  {'[CRÉÉ]' if created else '[EXISTE]'} {data['name']} (id={unit.id})")

    return units


# ---------------------------------------------------------------------------
# 2. Users
# ---------------------------------------------------------------------------

async def seed_users(session, units):
    """Crée les 10 utilisateurs."""
    print("\n--- Utilisateurs ---")

    bois = units["Atelier Bois"]
    cuisine = units["Atelier Cuisine"]
    bureau = units["Atelier Bureautique"]

    users_data = [
        {
            "email": "admin@cis.ch",
            "password": "Admin123!@#",
            "first_name": "Admin",
            "last_name": "Système",
            "role": "ADMIN",
            "unit_id": None,
            "is_superuser": True,
        },
        {
            "email": "rua1@cis.ch",
            "password": "Rua12345!@#",
            "first_name": "Pierre",
            "last_name": "Favre",
            "role": "RUA",
            "unit_id": None,
            "is_superuser": False,
        },
        {
            "email": "rua2@cis.ch",
            "password": "Rua12345!@#",
            "first_name": "Isabelle",
            "last_name": "Rochat",
            "role": "RUA",
            "unit_id": None,
            "is_superuser": False,
        },
        {
            "email": "res.bois@cis.ch",
            "password": "Res12345!@#",
            "first_name": "Marc",
            "last_name": "Dupont",
            "role": "RES",
            "unit_id": bois.id,
            "is_superuser": False,
        },
        {
            "email": "res.cuisine@cis.ch",
            "password": "Res12345!@#",
            "first_name": "Nathalie",
            "last_name": "Blanc",
            "role": "RES",
            "unit_id": cuisine.id,
            "is_superuser": False,
        },
        {
            "email": "msp.bois1@cis.ch",
            "password": "Msp12345!@#",
            "first_name": "Jean-Claude",
            "last_name": "Müller",
            "role": "MSP",
            "unit_id": bois.id,
            "is_superuser": False,
        },
        {
            "email": "msp.bois2@cis.ch",
            "password": "Msp12345!@#",
            "first_name": "Sophie",
            "last_name": "Roth",
            "role": "MSP",
            "unit_id": bois.id,
            "is_superuser": False,
        },
        {
            "email": "msp.cuisine1@cis.ch",
            "password": "Msp12345!@#",
            "first_name": "Philippe",
            "last_name": "Girard",
            "role": "MSP",
            "unit_id": cuisine.id,
            "is_superuser": False,
        },
        {
            "email": "msp.bureau1@cis.ch",
            "password": "Msp12345!@#",
            "first_name": "Marie",
            "last_name": "Favre",
            "role": "MSP",
            "unit_id": bureau.id,
            "is_superuser": False,
        },
        {
            "email": "consult@cis.ch",
            "password": "Consult123!@#",
            "first_name": "Laurent",
            "last_name": "Weber",
            "role": "CONSULT",
            "unit_id": None,
            "is_superuser": False,
        },
    ]

    users = {}
    for data in users_data:
        password = data.pop("password")
        user, created = await get_or_create(
            session,
            User,
            email=data["email"],
            defaults={
                "hashed_password": get_password_hash(password),
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "role": data["role"],
                "unit_id": data["unit_id"],
                "is_superuser": data["is_superuser"],
                "is_active": True,
            },
        )
        users[data["email"]] = user
        print(f"  {'[CRÉÉ]' if created else '[EXISTE]'} {data['email']} ({data['role']})")

    return users


# ---------------------------------------------------------------------------
# 3. Journal Categories
# ---------------------------------------------------------------------------

async def seed_journal_categories(session):
    """Crée les 10 catégories de journal."""
    print("\n--- Catégories de journal ---")

    categories_data = [
        {"name": "sante", "label": "Santé", "color": "#EF4444", "icon": "heart", "sort_order": 1},
        {"name": "comportement", "label": "Comportement", "color": "#F97316", "icon": "alert-triangle", "sort_order": 2},
        {"name": "competences", "label": "Compétences", "color": "#3B82F6", "icon": "book-open", "sort_order": 3},
        {"name": "social", "label": "Social", "color": "#22C55E", "icon": "users", "sort_order": 4},
        {"name": "professionnel", "label": "Professionnel", "color": "#8B5CF6", "icon": "briefcase", "sort_order": 5},
        {"name": "administratif", "label": "Administratif", "color": "#6B7280", "icon": "file-text", "sort_order": 6},
        {"name": "medical", "label": "Médical", "color": "#DC2626", "icon": "activity", "sort_order": 7},
        {"name": "famille", "label": "Famille", "color": "#14B8A6", "icon": "home", "sort_order": 8},
        {"name": "formation", "label": "Formation", "color": "#6366F1", "icon": "graduation-cap", "sort_order": 9},
        {"name": "general", "label": "Général", "color": "#64748B", "icon": "message-circle", "sort_order": 10},
    ]

    categories = {}
    for data in categories_data:
        cat, created = await get_or_create(
            session,
            JournalCategory,
            name=data["name"],
            defaults={
                "label": data["label"],
                "color": data["color"],
                "icon": data["icon"],
                "sort_order": data["sort_order"],
                "is_active": True,
            },
        )
        categories[data["name"]] = cat
        print(f"  {'[CRÉÉ]' if created else '[EXISTE]'} {data['name']} – {data['label']}")

    return categories


# ---------------------------------------------------------------------------
# 4. Skills (référentiel)
# ---------------------------------------------------------------------------

async def seed_skills(session):
    """Crée les 12 compétences de référence."""
    print("\n--- Compétences (référentiel) ---")

    skills_data = [
        {"name": "Ponctualité", "category": "savoir-être", "description": "Respecte les horaires d'arrivée et de pause."},
        {"name": "Assiduité", "category": "savoir-être", "description": "Présence régulière et constante à l'atelier."},
        {"name": "Autonomie", "category": "savoir-être", "description": "Capacité à travailler de manière indépendante."},
        {"name": "Travail d'équipe", "category": "social", "description": "Collaboration efficace avec les collègues."},
        {"name": "Communication", "category": "social", "description": "Expression claire et écoute active."},
        {"name": "Respect des consignes", "category": "savoir-être", "description": "Application correcte des instructions reçues."},
        {"name": "Qualité du travail", "category": "savoir-faire", "description": "Soin et précision dans la réalisation des tâches."},
        {"name": "Initiative", "category": "savoir-être", "description": "Propose des solutions et anticipe les besoins."},
        {"name": "Gestion du stress", "category": "savoir-être", "description": "Maintien du calme face aux situations difficiles."},
        {"name": "Organisation", "category": "savoir-faire", "description": "Planification et structuration du travail."},
        {"name": "Hygiène", "category": "savoir-être", "description": "Respect des règles d'hygiène personnelle et professionnelle."},
        {"name": "Sécurité", "category": "savoir-faire", "description": "Application des règles de sécurité au poste de travail."},
    ]

    skills = {}
    for idx, data in enumerate(skills_data):
        skill, created = await get_or_create(
            session,
            Skill,
            name=data["name"],
            defaults={
                "category": data["category"],
                "description": data["description"],
                "is_active": True,
                "sort_order": idx + 1,
            },
        )
        skills[data["name"]] = skill
        print(f"  {'[CRÉÉ]' if created else '[EXISTE]'} {data['name']}")

    return skills


# ---------------------------------------------------------------------------
# 5. Beneficiaries (12)
# ---------------------------------------------------------------------------

async def seed_beneficiaries(session, units, users):
    """Crée les 12 bénéficiaires avec données réalistes."""
    print("\n--- Bénéficiaires ---")

    bois = units["Atelier Bois"]
    cuisine = units["Atelier Cuisine"]
    bureau = units["Atelier Bureautique"]

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]
    admin = users["admin@cis.ch"]

    beneficiaries_data = [
        {
            "first_name": "Alain",
            "last_name": "Mercier",
            "date_of_birth": date(1985, 3, 15),
            "address": "Rue du Lac 12",
            "postal_code": "1000",
            "city": "Lausanne",
            "phone": "+41 21 312 45 67",
            "email": "alain.mercier@bluewin.ch",
            "language": "fr",
            "ai_number": "AI-2024-001",
            "pension_type": "quarter",
            "entry_date": date(2024, 1, 15),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("80.00"),
            "salary": Decimal("450.00"),
            "unit_id": bois.id,
            "referent_id": msp_bois1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Céline",
            "last_name": "Vuagnoux",
            "date_of_birth": date(1990, 7, 22),
            "address": "Avenue de la Gare 45",
            "postal_code": "1003",
            "city": "Lausanne",
            "phone": "+41 21 623 89 01",
            "email": "c.vuagnoux@sunrise.ch",
            "language": "fr",
            "ai_number": "AI-2024-002",
            "pension_type": "half",
            "entry_date": date(2024, 2, 1),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("60.00"),
            "salary": Decimal("340.00"),
            "unit_id": bois.id,
            "referent_id": msp_bois1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "David",
            "last_name": "Charrière",
            "date_of_birth": date(1978, 11, 30),
            "address": "Chemin des Pâquis 7",
            "postal_code": "1700",
            "city": "Fribourg",
            "phone": "+41 26 322 14 55",
            "email": None,
            "language": "fr",
            "ai_number": "AI-2023-015",
            "pension_type": "full",
            "entry_date": date(2023, 6, 15),
            "status": "active",
            "contract_type": "CDI",
            "occupation_rate": Decimal("50.00"),
            "salary": Decimal("280.00"),
            "unit_id": bois.id,
            "referent_id": msp_bois2.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Fatima",
            "last_name": "Benali",
            "date_of_birth": date(1992, 4, 10),
            "address": "Rue de Genève 88",
            "postal_code": "1004",
            "city": "Lausanne",
            "phone": "+41 78 912 34 56",
            "email": "fatima.benali@gmail.com",
            "language": "fr",
            "ai_number": "AI-2024-003",
            "pension_type": "quarter",
            "entry_date": date(2024, 3, 1),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("80.00"),
            "salary": Decimal("450.00"),
            "unit_id": cuisine.id,
            "referent_id": msp_cuisine1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Grégoire",
            "last_name": "Perrin",
            "date_of_birth": date(1988, 9, 5),
            "address": "Place du Marché 3",
            "postal_code": "1110",
            "city": "Morges",
            "phone": "+41 21 801 23 45",
            "email": "gregoire.perrin@bluewin.ch",
            "language": "fr",
            "ai_number": "AI-2023-022",
            "pension_type": "three_quarter",
            "entry_date": date(2023, 9, 1),
            "status": "active",
            "contract_type": "CDI",
            "occupation_rate": Decimal("60.00"),
            "salary": Decimal("340.00"),
            "unit_id": cuisine.id,
            "referent_id": msp_cuisine1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Hélène",
            "last_name": "Savary",
            "date_of_birth": date(1995, 1, 18),
            "address": "Rue du Simplon 22",
            "postal_code": "1800",
            "city": "Vevey",
            "phone": "+41 21 925 67 89",
            "email": "h.savary@outlook.com",
            "language": "fr",
            "ai_number": "AI-2024-004",
            "pension_type": "half",
            "entry_date": date(2024, 1, 10),
            "status": "paused",
            "contract_type": "CDD",
            "occupation_rate": Decimal("40.00"),
            "salary": Decimal("225.00"),
            "unit_id": cuisine.id,
            "referent_id": msp_cuisine1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Igor",
            "last_name": "Petrovic",
            "date_of_birth": date(1982, 6, 25),
            "address": "Boulevard de Pérolles 51",
            "postal_code": "1700",
            "city": "Fribourg",
            "phone": "+41 26 481 90 12",
            "email": "igor.petrovic@gmail.com",
            "language": "fr",
            "ai_number": "AI-2024-005",
            "pension_type": "full",
            "entry_date": date(2024, 4, 1),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("50.00"),
            "salary": Decimal("280.00"),
            "unit_id": bureau.id,
            "referent_id": msp_bureau1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Julie",
            "last_name": "Bonvin",
            "date_of_birth": date(1997, 12, 8),
            "address": "Rue de Lausanne 19",
            "postal_code": "1950",
            "city": "Sion",
            "phone": "+41 27 323 45 67",
            "email": "julie.bonvin@protonmail.ch",
            "language": "fr",
            "ai_number": "AI-2023-030",
            "pension_type": "quarter",
            "entry_date": date(2023, 10, 1),
            "status": "active",
            "contract_type": "CDI",
            "occupation_rate": Decimal("100.00"),
            "salary": Decimal("560.00"),
            "unit_id": bureau.id,
            "referent_id": msp_bureau1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Kevin",
            "last_name": "Morand",
            "date_of_birth": date(1975, 8, 14),
            "address": "Route de Berne 156",
            "postal_code": "1010",
            "city": "Lausanne",
            "phone": "+41 79 456 78 90",
            "email": None,
            "language": "fr",
            "ai_number": "AI-2023-011",
            "pension_type": "full",
            "entry_date": date(2023, 3, 1),
            "status": "paused",
            "contract_type": "CDI",
            "occupation_rate": Decimal("40.00"),
            "salary": Decimal("225.00"),
            "unit_id": bois.id,
            "referent_id": msp_bois2.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Laetitia",
            "last_name": "Currat",
            "date_of_birth": date(1991, 2, 28),
            "address": "Avenue de Beaulieu 8",
            "postal_code": "1400",
            "city": "Yverdon-les-Bains",
            "phone": "+41 24 425 12 34",
            "email": "l.currat@bluewin.ch",
            "language": "fr",
            "ai_number": "AI-2022-045",
            "pension_type": "half",
            "entry_date": date(2022, 8, 15),
            "exit_date": date(2024, 6, 30),
            "status": "exited",
            "contract_type": "CDI",
            "occupation_rate": Decimal("60.00"),
            "salary": Decimal("340.00"),
            "unit_id": cuisine.id,
            "referent_id": msp_cuisine1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Michel",
            "last_name": "Aeby",
            "date_of_birth": date(1986, 10, 3),
            "address": "Rue de Morat 24",
            "postal_code": "1700",
            "city": "Fribourg",
            "phone": "+41 26 322 56 78",
            "email": "m.aeby@sunrise.ch",
            "language": "fr",
            "ai_number": "AI-2024-006",
            "pension_type": "three_quarter",
            "entry_date": date(2024, 5, 1),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("80.00"),
            "salary": Decimal("450.00"),
            "unit_id": bureau.id,
            "referent_id": msp_bureau1.id,
            "created_by": admin.id,
        },
        {
            "first_name": "Nadia",
            "last_name": "Kessler",
            "date_of_birth": date(1993, 5, 20),
            "address": "Chemin de Mornex 15",
            "postal_code": "1003",
            "city": "Lausanne",
            "phone": "+41 78 234 56 78",
            "email": "nadia.kessler@gmail.com",
            "language": "fr",
            "ai_number": "AI-2024-007",
            "pension_type": "quarter",
            "entry_date": date(2024, 6, 1),
            "status": "active",
            "contract_type": "CDD",
            "occupation_rate": Decimal("70.00"),
            "salary": Decimal("395.00"),
            "unit_id": bois.id,
            "referent_id": msp_bois1.id,
            "created_by": admin.id,
        },
    ]

    beneficiaries = {}
    for data in beneficiaries_data:
        key = f"{data['first_name']} {data['last_name']}"
        ben, created = await get_or_create(
            session,
            Beneficiary,
            ai_number=data["ai_number"],
            defaults={k: v for k, v in data.items() if k != "ai_number"},
        )
        beneficiaries[key] = ben
        print(f"  {'[CRÉÉ]' if created else '[EXISTE]'} {key} ({data['status']}, {data['ai_number']})")

    return beneficiaries


# ---------------------------------------------------------------------------
# 6. Medical Data (encrypted) – pour quelques bénéficiaires
# ---------------------------------------------------------------------------

async def seed_medical_data(session, beneficiaries, users):
    """Crée des données médicales chiffrées pour certains bénéficiaires."""
    print("\n--- Données médicales ---")

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]

    medical_data = [
        {
            "beneficiary": "Alain Mercier",
            "medication": "Sertraline 50 mg (1x/jour matin)",
            "restrictions": "Port de charges limité à 10 kg (lombalgie chronique)",
            "allergies": "Aucune allergie connue",
            "medical_notes": "Suivi psychiatrique mensuel. Bonne compliance au traitement.",
            "updated_by": msp_bois1.id,
        },
        {
            "beneficiary": "David Charrière",
            "medication": "Ritaline LA 30 mg (1x/jour), Escitalopram 10 mg (1x/soir)",
            "restrictions": "Pauses régulières nécessaires (difficultés de concentration)",
            "allergies": "Pénicilline",
            "medical_notes": "TDAH diagnostiqué. Suivi neuropsychologique tous les 2 mois.",
            "updated_by": msp_bois1.id,
        },
        {
            "beneficiary": "Fatima Benali",
            "medication": "Aucun traitement en cours",
            "restrictions": "Pas de station debout prolongée (> 2h) – problème aux genoux",
            "allergies": "Lactose (intolérance)",
            "medical_notes": "Physiothérapie 1x/semaine. Évolution favorable.",
            "updated_by": msp_cuisine1.id,
        },
        {
            "beneficiary": "Igor Petrovic",
            "medication": "Lyrica 75 mg (2x/jour), Dafalgan 1g (si besoin)",
            "restrictions": "Éviter les mouvements répétitifs du poignet droit",
            "allergies": "Aspirine",
            "medical_notes": "Syndrome du canal carpien opéré en 2023. Rééducation terminée. "
            "Douleurs résiduelles occasionnelles.",
            "updated_by": msp_bureau1.id,
        },
        {
            "beneficiary": "Hélène Savary",
            "medication": "Venlafaxine 150 mg (1x/jour), Temesta 1 mg (si besoin)",
            "restrictions": "Éviter les situations de stress intense",
            "allergies": "Aucune allergie connue",
            "medical_notes": "Épisode dépressif majeur – actuellement en pause. "
            "Reprise progressive envisagée dans 4 semaines.",
            "updated_by": msp_cuisine1.id,
        },
    ]

    for data in medical_data:
        ben = beneficiaries[data["beneficiary"]]
        existing = await session.execute(
            select(BeneficiaryMedicalData).filter_by(beneficiary_id=ben.id)
        )
        if existing.scalar_one_or_none():
            print(f"  [EXISTE] Données médicales de {data['beneficiary']}")
            continue

        med = BeneficiaryMedicalData(
            beneficiary_id=ben.id,
            medication=encrypt_data(data["medication"]),
            restrictions=encrypt_data(data["restrictions"]),
            allergies=encrypt_data(data["allergies"]),
            medical_notes=encrypt_data(data["medical_notes"]),
            updated_by=data["updated_by"],
        )
        session.add(med)
        await session.flush()
        print(f"  [CRÉÉ] Données médicales de {data['beneficiary']}")


# ---------------------------------------------------------------------------
# 7. Contacts réseau
# ---------------------------------------------------------------------------

async def seed_contacts(session, beneficiaries):
    """Crée quelques contacts pour les bénéficiaires."""
    print("\n--- Contacts réseau ---")

    contacts_data = [
        {
            "beneficiary": "Alain Mercier",
            "contact_type": "doctor",
            "name": "Dr. Catherine Reymond",
            "organization": "Cabinet médical de la Gare",
            "phone": "+41 21 312 00 11",
            "email": "c.reymond@hin.ch",
            "is_emergency_contact": False,
            "notes": "Médecin traitant",
        },
        {
            "beneficiary": "Alain Mercier",
            "contact_type": "emergency",
            "name": "Françoise Mercier",
            "organization": None,
            "phone": "+41 79 456 12 34",
            "email": None,
            "is_emergency_contact": True,
            "notes": "Mère du bénéficiaire",
        },
        {
            "beneficiary": "Alain Mercier",
            "contact_type": "ai_referent",
            "name": "Stéphane Borel",
            "organization": "Office AI Vaud",
            "phone": "+41 21 345 67 89",
            "email": "s.borel@oai-vd.ch",
            "is_emergency_contact": False,
            "notes": "Conseiller AI principal",
        },
        {
            "beneficiary": "Fatima Benali",
            "contact_type": "doctor",
            "name": "Dr. Michel Barras",
            "organization": "Policlinique PMU",
            "phone": "+41 21 314 60 60",
            "email": None,
            "is_emergency_contact": False,
            "notes": "Médecin traitant",
        },
        {
            "beneficiary": "Fatima Benali",
            "contact_type": "emergency",
            "name": "Karim Benali",
            "organization": None,
            "phone": "+41 78 654 32 10",
            "email": None,
            "is_emergency_contact": True,
            "notes": "Frère de la bénéficiaire",
        },
        {
            "beneficiary": "David Charrière",
            "contact_type": "psychologist",
            "name": "Dr. Anne-Lise Moser",
            "organization": "Centre de psychiatrie ambulatoire",
            "phone": "+41 26 305 70 00",
            "email": "al.moser@rfsm.ch",
            "is_emergency_contact": False,
            "notes": "Psychiatre traitant – suivi mensuel",
        },
        {
            "beneficiary": "Igor Petrovic",
            "contact_type": "ai_referent",
            "name": "Valérie Ducret",
            "organization": "Office AI Fribourg",
            "phone": "+41 26 305 52 00",
            "email": "v.ducret@oai-fr.ch",
            "is_emergency_contact": False,
            "notes": "Conseillère AI – détermination mesures",
        },
    ]

    count_created = 0
    for data in contacts_data:
        ben = beneficiaries[data["beneficiary"]]
        # Check by beneficiary + name + contact_type
        existing = await session.execute(
            select(Contact).filter_by(
                beneficiary_id=ben.id,
                name=data["name"],
                contact_type=data["contact_type"],
            )
        )
        if existing.scalar_one_or_none():
            continue
        contact = Contact(
            beneficiary_id=ben.id,
            contact_type=data["contact_type"],
            name=data["name"],
            organization=data["organization"],
            phone=data["phone"],
            email=data["email"],
            is_emergency_contact=data["is_emergency_contact"],
            notes=data["notes"],
        )
        session.add(contact)
        count_created += 1

    await session.flush()
    print(f"  {count_created} contact(s) créé(s), {len(contacts_data) - count_created} existant(s)")


# ---------------------------------------------------------------------------
# 8. PAIs
# ---------------------------------------------------------------------------

async def seed_pais(session, beneficiaries, users):
    """Crée 5 PAIs avec différents statuts."""
    print("\n--- Plans d'Accompagnement Individualisé (PAI) ---")

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]

    pais_data = [
        {
            "beneficiary": "Alain Mercier",
            "status": "active",
            "valid_from": date(2024, 4, 1),
            "valid_to": date(2024, 12, 31),
            "strengths": "Bonne dextérité manuelle, motivé, ponctuel. "
            "Apprécie le travail du bois et montre un réel intérêt pour l'ébénisterie.",
            "difficulties": "Difficultés de concentration sur les tâches longues. "
            "Fatigue en fin de journée liée au traitement médicamenteux.",
            "beneficiary_wishes": "Souhaite obtenir une attestation de compétences en menuiserie. "
            "Envisage un placement en entreprise à moyen terme.",
            "created_by": msp_bois1.id,
        },
        {
            "beneficiary": "Céline Vuagnoux",
            "status": "active",
            "valid_from": date(2024, 5, 1),
            "valid_to": date(2025, 4, 30),
            "strengths": "Créative, soigneuse dans son travail, bonne relation avec les collègues. "
            "Aime les travaux de finition et de décoration.",
            "difficulties": "Manque de confiance en soi, tendance à se sous-estimer. "
            "Difficultés avec les calculs et les mesures.",
            "beneficiary_wishes": "Aimerait développer ses compétences en finition de meubles. "
            "Souhaite améliorer sa confiance en ses capacités.",
            "created_by": msp_bois1.id,
        },
        {
            "beneficiary": "David Charrière",
            "status": "draft",
            "valid_from": date(2025, 1, 1),
            "valid_to": date(2025, 6, 30),
            "strengths": "Expérience professionnelle préalable en menuiserie. "
            "Bonne compréhension technique.",
            "difficulties": "Difficultés d'attention (TDAH). Gestion émotionnelle fragile. "
            "Absences répétées pour rendez-vous médicaux.",
            "beneficiary_wishes": "Maintenir un rythme de travail stable. "
            "Retrouver un poste adapté dans le premier marché du travail.",
            "created_by": msp_bois2.id,
        },
        {
            "beneficiary": "Fatima Benali",
            "status": "active",
            "valid_from": date(2024, 6, 1),
            "valid_to": date(2025, 5, 31),
            "strengths": "Excellente organisation, sens du détail, rapidité d'exécution. "
            "Bonnes compétences culinaires de base.",
            "difficulties": "Limitations physiques (genoux). "
            "Difficultés à s'exprimer en groupe, timidité.",
            "beneficiary_wishes": "Obtenir un certificat en hygiène alimentaire. "
            "Travailler dans une cuisine collective à temps partiel.",
            "created_by": msp_cuisine1.id,
        },
        {
            "beneficiary": "Grégoire Perrin",
            "status": "closed",
            "valid_from": date(2023, 9, 1),
            "valid_to": date(2024, 8, 31),
            "strengths": "Travailleur, endurant, bon esprit d'équipe. "
            "Connaissances solides en pâtisserie.",
            "difficulties": "Difficultés relationnelles sous pression. "
            "Gestion du stress à améliorer.",
            "beneficiary_wishes": "Se perfectionner en pâtisserie. "
            "Obtenir un stage en milieu professionnel.",
            "created_by": msp_cuisine1.id,
        },
    ]

    pais = {}
    for data in pais_data:
        ben = beneficiaries[data["beneficiary"]]
        # Vérifier par bénéficiaire + date de début
        existing = await session.execute(
            select(PAI).filter_by(beneficiary_id=ben.id, valid_from=data["valid_from"])
        )
        pai = existing.scalar_one_or_none()
        if pai:
            pais[data["beneficiary"]] = pai
            print(f"  [EXISTE] PAI {data['beneficiary']} ({data['status']})")
            continue

        pai = PAI(
            beneficiary_id=ben.id,
            status=data["status"],
            valid_from=data["valid_from"],
            valid_to=data["valid_to"],
            strengths=data["strengths"],
            difficulties=data["difficulties"],
            beneficiary_wishes=data["beneficiary_wishes"],
            created_by=data["created_by"],
        )
        session.add(pai)
        await session.flush()
        pais[data["beneficiary"]] = pai
        print(f"  [CRÉÉ] PAI {data['beneficiary']} ({data['status']}, id={pai.id})")

    return pais


# ---------------------------------------------------------------------------
# 9. Objectives (15)
# ---------------------------------------------------------------------------

async def seed_objectives(session, beneficiaries, pais, users):
    """Crée 15 objectifs variés avec indicateurs et actions."""
    print("\n--- Objectifs ---")

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]

    objectives_data = [
        # --- Alain Mercier (PAI active) ---
        {
            "beneficiary": "Alain Mercier",
            "pai": "Alain Mercier",
            "title": "Maîtriser les techniques de base du ponçage",
            "description": "Apprendre et appliquer correctement les techniques de ponçage "
            "sur différentes essences de bois (résineux et feuillus).",
            "objective_type": "pai",
            "term": "short",
            "priority": "high",
            "status": "in_progress",
            "progress": 65,
            "due_date": date(2024, 9, 30),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Connaît les différents grains de papier", "is_achieved": True},
                {"description": "Ponce une surface plane sans défaut", "is_achieved": True},
                {"description": "Ponce des surfaces courbes correctement", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Exercices pratiques sur chutes de bois (2x/semaine)",
                    "responsible": "beneficiary",
                    "responsible_name": "Alain Mercier",
                    "status": "done",
                },
                {
                    "description": "Démonstration par le MSP des techniques avancées",
                    "responsible": "msp",
                    "responsible_name": "Jean-Claude Müller",
                    "status": "done",
                },
            ],
        },
        {
            "beneficiary": "Alain Mercier",
            "pai": "Alain Mercier",
            "title": "Améliorer la gestion de la fatigue",
            "description": "Mettre en place des stratégies pour gérer la fatigue liée au "
            "traitement médicamenteux et maintenir une productivité stable.",
            "objective_type": "behavioral",
            "term": "medium",
            "priority": "medium",
            "status": "in_progress",
            "progress": 40,
            "due_date": date(2024, 12, 31),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Prend des pauses régulières sans rappel", "is_achieved": False},
                {"description": "Signale sa fatigue de manière appropriée", "is_achieved": True},
            ],
            "actions": [
                {
                    "description": "Planifier des pauses toutes les 90 minutes",
                    "responsible": "beneficiary",
                    "responsible_name": "Alain Mercier",
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "Alain Mercier",
            "pai": "Alain Mercier",
            "title": "Respecter les consignes de sécurité à l'atelier",
            "description": "Appliquer systématiquement les règles de sécurité lors de "
            "l'utilisation des machines et outils.",
            "objective_type": "operational",
            "term": "short",
            "priority": "high",
            "status": "achieved",
            "progress": 100,
            "due_date": date(2024, 6, 30),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Porte les EPI systématiquement", "is_achieved": True},
                {"description": "Vérifie les machines avant utilisation", "is_achieved": True},
            ],
            "actions": [],
        },
        # --- Céline Vuagnoux (PAI active) ---
        {
            "beneficiary": "Céline Vuagnoux",
            "pai": "Céline Vuagnoux",
            "title": "Développer les techniques de finition",
            "description": "Acquérir les compétences en vernissage, teinture et cirage "
            "sur différents types de bois.",
            "objective_type": "pai",
            "term": "medium",
            "priority": "high",
            "status": "in_progress",
            "progress": 30,
            "due_date": date(2025, 3, 31),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Applique un vernis uniforme", "is_achieved": False},
                {"description": "Maîtrise la teinture sur bois clair", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Formation interne aux techniques de vernissage",
                    "responsible": "msp",
                    "responsible_name": "Jean-Claude Müller",
                    "due_date": date(2024, 11, 30),
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "Céline Vuagnoux",
            "pai": "Céline Vuagnoux",
            "title": "Renforcer la confiance en soi",
            "description": "Développer l'estime de soi à travers des réussites progressives "
            "et la reconnaissance des compétences acquises.",
            "objective_type": "behavioral",
            "term": "long",
            "priority": "medium",
            "status": "in_progress",
            "progress": 20,
            "due_date": date(2025, 4, 30),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Présente un travail terminé au groupe", "is_achieved": False},
                {"description": "Demande de l'aide sans hésitation excessive", "is_achieved": False},
            ],
            "actions": [],
        },
        # --- David Charrière (PAI draft) ---
        {
            "beneficiary": "David Charrière",
            "pai": "David Charrière",
            "title": "Stabiliser la fréquentation de l'atelier",
            "description": "Réduire les absences non justifiées et maintenir une présence "
            "régulière d'au moins 4 jours par semaine.",
            "objective_type": "behavioral",
            "term": "short",
            "priority": "high",
            "status": "pending",
            "progress": 0,
            "due_date": date(2025, 3, 31),
            "created_by": msp_bois2.id,
            "indicators": [
                {"description": "Moins de 2 absences non justifiées par mois", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Entretien hebdomadaire de suivi avec le MSP",
                    "responsible": "msp",
                    "responsible_name": "Sophie Roth",
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "David Charrière",
            "pai": "David Charrière",
            "title": "Reprendre les tâches de menuiserie de base",
            "description": "Réintégrer progressivement les activités de découpe et "
            "d'assemblage simples.",
            "objective_type": "pai",
            "term": "medium",
            "priority": "medium",
            "status": "pending",
            "progress": 0,
            "due_date": date(2025, 6, 30),
            "created_by": msp_bois2.id,
            "indicators": [],
            "actions": [],
        },
        # --- Fatima Benali (PAI active) ---
        {
            "beneficiary": "Fatima Benali",
            "pai": "Fatima Benali",
            "title": "Obtenir le certificat d'hygiène alimentaire",
            "description": "Préparer et réussir l'examen du certificat cantonal "
            "d'hygiène alimentaire.",
            "objective_type": "pai",
            "term": "medium",
            "priority": "high",
            "status": "in_progress",
            "progress": 55,
            "due_date": date(2025, 3, 31),
            "created_by": msp_cuisine1.id,
            "indicators": [
                {"description": "Connaît les normes HACCP", "is_achieved": True},
                {"description": "Réussit le test blanc", "is_achieved": False},
                {"description": "Obtient le certificat officiel", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Inscription au cours de préparation à l'examen",
                    "responsible": "msp",
                    "responsible_name": "Philippe Girard",
                    "status": "done",
                },
                {
                    "description": "Révision quotidienne des fiches (15 min)",
                    "responsible": "beneficiary",
                    "responsible_name": "Fatima Benali",
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "Fatima Benali",
            "pai": "Fatima Benali",
            "title": "Améliorer la communication en groupe",
            "description": "Participer activement aux réunions d'équipe et exprimer "
            "ses idées devant le groupe.",
            "objective_type": "behavioral",
            "term": "long",
            "priority": "low",
            "status": "in_progress",
            "progress": 15,
            "due_date": date(2025, 5, 31),
            "created_by": msp_cuisine1.id,
            "indicators": [
                {"description": "Prend la parole au moins 1x par réunion", "is_achieved": False},
            ],
            "actions": [],
        },
        {
            "beneficiary": "Fatima Benali",
            "pai": "Fatima Benali",
            "title": "Adapter le poste de travail ergonomique",
            "description": "Mettre en place un aménagement du poste de cuisine permettant "
            "d'alterner les positions assise et debout.",
            "objective_type": "operational",
            "term": "short",
            "priority": "high",
            "status": "achieved",
            "progress": 100,
            "due_date": date(2024, 8, 31),
            "created_by": msp_cuisine1.id,
            "indicators": [
                {"description": "Tabouret ergonomique installé", "is_achieved": True},
                {"description": "Tapis anti-fatigue en place", "is_achieved": True},
            ],
            "actions": [
                {
                    "description": "Commander le mobilier ergonomique",
                    "responsible": "msp",
                    "responsible_name": "Philippe Girard",
                    "status": "done",
                },
            ],
        },
        # --- Grégoire Perrin (PAI closed) ---
        {
            "beneficiary": "Grégoire Perrin",
            "pai": "Grégoire Perrin",
            "title": "Maîtriser les bases de la pâtisserie",
            "description": "Réaliser de manière autonome les recettes de base (pâtes, "
            "crèmes, biscuits).",
            "objective_type": "pai",
            "term": "medium",
            "priority": "high",
            "status": "achieved",
            "progress": 100,
            "due_date": date(2024, 6, 30),
            "created_by": msp_cuisine1.id,
            "indicators": [
                {"description": "Réalise une pâte brisée seul", "is_achieved": True},
                {"description": "Réalise une crème pâtissière sans aide", "is_achieved": True},
            ],
            "actions": [],
        },
        {
            "beneficiary": "Grégoire Perrin",
            "pai": "Grégoire Perrin",
            "title": "Gérer les situations de stress en cuisine",
            "description": "Développer des techniques de gestion du stress lors des "
            "périodes de rush ou de commandes importantes.",
            "objective_type": "behavioral",
            "term": "medium",
            "priority": "medium",
            "status": "abandoned",
            "progress": 25,
            "due_date": date(2024, 8, 31),
            "created_by": msp_cuisine1.id,
            "indicators": [
                {"description": "Utilise la respiration contrôlée", "is_achieved": False},
            ],
            "actions": [],
        },
        # --- Objectifs hors PAI ---
        {
            "beneficiary": "Julie Bonvin",
            "pai": None,
            "title": "Maîtriser le logiciel de comptabilité",
            "description": "Apprendre à utiliser le logiciel Banana Comptabilité pour la "
            "saisie de factures et le suivi des paiements.",
            "objective_type": "operational",
            "term": "medium",
            "priority": "high",
            "status": "in_progress",
            "progress": 45,
            "due_date": date(2025, 3, 31),
            "created_by": msp_bureau1.id,
            "indicators": [
                {"description": "Saisit une facture sans erreur", "is_achieved": True},
                {"description": "Effectue un rapprochement bancaire", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Suivre le tutoriel en ligne Banana (modules 1-5)",
                    "responsible": "beneficiary",
                    "responsible_name": "Julie Bonvin",
                    "status": "done",
                },
                {
                    "description": "Exercices pratiques sur données fictives",
                    "responsible": "msp",
                    "responsible_name": "Marie Favre",
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "Michel Aeby",
            "pai": None,
            "title": "Améliorer la vitesse de frappe",
            "description": "Atteindre une vitesse de frappe de 40 mots/minute avec un "
            "taux d'erreur inférieur à 5%.",
            "objective_type": "operational",
            "term": "short",
            "priority": "medium",
            "status": "in_progress",
            "progress": 60,
            "due_date": date(2025, 2, 28),
            "created_by": msp_bureau1.id,
            "indicators": [
                {"description": "30 mots/minute atteints", "is_achieved": True},
                {"description": "40 mots/minute atteints", "is_achieved": False},
            ],
            "actions": [
                {
                    "description": "Exercice de dactylographie 15 min/jour sur typing.com",
                    "responsible": "beneficiary",
                    "responsible_name": "Michel Aeby",
                    "status": "pending",
                },
            ],
        },
        {
            "beneficiary": "Nadia Kessler",
            "pai": None,
            "title": "S'intégrer dans l'équipe de l'atelier",
            "description": "Créer des liens professionnels avec les collègues et participer "
            "activement à la vie de l'atelier.",
            "objective_type": "behavioral",
            "term": "short",
            "priority": "medium",
            "status": "in_progress",
            "progress": 50,
            "due_date": date(2024, 12, 31),
            "created_by": msp_bois1.id,
            "indicators": [
                {"description": "Participe aux pauses avec le groupe", "is_achieved": True},
                {"description": "Collabore sur un projet commun", "is_achieved": False},
            ],
            "actions": [],
        },
    ]

    objectives = []
    for data in objectives_data:
        ben = beneficiaries[data["beneficiary"]]
        pai = pais.get(data["pai"]) if data["pai"] else None

        # Vérifier par titre + bénéficiaire
        existing = await session.execute(
            select(Objective).filter_by(beneficiary_id=ben.id, title=data["title"])
        )
        if existing.scalar_one_or_none():
            print(f"  [EXISTE] {data['title'][:60]}...")
            continue

        obj = Objective(
            pai_id=pai.id if pai else None,
            beneficiary_id=ben.id,
            title=data["title"],
            description=data["description"],
            objective_type=data["objective_type"],
            term=data["term"],
            priority=data["priority"],
            status=data["status"],
            progress=data["progress"],
            due_date=data.get("due_date"),
            created_by=data["created_by"],
        )
        session.add(obj)
        await session.flush()

        # Indicateurs
        for ind_data in data.get("indicators", []):
            indicator = ObjectiveIndicator(
                objective_id=obj.id,
                description=ind_data["description"],
                is_achieved=ind_data["is_achieved"],
                achieved_at=_dt(2024, 10, 15) if ind_data["is_achieved"] else None,
            )
            session.add(indicator)

        # Actions
        for act_data in data.get("actions", []):
            action = Action(
                objective_id=obj.id,
                description=act_data["description"],
                responsible=act_data.get("responsible"),
                responsible_name=act_data.get("responsible_name"),
                due_date=act_data.get("due_date"),
                status=act_data.get("status", "pending"),
            )
            session.add(action)

        await session.flush()
        objectives.append(obj)
        print(f"  [CRÉÉ] {data['title'][:60]}...")

    return objectives


# ---------------------------------------------------------------------------
# 10. Journal Entries (25)
# ---------------------------------------------------------------------------

async def seed_journal_entries(session, beneficiaries, users, categories):
    """Crée 25 entrées de journal variées."""
    print("\n--- Entrées de journal ---")

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]
    res_bois = users["res.bois@cis.ch"]
    res_cuisine = users["res.cuisine@cis.ch"]

    entries_data = [
        # --- Alain Mercier ---
        {
            "beneficiary": "Alain Mercier",
            "author_id": msp_bois1.id,
            "title": "Bonne progression en ponçage",
            "content": "Alain a réalisé le ponçage complet d'un plateau de table en chêne "
            "aujourd'hui. Le résultat est très satisfaisant, la surface est uniforme. "
            "Il commence à bien maîtriser les changements de grain.",
            "entry_date": _dt(2024, 10, 14, 16, 30),
            "visibility": "unit",
            "categories": ["competences", "professionnel"],
            "tags": ["ponçage", "progression"],
        },
        {
            "beneficiary": "Alain Mercier",
            "author_id": msp_bois1.id,
            "title": "Fatigue marquée en fin de matinée",
            "content": "Alain montre des signes de fatigue importants dès 11h. "
            "Il a dû s'asseoir à plusieurs reprises. Lui ai rappelé de prendre ses "
            "pauses régulières. À surveiller dans les prochains jours.",
            "entry_date": _dt(2024, 10, 10, 11, 45),
            "visibility": "unit",
            "categories": ["sante"],
            "tags": ["fatigue", "traitement"],
        },
        {
            "beneficiary": "Alain Mercier",
            "author_id": res_bois.id,
            "title": "Entretien de suivi trimestriel",
            "content": "Entretien réalisé avec Alain et son MSP référent. Points abordés :\n"
            "- Progression technique très encourageante\n"
            "- Fatigue à gérer avec le médecin traitant\n"
            "- Objectif de stage en entreprise maintenu pour début 2025\n"
            "Prochain entretien prévu le 15 janvier 2025.",
            "entry_date": _dt(2024, 10, 8, 14, 0),
            "visibility": "inter_unit",
            "categories": ["professionnel", "administratif"],
            "tags": ["entretien", "bilan"],
        },
        # --- Céline Vuagnoux ---
        {
            "beneficiary": "Céline Vuagnoux",
            "author_id": msp_bois1.id,
            "title": "Premier essai de vernissage",
            "content": "Céline a réalisé son premier vernissage sur un petit coffret. "
            "Le résultat présente quelques coulures mais l'application est globalement "
            "correcte. Elle était contente du résultat et motivée à recommencer.",
            "entry_date": _dt(2024, 10, 12, 15, 0),
            "visibility": "unit",
            "categories": ["competences"],
            "tags": ["vernissage", "première fois"],
        },
        {
            "beneficiary": "Céline Vuagnoux",
            "author_id": msp_bois1.id,
            "title": "Difficulté avec les mesures",
            "content": "Céline a eu des difficultés à lire le mètre ruban et à reporter "
            "les mesures sur le bois. Nous avons pris du temps pour revoir les bases. "
            "Elle semble frustrée mais reste volontaire.",
            "entry_date": _dt(2024, 10, 7, 10, 30),
            "visibility": "team",
            "categories": ["competences", "comportement"],
            "tags": ["mesures", "apprentissage"],
        },
        {
            "beneficiary": "Céline Vuagnoux",
            "author_id": msp_bois1.id,
            "title": "Interaction positive avec le groupe",
            "content": "Céline a spontanément aidé Nadia à ranger l'atelier en fin de journée. "
            "C'est la première fois qu'elle prend ce type d'initiative sociale. "
            "À encourager.",
            "entry_date": _dt(2024, 10, 15, 17, 0),
            "visibility": "unit",
            "categories": ["social", "comportement"],
            "tags": ["initiative", "entraide"],
        },
        # --- David Charrière ---
        {
            "beneficiary": "David Charrière",
            "author_id": msp_bois2.id,
            "title": "Absence non justifiée",
            "content": "David ne s'est pas présenté à l'atelier ce matin et n'a pas prévenu. "
            "Tentative de contact par téléphone restée sans réponse. "
            "C'est la 3ème absence ce mois.",
            "entry_date": _dt(2024, 10, 9, 9, 0),
            "visibility": "unit",
            "categories": ["comportement", "administratif"],
            "tags": ["absence", "suivi"],
        },
        {
            "beneficiary": "David Charrière",
            "author_id": msp_bois2.id,
            "title": "Retour après absence – entretien",
            "content": "David est revenu aujourd'hui. Entretien mené pour comprendre les raisons "
            "de son absence. Il évoque des difficultés de sommeil et un oubli de "
            "médicament. Rappel de l'importance de prévenir en cas d'absence. "
            "Contact avec le psychiatre prévu.",
            "entry_date": _dt(2024, 10, 11, 8, 30),
            "visibility": "unit",
            "categories": ["sante", "comportement"],
            "tags": ["absence", "entretien", "médication"],
        },
        # --- Fatima Benali ---
        {
            "beneficiary": "Fatima Benali",
            "author_id": msp_cuisine1.id,
            "title": "Excellente prestation lors du repas collectif",
            "content": "Fatima a préparé le repas pour 35 personnes quasiment seule "
            "aujourd'hui (avec aide ponctuelle). Le menu (gratin de légumes, salade, "
            "dessert) était très réussi. Bonne gestion du temps et des quantités.",
            "entry_date": _dt(2024, 10, 14, 14, 30),
            "visibility": "inter_unit",
            "categories": ["competences", "professionnel"],
            "tags": ["cuisine", "autonomie", "réussite"],
        },
        {
            "beneficiary": "Fatima Benali",
            "author_id": msp_cuisine1.id,
            "title": "Douleur au genou – adaptation du poste",
            "content": "Fatima se plaint de douleurs au genou droit depuis ce matin. "
            "Le tabouret ergonomique a été repositionné. Elle peut alterner "
            "position assise/debout. Si douleur persistante, consultation médicale.",
            "entry_date": _dt(2024, 10, 3, 10, 0),
            "visibility": "team",
            "categories": ["sante", "medical"],
            "tags": ["genou", "ergonomie"],
        },
        {
            "beneficiary": "Fatima Benali",
            "author_id": msp_cuisine1.id,
            "title": "Préparation examen hygiène – test blanc",
            "content": "Fatima a passé le test blanc de l'examen d'hygiène alimentaire. "
            "Résultat : 72%. Le seuil de réussite est à 80%. Points à revoir : "
            "température de conservation, marche en avant. Prochain test dans 2 semaines.",
            "entry_date": _dt(2024, 10, 11, 16, 0),
            "visibility": "unit",
            "categories": ["formation", "competences"],
            "tags": ["hygiène", "examen", "formation"],
        },
        # --- Grégoire Perrin ---
        {
            "beneficiary": "Grégoire Perrin",
            "author_id": msp_cuisine1.id,
            "title": "Incident en cuisine – gestion du stress",
            "content": "Lors du service de midi, Grégoire s'est emporté verbalement "
            "après avoir fait tomber un plat. Il a haussé le ton devant les collègues. "
            "Après discussion, il s'est excusé. Cet incident montre que la gestion "
            "du stress reste un point de travail important.",
            "entry_date": _dt(2024, 10, 2, 13, 30),
            "visibility": "unit",
            "categories": ["comportement", "social"],
            "tags": ["incident", "stress", "conflit"],
        },
        {
            "beneficiary": "Grégoire Perrin",
            "author_id": msp_cuisine1.id,
            "title": "Réussite pâtisserie – tarte aux pommes",
            "content": "Grégoire a réalisé une tarte aux pommes de A à Z, de la pâte "
            "brisée à la cuisson. Résultat excellent, belle présentation. "
            "Il peut être fier de cette réalisation.",
            "entry_date": _dt(2024, 9, 25, 15, 0),
            "visibility": "unit",
            "categories": ["competences", "professionnel"],
            "tags": ["pâtisserie", "réussite", "autonomie"],
        },
        {
            "beneficiary": "Grégoire Perrin",
            "author_id": res_cuisine.id,
            "title": "Discussion sur orientation future",
            "content": "Entretien avec Grégoire concernant la suite de son parcours. "
            "Il exprime le souhait de faire un stage en pâtisserie dans le commerce. "
            "Contact à prendre avec la Boulangerie-Pâtisserie Grandjean à Morges. "
            "Dossier AI à mettre à jour.",
            "entry_date": _dt(2024, 10, 5, 10, 0),
            "visibility": "inter_unit",
            "categories": ["professionnel", "administratif"],
            "tags": ["orientation", "stage", "AI"],
        },
        # --- Hélène Savary ---
        {
            "beneficiary": "Hélène Savary",
            "author_id": msp_cuisine1.id,
            "title": "Mise en pause – raisons médicales",
            "content": "Suite à la recommandation du psychiatre traitant, Hélène est mise "
            "en pause pour une durée estimée de 6 semaines. Certificat médical reçu. "
            "Reprise progressive prévue avec taux réduit dans un premier temps.",
            "entry_date": _dt(2024, 9, 20, 9, 0),
            "visibility": "inter_unit",
            "categories": ["medical", "administratif"],
            "tags": ["pause", "certificat", "psychiatrie"],
        },
        {
            "beneficiary": "Hélène Savary",
            "author_id": msp_cuisine1.id,
            "title": "Appel téléphonique de suivi",
            "content": "Pris des nouvelles d'Hélène par téléphone. Elle dit se sentir "
            "un peu mieux. Le nouveau dosage de Venlafaxine semble aider. "
            "Elle est motivée à reprendre mais le médecin préconise d'attendre encore.",
            "entry_date": _dt(2024, 10, 7, 11, 0),
            "visibility": "team",
            "categories": ["sante", "medical"],
            "tags": ["suivi", "téléphone", "traitement"],
        },
        # --- Igor Petrovic ---
        {
            "beneficiary": "Igor Petrovic",
            "author_id": msp_bureau1.id,
            "title": "Bonne adaptation au poste bureautique",
            "content": "Igor s'adapte bien à l'atelier bureautique. Il maîtrise déjà "
            "les bases de Word et Excel. Son expérience professionnelle antérieure "
            "(magasinier) lui donne de bonnes bases en organisation.",
            "entry_date": _dt(2024, 10, 8, 16, 0),
            "visibility": "unit",
            "categories": ["competences", "professionnel"],
            "tags": ["intégration", "bureautique"],
        },
        {
            "beneficiary": "Igor Petrovic",
            "author_id": msp_bureau1.id,
            "title": "Douleur au poignet – pause nécessaire",
            "content": "Igor signale une douleur au poignet droit en fin de journée. "
            "Rappel de faire les exercices d'étirement. Position du clavier ajustée. "
            "Si douleur persistante, consultation de contrôle à prévoir.",
            "entry_date": _dt(2024, 10, 14, 16, 30),
            "visibility": "team",
            "categories": ["sante"],
            "tags": ["poignet", "ergonomie", "douleur"],
        },
        # --- Julie Bonvin ---
        {
            "beneficiary": "Julie Bonvin",
            "author_id": msp_bureau1.id,
            "title": "Progression rapide en comptabilité",
            "content": "Julie a terminé les 5 premiers modules du tutoriel Banana Comptabilité. "
            "Elle saisit maintenant les factures de manière autonome. Très bonne "
            "compréhension de la logique comptable.",
            "entry_date": _dt(2024, 10, 10, 14, 0),
            "visibility": "unit",
            "categories": ["competences", "formation"],
            "tags": ["comptabilité", "progression", "Banana"],
        },
        # --- Kevin Morand ---
        {
            "beneficiary": "Kevin Morand",
            "author_id": msp_bois2.id,
            "title": "Mise en pause suite à rechute",
            "content": "Kevin a annoncé vouloir suspendre son activité. Il traverse une "
            "période difficile (séparation, problèmes financiers). Le mise en pause "
            "est effective dès demain. Contact avec l'assistante sociale de l'OAI prévu.",
            "entry_date": _dt(2024, 8, 15, 10, 0),
            "visibility": "inter_unit",
            "categories": ["social", "famille", "administratif"],
            "tags": ["pause", "social", "OAI"],
        },
        # --- Laetitia Currat ---
        {
            "beneficiary": "Laetitia Currat",
            "author_id": msp_cuisine1.id,
            "title": "Bilan de sortie positif",
            "content": "Entretien de sortie avec Laetitia. Après 2 ans dans l'atelier, "
            "elle a considérablement progressé. Elle a trouvé un poste adapté à 60% "
            "dans un restaurant collectif à Yverdon. Fin de mesure le 30 juin 2024.",
            "entry_date": _dt(2024, 6, 28, 14, 0),
            "visibility": "inter_unit",
            "categories": ["professionnel", "administratif"],
            "tags": ["sortie", "placement", "réussite"],
        },
        # --- Michel Aeby ---
        {
            "beneficiary": "Michel Aeby",
            "author_id": msp_bureau1.id,
            "title": "Progrès en dactylographie",
            "content": "Michel atteint maintenant 32 mots/minute avec un taux d'erreur "
            "de 4%. Il y a un mois il était à 22 mots/minute. La pratique quotidienne "
            "porte ses fruits. L'encourager à continuer.",
            "entry_date": _dt(2024, 10, 15, 11, 0),
            "visibility": "unit",
            "categories": ["competences"],
            "tags": ["dactylographie", "progression"],
        },
        {
            "beneficiary": "Michel Aeby",
            "author_id": msp_bureau1.id,
            "title": "Conflit avec collègue résolu",
            "content": "Un désaccord entre Michel et Igor concernant le partage de "
            "l'imprimante a été résolu par une discussion en commun. "
            "Un planning d'utilisation a été mis en place. "
            "Les deux collègues se sont montrés constructifs.",
            "entry_date": _dt(2024, 10, 9, 15, 30),
            "visibility": "team",
            "categories": ["social", "comportement"],
            "tags": ["conflit", "résolution"],
        },
        # --- Nadia Kessler ---
        {
            "beneficiary": "Nadia Kessler",
            "author_id": msp_bois1.id,
            "title": "Première semaine d'intégration",
            "content": "Première semaine de Nadia à l'atelier Bois. Elle est discrète mais "
            "attentive. Elle a participé à un exercice de ponçage et montre de la "
            "précision. A faire connaissance avec l'équipe progressivement.",
            "entry_date": _dt(2024, 6, 7, 16, 0),
            "visibility": "unit",
            "categories": ["professionnel", "social"],
            "tags": ["intégration", "nouvelle"],
        },
        {
            "beneficiary": "Nadia Kessler",
            "author_id": msp_bois1.id,
            "title": "Contact famille – information",
            "content": "Appel de la mère de Nadia pour informer que sa fille a un rendez-vous "
            "médical jeudi matin. Absence prévue jusqu'à 10h30. La mère se montre "
            "très impliquée dans le suivi.",
            "entry_date": _dt(2024, 10, 13, 9, 30),
            "visibility": "team",
            "categories": ["famille", "administratif"],
            "tags": ["famille", "rendez-vous", "absence"],
        },
    ]

    count_created = 0
    for data in entries_data:
        ben = beneficiaries[data["beneficiary"]]

        # Vérifier par titre + bénéficiaire + date
        existing = await session.execute(
            select(JournalEntry).filter_by(
                beneficiary_id=ben.id,
                title=data["title"],
            )
        )
        if existing.scalar_one_or_none():
            continue

        entry = JournalEntry(
            beneficiary_id=ben.id,
            author_id=data["author_id"],
            title=data["title"],
            content=data["content"],
            entry_date=data["entry_date"],
            visibility=data["visibility"],
        )
        session.add(entry)
        await session.flush()

        # Catégories associées
        for cat_name in data.get("categories", []):
            cat = categories.get(cat_name)
            if cat:
                jec = JournalEntryCategory(
                    journal_entry_id=entry.id,
                    category_id=cat.id,
                )
                session.add(jec)

        # Tags
        for tag_text in data.get("tags", []):
            tag = JournalEntryTag(
                journal_entry_id=entry.id,
                tag=tag_text,
            )
            session.add(tag)

        await session.flush()
        count_created += 1

    total = len(entries_data)
    print(f"  {count_created} entrée(s) créée(s), {total - count_created} existante(s)")


# ---------------------------------------------------------------------------
# 11. Time Entries
# ---------------------------------------------------------------------------

async def seed_time_entries(session, beneficiaries):
    """Crée des pointages pour quelques bénéficiaires."""
    print("\n--- Pointages ---")

    # Vérifier si des pointages existent déjà
    existing = await session.execute(select(TimeEntry).limit(1))
    if existing.scalar_one_or_none():
        print("  [EXISTE] Des pointages existent déjà")
        return

    # Semaine du 7 au 11 octobre 2024
    week_dates = [date(2024, 10, d) for d in range(7, 12)]
    active_beneficiaries = [
        "Alain Mercier", "Céline Vuagnoux", "Fatima Benali",
        "Grégoire Perrin", "Igor Petrovic", "Julie Bonvin",
        "Michel Aeby", "Nadia Kessler",
    ]

    time_schedules = {
        "Alain Mercier": (time(8, 0), time(12, 0), time(13, 0), time(16, 30)),
        "Céline Vuagnoux": (time(8, 30), time(12, 0), time(13, 0), time(15, 30)),
        "Fatima Benali": (time(7, 30), time(12, 0), time(13, 0), time(15, 0)),
        "Grégoire Perrin": (time(7, 30), time(12, 0), time(13, 0), time(15, 30)),
        "Igor Petrovic": (time(9, 0), time(12, 0), time(13, 30), time(16, 0)),
        "Julie Bonvin": (time(8, 0), time(12, 0), time(13, 0), time(17, 0)),
        "Michel Aeby": (time(8, 0), time(12, 0), time(13, 0), time(16, 30)),
        "Nadia Kessler": (time(8, 0), time(12, 0), time(13, 0), time(15, 30)),
    }

    count = 0
    for name in active_beneficiaries:
        ben = beneficiaries[name]
        sched = time_schedules[name]

        for d in week_dates:
            # Matin
            hours_am = Decimal(str(
                (datetime.combine(d, sched[1]) - datetime.combine(d, sched[0])).seconds / 3600
            )).quantize(Decimal("0.01"))
            entry_am = TimeEntry(
                beneficiary_id=ben.id,
                entry_date=d,
                time_in=sched[0],
                time_out=sched[1],
                entry_type="work",
                hours_worked=hours_am,
            )
            session.add(entry_am)

            # Après-midi
            hours_pm = Decimal(str(
                (datetime.combine(d, sched[3]) - datetime.combine(d, sched[2])).seconds / 3600
            )).quantize(Decimal("0.01"))
            entry_pm = TimeEntry(
                beneficiary_id=ben.id,
                entry_date=d,
                time_in=sched[2],
                time_out=sched[3],
                entry_type="work",
                hours_worked=hours_pm,
            )
            session.add(entry_pm)
            count += 2

    # Quelques entrées de type formation
    entry_training = TimeEntry(
        beneficiary_id=beneficiaries["Fatima Benali"].id,
        entry_date=date(2024, 10, 11),
        time_in=time(13, 30),
        time_out=time(15, 30),
        entry_type="training",
        hours_worked=Decimal("2.00"),
        notes="Cours de préparation à l'examen d'hygiène alimentaire",
    )
    session.add(entry_training)
    count += 1

    entry_rdv = TimeEntry(
        beneficiary_id=beneficiaries["David Charrière"].id,
        entry_date=date(2024, 10, 10),
        time_in=time(9, 0),
        time_out=time(10, 30),
        entry_type="appointment",
        hours_worked=Decimal("1.50"),
        notes="Rendez-vous neuropsychologique",
    )
    session.add(entry_rdv)
    count += 1

    await session.flush()
    print(f"  {count} pointage(s) créé(s)")


# ---------------------------------------------------------------------------
# 12. Absences
# ---------------------------------------------------------------------------

async def seed_absences(session, beneficiaries, users):
    """Crée des absences pour quelques bénéficiaires."""
    print("\n--- Absences ---")

    existing = await session.execute(select(Absence).limit(1))
    if existing.scalar_one_or_none():
        print("  [EXISTE] Des absences existent déjà")
        return

    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]

    absences_data = [
        {
            "beneficiary": "David Charrière",
            "absence_type": "unauthorized",
            "start_date": date(2024, 10, 9),
            "end_date": date(2024, 10, 9),
            "notes": "Absence non justifiée – pas de nouvelles",
            "validated_by": msp_bois2.id,
            "validated_at": _dt(2024, 10, 11, 9, 0),
        },
        {
            "beneficiary": "David Charrière",
            "absence_type": "sick",
            "start_date": date(2024, 9, 23),
            "end_date": date(2024, 9, 25),
            "notes": "Certificat médical reçu – gastro-entérite",
            "validated_by": msp_bois2.id,
            "validated_at": _dt(2024, 9, 26, 8, 30),
        },
        {
            "beneficiary": "Hélène Savary",
            "absence_type": "sick",
            "start_date": date(2024, 9, 20),
            "end_date": date(2024, 11, 1),
            "notes": "Arrêt maladie – épisode dépressif majeur. Certificat médical du "
            "Dr. Morand, psychiatre.",
            "validated_by": msp_cuisine1.id,
            "validated_at": _dt(2024, 9, 20, 10, 0),
        },
        {
            "beneficiary": "Alain Mercier",
            "absence_type": "vacation",
            "start_date": date(2024, 7, 15),
            "end_date": date(2024, 7, 26),
            "notes": "Vacances d'été",
            "validated_by": None,
            "validated_at": None,
        },
        {
            "beneficiary": "Fatima Benali",
            "absence_type": "other",
            "start_date": date(2024, 10, 3),
            "end_date": date(2024, 10, 3),
            "notes": "Rendez-vous au Service de population – renouvellement permis",
            "validated_by": msp_cuisine1.id,
            "validated_at": _dt(2024, 10, 2, 16, 0),
        },
        {
            "beneficiary": "Kevin Morand",
            "absence_type": "sick",
            "start_date": date(2024, 8, 12),
            "end_date": date(2024, 8, 14),
            "notes": "Certificat médical reçu",
            "validated_by": msp_bois2.id,
            "validated_at": _dt(2024, 8, 15, 9, 0),
        },
        {
            "beneficiary": "Igor Petrovic",
            "absence_type": "accident",
            "start_date": date(2024, 7, 5),
            "end_date": date(2024, 7, 5),
            "notes": "Chute dans les escaliers – contusion au genou. Retour le lendemain.",
            "validated_by": msp_bureau1.id,
            "validated_at": _dt(2024, 7, 8, 8, 0),
        },
    ]

    for data in absences_data:
        ben = beneficiaries[data["beneficiary"]]
        absence = Absence(
            beneficiary_id=ben.id,
            absence_type=data["absence_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            notes=data["notes"],
            validated_by=data["validated_by"],
            validated_at=data["validated_at"],
        )
        session.add(absence)

    await session.flush()
    print(f"  {len(absences_data)} absence(s) créée(s)")


# ---------------------------------------------------------------------------
# 13. Vacation Balances
# ---------------------------------------------------------------------------

async def seed_vacation_balances(session, beneficiaries):
    """Crée les soldes de vacances 2024."""
    print("\n--- Soldes de vacances ---")

    existing = await session.execute(select(VacationBalance).limit(1))
    if existing.scalar_one_or_none():
        print("  [EXISTE] Des soldes de vacances existent déjà")
        return

    balances_data = [
        {"beneficiary": "Alain Mercier", "entitled": Decimal("20.00"), "taken": Decimal("10.00")},
        {"beneficiary": "Céline Vuagnoux", "entitled": Decimal("15.00"), "taken": Decimal("5.00")},
        {"beneficiary": "David Charrière", "entitled": Decimal("20.00"), "taken": Decimal("8.00")},
        {"beneficiary": "Fatima Benali", "entitled": Decimal("15.00"), "taken": Decimal("3.00")},
        {"beneficiary": "Grégoire Perrin", "entitled": Decimal("20.00"), "taken": Decimal("15.00")},
        {"beneficiary": "Hélène Savary", "entitled": Decimal("10.00"), "taken": Decimal("2.00")},
        {"beneficiary": "Igor Petrovic", "entitled": Decimal("12.00"), "taken": Decimal("0.00")},
        {"beneficiary": "Julie Bonvin", "entitled": Decimal("25.00"), "taken": Decimal("12.00")},
        {"beneficiary": "Kevin Morand", "entitled": Decimal("10.00"), "taken": Decimal("4.00")},
        {"beneficiary": "Michel Aeby", "entitled": Decimal("12.00"), "taken": Decimal("2.00")},
        {"beneficiary": "Nadia Kessler", "entitled": Decimal("10.00"), "taken": Decimal("0.00")},
    ]

    for data in balances_data:
        ben = beneficiaries[data["beneficiary"]]
        vb = VacationBalance(
            beneficiary_id=ben.id,
            year=2024,
            entitled_days=data["entitled"],
            taken_days=data["taken"],
        )
        session.add(vb)

    await session.flush()
    print(f"  {len(balances_data)} solde(s) créé(s)")


# ---------------------------------------------------------------------------
# 14. Beneficiary Skills (evaluations)
# ---------------------------------------------------------------------------

async def seed_beneficiary_skills(session, beneficiaries, skills, users):
    """Crée des évaluations de compétences pour quelques bénéficiaires."""
    print("\n--- Évaluations de compétences ---")

    existing = await session.execute(select(BeneficiarySkill).limit(1))
    if existing.scalar_one_or_none():
        print("  [EXISTE] Des évaluations existent déjà")
        return

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]

    evaluations = [
        # Alain Mercier
        ("Alain Mercier", "Ponctualité", "acquired", msp_bois1.id, date(2024, 9, 30), "Toujours à l'heure, très fiable."),
        ("Alain Mercier", "Assiduité", "acquired", msp_bois1.id, date(2024, 9, 30), "Présence régulière, rarement absent."),
        ("Alain Mercier", "Autonomie", "in_progress", msp_bois1.id, date(2024, 9, 30), "Progresse bien mais demande encore des confirmations."),
        ("Alain Mercier", "Qualité du travail", "in_progress", msp_bois1.id, date(2024, 9, 30), "Bon travail, attention aux détails en progression."),
        ("Alain Mercier", "Sécurité", "mastered", msp_bois1.id, date(2024, 9, 30), "Excellente maîtrise des consignes de sécurité."),
        ("Alain Mercier", "Gestion du stress", "in_progress", msp_bois1.id, date(2024, 9, 30), "En amélioration, liée à la fatigue."),
        # Fatima Benali
        ("Fatima Benali", "Ponctualité", "mastered", msp_cuisine1.id, date(2024, 9, 30), "Exemplaire, toujours en avance."),
        ("Fatima Benali", "Organisation", "acquired", msp_cuisine1.id, date(2024, 9, 30), "Très bien organisée dans son travail."),
        ("Fatima Benali", "Hygiène", "acquired", msp_cuisine1.id, date(2024, 9, 30), "Respecte scrupuleusement les normes."),
        ("Fatima Benali", "Communication", "in_progress", msp_cuisine1.id, date(2024, 9, 30), "Difficultés à s'exprimer en groupe."),
        ("Fatima Benali", "Travail d'équipe", "in_progress", msp_cuisine1.id, date(2024, 9, 30), "Collaborative mais effacée."),
        # Julie Bonvin
        ("Julie Bonvin", "Ponctualité", "acquired", msp_bureau1.id, date(2024, 9, 30), None),
        ("Julie Bonvin", "Autonomie", "acquired", msp_bureau1.id, date(2024, 9, 30), "Travaille de manière très indépendante."),
        ("Julie Bonvin", "Communication", "mastered", msp_bureau1.id, date(2024, 9, 30), "Excellente communication orale et écrite."),
        ("Julie Bonvin", "Organisation", "mastered", msp_bureau1.id, date(2024, 9, 30), "Très structurée, gère bien ses tâches."),
        ("Julie Bonvin", "Initiative", "acquired", msp_bureau1.id, date(2024, 9, 30), "Propose souvent des améliorations."),
        # David Charrière
        ("David Charrière", "Ponctualité", "not_acquired", users["msp.bois2@cis.ch"].id, date(2024, 9, 30), "Retards fréquents, à travailler."),
        ("David Charrière", "Assiduité", "not_acquired", users["msp.bois2@cis.ch"].id, date(2024, 9, 30), "Absences répétées, problème principal."),
        ("David Charrière", "Qualité du travail", "acquired", users["msp.bois2@cis.ch"].id, date(2024, 9, 30), "Quand il est présent, bon travail."),
        ("David Charrière", "Respect des consignes", "in_progress", users["msp.bois2@cis.ch"].id, date(2024, 9, 30), "Difficultés liées au TDAH."),
    ]

    count = 0
    for (ben_name, skill_name, level, evaluator_id, eval_date, comment) in evaluations:
        ben = beneficiaries[ben_name]
        skill = skills[skill_name]
        bs = BeneficiarySkill(
            beneficiary_id=ben.id,
            skill_id=skill.id,
            level=level,
            evaluation_date=eval_date,
            evaluated_by=evaluator_id,
            comments=comment,
        )
        session.add(bs)
        count += 1

    await session.flush()
    print(f"  {count} évaluation(s) créée(s)")


# ---------------------------------------------------------------------------
# 15. Notifications
# ---------------------------------------------------------------------------

async def seed_notifications(session, users):
    """Crée quelques notifications pour les utilisateurs."""
    print("\n--- Notifications ---")

    existing = await session.execute(select(Notification).limit(1))
    if existing.scalar_one_or_none():
        print("  [EXISTE] Des notifications existent déjà")
        return

    msp_bois1 = users["msp.bois1@cis.ch"]
    msp_bois2 = users["msp.bois2@cis.ch"]
    msp_cuisine1 = users["msp.cuisine1@cis.ch"]
    msp_bureau1 = users["msp.bureau1@cis.ch"]
    res_bois = users["res.bois@cis.ch"]

    notifications_data = [
        {
            "user_id": msp_bois1.id,
            "notification_type": "objective_reminder",
            "title": "Échéance objectif proche",
            "message": "L'objectif « Maîtriser les techniques de base du ponçage » "
            "d'Alain Mercier arrive à échéance le 30.09.2024.",
            "link": "/beneficiaries/1/objectives",
            "is_read": True,
        },
        {
            "user_id": msp_bois2.id,
            "notification_type": "absence_alert",
            "title": "Absence non justifiée",
            "message": "David Charrière est absent depuis ce matin sans justification.",
            "link": "/beneficiaries/3/absences",
            "is_read": True,
        },
        {
            "user_id": msp_cuisine1.id,
            "notification_type": "pai_expiration",
            "title": "PAI arrivant à échéance",
            "message": "Le PAI de Grégoire Perrin (Atelier Cuisine) expire le 31.08.2024. "
            "Veuillez procéder au bilan et à la clôture.",
            "link": "/beneficiaries/5/pai",
            "is_read": True,
        },
        {
            "user_id": res_bois.id,
            "notification_type": "new_journal_entry",
            "title": "Nouvelle entrée de journal",
            "message": "Jean-Claude Müller a ajouté une entrée pour Alain Mercier : "
            "« Bonne progression en ponçage ».",
            "link": "/beneficiaries/1/journal",
            "is_read": False,
        },
        {
            "user_id": msp_bureau1.id,
            "notification_type": "objective_reminder",
            "title": "Objectif à mettre à jour",
            "message": "L'objectif « Améliorer la vitesse de frappe » de Michel Aeby "
            "est en cours depuis 3 mois. Merci de mettre à jour la progression.",
            "link": "/beneficiaries/11/objectives",
            "is_read": False,
        },
        {
            "user_id": msp_bois1.id,
            "notification_type": "new_beneficiary",
            "title": "Nouveau bénéficiaire attribué",
            "message": "Nadia Kessler a été attribuée à votre suivi à l'Atelier Bois.",
            "link": "/beneficiaries/12",
            "is_read": True,
        },
        {
            "user_id": msp_cuisine1.id,
            "notification_type": "medical_update",
            "title": "Mise à jour données médicales",
            "message": "Les données médicales d'Hélène Savary ont été mises à jour "
            "par le responsable d'unité.",
            "link": "/beneficiaries/6/medical",
            "is_read": False,
        },
    ]

    for data in notifications_data:
        notif = Notification(**data)
        session.add(notif)

    await session.flush()
    print(f"  {len(notifications_data)} notification(s) créée(s)")


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

async def seed():
    """Fonction principale de seed – crée toutes les données de test."""
    print("=" * 60)
    print("  CIS – Script de seed (données de test)")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # 1. Unités
            units = await seed_units(session)

            # 2. Utilisateurs
            users = await seed_users(session, units)

            # 3. Catégories de journal
            categories = await seed_journal_categories(session)

            # 4. Compétences (référentiel)
            skills = await seed_skills(session)

            # 5. Bénéficiaires
            beneficiaries = await seed_beneficiaries(session, units, users)

            # 6. Données médicales (chiffrées)
            await seed_medical_data(session, beneficiaries, users)

            # 7. Contacts réseau
            await seed_contacts(session, beneficiaries)

            # 8. Plans d'Accompagnement Individualisé (PAI)
            pais = await seed_pais(session, beneficiaries, users)

            # 9. Objectifs + indicateurs + actions
            await seed_objectives(session, beneficiaries, pais, users)

            # 10. Entrées de journal
            await seed_journal_entries(session, beneficiaries, users, categories)

            # 11. Pointages
            await seed_time_entries(session, beneficiaries)

            # 12. Absences
            await seed_absences(session, beneficiaries, users)

            # 13. Soldes de vacances
            await seed_vacation_balances(session, beneficiaries)

            # 14. Évaluations de compétences
            await seed_beneficiary_skills(session, beneficiaries, skills, users)

            # 15. Notifications
            await seed_notifications(session, users)

            await session.commit()

            print("\n" + "=" * 60)
            print("  Seed terminé avec succès !")
            print("=" * 60)
            print("\nComptes de test :")
            print("  admin@cis.ch      / Admin123!@#     (ADMIN)")
            print("  rua1@cis.ch       / Rua12345!@#     (RUA)")
            print("  rua2@cis.ch       / Rua12345!@#     (RUA)")
            print("  res.bois@cis.ch   / Res12345!@#     (RES, Atelier Bois)")
            print("  res.cuisine@cis.ch/ Res12345!@#     (RES, Atelier Cuisine)")
            print("  msp.bois1@cis.ch  / Msp12345!@#     (MSP, Atelier Bois)")
            print("  msp.bois2@cis.ch  / Msp12345!@#     (MSP, Atelier Bois)")
            print("  msp.cuisine1@cis.ch / Msp12345!@#   (MSP, Atelier Cuisine)")
            print("  msp.bureau1@cis.ch/ Msp12345!@#     (MSP, Atelier Bureautique)")
            print("  consult@cis.ch    / Consult123!@#   (CONSULT)")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERREUR] Seed échoué : {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
