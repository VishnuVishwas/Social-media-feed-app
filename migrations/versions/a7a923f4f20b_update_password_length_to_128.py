"""Update password length to 128

Revision ID: a7a923f4f20b
Revises: c526e08c790a
Create Date: 2024-10-15 22:29:55.479444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a923f4f20b'
down_revision = 'c526e08c790a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=80),
               type_=sa.String(length=130),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=130),
               type_=sa.VARCHAR(length=80),
               existing_nullable=False)

    # ### end Alembic commands ###
