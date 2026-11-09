"""001_initial_schema - Comprehensive Baseline Migration for Amit AI Concierge

Revision ID: 266d4294e882
Revises: 
Create Date: 2026-11-08 18:24:34.471243

Comprehensive baseline containing all 20 core tables + pgvector extension support.
Designed to succeed idempotently against both clean PostgreSQL instances and local SQLite runtimes.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

# revision identifiers, used by Alembic.
revision: str = '266d4294e882'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # Enable pgvector on PostgreSQL
    if is_postgres:
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector;"))

    # Vector column type resolution
    vector_type = Vector(256) if Vector is not None else sa.Text()

    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='STAFF'),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. revoked_tokens
    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=255), nullable=False),
        sa.Column('token_type', sa.String(length=50), nullable=False, server_default='refresh'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=False),
        sa.Column('revocation_reason', sa.String(length=255), nullable=False, server_default='ROTATED'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_revoked_tokens_user_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_revoked_tokens_id'), 'revoked_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_revoked_tokens_jti'), 'revoked_tokens', ['jti'], unique=True)
    op.create_index(op.f('ix_revoked_tokens_user_id'), 'revoked_tokens', ['user_id'], unique=False)

    # 3. restaurants
    op.create_table(
        'restaurants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True, server_default='New Delhi'),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_restaurants_id'), 'restaurants', ['id'], unique=False)
    op.create_index(op.f('ix_restaurants_slug'), 'restaurants', ['slug'], unique=True)

    # 4. outlets
    op.create_table(
        'outlets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('outlet_type', sa.String(length=100), nullable=False),
        sa.Column('cuisine_type', sa.String(length=255), nullable=False),
        sa.Column('opening_time', sa.String(length=20), nullable=True, server_default='17:30'),
        sa.Column('closing_time', sa.String(length=20), nullable=True, server_default='01:30'),
        sa.Column('dress_code', sa.String(length=255), nullable=True, server_default='Smart Casual'),
        sa.Column('seating_capacity', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_popular', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], name='fk_outlets_restaurant_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_outlets_id'), 'outlets', ['id'], unique=False)
    op.create_index(op.f('ix_outlets_slug'), 'outlets', ['slug'], unique=True)

    # 5. menu_categories
    op.create_table(
        'menu_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('outlet_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=10), nullable=True, server_default='DEMO'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_menu_categories_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_menu_categories_id'), 'menu_categories', ['id'], unique=False)
    op.create_index(op.f('ix_menu_categories_environment'), 'menu_categories', ['environment'], unique=False)

    # 6. menu_items
    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('outlet_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=10), nullable=True, server_default='DEMO'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True, server_default='INR'),
        sa.Column('dietary_flags', sa.String(length=255), nullable=True, server_default='VEG'),
        sa.Column('is_available', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('is_signature', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], name='fk_menu_items_category_id'),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_menu_items_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_menu_items_id'), 'menu_items', ['id'], unique=False)
    op.create_index(op.f('ix_menu_items_outlet_id'), 'menu_items', ['outlet_id'], unique=False)
    op.create_index(op.f('ix_menu_items_environment'), 'menu_items', ['environment'], unique=False)

    # 7. customers
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_index(op.f('ix_customers_phone'), 'customers', ['phone'], unique=False)
    op.create_index(op.f('ix_customers_email'), 'customers', ['email'], unique=False)

    # 8. conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='ACTIVE'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='EN'),
        sa.Column('channel', sa.String(length=50), nullable=True, server_default='WEB'),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_conversations_customer_id'),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_conversations_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=True)
    op.create_index(op.f('ix_conversations_environment'), 'conversations', ['environment'], unique=False)

    # 9. messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations_json', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('response_latency_ms', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_messages_conversation_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    # 10. knowledge_documents
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True, server_default='GENERAL'),
        sa.Column('verification_status', sa.String(length=50), nullable=True, server_default='UNVERIFIED'),
        sa.Column('verified_by', sa.String(length=255), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_knowledge_documents_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_documents_id'), 'knowledge_documents', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_environment'), 'knowledge_documents', ['environment'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_outlet_id'), 'knowledge_documents', ['outlet_id'], unique=False)

    # 11. knowledge_chunks
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('embedding_json', sa.Text(), nullable=True),
        sa.Column('embedding', vector_type, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], name='fk_knowledge_chunks_doc_id'),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_knowledge_chunks_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_chunks_id'), 'knowledge_chunks', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_document_id'), 'knowledge_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_environment'), 'knowledge_chunks', ['environment'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_outlet_id'), 'knowledge_chunks', ['outlet_id'], unique=False)

    # 12. policies
    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('policy_type', sa.String(length=100), nullable=True, server_default='GENERAL'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_policies_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_policies_id'), 'policies', ['id'], unique=False)
    op.create_index(op.f('ix_policies_outlet_id'), 'policies', ['outlet_id'], unique=False)
    op.create_index(op.f('ix_policies_environment'), 'policies', ['environment'], unique=False)

    # 13. faqs
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('outlet_id', sa.Integer(), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('category', sa.String(length=100), nullable=True, server_default='GENERAL'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_faqs_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_faqs_id'), 'faqs', ['id'], unique=False)
    op.create_index(op.f('ix_faqs_outlet_id'), 'faqs', ['outlet_id'], unique=False)
    op.create_index(op.f('ix_faqs_environment'), 'faqs', ['environment'], unique=False)

    # 14. reservation_requests
    op.create_table(
        'reservation_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(length=50), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('outlet_id', sa.Integer(), nullable=False),
        sa.Column('outlet_name', sa.String(length=255), nullable=False),
        sa.Column('guest_name', sa.String(length=255), nullable=False),
        sa.Column('guest_phone', sa.String(length=50), nullable=False),
        sa.Column('guest_email', sa.String(length=255), nullable=True),
        sa.Column('guest_count', sa.Integer(), nullable=True, server_default='2'),
        sa.Column('reservation_date', sa.String(length=20), nullable=False),
        sa.Column('reservation_time', sa.String(length=20), nullable=False),
        sa.Column('seating_preference', sa.String(length=50), nullable=True, server_default='ROOFTOP'),
        sa.Column('special_requests', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='NEW'),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('assigned_staff_id', sa.Integer(), nullable=True),
        sa.Column('assigned_staff_name', sa.String(length=255), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_staff_id'], ['users.id'], name='fk_res_assigned_staff_id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_res_conversation_id'),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_res_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reservation_requests_id'), 'reservation_requests', ['id'], unique=False)
    op.create_index(op.f('ix_reservation_requests_reference_id'), 'reservation_requests', ['reference_id'], unique=True)
    op.create_index(op.f('ix_reservation_requests_outlet_id'), 'reservation_requests', ['outlet_id'], unique=False)
    op.create_index(op.f('ix_reservation_requests_environment'), 'reservation_requests', ['environment'], unique=False)
    op.create_index(op.f('ix_reservation_requests_status'), 'reservation_requests', ['status'], unique=False)
    op.create_index(op.f('ix_reservation_requests_session_id'), 'reservation_requests', ['session_id'], unique=False)

    # 15. reservation_status_history
    op.create_table(
        'reservation_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reservation_id', sa.Integer(), nullable=False),
        sa.Column('changed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('changed_by_name', sa.String(length=255), nullable=True, server_default='System'),
        sa.Column('user_role', sa.String(length=50), nullable=True, server_default='STAFF'),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], name='fk_rsh_changed_by_user_id'),
        sa.ForeignKeyConstraint(['reservation_id'], ['reservation_requests.id'], ondelete='CASCADE', name='fk_rsh_reservation_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reservation_status_history_id'), 'reservation_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_reservation_status_history_reservation_id'), 'reservation_status_history', ['reservation_id'], unique=False)

    # 16. leads
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(length=50), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('outlet_id', sa.Integer(), nullable=False),
        sa.Column('outlet_name', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('enquiry_type', sa.String(length=100), nullable=True, server_default='PRIVATE_DINING'),
        sa.Column('guest_count', sa.Integer(), nullable=True, server_default='20'),
        sa.Column('target_date', sa.String(length=20), nullable=False),
        sa.Column('budget_range', sa.String(length=100), nullable=True, server_default='₹2,50,000 - ₹5,00,000'),
        sa.Column('source', sa.String(length=50), nullable=True, server_default='CHATBOT'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='NEW'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('assigned_staff_id', sa.Integer(), nullable=True),
        sa.Column('assigned_staff_name', sa.String(length=255), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_staff_id'], ['users.id'], name='fk_leads_assigned_staff_id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_leads_conversation_id'),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], name='fk_leads_outlet_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)
    op.create_index(op.f('ix_leads_reference_id'), 'leads', ['reference_id'], unique=True)
    op.create_index(op.f('ix_leads_outlet_id'), 'leads', ['outlet_id'], unique=False)
    op.create_index(op.f('ix_leads_environment'), 'leads', ['environment'], unique=False)
    op.create_index(op.f('ix_leads_status'), 'leads', ['status'], unique=False)
    op.create_index(op.f('ix_leads_session_id'), 'leads', ['session_id'], unique=False)

    # 17. lead_status_history
    op.create_table(
        'lead_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('changed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('changed_by_name', sa.String(length=255), nullable=True, server_default='System'),
        sa.Column('user_role', sa.String(length=50), nullable=True, server_default='STAFF'),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], name='fk_lsh_changed_by_user_id'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='CASCADE', name='fk_lsh_lead_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lead_status_history_id'), 'lead_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_lead_status_history_lead_id'), 'lead_status_history', ['lead_id'], unique=False)

    # 18. environment_settings
    op.create_table(
        'environment_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('active_environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_name', sa.String(length=255), nullable=True, server_default='System'),
        sa.Column('switch_reason', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], name='fk_env_updated_by_user_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_environment_settings_id'), 'environment_settings', ['id'], unique=False)

    # 19. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('user_role', sa.String(length=50), nullable=True, server_default='STAFF'),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('environment', sa.String(length=10), nullable=True, server_default='DEMO'),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_user_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    # 20. ai_configurations
    op.create_table(
        'ai_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=10), nullable=False, server_default='DEMO'),
        sa.Column('model_name', sa.String(length=100), nullable=True, server_default='gemini-1.5-flash'),
        sa.Column('temperature', sa.Float(), nullable=True, server_default='0.2'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('top_k_retrievals', sa.Integer(), nullable=True, server_default='4'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_configurations_id'), 'ai_configurations', ['id'], unique=False)


def downgrade() -> None:
    tables = [
        'ai_configurations',
        'audit_logs',
        'environment_settings',
        'lead_status_history',
        'leads',
        'reservation_status_history',
        'reservation_requests',
        'faqs',
        'policies',
        'knowledge_chunks',
        'knowledge_documents',
        'messages',
        'conversations',
        'customers',
        'menu_items',
        'menu_categories',
        'outlets',
        'restaurants',
        'revoked_tokens',
        'users',
    ]
    for tbl in tables:
        op.drop_table(tbl)
