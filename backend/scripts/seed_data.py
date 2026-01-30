"""Seed script to generate realistic mockup data for the CIS application.

Run AFTER init_db.py to populate the database with test data.

Usage:
    cd backend
    python scripts/seed_data.py
"""

import asyncio
import random
import sys
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

sys.path.insert(0, ".")

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.beneficiary import Beneficiary, BeneficiaryMedicalData, Contact, RiskBehavior
from app.models.journal import JournalCategory, JournalEntry, JournalEntryCategory
from app.models.objective import Action, Objective, ObjectiveIndicator
from app.models.pai import PAI
from app.models.skill import BeneficiarySkill, Skill
from app.models.time_tracking import Absence, TimeEntry, VacationBalance
from app.models.unit import Unit
from app.models.user import User
from app.utils.security import get_password_hash

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

TODAY = date.today()
NOW = datetime.now(UTC)

USERS_DATA = [
    # (email, first_name, last_name, role, unit_name)
    ("m.rochat@cis.local", "Marc", "Rochat", "RUA", None),
    ("s.muller@cis.local", "Sophie", "Muller", "RES", "Atelier Bois"),
    ("p.favre@cis.local", "Philippe", "Favre", "RES", "Atelier Cuisine"),
    ("l.bonvin@cis.local", "Laurent", "Bonvin", "MSP", "Atelier Bois"),
    ("n.chevalley@cis.local", "Nathalie", "Chevalley", "MSP", "Atelier Metal"),
    ("j.meylan@cis.local", "Jean", "Meylan", "MSP", "Atelier Cuisine"),
    ("c.martin@cis.local", "Claire", "Martin", "CONSULT", None),
]

BENEFICIARIES_DATA = [
    # (first, last, dob, city, postal, phone, ai_number, pension, status, occ_rate, unit_name, msp_email)
    ("David", "Schneider", date(1985, 3, 15), "Lausanne", "1003", "079 123 45 67", "756.1234.5678.90", "half", "active", 60, "Atelier Bois", "l.bonvin@cis.local"),
    ("Marie", "Jolivet", date(1990, 7, 22), "Yverdon-les-Bains", "1400", "078 234 56 78", "756.2345.6789.01", "quarter", "active", 50, "Atelier Bois", "l.bonvin@cis.local"),
    ("Patrick", "Vuilloud", date(1978, 11, 3), "Nyon", "1260", "079 345 67 89", "756.3456.7890.12", "full", "active", 100, "Atelier Metal", "n.chevalley@cis.local"),
    ("Isabelle", "Croisier", date(1992, 1, 28), "Lausanne", "1007", "076 456 78 90", "756.4567.8901.23", "three_quarter", "active", 80, "Atelier Metal", "n.chevalley@cis.local"),
    ("Alain", "Reymond", date(1970, 6, 10), "Morges", "1110", "079 567 89 01", "756.5678.9012.34", "half", "active", 50, "Atelier Cuisine", "j.meylan@cis.local"),
    ("Sandra", "Blanc", date(1988, 9, 5), "Renens", "1020", "078 678 90 12", "756.6789.0123.45", "quarter", "active", 40, "Atelier Cuisine", "j.meylan@cis.local"),
    ("Thomas", "Aubert", date(1982, 4, 18), "Lausanne", "1005", "076 789 01 23", "756.7890.1234.56", "half", "active", 60, "Atelier Bois", "l.bonvin@cis.local"),
    ("Carole", "Menoud", date(1995, 12, 30), "Vevey", "1800", "079 890 12 34", "756.8901.2345.67", "quarter", "active", 50, "Atelier Metal", "n.chevalley@cis.local"),
    ("Nicolas", "Piguet", date(1975, 8, 14), "Echallens", "1040", "078 901 23 45", "756.9012.3456.78", "full", "active", 80, "Atelier Cuisine", "j.meylan@cis.local"),
    ("Laure", "Grandjean", date(1998, 2, 7), "Lausanne", "1006", "076 012 34 56", "756.0123.4567.89", "half", "active", 60, "Atelier Bois", "l.bonvin@cis.local"),
    ("Yves", "Tinguely", date(1980, 5, 25), "Pully", "1009", "079 111 22 33", "756.1111.2222.33", "three_quarter", "paused", 70, "Atelier Metal", "n.chevalley@cis.local"),
    ("Sylvie", "Baumgartner", date(1986, 10, 12), "Prilly", "1008", "078 222 33 44", "756.2222.3333.44", "half", "exited", 50, "Atelier Cuisine", "j.meylan@cis.local"),
]

