"""002_notification_logs - Table for Transactional Notification Audit Trail

Revision ID: 7a8b9c0d1e2f
Revises: 266d4294e882
Create Date: 2026-11-10 11:45:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = '7a8b9c0d1e2f'
down_revision: Union[str, None] = '266d4294e882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "notification_logs" not in existing_tables:
        op.create_table(
            "notification_logs",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("entity_type", sa.String(50), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=False, index=True),
            sa.Column("reference_id", sa.String(100), nullable=True, index=True),
            sa.Column("channel", sa.String(20), nullable=False),
            sa.Column("recipient", sa.String(255), nullable=False),
            sa.Column("event_type", sa.String(50), nullable=False),
            sa.Column("idempotency_key", sa.String(255), unique=True, index=True, nullable=False),
            sa.Column("status", sa.String(20), default="SENT"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("environment", sa.String(10), default="DEMO"),
            sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        )

def downgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "notification_logs" in existing_tables:
        op.drop_table("notification_logs")
