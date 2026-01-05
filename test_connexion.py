"""
Script de test pour vérifier la connexion à MongoDB
"""
from database import db

print("🔄 Test de connexion à MongoDB Atlas...")
print("-" * 50)

if db.connect():
    print("✅ Connexion réussie!")
    print("\n📦 Collections créées:")
    collections = db.db.list_collection_names()
    for coll in collections:
        print(f"  • {coll}")
    
    print("\n✅ Tout est prêt! Vous pouvez utiliser l'application.")
else:
    print("❌ Échec de la connexion.")
    print("Vérifiez votre mot de passe dans le fichier .env")

db.close()
