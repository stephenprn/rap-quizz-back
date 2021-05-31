"""add year response

Revision ID: 322e24fbc745
Revises: 0fbc5c9ccd33
Create Date: 2021-05-02 18:16:39.428018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '322e24fbc745'
down_revision = '0fbc5c9ccd33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'question',
        sa.Column(
            'response_precise',
            sa.String(),
            nullable=True))
    op.execute('COMMIT')
    op.execute('ALTER TYPE responsetype ADD VALUE \'YEAR\'')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'response_precise')
    # ### end Alembic commands ###
