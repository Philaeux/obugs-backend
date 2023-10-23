"""empty message

Revision ID: 0999797c9ca6
Revises: f4402ea7d8f8
Create Date: 2023-10-23 16:14:34.909711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0999797c9ca6'
down_revision: Union[str, None] = 'f4402ea7d8f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('reddit_id', sa.String(), nullable=True))
    op.add_column('user', sa.Column('reddit_name', sa.String(), nullable=True))
    op.create_index(op.f('ix_user_reddit_id'), 'user', ['reddit_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_reddit_id'), table_name='user')
    op.drop_column('user', 'reddit_name')
    op.drop_column('user', 'reddit_id')
    # ### end Alembic commands ###
