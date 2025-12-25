"""Initial migration

Revision ID: 9be86f57bf7b
Revises: 
Create Date: 2025-12-25 10:52:17.436832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9be86f57bf7b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('creator_id', sa.String(), nullable=False),
        sa.Column('video_created_at', sa.DateTime(), nullable=False),
        sa.Column('views_count', sa.BigInteger(), nullable=True),
        sa.Column('likes_count', sa.BigInteger(), nullable=True),
        sa.Column('comments_count', sa.BigInteger(), nullable=True),
        sa.Column('reports_count', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_videos_creator_id'), 'videos', ['creator_id'], unique=False)
    op.create_index(op.f('ix_videos_video_created_at'), 'videos', ['video_created_at'], unique=False)

    # Create video_snapshots table
    op.create_table(
        'video_snapshots',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('video_id', sa.String(), nullable=False),
        sa.Column('views_count', sa.BigInteger(), nullable=True),
        sa.Column('likes_count', sa.BigInteger(), nullable=True),
        sa.Column('comments_count', sa.BigInteger(), nullable=True),
        sa.Column('reports_count', sa.BigInteger(), nullable=True),
        sa.Column('delta_views_count', sa.BigInteger(), nullable=True),
        sa.Column('delta_likes_count', sa.BigInteger(), nullable=True),
        sa.Column('delta_comments_count', sa.BigInteger(), nullable=True),
        sa.Column('delta_reports_count', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_snapshots_video_id'), 'video_snapshots', ['video_id'], unique=False)
    op.create_index(op.f('ix_video_snapshots_created_at'), 'video_snapshots', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_video_snapshots_created_at'), table_name='video_snapshots')
    op.drop_index(op.f('ix_video_snapshots_video_id'), table_name='video_snapshots')
    op.drop_table('video_snapshots')
    op.drop_index(op.f('ix_videos_video_created_at'), table_name='videos')
    op.drop_index(op.f('ix_videos_creator_id'), table_name='videos')
    op.drop_table('videos')

