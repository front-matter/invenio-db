# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click command-line interface for database management."""

import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from .proxies import current_db
from .utils import create_alembic_version_table, drop_alembic_version_table, has_table


def abort_if_false(ctx, param, value):
    """Abort command is value is False."""
    if not value:
        ctx.abort()


def render_url(url):
    """Render the URL for CLI output."""
    return url.render_as_string(hide_password=True)


#
# Database commands
#
@click.group(chain=True)
def db():
    """Database commands."""


@db.command()
@click.option("-v", "--verbose", is_flag=True, default=False)
@with_appcontext
def create(verbose):
    """Create tables."""
    alembic = current_app.extensions["invenio-db"].alembic
    if not alembic.migration_context._has_version_table():
        click.secho("Creating all tables!", fg="yellow", bold=True)
        with click.progressbar(current_db.metadata.sorted_tables) as bar:
            for table in bar:
                if verbose:
                    click.echo(f" Creating table {table}")
                table.create(bind=current_db.engine, checkfirst=True)
        create_alembic_version_table()
        click.secho("Created all tables!", fg="green")
    else:
        click.secho(
            "Alembic version table already exists, skipping table creation.",
            fg="yellow",
        )


@db.command()
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you know that you are going to drop the db?",
)
@with_appcontext
def drop(verbose):
    """Drop tables."""
    click.secho("Dropping all tables!", fg="red", bold=True)
    with click.progressbar(reversed(current_db.metadata.sorted_tables)) as bar:
        for table in bar:
            if verbose:
                click.echo(f" Dropping table {table}")
            table.drop(bind=current_db.engine, checkfirst=True)
        drop_alembic_version_table()
    click.secho("Dropped all tables!", fg="green")


@db.command()
@with_appcontext
def init():
    """Create database."""
    displayed_database = render_url(current_db.engine.url)
    click.secho(f"Creating database {displayed_database}", fg="green")
    database_url = current_db.engine.url.render_as_string(hide_password=False)
    if not database_exists(database_url):
        create_database(database_url)


@db.command()
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you know that you are going to destroy the db?",
)
@with_appcontext
def destroy():
    """Drop database."""
    displayed_database = render_url(current_db.engine.url)
    click.secho(f"Destroying database {displayed_database}", fg="red", bold=True)
    plain_url = current_db.engine.url.render_as_string(hide_password=False)
    if current_db.engine.name == "sqlite":
        try:
            drop_database(plain_url)
        except FileNotFoundError:
            click.secho("Sqlite database has not been initialised", fg="red", bold=True)
    else:
        drop_database(plain_url)
