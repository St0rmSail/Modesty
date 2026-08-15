"""
bootstrap.py
============

Purpose:
    Starts Modesty.

Responsibilities:
    - Initialise Core
    - Verify required components
    - Wake Executive Agent

Author:
    Andrew & ChatGPT

Current through:
    0.14.0 — Time and Presence
"""

import sqlite3

from rich import print
from Runtime.Core import team_status
from Runtime.Knowledge import KnowledgeStores
from Runtime.Knowledge.stores import KnowledgeStoreError
from Brain.Team.archivist import Archivist
from Brain.Team.researcher import Researcher

from Runtime.Core import config
from Runtime.Time import PresenceSession


def startup(presence: PresenceSession | None = None):

    team_status.reset()

    print("\n[bold cyan]MODESTY : INITIALISING[/]\n")

    # -------------------------------------------------
    # Private Filing Cabinet and living Bookshelf
    # -------------------------------------------------

    try:
        stores = KnowledgeStores(config.KNOWLEDGE_STORES_CONFIG).initialize()
    except KnowledgeStoreError as error:
        print(f"[red]{error}[/]")
    else:
        print(f"[green]Filing Cabinet : READY[/]  {stores.filing_cabinet}")
        print(f"[green]Bookshelf      : READY[/]  {stores.bookshelf}")
        try:
            report = Archivist(stores).inventory()
        except (OSError, sqlite3.Error, UnicodeError) as error:
            print(f"[yellow]Archivist     : ATTENTION  {error}[/]")
        else:
            team_status.set_member_state("archivist", "ready")
            print(
                f"[green]Archivist     : READY[/]  {report.documents} documents; "
                f"{report.warnings} warnings"
            )

    try:
        Researcher()
    except (ImportError, RuntimeError, ValueError) as error:
        print(f"[yellow]Researcher    : ATTENTION  {error}[/]")
    else:
        team_status.set_member_state("researcher", "ready")
        print("[green]Researcher    : READY[/]  bounded discovery")

    print("Grand Library : CLOSED")
    if presence is not None:
        print("Time & Presence: READY  local session ledger")

    print()
    team_status.set_core_ready(True)
    print(
        "[bold green]MODESTY : READY[/]"
        if team_status.system_ready()
        else "[bold yellow]MODESTY : READY WITH ATTENTION[/]"
    )

