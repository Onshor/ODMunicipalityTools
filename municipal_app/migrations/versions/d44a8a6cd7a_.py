"""empty message

Revision ID: d44a8a6cd7a
Revises: None
Create Date: 2018-07-09 14:13:12.778905

"""

# revision identifiers, used by Alembic.
revision = 'd44a8a6cd7a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auto_update',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('municipal_id', sa.String(), nullable=True),
    sa.Column('file_name', sa.String(), nullable=True),
    sa.Column('ressource_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['municipal_id'], ['municipality.municipal_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('municipal_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('datetime_log', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['auto_update.id'], ),
    sa.ForeignKeyConstraint(['municipal_id'], ['municipality.municipal_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'municipality', 'approved',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text(u'false'))
    op.alter_column(u'municipality', 'deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text(u'false'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'municipality', 'deleted',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text(u'false'))
    op.alter_column(u'municipality', 'approved',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text(u'false'))
    op.drop_table('file_log')
    op.drop_table('auto_update')
    ### end Alembic commands ###