CONTACTS_DATA = [
    # (contact_type, name, organization, phone, is_emergency)
    ("emergency", "Mireille {last}", None, "079 999 {i:02d} {i:02d}", True),
    ("doctor", "Dr. Pierre Lugon", "Cabinet medical du Flon", "021 312 45 67", False),
    ("psychologist", "Dr. Anne Rossier", "Centre de sante mentale", "021 314 78 90", False),
    ("ai_referent", "Catherine Dubois", "Office AI Vaud", "021 345 67 89", False),
]

SKILLS_DATA = [
    ("Ponctualite", "comportement", "Respect des horaires de travail"),
    ("Travail en equipe", "social", "Capacite a collaborer avec les collegues"),
    ("Autonomie", "competence", "Capacite a travailler de maniere independante"),
    ("Qualite du travail", "technique", "Precision et soin dans l'execution des taches"),
    ("Respect des consignes", "comportement", "Suivi des instructions donnees"),
    ("Communication", "social", "Capacite a s'exprimer clairement"),
    ("Gestion du stress", "comportement", "Capacite a gerer les situations stressantes"),
    ("Initiative", "competence", "Capacite a proposer des solutions"),
    ("Hygiene et securite", "technique", "Respect des regles de securite au travail"),
    ("Endurance physique", "physique", "Capacite a maintenir un effort physique prolonge"),
]

PAI_STRENGTHS = [
    "Tres motive et ponctuel. Montre un reel interet pour les activites proposees.",
    "Bonne capacite d'ecoute et de communication. S'integre facilement dans le groupe.",
    "Grande minutie dans le travail. Souci du detail remarquable.",
    "Bon esprit d'equipe, aide volontiers ses collegues. Attitude positive.",
    "Creativite et bonne dexterite manuelle. Apprend rapidement les nouvelles techniques.",
    "Perseverant et courageux face aux difficultes. Ne se decourage pas facilement.",
    "Autonome dans les taches connues. Respecte bien les consignes de securite.",
    "Excellente memoire de travail. Retient bien les procedures apprises.",
]

PAI_DIFFICULTIES = [
    "Difficultes de concentration sur les taches longues. Fatigue rapide l'apres-midi.",
    "Anxiete sociale qui complique les interactions en grand groupe.",
    "Douleurs chroniques au dos limitant les efforts physiques prolonges.",
    "Difficultes a gerer les imprevu. Besoin de routine et de structure.",
    "Faible confiance en soi, tendance a se sous-estimer.",
    "Problemes de gestion du temps et d'organisation personnelle.",
    "Lenteur d'execution due aux effets secondaires de la medication.",
    "Difficultes avec les taches impliquant de la lecture ou de l'ecriture.",
]

PAI_WISHES = [
    "Souhaite retrouver un emploi dans le domaine de la menuiserie.",
    "Aimerait ameliorer ses competences informatiques pour envisager un travail de bureau.",
    "Souhaite gagner en autonomie pour pouvoir vivre de maniere plus independante.",
    "Desire developper ses competences sociales pour faciliter la reinsertion.",
    "Objectif a terme: travailler a temps partiel dans la restauration.",
    "Souhaite obtenir une attestation de competences en cuisine.",
    "Aimerait pouvoir augmenter progressivement son taux d'occupation.",
    "Desire retrouver confiance en ses capacites professionnelles.",
]

OBJECTIVE_TEMPLATES = [
    # (title, description, type, term, priority)
    ("Ameliorer la ponctualite", "Arriver a l'heure tous les jours pendant 3 mois consecutifs", "behavioral", "short", "high"),
    ("Developper l'autonomie au poste de travail", "Realiser les taches courantes sans aide dans un delai de 6 mois", "pai", "medium", "high"),
    ("Gerer les conflits de maniere constructive", "Apprendre a exprimer ses desaccords calmement et a chercher des solutions", "behavioral", "medium", "medium"),
    ("Augmenter le taux d'occupation", "Passer de 50% a 70% d'ici la fin de l'annee", "pai", "long", "medium"),
    ("Maitriser les outils de l'atelier", "Connaitre et utiliser correctement les 5 machines principales", "operational", "short", "high"),
    ("Ameliorer la gestion du stress", "Mettre en place des strategies de gestion du stress au quotidien", "behavioral", "medium", "medium"),
    ("Respecter les consignes de securite", "Appliquer systematiquement les protocoles de securite de l'atelier", "operational", "short", "high"),
    ("Developper les competences en communication", "Participer activement aux reunions d'equipe et exprimer ses idees", "pai", "medium", "low"),
    ("Ameliorer l'endurance au travail", "Maintenir un rythme de travail regulier sur une journee complete", "operational", "long", "medium"),
    ("Preparer la reinsertion professionnelle", "Effectuer 2 stages d'observation en milieu ordinaire", "pai", "long", "high"),
]

