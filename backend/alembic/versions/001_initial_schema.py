"""Initial schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-01-28
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === Units ===
    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # === Users ===
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="MSP"),
        sa.Column("unit_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_unit_id", "users", ["unit_id"])

    # === Contacts (created before beneficiaries due to guardian FK) ===
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=True),
        sa.Column("contact_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("organization", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "is_emergency_contact",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contacts_beneficiary_id", "contacts", ["beneficiary_id"])
    op.create_index("ix_contacts_contact_type", "contacts", ["contact_type"])

    # === Beneficiaries ===
    op.create_table(
        "beneficiaries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="fr"),
        sa.Column("ai_number", sa.String(50), nullable=True),
        sa.Column("pension_type", sa.String(20), nullable=True),
        sa.Column("guardianship_status", sa.String(50), nullable=True),
        sa.Column("guardian_contact_id", sa.Integer(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("exit_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("contract_type", sa.String(50), nullable=True),
        sa.Column("occupation_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("salary", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit_id", sa.Integer(), nullable=True),
        sa.Column("referent_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.ForeignKeyConstraint(["referent_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["guardian_contact_id"], ["contacts.id"], use_alter=True
        ),
    )
    op.create_index("ix_beneficiaries_last_name", "beneficiaries", ["last_name"])
    op.create_index("ix_beneficiaries_status", "beneficiaries", ["status"])
    op.create_index("ix_beneficiaries_unit_id", "beneficiaries", ["unit_id"])
    op.create_index("ix_beneficiaries_referent_id", "beneficiaries", ["referent_id"])

    # Add FK from contacts to beneficiaries
    op.create_foreign_key(
        "fk_contacts_beneficiary_id",
        "contacts",
        "beneficiaries",
        ["beneficiary_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # === Beneficiary Medical Data ===
    op.create_table(
        "beneficiary_medical_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("medication", sa.Text(), nullable=True),
        sa.Column("restrictions", sa.Text(), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.UniqueConstraint("beneficiary_id"),
    )

    # === Risk Behaviors ===
    op.create_table(
        "risk_behaviors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("risk_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("preventive_measures", sa.Text(), nullable=True),
        sa.Column("reported_date", sa.Date(), nullable=False),
        sa.Column("reported_by", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["reported_by"], ["users.id"]),
    )
    op.create_index(
        "ix_risk_behaviors_beneficiary_id", "risk_behaviors", ["beneficiary_id"]
    )
    op.create_index("ix_risk_behaviors_severity", "risk_behaviors", ["severity"])
    op.create_index("ix_risk_behaviors_is_active", "risk_behaviors", ["is_active"])

    # === PAIs ===
    op.create_table(
        "pais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("difficulties", sa.Text(), nullable=True),
        sa.Column("beneficiary_wishes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_index("ix_pais_beneficiary_id", "pais", ["beneficiary_id"])
    op.create_index("ix_pais_status", "pais", ["status"])

    # === Objectives ===
    op.create_table(
        "objectives",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pai_id", sa.Integer(), nullable=True),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("objective_type", sa.String(30), nullable=False),
        sa.Column("term", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(10), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("reminder_frequency", sa.String(20), nullable=True),
        sa.Column("last_reminder_sent", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["pai_id"], ["pais.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_index("ix_objectives_pai_id", "objectives", ["pai_id"])
    op.create_index("ix_objectives_beneficiary_id", "objectives", ["beneficiary_id"])
    op.create_index("ix_objectives_status", "objectives", ["status"])
    op.create_index("ix_objectives_due_date", "objectives", ["due_date"])

    # === Objective Indicators ===
    op.create_table(
        "objective_indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("objective_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column(
            "is_achieved", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("achieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["objective_id"], ["objectives.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_objective_indicators_objective_id",
        "objective_indicators",
        ["objective_id"],
    )

    # === Actions ===
    op.create_table(
        "actions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("objective_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("responsible", sa.String(50), nullable=True),
        sa.Column("responsible_name", sa.String(100), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["objective_id"], ["objectives.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_actions_objective_id", "actions", ["objective_id"])
    op.create_index("ix_actions_status", "actions", ["status"])

    # === Journal Categories ===
    op.create_table(
        "journal_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # === Journal Entries ===
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "entry_date",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="unit"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
    )
    op.create_index(
        "ix_journal_entries_beneficiary_id", "journal_entries", ["beneficiary_id"]
    )
    op.create_index("ix_journal_entries_author_id", "journal_entries", ["author_id"])
    op.create_index(
        "ix_journal_entries_entry_date", "journal_entries", ["entry_date"]
    )

    # === Journal Entry Categories (M2M) ===
    op.create_table(
        "journal_entry_categories",
        sa.Column("journal_entry_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("journal_entry_id", "category_id"),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["category_id"], ["journal_categories.id"]),
    )
    op.create_index(
        "ix_journal_entry_categories_category_id",
        "journal_entry_categories",
        ["category_id"],
    )

    # === Journal Entry Tags ===
    op.create_table(
        "journal_entry_tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_journal_entry_tags_journal_entry_id",
        "journal_entry_tags",
        ["journal_entry_id"],
    )
    op.create_index("ix_journal_entry_tags_tag", "journal_entry_tags", ["tag"])

    # === Documents ===
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("document_date", sa.Date(), nullable=True),
        sa.Column(
            "confidentiality",
            sa.String(20),
            nullable=False,
            server_default="standard",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("previous_version_id", sa.Integer(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["previous_version_id"], ["documents.id"]),
    )
    op.create_index("ix_documents_beneficiary_id", "documents", ["beneficiary_id"])
    op.create_index("ix_documents_document_type", "documents", ["document_type"])
    op.create_index("ix_documents_uploaded_at", "documents", ["uploaded_at"])

    # === Skills ===
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )

    # === Beneficiary Skills ===
    op.create_table(
        "beneficiary_skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("evaluation_date", sa.Date(), nullable=False),
        sa.Column("evaluated_by", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.ForeignKeyConstraint(["evaluated_by"], ["users.id"]),
    )
    op.create_index(
        "ix_beneficiary_skills_beneficiary_id",
        "beneficiary_skills",
        ["beneficiary_id"],
    )

    # === Trainings ===
    op.create_table(
        "trainings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("training_date", sa.Date(), nullable=False),
        sa.Column("duration_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("trainer", sa.String(200), nullable=True),
        sa.Column("certificate_document_id", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["certificate_document_id"], ["documents.id"]),
    )
    op.create_index("ix_trainings_beneficiary_id", "trainings", ["beneficiary_id"])

    # === Time Entries ===
    op.create_table(
        "time_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("time_in", sa.Time(), nullable=True),
        sa.Column("time_out", sa.Time(), nullable=True),
        sa.Column(
            "entry_type", sa.String(20), nullable=False, server_default="work"
        ),
        sa.Column("hours_worked", sa.Numeric(4, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_time_entries_beneficiary_id", "time_entries", ["beneficiary_id"]
    )
    op.create_index("ix_time_entries_entry_date", "time_entries", ["entry_date"])

    # === Absences ===
    op.create_table(
        "absences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("absence_type", sa.String(30), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("justification_document_id", sa.Integer(), nullable=True),
        sa.Column("validated_by", sa.Integer(), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["justification_document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["validated_by"], ["users.id"]),
    )
    op.create_index("ix_absences_beneficiary_id", "absences", ["beneficiary_id"])
    op.create_index("ix_absences_absence_type", "absences", ["absence_type"])
    op.create_index("ix_absences_start_date", "absences", ["start_date"])

    # === Vacation Balances ===
    op.create_table(
        "vacation_balances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("beneficiary_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("entitled_days", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "taken_days", sa.Numeric(5, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["beneficiary_id"], ["beneficiaries.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_vacation_balances_beneficiary_id",
        "vacation_balances",
        ["beneficiary_id"],
    )

    # === Audit Logs ===
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("old_values", postgresql.JSONB(), nullable=True),
        sa.Column("new_values", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # === Notifications ===
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column(
            "is_read", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("vacation_balances")
    op.drop_table("absences")
    op.drop_table("time_entries")
    op.drop_table("trainings")
    op.drop_table("beneficiary_skills")
    op.drop_table("skills")
    op.drop_table("documents")
    op.drop_table("journal_entry_tags")
    op.drop_table("journal_entry_categories")
    op.drop_table("journal_entries")
    op.drop_table("journal_categories")
    op.drop_table("actions")
    op.drop_table("objective_indicators")
    op.drop_table("objectives")
    op.drop_table("pais")
    op.drop_table("risk_behaviors")
    op.drop_table("beneficiary_medical_data")
    op.drop_table("beneficiaries")
    op.drop_table("contacts")
    op.drop_table("users")
    op.drop_table("units")
