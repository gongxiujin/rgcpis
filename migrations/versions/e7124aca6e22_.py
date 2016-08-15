"""empty message

Revision ID: e7124aca6e22
Revises: ff15f80c4587
Create Date: 2016-08-12 16:27:27.769850

"""

# revision identifiers, used by Alembic.
revision = 'e7124aca6e22'
down_revision = 'ff15f80c4587'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=191), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.Column('lastseen', sa.DateTime(), nullable=True),
    sa.Column('lastip', sa.String(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    ### end Alembic commands ###
