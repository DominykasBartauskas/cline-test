"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2025-06-18 09:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables
    # Genre table
    op.create_table(
        'genre',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('type', sa.String(), nullable=False, index=True),
    )

    # Movie table
    op.create_table(
        'movie',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=False, index=True),
        sa.Column('title', sa.String(), nullable=False, index=True),
        sa.Column('original_title', sa.String(), nullable=True),
        sa.Column('overview', sa.String(), nullable=True),
        sa.Column('poster_path', sa.String(), nullable=True),
        sa.Column('backdrop_path', sa.String(), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=True, index=True),
        sa.Column('popularity', sa.Float(), nullable=True, index=True),
        sa.Column('vote_average', sa.Float(), nullable=True, index=True),
        sa.Column('vote_count', sa.Integer(), nullable=True),
        sa.Column('adult', sa.Boolean(), nullable=True),
        sa.Column('original_language', sa.String(), nullable=True),
        sa.Column('director_name', sa.String(), nullable=True),
        sa.Column('director_tmdb_id', sa.Integer(), nullable=True),
        sa.Column('actor1_name', sa.String(), nullable=True),
        sa.Column('actor1_tmdb_id', sa.Integer(), nullable=True),
        sa.Column('actor2_name', sa.String(), nullable=True),
        sa.Column('actor2_tmdb_id', sa.Integer(), nullable=True),
        sa.Column('actor3_name', sa.String(), nullable=True),
        sa.Column('actor3_tmdb_id', sa.Integer(), nullable=True),
    )

    # TV Show table
    op.create_table(
        'tvshow',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('original_name', sa.String(), nullable=True),
        sa.Column('overview', sa.String(), nullable=True),
        sa.Column('poster_path', sa.String(), nullable=True),
        sa.Column('backdrop_path', sa.String(), nullable=True),
        sa.Column('first_air_date', sa.Date(), nullable=True, index=True),
        sa.Column('popularity', sa.Float(), nullable=True, index=True),
        sa.Column('vote_average', sa.Float(), nullable=True, index=True),
        sa.Column('vote_count', sa.Integer(), nullable=True),
        sa.Column('original_language', sa.String(), nullable=True),
        sa.Column('number_of_seasons', sa.Integer(), nullable=True),
        sa.Column('number_of_episodes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True, index=True),
    )

    # User table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
    )

    # Association tables
    op.create_table(
        'movie_genre',
        sa.Column('movie_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('movie.id'), primary_key=True),
        sa.Column('genre_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('genre.id'), primary_key=True),
    )

    op.create_table(
        'tv_show_genre',
        sa.Column('tv_show_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tvshow.id'), primary_key=True),
        sa.Column('genre_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('genre.id'), primary_key=True),
    )

    op.create_table(
        'user_movie_watchlist',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), primary_key=True),
        sa.Column('movie_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('movie.id'), primary_key=True),
    )

    op.create_table(
        'user_tv_show_watchlist',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), primary_key=True),
        sa.Column('tv_show_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tvshow.id'), primary_key=True),
    )

    # Rating tables
    op.create_table(
        'movierating',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('movie_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('movie.id'), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
    )

    op.create_table(
        'tvshowrating',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('tv_show_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tvshow.id'), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tvshowrating')
    op.drop_table('movierating')
    op.drop_table('user_tv_show_watchlist')
    op.drop_table('user_movie_watchlist')
    op.drop_table('tv_show_genre')
    op.drop_table('movie_genre')
    op.drop_table('user')
    op.drop_table('tvshow')
    op.drop_table('movie')
    op.drop_table('genre')
