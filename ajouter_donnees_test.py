"""
Script pour ajouter des données de test dans MongoDB
"""
from database import db
from datetime import datetime

print("🔄 Ajout de données de test...")
print("-" * 50)

# Connexion à la base de données
if not db.connect():
    print("❌ Erreur de connexion à MongoDB")
    exit(1)

print("\n📚 Ajout des matières...")
matieres = [
    {"titre": "Programmation Python", "code": "INFO101", "prof": "Prof. Dupont"},
    {"titre": "Base de données", "code": "INFO102", "prof": "Prof. Martin"},
    {"titre": "Algorithmique", "code": "INFO103", "prof": "Prof. Bernard"},
    {"titre": "Réseaux", "code": "INFO104", "prof": "Prof. Lefebvre"},
]

for matiere in matieres:
    result = db.ajouter_matiere(
        titre=matiere["titre"],
        code=matiere["code"],
        prof=matiere["prof"]
    )
    if result:
        print(f"  ✓ {matiere['titre']} ({matiere['code']})")

print("\n👥 Ajout des délégués...")
delegues = [
    {"nom": "KOUASSI Jean", "level": "L3", "matricule": "DEL001", "email": "jean.kouassi@univ.edu"},
    {"nom": "TRAORE Marie", "level": "L3", "matricule": "DEL002", "email": "marie.traore@univ.edu"},
]

for delegue in delegues:
    result = db.ajouter_etudiant(
        nom=delegue["nom"],
        level=delegue["level"],
        matricule=delegue["matricule"],
        email=delegue["email"],
        titre="Delegue",
        device_id=None  # Les délégués n'ont pas besoin de device_id
    )
    if result:
        print(f"  ✓ {delegue['nom']} - {delegue['matricule']}")

print("\n🎓 Ajout des étudiants...")
etudiants = [
    {"nom": "DIALLO Amadou", "level": "L3", "matricule": "ETU001", "email": "amadou.diallo@univ.edu"},
    {"nom": "KONE Fatou", "level": "L3", "matricule": "ETU002", "email": "fatou.kone@univ.edu"},
    {"nom": "BAMBA Ibrahim", "level": "L3", "matricule": "ETU003", "email": "ibrahim.bamba@univ.edu"},
    {"nom": "SYLLA Aicha", "level": "L3", "matricule": "ETU004", "email": "aicha.sylla@univ.edu"},
    {"nom": "TOURE Moussa", "level": "L3", "matricule": "ETU005", "email": "moussa.toure@univ.edu"},
    {"nom": "CAMARA Fatoumata", "level": "L3", "matricule": "ETU006", "email": "fatoumata.camara@univ.edu"},
    {"nom": "SANGARE Youssouf", "level": "L3", "matricule": "ETU007", "email": "youssouf.sangare@univ.edu"},
    {"nom": "OUATTARA Awa", "level": "L3", "matricule": "ETU008", "email": "awa.ouattara@univ.edu"},
]

for etudiant in etudiants:
    result = db.ajouter_etudiant(
        nom=etudiant["nom"],
        level=etudiant["level"],
        matricule=etudiant["matricule"],
        email=etudiant["email"],
        titre="Etudiant",
        device_id=None  # Pas encore validé
    )
    if result:
        print(f"  ✓ {etudiant['nom']} - {etudiant['matricule']}")

print("\n" + "=" * 50)
print("✅ Données de test ajoutées avec succès!")
print("\n📊 Résumé:")
print(f"  • {len(matieres)} matières")
print(f"  • {len(delegues)} délégués")
print(f"  • {len(etudiants)} étudiants")
print("\n💡 Vous pouvez maintenant:")
print("  1. Lancer l'application: python Page2.py")
print("  2. Se connecter en tant que délégué (DEL001 ou DEL002)")
print("  3. Créer une séance de cours")
print("=" * 50)

db.close()
