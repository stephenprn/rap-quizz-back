"""add explaintation to question

Revision ID: 7e7bffaf9984
Revises: 414ece2c7bc5
Create Date: 2021-06-10 20:00:59.750229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e7bffaf9984'
down_revision = '414ece2c7bc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('explaination', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'explaination')
    # ### end Alembic commands ###
