"""add SUPER_ADMIN to roles

Revision ID: 414ece2c7bc5
Revises: 2840882cf612
Create Date: 2021-06-08 23:13:02.240544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '414ece2c7bc5'
down_revision = '2840882cf612'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('COMMIT')
    op.execute('ALTER TYPE userrole ADD VALUE \'SUPER_ADMIN\'')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('COMMIT')
    # ### end Alembic commands ###
