"""Phase 20.1 security, currency, and financial integrity upgrades

Revision ID: a1b2c3d4e5f6
Revises: 9c0d1e2f3a4b
Create Date: 2026-11-10 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9c0d1e2f3a4b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. guest_profiles
    with op.batch_alter_table('guest_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(length=10), server_default='INR', nullable=True))
        batch_op.add_column(sa.Column('is_shared_contact', sa.Boolean(), server_default='0', nullable=True))

    # 2. reservation_modification_requests
    with op.batch_alter_table('reservation_modification_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('old_status', sa.String(length=30), nullable=True))

    # 3. notification_logs
    with op.batch_alter_table('notification_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attempts', sa.Integer(), server_default='1', nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('notification_logs', schema=None) as batch_op:
        batch_op.drop_column('attempts')

    with op.batch_alter_table('reservation_modification_requests', schema=None) as batch_op:
        batch_op.drop_column('old_status')

    with op.batch_alter_table('guest_profiles', schema=None) as batch_op:
        batch_op.drop_column('is_shared_contact')
        batch_op.drop_column('currency')