INDICATOR_TEMPLATES = [
    "Aucun retard enregistre sur le mois",
    "Tache realisee de maniere autonome dans les delais",
    "Aucun incident de conflit signale",
    "Taux d'occupation augmente selon planning",
    "Machine utilisee correctement sans assistance",
    "Strategies de gestion du stress identifiees et pratiquees",
    "Aucun incident de securite sur la periode",
    "Participation active lors des reunions",
    "Journee complete de travail accomplie regulierement",
    "Stage d'observation effectue avec rapport positif",
]

ACTION_TEMPLATES = [
    # (description, responsible)
    ("Mettre en place un rappel quotidien et discuter des obstacles", "msp"),
    ("Definir un plan de progression par etapes avec validation", "msp"),
    ("Participer a un atelier de gestion des emotions", "beneficiary"),
    ("Etablir un planning progressif avec le medecin traitant", "other"),
    ("Suivre la formation securite de l'atelier", "beneficiary"),
    ("Pratiquer des exercices de respiration chaque jour", "beneficiary"),
    ("Organiser une visite d'entreprise avec l'office AI", "msp"),
    ("Tenir un journal de bord des taches accomplies", "beneficiary"),
]

JOURNAL_ENTRIES_DATA = [
    # (title, content, category_name, visibility)
    (
        "Bonne journee en atelier",
        "A bien travaille aujourd'hui, a termine sa piece en avance. Motivation visible, a aide un collegue en difficulte. Continue ses progres en autonomie.",
        "progress",
        "unit",
    ),
    (
        "Absence non justifiee",
        "Ne s'est pas presente ce matin sans prevenir. Contact telephonique dans l'apres-midi : probleme de transport. Rappel des procedures d'annonce d'absence.",
        "behavior",
        "team",
    ),
    (
        "Entretien de suivi mensuel",
        "Entretien realise ce jour. Discussion sur les objectifs en cours. Se dit satisfait de sa progression mais exprime des inquietudes concernant l'augmentation du taux. Prochaine evaluation dans 4 semaines.",
        "interview",
        "unit",
    ),
    (
        "Fatigue importante observee",
        "Semble tres fatigue depuis plusieurs jours. A mentionne des troubles du sommeil. Suggestion de consulter le medecin traitant. A surveiller dans les prochains jours.",
        "health",
        "team",
    ),
    (
        "Conflit avec un collegue",
        "Altercation verbale avec T. Aubert a la pause de 10h. Mediation effectuee. Les deux parties ont pu s'exprimer. Situation apaisee en fin de matinee.",
        "conflict",
        "unit",
    ),
    (
        "Progres en formation",
        "A reussi l'evaluation pratique sur la scie a ruban. Bonne maitrise des consignes de securite. Peut desormais utiliser la machine de maniere autonome.",
        "skills",
        "unit",
    ),
    (
        "Difficultes personnelles",
        "A confie traverser une periode difficile sur le plan familial. Propose un entretien plus approfondi la semaine prochaine. Reste professionnel malgre la situation.",
        "private",
        "team",
    ),
    (
        "Incident en atelier",
        "Coupure legere au doigt lors de l'utilisation du cutter. Premiers soins administres. Rappel des consignes de securite. Formulaire d'incident rempli.",
        "incident",
        "unit",
    ),
    (
        "Echange avec l'atelier Metal",
        "A participe a une journee decouverte a l'atelier Metal. Retour positif, montre de l'interet pour la soudure. A discuter lors du prochain bilan PAI.",
        "inter_unit",
        "inter_unit",
    ),
    (
        "Consultation psychologique",
        "Retour de consultation avec Dr. Rossier. Ajustement du traitement prevu. Se dit plus serein depuis le debut du suivi. Prochaine consultation dans 2 semaines.",
        "health",
        "team",
    ),
    (
        "Attitude positive remarquee",
        "Tres bonne semaine dans l'ensemble. A pris des initiatives pour ranger l'atelier. Felicitations transmises devant le groupe.",
        "progress",
        "unit",
    ),
    (
        "Objectif de ponctualite atteint",
        "Aucun retard enregistre ce mois-ci. Objectif de ponctualite sur 3 mois quasiment atteint (2 mois completes). Encouragements donnes.",
        "progress",
        "unit",
    ),
]

