"""empty message

Revision ID: 347f3bae4662
Revises: None
Create Date: 2016-07-06 20:56:35.465375

"""

# revision identifiers, used by Alembic.
revision = '347f3bae4662'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=127), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_paper',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('subject', sa.Integer(), nullable=True),
    sa.Column('single_choice', sa.String(length=255), nullable=True),
    sa.Column('blank_fill', sa.String(length=255), nullable=True),
    sa.Column('essay', sa.String(length=255), nullable=True),
    sa.Column('add_date', sa.Date(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['subject'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=127), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('blank_fill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=True),
    sa.Column('difficult_level', sa.Float(), nullable=True),
    sa.Column('add_date', sa.Date(), nullable=True),
    sa.Column('faq', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('points_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('answer', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['points_id'], ['points.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('single_choice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=True),
    sa.Column('difficult_level', sa.Float(), nullable=True),
    sa.Column('add_date', sa.Date(), nullable=True),
    sa.Column('faq', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('points_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('answer', sa.Enum('A', 'B', 'C', 'D'), nullable=True),
    sa.Column('A', sa.Text(), nullable=True),
    sa.Column('B', sa.Text(), nullable=True),
    sa.Column('C', sa.Text(), nullable=True),
    sa.Column('D', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['points_id'], ['points.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('essay',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=True),
    sa.Column('difficult_level', sa.Float(), nullable=True),
    sa.Column('add_date', sa.Date(), nullable=True),
    sa.Column('faq', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('points_id', sa.Integer(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('answer', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['points_id'], ['points.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('essay')
    op.drop_table('single_choice')
    op.drop_table('blank_fill')
    op.drop_table('points')
    op.drop_table('test_paper')
    op.drop_table('subject')
    op.drop_table('users')
    ### end Alembic commands ###
