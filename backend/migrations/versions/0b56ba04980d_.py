"""empty message

Revision ID: 0b56ba04980d
Revises: 
Create Date: 2024-11-10 10:22:01.243420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b56ba04980d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Average_Rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('is_visible', sa.Boolean(), nullable=True))
        batch_op.drop_column('Average_Customer_Rating')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Average_Customer_Rating', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        batch_op.drop_column('is_visible')
        batch_op.drop_column('Average_Rating')

    # ### end Alembic commands ###