RISK_BEHAVIORS_DATA = [
    # (risk_type, description, severity, preventive_measures)
    ("Agressivite verbale", "Episodes d'irritabilite pouvant mener a des propos agressifs envers les collegues, principalement en fin de journee lorsque la fatigue s'installe.", "medium", "Proposer des pauses regulieres. Intervenir des les premiers signes d'agitation. Entretien de debriefing si incident."),
    ("Automutilation", "Antecedents d'automutilation en periode de crise. Actuellement stabilise avec suivi psychologique.", "high", "Suivi psychologique regulier. Alerter immediatement le RES en cas de signes de detresse. Numeros d'urgence affiches."),
    ("Consommation substances", "Consommation d'alcool occasionnelle pouvant impacter la presence et la qualite du travail.", "medium", "Dialogue ouvert sur le sujet. Orientation vers un suivi specialise si aggravation. Surveillance discrete de l'etat a l'arrivee."),
    ("Ideation suicidaire", "Pensees suicidaires exprimees par le passe. Actuellement sous traitement et suivi regulier.", "critical", "Suivi psychiatrique hebdomadaire. Plan de securite etabli. Numeros d'urgence transmis. Ne jamais laisser seul en cas de crise."),
    ("Fugue", "Tendance a quitter l'atelier sans prevenir en cas de frustration ou de conflit.", "low", "Dialogue sur les mecanismes de fuite. Proposer un espace de retrait calme. Prevenir le MSP referent immediatement."),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def random_date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))


def random_past_date(days_back: int = 90) -> date:
    return TODAY - timedelta(days=random.randint(1, days_back))


