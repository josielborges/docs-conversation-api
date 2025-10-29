"""add enabled and source_id to embeddings

Revision ID: 003
Revises: 002
Create Date: 2025-10-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('document_embeddings', sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('document_embeddings', sa.Column('source_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_document_embeddings_source_id', 'document_embeddings', 'sources', ['source_id'], ['id'], ondelete='CASCADE')
    op.execute('UPDATE document_embeddings SET source_id = (SELECT id FROM sources WHERE sources.name = document_embeddings.filename AND sources.notebook_id = document_embeddings.notebook_id LIMIT 1)')
    op.alter_column('document_embeddings', 'source_id', nullable=False)


def downgrade() -> None:
    op.drop_constraint('fk_document_embeddings_source_id', 'document_embeddings', type_='foreignkey')
    op.drop_column('document_embeddings', 'source_id')
    op.drop_column('document_embeddings', 'enabled')
