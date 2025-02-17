"""Genère une carte avec folium."""

import sqlite3

import folium

import db


def create_popup(lieu: dict) -> folium.Popup:
    popup_html = f"""
    <div style='font-family: Sans-Serif;'>
    <h4>{lieu["site"]}</h4>
    <h5>{lieu["departement"]} - {lieu["region"]}</h5>
    <p>{lieu["adresseChamp1"]} {lieu["adresseChamp2"]} {lieu["adresseChamp3"]} {lieu["codePostal"]} {lieu["ville"]}
    """
    if lieu["alternance"]:
        popup_html += "<p><b>La formation est en alternance</b></p>"
    if lieu["urlSiteRecrutement"]:
        popup_html += f"<a href='{lieu['urlSiteRecrutement']}'>Lien inscription</a>"
    nb_place = f"{lieu['col']}" if lieu["col"] else "[NA]"
    popup_html += f"<p>Nombre de places : {nb_place}</p>"
    taux_acces = (
        f"{round(lieu['tauxAcces'], 2) * 100}%" if lieu["tauxAcces"] else "[NA]"
    )
    popup_html += f"<p>Taux d'accés : <b>{taux_acces}</b></p>"
    dernier_appele = lieu["rangDernierAppele"] if lieu["rangDernierAppele"] else "[NA]"
    nb_candidature = (
        lieu["nbCandidateuresConfirmees"]
        if lieu["nbCandidateuresConfirmees"]
        else "[NA]"
    )
    popup_html += f"<p>Rang dernier appelé : {dernier_appele} sur {nb_candidature} candidatures</p>"
    popup_html += (
        f"<p>{lieu['commentaire']}</p>"
        if lieu["commentaire"]
        else "<p>Pas de commentaire</p>"
    )
    popup_html += f"<p>{lieu['motif']}</p>" if lieu["motif"] else "<p>Pas de motif</p>"
    popup_html += f"<i style='color: grey;'><time datetime='{lieu['lastModified']}'>{lieu['lastModified']}</time></i>"
    popup_html += "</div>"
    frame = folium.IFrame(html=popup_html)
    popup = folium.Popup(frame, min_width=350, max_width=500)
    return popup


m = folium.Map(location=(46.603354, 1.888334), zoom_start=6)

db.conn.row_factory = sqlite3.Row # Récupère les données sous forme de dict.
cursor = db.conn.cursor()

# Master de Marseille qui a une erreur de longitude.
cursor.execute("""
UPDATE Lieux
SET lon = 5.436765
WHERE adresseChamp1 = '163 avenue de Luminy'
""")

# Requète principale.
cursor.execute("""
select *
from Lieux  L
join Formation F ON (L.id_formation=F.id)
left join Indicateur I ON (I.id_formation=F.id)
left join MotifsLibres M ON (M.id_formation=F.id)
where lat is not NULL and
intituleMention	in ('Informatique', 'Science des données',  'Intelligence artificielle', 'Intelligence Artificielle')
""")
lieux = [dict(row) for row in cursor.fetchall()]
for lieu in lieux:
    # Tooltip.
    tooltip_html = f"[{lieu['intituleMention']}]"
    if lieu["intituleParcours"]:
        tooltip_html += f" - {lieu['intituleParcours']}"

    # Popup.
    popup = create_popup(lieu)

    # Color marker.
    color = "green" if lieu["alternance"] == 1 else "blue"

    folium.Marker(
        location=[lieu["lat"], lieu["lon"]],
        tooltip=tooltip_html,
        popup=popup,
        icon=folium.Icon(icon="building-columns", prefix="fa", color=color),
    ).add_to(m)

path = "carte_monmaster.html"
m.save(path)
print(f"Carte créée {path}")
