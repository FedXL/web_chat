"""empty message

Revision ID: a911c3fa9b9e
Revises: b75547e4e7e7
Create Date: 2023-08-29 02:01:43.323052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a911c3fa9b9e'
down_revision: Union[str, None] = 'b75547e4e7e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('web_photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photo_path', sa.String(), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['web_messages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('web_photos')
    # ### end Alembic commands ###