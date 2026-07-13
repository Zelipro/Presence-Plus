"""
Script de test pour vérifier la connexion à Supabase
"""
from database import db

print("🔄 Test de connexion à Supabase...")
print("-" * 50)

if db.connect():
    print("✅ Connexion réussie!")
    print("\n📦 Tables attendues: etudiants, matieres, seances, presences")
    print("   (créées via supabase_schema.sql dans l'éditeur SQL Supabase)")
    print("\n✅ Tout est prêt! Vous pouvez utiliser l'application.")
else:
    print("❌ Échec de la connexion.")
    print("Vérifiez SUPABASE_URL et SUPABASE_KEY dans le fichier .env")

db.close()
