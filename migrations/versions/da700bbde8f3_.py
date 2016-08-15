"""empty message

Revision ID: da700bbde8f3
Revises: b492e1cf9101
Create Date: 2016-08-15 11:47:21.222247

"""

# revision identifiers, used by Alembic.
revision = 'da700bbde8f3'
down_revision = 'b492e1cf9101'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('ip_mac', sa.String(length=30), nullable=True))
    op.add_column('service', sa.Column('ipmi_ip_mac', sa.String(length=30), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'ipmi_ip_mac')
    op.drop_column('service', 'ip_mac')
    ### end Alembic commands ###
