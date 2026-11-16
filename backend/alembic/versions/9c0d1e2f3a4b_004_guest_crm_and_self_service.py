"""004_guest_crm_and_self_service - Unified Guest CRM, Verifications, and Self-Service Modifications

Revision ID: 9c0d1e2f3a4b
Revises: 8b9c0d1e2f3a
Create Date: 2026-11-10 17:35:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = '9c0d1e2f3a4b'
down_revision: Union[str, None] = '8b9c0d1e2f3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # 1. Create guest_profiles table
    if "guest_profiles" not in existing_tables:
        op.create_table(
            "guest_profiles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("guest_uuid", sa.String(50), nullable=False),
            sa.Column("environment", sa.String(10), server_default="DEMO", nullable=False),
            sa.Column("full_name", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(50), nullable=False),
            sa.Column("phone_normalized", sa.String(50), nullable=False),
            sa.Column("email", sa.String(255), nullable=True),
            sa.Column("email_normalized", sa.String(255), nullable=True),
            sa.Column("preferred_channel", sa.String(20), server_default="SMS", nullable=True),
            sa.Column("dietary_preferences", sa.String(100), server_default="NONE", nullable=True),
            sa.Column("allergies", sa.Text(), nullable=True),
            sa.Column("cuisine_preferences", sa.String(255), nullable=True),
            sa.Column("special_occasions", sa.String(255), nullable=True),
            sa.Column("accessibility_requirements", sa.Text(), nullable=True),
            sa.Column("staff_notes", sa.Text(), nullable=True),
            sa.Column("vip_status", sa.Boolean(), server_default=sa.false(), nullable=True),
            sa.Column("total_visits", sa.Integer(), server_default="1", nullable=True),
            sa.Column("total_spend", sa.Float(), server_default="0.0", nullable=True),
            sa.Column("preferred_outlet_id", sa.Integer(), sa.ForeignKey("outlets.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_guest_profiles_id", "guest_profiles", ["id"])
        op.create_index("ix_guest_profiles_guest_uuid", "guest_profiles", ["guest_uuid"], unique=True)
        op.create_index("ix_guest_profiles_environment", "guest_profiles", ["environment"])
        op.create_index("ix_guest_profiles_full_name", "guest_profiles", ["full_name"])
        op.create_index("ix_guest_profiles_phone", "guest_profiles", ["phone"])
        op.create_index("ix_guest_profiles_phone_normalized", "guest_profiles", ["phone_normalized"])
        op.create_index("ix_guest_profiles_email", "guest_profiles", ["email"])
        op.create_index("ix_guest_profiles_email_normalized", "guest_profiles", ["email_normalized"])
        op.create_index("ix_guest_profiles_vip_status", "guest_profiles", ["vip_status"])
        op.create_index("ix_guest_profiles_preferred_outlet_id", "guest_profiles", ["preferred_outlet_id"])
        op.create_index("ix_guest_phone_env", "guest_profiles", ["phone_normalized", "environment"])
        op.create_index("ix_guest_email_env", "guest_profiles", ["email_normalized", "environment"])

    # 2. Add guest_profile_id to reservation_requests
    if "reservation_requests" in existing_tables:
        res_columns = [c["name"] for c in inspector.get_columns("reservation_requests")]
        if "guest_profile_id" not in res_columns:
            op.add_column("reservation_requests", sa.Column("guest_profile_id", sa.Integer(), nullable=True))
            try:
                op.create_index("ix_reservation_requests_guest_profile_id", "reservation_requests", ["guest_profile_id"])
            except Exception:
                pass

    # 3. Create guest_verifications table
    if "guest_verifications" not in existing_tables:
        op.create_table(
            "guest_verifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reservation_id", sa.Integer(), sa.ForeignKey("reservation_requests.id", ondelete="CASCADE"), nullable=False),
            sa.Column("reference_id", sa.String(50), nullable=False),
            sa.Column("target_type", sa.String(20), nullable=False),
            sa.Column("target_masked", sa.String(255), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False),
            sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
            sa.Column("max_attempts", sa.Integer(), server_default="5", nullable=False),
            sa.Column("is_used", sa.Boolean(), server_default=sa.false(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_guest_verifications_id", "guest_verifications", ["id"])
        op.create_index("ix_guest_verifications_reservation_id", "guest_verifications", ["reservation_id"])
        op.create_index("ix_guest_verifications_reference_id", "guest_verifications", ["reference_id"])
        op.create_index("ix_guest_verifications_is_used", "guest_verifications", ["is_used"])
        op.create_index("ix_guest_verifications_expires_at", "guest_verifications", ["expires_at"])

    # 4. Create guest_access_audits table
    if "guest_access_audits" not in existing_tables:
        op.create_table(
            "guest_access_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reference_id", sa.String(50), nullable=True),
            sa.Column("reservation_id", sa.Integer(), nullable=True),
            sa.Column("action", sa.String(50), nullable=False),
            sa.Column("status", sa.String(20), nullable=False),
            sa.Column("ip_address", sa.String(100), nullable=True),
            sa.Column("user_agent", sa.String(255), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_guest_access_audits_id", "guest_access_audits", ["id"])
        op.create_index("ix_guest_access_audits_reference_id", "guest_access_audits", ["reference_id"])
        op.create_index("ix_guest_access_audits_action", "guest_access_audits", ["action"])

    # 5. Create reservation_modification_requests table
    if "reservation_modification_requests" not in existing_tables:
        op.create_table(
            "reservation_modification_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reservation_id", sa.Integer(), sa.ForeignKey("reservation_requests.id", ondelete="CASCADE"), nullable=False),
            sa.Column("reference_id", sa.String(50), nullable=False),
            sa.Column("requested_by", sa.String(50), server_default="GUEST", nullable=False),
            sa.Column("old_date", sa.String(20), nullable=False),
            sa.Column("new_date", sa.String(20), nullable=False),
            sa.Column("old_time", sa.String(20), nullable=False),
            sa.Column("new_time", sa.String(20), nullable=False),
            sa.Column("old_guest_count", sa.Integer(), nullable=False),
            sa.Column("new_guest_count", sa.Integer(), nullable=False),
            sa.Column("old_special_requests", sa.Text(), nullable=True),
            sa.Column("new_special_requests", sa.Text(), nullable=True),
            sa.Column("status", sa.String(30), server_default="APPLIED", nullable=False),
            sa.Column("review_notes", sa.Text(), nullable=True),
            sa.Column("reviewed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("reviewed_by_name", sa.String(255), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_reservation_modification_requests_id", "reservation_modification_requests", ["id"])
        op.create_index("ix_reservation_modification_requests_reservation_id", "reservation_modification_requests", ["reservation_id"])
        op.create_index("ix_reservation_modification_requests_reference_id", "reservation_modification_requests", ["reference_id"])
        op.create_index("ix_reservation_modification_requests_status", "reservation_modification_requests", ["status"])

def downgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "reservation_modification_requests" in existing_tables:
        op.drop_table("reservation_modification_requests")

    if "guest_access_audits" in existing_tables:
        op.drop_table("guest_access_audits")

    if "guest_verifications" in existing_tables:
        op.drop_table("guest_verifications")

    if "reservation_requests" in existing_tables:
        res_columns = [c["name"] for c in inspector.get_columns("reservation_requests")]
        if "guest_profile_id" in res_columns:
            try:
                op.drop_index("ix_reservation_requests_guest_profile_id", table_name="reservation_requests")
            except Exception:
                pass
            op.drop_column("reservation_requests", "guest_profile_id")

    if "guest_profiles" in existing_tables:
        op.drop_table("guest_profiles")
