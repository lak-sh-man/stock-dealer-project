"""first revision

Revision ID: 0d6e8ba66c4f
Revises: 50ab2327fe01
Create Date: 2025-03-06 15:24:28.824979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d6e8ba66c4f'
down_revision: Union[str, None] = '50ab2327fe01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
