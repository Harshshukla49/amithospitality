"""003_notification_logs_outlet_id - Add outlet_id column for tenant-isolated notification auditing

Revision ID: 8b9c0d1e2f3a
Revises: 7a8b9c0d1e2f
Create Date: 2026-11-10 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = '8b9c0d1e2f3a'
down_revision: Union[str, None] = '7a8b9c0d1e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "notification_logs" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("notification_logs")]
        if "outlet_id" not in columns:
            op.add_column("notification_logs", sa.Column("outlet_id", sa.Integer(), nullable=True))
            try:
                op.create_index("ix_notification_logs_outlet_id", "notification_logs", ["outlet_id"])
            except Exception:
                pass

def downgrade() -> None:
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if "notification_logs" in existing_tables:
        columns = [c["name"] for c in inspector.get_columns("notification_logs")]
        if "outlet_id" in columns:
            try:
                op.drop_index("ix_notification_logs_outlet_id", table_name="notification_logs")
            except Exception:
                pass
            op.drop_column("notification_logs", "outlet_id")
