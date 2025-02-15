import requests
import db


def get_data(recherche: str | None = None):
    headers = {}
    params = {
        "size": "5000",
        "page": "0",
    }

    json_data = {
        "mentions": ["Informatique", 
                     "Intelligence artificielle", 
                     "Science des données"]
    }

    if recherche:
        json_data["recherche"] = recherche

    response = requests.post(
        "https://monmaster.gouv.fr/api/candidat/mm1/formations",
        params=params,
        headers=headers,
        json=json_data,
    )
    return response


def get_colnames(table_name: str, conn):
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT name FROM pragma_table_info(?);
    """,
        [table_name],
    )
    colnames = [row[0] for row in cursor.fetchall()]
    return colnames


def check_value_dict(dictionnaire: dict, colnames: list[str]):
    for colname in colnames:
        if colname not in dictionnaire.keys():
            dictionnaire[colname] = None
    return dictionnaire


def insert_formation(formation: dict, conn):
    cursor = conn.cursor()

    # Vérifie les champs non présent.
    colnames = get_colnames("Formation", conn)
    check_value_dict(formation, colnames)

    # Insert les données.
    cursor.execute(
        """
    INSERT INTO Formation 
    VALUES (
        NULL,
        NULL,
        :ifc,
        :inm,
        :inmp,
        :uai,
        :intituleMention,
        :intituleParcours,
        :candidatable,
        :alternance,
        :col,
        :juryRectoral,
        :lastModified,
        :commentaire,
        :debutRecrutementDate,
        :finRecrutementDate,
        :motifNonRecrutement,
        :urlSiteRecrutement,
        :urlSiteDroitsInscription
    )
    """,
        formation,
    )
    conn.commit()
    return cursor.lastrowid


def insert_indicateur(indicateur: dict, id_formation: int, conn):
    if not indicateur:
        return
    cursor = conn.cursor()

    # Vérifie les champs non présent.
    indicateur["id_formation"] = id_formation
    colnames = get_colnames("Indicateur", conn)
    check_value_dict(indicateur, colnames)

    # Insère les données.
    cursor.execute(
        """
    INSERT INTO Indicateur
    VALUES (
        NULL,
        :id_formation,
        :tauxAcces,
        :rangDernierAppele,
        :nbCandidaturesConfirmees
    )

    """,
        indicateur,
    )
    conn.commit()
    id_indicateur = cursor.lastrowid
    cursor.execute(
        """
    UPDATE Formation 
    SET id_indicateur=? 
    WHERE id=?""",
        [id_indicateur, id_formation],
    )
    return id_indicateur


def insert_motif_libre(motif_libre: list, id_formation: int, conn):
    if not motif_libre:
        return
    cursor = conn.cursor()
    ids_motifs_libres = []
    for motif in motif_libre:
        cursor.execute(
            """
        INSERT INTO MotifsLibres 
        VALUES (NULL, ?, ?)
        """,
            [id_formation, motif],
        )
        ids_motifs_libres.append(cursor.lastrowid)
    conn.commit()
    return ids_motifs_libres


def insert_modalite(modalites: list, id_formation: int, conn):
    if not modalites:
        return
    cursor = conn.cursor()
    ids_modalites = []
    for modalite in modalites:
        cursor.execute(
            """
        INSERT INTO Modalites 
        VALUES (NULL, ?, ?)
        """,
            [id_formation, modalite],
        )
        ids_modalites.append(cursor.lastrowid)
    conn.commit()
    return ids_modalites


def insert_lieu(lieux: list[dict], id_formation: int, conn):
    if not lieux:
        return
    cursor = conn.cursor()
    colnames = get_colnames("Lieux", conn)
    ids_lieux = []
    for lieu in lieux:
        # Construit colonne id_formation.
        lieu["id_formation"] = id_formation

        # Vérifie les champs non présent.
        check_value_dict(lieu, colnames)

        # Construit les colonnes latitude longitude.
        if "latLon" in lieu.keys():
            ll = lieu.pop("latLon")
            lieu["lat"] = ll["lat"]
            lieu["lon"] = ll["lon"]
        else:
            lieu["lat"] = None
            lieu["lon"] = None

        # Construit les colonnes region et département.
        if "regionEtDepartement" in lieu.keys():
            rd = lieu.pop("regionEtDepartement")
            lieu["region"] = rd[0]
            lieu["departement"] = rd[1]
        else:
            lieu["region"] = None
            lieu["departement"] = None

        cursor.execute(
            """
        INSERT INTO Lieux 
        VALUES (
            NULL,
            :id_formation,
            :name,
            :site,
            :adresseChamp1,
            :adresseChamp2,
            :adresseChamp3,
            :codePostal,
            :ville,
            :lat,
            :lon,
            :region,
            :departement,
            :villeEtrangere
        )
        """,
            lieu,
        )
        ids_lieux.append(cursor.lastrowid)
    conn.commit()
    return ids_lieux


def run():
    response = get_data(recherche="informatique")
    print(response.status_code)
    r = response.json()
    content = r["content"]
    for i, formation in enumerate(content, start=1):
        print(f"\rInserting formation {i:3}/{len(content)}", end="")

        # Divise les différents champs.
        indicateur = formation.pop("indicateursAnneeDerniere")
        motif_libre = formation.pop("motifsLibres")
        modalite = formation.pop("modalitesEnseignement")
        lieu = formation.pop("lieux")

        # Insert les données.
        id_formation = insert_formation(formation, db.conn)
        id_indicateur = insert_indicateur(indicateur, id_formation, db.conn)
        id_motifs = insert_motif_libre(motif_libre, id_formation, db.conn)
        ids_modalites = insert_modalite(modalite, id_formation, db.conn)
        ids_lieux = insert_lieu(lieu, id_formation, db.conn)
    print("\n", end="")


if __name__ == "__main__":
    db.init()
    run()
