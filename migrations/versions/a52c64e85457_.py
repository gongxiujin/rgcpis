"""empty message

Revision ID: a52c64e85457
Revises: 107f06a9e803
Create Date: 2016-10-04 15:27:30.765520

"""

# revision identifiers, used by Alembic.
revision = 'a52c64e85457'
down_revision = '107f06a9e803'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_version', sa.Column('type', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_version', 'type')
    ### end Alembic commands ###
