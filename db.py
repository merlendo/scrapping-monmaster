"""Création des tables."""

import sqlite3

FORMATION = """
CREATE TABLE IF NOT EXISTS Formation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_indicateur INTEGER,
    ifc STRING,
    inm STRING,
    inmp STRING,
    uai STRING,
    intituleMention STRING,
    intituleParcours STRING,
    candidatable BOOL,
    alternance BOOL,
    col INTEGER,
    juryRectoral BOOL,
    lastModified DATE,
    commentaire STRING,
    debutRecrutementDate DATE,
    finRecrutementDate DATE,
    motifNonRecrutement STRING,
    urlSiteRecrutement STRING,
    urlSiteDroitsInscription STRING
);
"""

LIEUX = """
CREATE TABLE IF NOT EXISTS Lieux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_formation INTEGER,
    name STRING,
    site STRING,
    adresseChamp1 STRING,
    adresseChamp2 STRING,
    adresseChamp3 STRING,
    codePostal STRING,
    ville STRING,
    lat FLOAT,
    lon FLOAT,
    region STRING,
    departement STRING,
    villeEtrangere BOOL
);
"""

MODALITES = """
CREATE TABLE IF NOT EXISTS Modalites (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   id_formation INTEGER,
   modalite STRING
);
"""

INDICATEURS = """
CREATE TABLE IF NOT EXISTS Indicateur (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   id_formation INTEGER,
   tauxAcces FLOAT,
   rangDernierAppele INT,
   nbCandidateuresConfirmees INT
);
"""

MOTIFSLIBRES = """
CREATE TABLE IF NOT EXISTS MotifsLibres (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   id_formation INTEGER,
   motif STRING
);
"""
conn = sqlite3.connect("monmaster.db")


def init():
    conn.execute(FORMATION)
    conn.execute(LIEUX)
    conn.execute(MODALITES)
    conn.execute(INDICATEURS)
    conn.execute(MOTIFSLIBRES)
    print("[INFO] : Init tables")

