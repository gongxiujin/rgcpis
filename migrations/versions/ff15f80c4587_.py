"""empty message

Revision ID: ff15f80c4587
Revises: 0626555fde49
Create Date: 2016-08-02 19:09:43.761258

"""

# revision identifiers, used by Alembic.
revision = 'ff15f80c4587'
down_revision = '0626555fde49'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('ipmi_ip', sa.String(length=15), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'ipmi_ip')
    ### end Alembic commands ###
