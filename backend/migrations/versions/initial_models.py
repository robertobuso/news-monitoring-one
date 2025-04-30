"""
Initial database models migration.

Revision ID: 0001
Revises: 
Create Date: 2023-11-15 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE feed_type AS ENUM ('rss', 'api', 'web')")
    op.execute("CREATE TYPE health_status AS ENUM ('healthy', 'warning', 'error')")
    op.execute("CREATE TYPE report_status AS ENUM ('pending', 'generating', 'ready', 'sent', 'error')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create client_profiles table
    op.create_table(
        'client_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create news_feeds table
    op.create_table(
        'news_feeds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('rss', 'api', 'web', name='feed_type'), nullable=False),
        sa.Column('check_frequency', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_checked', sa.DateTime()),
        sa.Column('health_status', sa.Enum('healthy', 'warning', 'error', name='health_status'), nullable=False, server_default='healthy'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('feed_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('news_feeds.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False, unique=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('author', sa.String()),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create article_relevances table
    op.create_table(
        'article_relevances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id'), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('client_profiles.id'), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('is_included', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('client_profiles.id'), nullable=False),
        sa.Column('report_date', sa.DateTime(), nullable=False),
        sa.Column('pdf_path', sa.String()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('sent_at', sa.DateTime()),
        sa.Column('recipient_email', sa.String()),
        sa.Column('status', sa.Enum('pending', 'generating', 'ready', 'sent', 'error', name='report_status'), nullable=False, server_default='pending'),
    )
    
    # Create report_articles table
    op.create_table(
        'report_articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id'), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('position', sa.Integer(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_articles_content_gin', 'articles', ['content'], postgresql_using='gin')
    op.create_index('ix_articles_published_at', 'articles', ['published_at'])
    op.create_index('ix_article_relevances_client_id_relevance_score', 'article_relevances', ['client_id', 'relevance_score'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('report_articles')
    op.drop_table('reports')
    op.drop_table('article_relevances')
    op.drop_table('articles')
    op.drop_table('news_feeds')
    op.drop_table('client_profiles')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE report_status")
    op.execute("DROP TYPE health_status")
    op.execute("DROP TYPE feed_type")