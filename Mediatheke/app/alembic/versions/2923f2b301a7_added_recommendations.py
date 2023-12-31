"""added recommendations

Revision ID: 2923f2b301a7
Revises: 674654a844f1
Create Date: 2023-09-01 14:37:36.359276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2923f2b301a7'
down_revision: Union[str, None] = '674654a844f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_role_id', table_name='users')
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_index('ix_users_role_id', 'users', ['role_id'], unique=False)
    # ### end Alembic commands ###