def random_past_datetime(days_back: int = 90) -> datetime:
    d = random_past_date(days_back)
    h = random.randint(8, 16)
    m = random.choice([0, 15, 30, 45])
    return datetime(d.year, d.month, d.day, h, m, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

async def seed():
    async with AsyncSessionLocal() as session:
        # ------------------------------------------------------------------
        # 1. Fetch existing units & admin
        # ------------------------------------------------------------------
        result = await session.execute(select(Unit))
        units = {u.name: u for u in result.scalars().all()}

        result = await session.execute(select(User).where(User.email == "admin@cis.local"))
        admin = result.scalar_one_or_none()
        if not admin:
            print("ERROR: admin user not found. Run init_db.py first.")
            return

        # Fetch journal categories
        result = await session.execute(select(JournalCategory))
        categories = {c.name: c for c in result.scalars().all()}

        print(f"Found {len(units)} units, {len(categories)} journal categories.")

        # ------------------------------------------------------------------
        # 2. Create users
        # ------------------------------------------------------------------
        password_hash = get_password_hash("User1234!@#$")
        users: dict[str, User] = {"admin@cis.local": admin}

        for email, first, last, role, unit_name in USERS_DATA:
            user = User(
                email=email,
                hashed_password=password_hash,
                first_name=first,
                last_name=last,
                role=role,
                unit_id=units[unit_name].id if unit_name else None,
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            users[email] = user

        await session.flush()
        print(f"Created {len(USERS_DATA)} users.")

        # ------------------------------------------------------------------
        # 3. Create beneficiaries
        # ------------------------------------------------------------------
        beneficiaries: list[Beneficiary] = []
        for _i, (first, last, dob, city, postal, phone, ai_num, pension, status, occ_rate, unit_name, msp_email) in enumerate(BENEFICIARIES_DATA):
            entry_date = TODAY - timedelta(days=random.randint(90, 730))
            exit_date = (TODAY - timedelta(days=random.randint(1, 30))) if status == "exited" else None

            b = Beneficiary(
                first_name=first,
                last_name=last,
                date_of_birth=dob,
                address=f"Rue {random.choice(['du Lac', 'de la Gare', 'du Marche', 'des Alpes', 'du Mont-Blanc', 'de Lausanne', 'du Simplon', 'de Bourg'])} {random.randint(1, 45)}",
                postal_code=postal,
                city=city,
                phone=phone,
                email=f"{first.lower()}.{last.lower()}@email.ch",
                language="fr",
                ai_number=ai_num,
                pension_type=pension,
                entry_date=entry_date,
                exit_date=exit_date,
                status=status,
                occupation_rate=Decimal(str(occ_rate)),
                unit_id=units[unit_name].id,
                referent_id=users[msp_email].id,
                created_by=admin.id,
            )
            session.add(b)
            beneficiaries.append(b)

        await session.flush()
        print(f"Created {len(beneficiaries)} beneficiaries.")

        # ------------------------------------------------------------------
        # 4. Create contacts (2-3 per beneficiary)
        # ------------------------------------------------------------------
        contact_count = 0
        for b in beneficiaries:
            num_contacts = random.randint(2, 3)
            selected = random.sample(CONTACTS_DATA, num_contacts)
            for ct, name_tpl, org, phone_tpl, is_emg in selected:
                c = Contact(
                    beneficiary_id=b.id,
                    contact_type=ct,
                    name=name_tpl.format(last=b.last_name, i=b.id),
                    organization=org,
                    phone=phone_tpl.format(i=b.id) if phone_tpl else None,
                    is_emergency_contact=is_emg,
                )
                session.add(c)
                contact_count += 1

        await session.flush()
        print(f"Created {contact_count} contacts.")

        # ------------------------------------------------------------------
        # 5. Create medical data (1 per beneficiary)
        # ------------------------------------------------------------------
        medications = [
            "Sertraline 50mg 1x/jour", "Ritaline 10mg 2x/jour",
            "Lyrica 75mg matin et soir", "Temesta 1mg si besoin (max 2/jour)",
            None, None, "Dafalgan 1g si douleurs (max 4/jour)",
            "Cipralex 10mg 1x/jour", None, "Quetiapine 25mg au coucher",
        ]
        for i, b in enumerate(beneficiaries):
            med = BeneficiaryMedicalData(
                beneficiary_id=b.id,
                medication=medications[i % len(medications)],
                restrictions="Pas de port de charges lourdes (>10kg)" if i % 4 == 0 else None,
                allergies="Penicilline" if i % 5 == 0 else None,
                medical_notes="Suivi psychiatrique regulier" if i % 3 == 0 else None,
                updated_by=admin.id,
            )
            session.add(med)

        await session.flush()
        print("Created medical data.")

        # ------------------------------------------------------------------
        # 6. Create skills reference
        # ------------------------------------------------------------------
        skills: list[Skill] = []
        for idx, (name, cat, desc) in enumerate(SKILLS_DATA):
            s = Skill(name=name, category=cat, description=desc, is_active=True, sort_order=idx + 1)
            session.add(s)
            skills.append(s)

        await session.flush()
        print(f"Created {len(skills)} skills.")

        # ------------------------------------------------------------------
        # 7. Create PAIs (1 per active beneficiary)
        # ------------------------------------------------------------------
        pais: dict[int, PAI] = {}
        active_beneficiaries = [b for b in beneficiaries if b.status == "active"]
        for i, b in enumerate(active_beneficiaries):
            status = "active" if i < 8 else "draft"
            valid_from = b.entry_date + timedelta(days=random.randint(14, 60))
            valid_to = valid_from + timedelta(days=365)

            pai = PAI(
                beneficiary_id=b.id,
                status=status,
                valid_from=valid_from,
                valid_to=valid_to,
                strengths=random.choice(PAI_STRENGTHS),
                difficulties=random.choice(PAI_DIFFICULTIES),
                beneficiary_wishes=random.choice(PAI_WISHES),
                created_by=b.referent_id,
            )
            session.add(pai)
            pais[b.id] = pai

        await session.flush()
        print(f"Created {len(pais)} PAIs.")

        # ------------------------------------------------------------------
        # 8. Create objectives (2-4 per PAI)
        # ------------------------------------------------------------------
        objective_count = 0
        all_objectives: list[Objective] = []
        statuses = ["pending", "in_progress", "achieved", "in_progress", "pending"]

        for b_id, pai in pais.items():
            b = next(x for x in beneficiaries if x.id == b_id)
            num_obj = random.randint(2, 4)
            selected_obj = random.sample(OBJECTIVE_TEMPLATES, num_obj)

            for j, (title, desc, obj_type, term, priority) in enumerate(selected_obj):
                obj_status = statuses[j % len(statuses)]
                progress = {"pending": 0, "in_progress": random.randint(20, 70), "achieved": 100, "abandoned": 0}[obj_status]

                # Some overdue
                if obj_status in ("pending", "in_progress") and random.random() < 0.3:
                    due = TODAY - timedelta(days=random.randint(1, 30))
                else:
                    due = TODAY + timedelta(days=random.randint(30, 180))

                obj = Objective(
                    pai_id=pai.id,
                    beneficiary_id=b.id,
                    title=title,
                    description=desc,
                    objective_type=obj_type,
                    term=term,
                    priority=priority,
                    status=obj_status,
                    progress=progress,
                    due_date=due,
                    created_by=b.referent_id,
                )
                session.add(obj)
                all_objectives.append(obj)
                objective_count += 1

        await session.flush()
        print(f"Created {objective_count} objectives.")

        # ------------------------------------------------------------------
        # 9. Create indicators and actions for objectives
        # ------------------------------------------------------------------
        ind_count = 0
        act_count = 0
        for obj in all_objectives:
            # 1-2 indicators
            num_ind = random.randint(1, 2)
            for _ in range(num_ind):
                achieved = obj.status == "achieved" or (obj.status == "in_progress" and random.random() < 0.3)
                ind = ObjectiveIndicator(
                    objective_id=obj.id,
                    description=random.choice(INDICATOR_TEMPLATES),
                    is_achieved=achieved,
                    achieved_at=random_past_datetime(60) if achieved else None,
                )
                session.add(ind)
                ind_count += 1

            # 1-2 actions
            num_act = random.randint(1, 2)
            for _ in range(num_act):
                desc, responsible = random.choice(ACTION_TEMPLATES)
                act_status = "done" if obj.status == "achieved" else random.choice(["pending", "pending", "done"])
                act = Action(
                    objective_id=obj.id,
                    description=desc,
                    responsible=responsible,
                    due_date=obj.due_date - timedelta(days=random.randint(0, 30)) if obj.due_date else None,
                    status=act_status,
                )
                session.add(act)
                act_count += 1

        await session.flush()
        print(f"Created {ind_count} indicators and {act_count} actions.")

        # ------------------------------------------------------------------
        # 10. Create journal entries (3-5 per beneficiary)
        # ------------------------------------------------------------------
        je_count = 0
        # Collect MSP user IDs for authorship
        msp_ids = [u.id for u in users.values() if u.role in ("MSP", "RES")]

        for b in beneficiaries:
            num_entries = random.randint(3, 5)
            selected_entries = random.sample(JOURNAL_ENTRIES_DATA, num_entries)

            for title, content, cat_name, visibility in selected_entries:
                entry_date = random_past_datetime(90)
                je = JournalEntry(
                    beneficiary_id=b.id,
                    author_id=b.referent_id or random.choice(msp_ids),
                    title=title,
                    content=content,
                    entry_date=entry_date,
                    visibility=visibility,
                )
                session.add(je)
                await session.flush()

                # Link category
                if cat_name in categories:
                    jec = JournalEntryCategory(
                        journal_entry_id=je.id,
                        category_id=categories[cat_name].id,
                    )
                    session.add(jec)

                je_count += 1

        await session.flush()
        print(f"Created {je_count} journal entries.")

        # ------------------------------------------------------------------
        # 11. Create time entries (last 30 working days for active beneficiaries)
        # ------------------------------------------------------------------
        te_count = 0
        for b in active_beneficiaries:
            # Generate working days over last 30 calendar days
            for day_offset in range(30):
                d = TODAY - timedelta(days=day_offset)
                if d.weekday() >= 5:  # skip weekends
                    continue
                # ~80% attendance
                if random.random() < 0.2:
                    continue

                hour_in = random.choice([7, 8, 8, 8, 9])
                min_in = random.choice([0, 15, 30])
                hour_out = hour_in + random.randint(4, 8)
                hour_out = min(hour_out, 17)
                min_out = random.choice([0, 15, 30, 45])

                entry_type = "training" if random.random() < 0.1 else "work"
                hours = round((hour_out - hour_in) + (min_out - min_in) / 60, 2)

                te = TimeEntry(
                    beneficiary_id=b.id,
                    entry_date=d,
                    time_in=time(hour_in, min_in),
                    time_out=time(hour_out, min_out),
                    entry_type=entry_type,
                    hours_worked=Decimal(str(hours)),
                )
                session.add(te)
                te_count += 1

        await session.flush()
        print(f"Created {te_count} time entries.")

        # ------------------------------------------------------------------
        # 12. Create absences
        # ------------------------------------------------------------------
        abs_count = 0
        absence_configs = [
            ("sick", 3, True),
            ("sick", 1, False),
            ("vacation", 5, True),
            ("vacation", 3, True),
            ("accident", 10, True),
            ("unauthorized", 1, False),
            ("sick", 2, True),
            ("vacation", 2, False),
        ]
        # Distribute absences across some beneficiaries
        for i, (abs_type, duration, validated) in enumerate(absence_configs):
            b = active_beneficiaries[i % len(active_beneficiaries)]
            start = random_past_date(60)
            end = start + timedelta(days=duration - 1)

            validator = random.choice(list(users.values()))
            absence = Absence(
                beneficiary_id=b.id,
                absence_type=abs_type,
                start_date=start,
                end_date=end,
                validated_by=validator.id if validated else None,
                validated_at=random_past_datetime(30) if validated else None,
                notes=f"Absence {abs_type} de {duration} jour(s)" if random.random() < 0.5 else None,
            )
            session.add(absence)
            abs_count += 1

        await session.flush()
        print(f"Created {abs_count} absences.")

        # ------------------------------------------------------------------
        # 13. Create vacation balances (current year)
        # ------------------------------------------------------------------
        vb_count = 0
        current_year = TODAY.year
        for b in beneficiaries:
            entitled = Decimal("25.00")
            taken = Decimal(str(random.randint(0, 15)))
            vb = VacationBalance(
                beneficiary_id=b.id,
                year=current_year,
                entitled_days=entitled,
                taken_days=taken,
            )
            session.add(vb)
            vb_count += 1

        await session.flush()
        print(f"Created {vb_count} vacation balances.")

        # ------------------------------------------------------------------
        # 14. Create skill evaluations
        # ------------------------------------------------------------------
        eval_count = 0
        levels = ["not_acquired", "in_progress", "acquired", "mastered"]
        for b in beneficiaries:
            # Evaluate 6-10 skills per beneficiary
            num_skills = random.randint(6, min(10, len(skills)))
            selected_skills = random.sample(skills, num_skills)
            for s in selected_skills:
                bs = BeneficiarySkill(
                    beneficiary_id=b.id,
                    skill_id=s.id,
                    level=random.choice(levels),
                    evaluation_date=random_past_date(90),
                    evaluated_by=b.referent_id,
                    comments=None if random.random() < 0.6 else "En progression, a revaluer le mois prochain.",
                )
                session.add(bs)
                eval_count += 1

        await session.flush()
        print(f"Created {eval_count} skill evaluations.")

        # ------------------------------------------------------------------
        # 15. Create risk behaviors (on 3-4 beneficiaries)
        # ------------------------------------------------------------------
        rb_count = 0
        risk_beneficiaries = random.sample(active_beneficiaries, min(4, len(active_beneficiaries)))
        for _i, b in enumerate(risk_beneficiaries):
            # 1-2 risk behaviors per selected beneficiary
            num_risks = random.randint(1, 2)
            selected_risks = random.sample(RISK_BEHAVIORS_DATA, num_risks)
            for risk_type, desc, severity, measures in selected_risks:
                rb = RiskBehavior(
                    beneficiary_id=b.id,
                    risk_type=risk_type,
                    description=desc,
                    severity=severity,
                    preventive_measures=measures,
                    reported_date=random_past_date(120),
                    reported_by=b.referent_id,
                    is_active=True,
                )
                session.add(rb)
                rb_count += 1

        await session.flush()
        print(f"Created {rb_count} risk behaviors.")

        # ------------------------------------------------------------------
        # Commit everything
        # ------------------------------------------------------------------
        await session.commit()
        print("\n--- Seed completed successfully! ---")
        print(f"Users: {len(USERS_DATA) + 1} (including admin)")
        print(f"Beneficiaries: {len(beneficiaries)}")
        print("Login with any user: email / User1234!@#$")
        print("Admin login: admin@cis.local / Admin123!@#$")


if __name__ == "__main__":
    asyncio.run(seed())
