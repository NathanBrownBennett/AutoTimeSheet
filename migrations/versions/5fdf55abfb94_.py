"""empty message

Revision ID: 5fdf55abfb94
Revises: 18f24f9a8f9e
Create Date: 2024-08-29 17:09:58.975736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fdf55abfb94'
down_revision = '18f24f9a8f9e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organisation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_generated_code', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('last_generated_code_time', sa.DateTime(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_generated_code', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('last_generated_code_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_generated_code_time')
        batch_op.drop_column('last_generated_code')

    with op.batch_alter_table('organisation', schema=None) as batch_op:
        batch_op.drop_column('last_generated_code_time')
        batch_op.drop_column('last_generated_code')

    # ### end Alembic commands ###
