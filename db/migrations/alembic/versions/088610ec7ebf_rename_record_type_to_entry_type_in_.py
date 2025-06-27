"""rename record_type to entry_type in listening_history

Revision ID: 088610ec7ebf
Revises: 6414d4a1e2f8
Create Date: 2025-06-27 00:10:55.358130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '088610ec7ebf'
down_revision: Union[str, Sequence[str], None] = '6414d4a1e2f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('spotilens__listening_history', 'record_type', new_column_name='entry_type')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('spotilens__listening_history', 'entry_type', new_column_name='record_type')
