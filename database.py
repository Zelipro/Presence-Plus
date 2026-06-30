from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("DATABASE_NAME", "Presence_Plus")
        self.client = None
        self.db = None
        self.initialized = True
        
    def connect(self):
        """Établit la connexion à MongoDB Atlas"""
        if self.client is not None:
            return True
        if not self.uri:
            print("✗ MONGODB_URI manquant dans le fichier .env")
            return False
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            # Test de connexion
            self.client.admin.command('ping')
            print("✓ Connexion à MongoDB réussie!")
            self.create_collections()
            return True
        except Exception as e:
            print(f"✗ Erreur de connexion à MongoDB: {e}")
            self.client = None
            return False
    
    def create_collections(self):
        """Crée les collections nécessaires si elles n'existent pas"""
        collections = ["etudiants", "matieres", "seances", "presences"]
        existing = self.db.list_collection_names()
        
        for coll in collections:
            if coll not in existing:
                self.db.create_collection(coll)
                print(f"✓ Collection '{coll}' créée")
                
                if coll == "etudiants":
                    self.db[coll].create_index("matricule", unique=True)
                    self.db[coll].create_index("email", unique=True)
                elif coll == "matieres":
                    self.db[coll].create_index("code", unique=True)
                elif coll == "presences":
                    self.db[coll].create_index([("seance_id", 1), ("matricule", 1)])
    
    def get_collection(self, collection_name):
        """Retourne une collection spécifique"""
        if self.db is None:
            raise Exception("Base de données non connectée. Appelez connect() d'abord.")
        return self.db[collection_name]
    
    # ========== OPERATIONS ETUDIANTS ==========
    
    def ajouter_etudiant(self, nom, level, matricule, email, titre="Etudiant", device_id=None):
        """Ajoute un étudiant ou délégué"""
        etudiant = {
            "nom": nom,
            "level": level,
            "matricule": matricule,
            "email": email,
            "titre": titre,
            "device_id": device_id,
            "date_creation": datetime.now()
        }
        try:
            result = self.db.etudiants.insert_one(etudiant)
            print(f"✓ {titre} ajouté: {nom}")
            return result.inserted_id
        except Exception as e:
            print(f"✗ Erreur lors de l'ajout: {e}")
            return None
    
    def obtenir_etudiant(self, matricule):
        """Récupère un étudiant par matricule"""
        return self.db.etudiants.find_one({"matricule": matricule})
    
    def obtenir_tous_etudiants(self, titre=None):
        """Récupère tous les étudiants ou filtre par titre (Etudiant/Delegue)"""
        query = {"titre": titre} if titre else {}
        return list(self.db.etudiants.find(query))
    
    def modifier_etudiant(self, matricule, updates):
        """Modifie un étudiant"""
        result = self.db.etudiants.update_one(
            {"matricule": matricule},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def supprimer_etudiant(self, matricule):
        """Supprime un étudiant"""
        result = self.db.etudiants.delete_one({"matricule": matricule})
        return result.deleted_count > 0
    
    def valider_etudiant(self, matricule, device_id):
        """Associe un device_id à un étudiant (validation)"""
        result = self.db.etudiants.update_one(
            {"matricule": matricule},
            {"$set": {"device_id": device_id}}
        )
        return result.modified_count > 0
    
    # ========== OPERATIONS MATIERES ==========
    
    def ajouter_matiere(self, titre, code, prof):
        """Ajoute une matière"""
        matiere = {
            "titre": titre,
            "code": code,
            "prof": prof,
            "date_creation": datetime.now()
        }
        try:
            result = self.db.matieres.insert_one(matiere)
            print(f"✓ Matière ajoutée: {titre}")
            return result.inserted_id
        except Exception as e:
            print(f"✗ Erreur lors de l'ajout de la matière: {e}")
            return None
    
    def obtenir_matiere(self, code):
        """Récupère une matière par code"""
        return self.db.matieres.find_one({"code": code})
    
    def obtenir_toutes_matieres(self):
        """Récupère toutes les matières"""
        return list(self.db.matieres.find())
    
    def modifier_matiere(self, code, updates):
        """Modifie une matière"""
        result = self.db.matieres.update_one(
            {"code": code},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def supprimer_matiere(self, code):
        """Supprime une matière"""
        result = self.db.matieres.delete_one({"code": code})
        return result.deleted_count > 0
    
    # ========== OPERATIONS SEANCES ==========
    
    def creer_seance(self, matiere_code, date, localisation, duree, delegue_matricule):
        """Crée une séance de cours"""
        seance = {
            "matiere_code": matiere_code,
            "date": date,
            "localisation": localisation,
            "duree": duree,
            "delegue_matricule": delegue_matricule,
            "latitude": None,
            "longitude": None,
            "presences": [],
            "absences": [],
            "statut": "en_cours",
            "date_creation": datetime.now()
        }
        try:
            result = self.db.seances.insert_one(seance)
            print(f"✓ Séance créée pour {matiere_code}")
            return result.inserted_id
        except Exception as e:
            print(f"✗ Erreur lors de la création de la séance: {e}")
            return None
    
    def obtenir_seance(self, seance_id):
        """Récupère une séance par ID"""
        from bson import ObjectId
        return self.db.seances.find_one({"_id": ObjectId(seance_id)})
    
    def obtenir_seances_actives(self):
        """Récupère toutes les séances en cours et non expirées"""
        from datetime import datetime, timedelta
        
        seances = list(self.db.seances.find({"statut": "en_cours"}))
        seances_actives = []
        
        for seance in seances:
            temps_ecoule = datetime.now() - seance["date_creation"]
            duree_totale = timedelta(minutes=seance["duree"])
            
            if temps_ecoule < duree_totale:
                seances_actives.append(seance)
            else:
                from bson import ObjectId
                self.db.seances.update_one(
                    {"_id": seance["_id"]},
                    {"$set": {"statut": "terminee"}}
                )
        
        return seances_actives
    
    def obtenir_toutes_seances(self):
        """Récupère toutes les séances"""
        return list(self.db.seances.find())
    
    def marquer_presence(self, seance_id, matricule, present=True):
        """Marque la présence ou l'absence d'un étudiant"""
        from bson import ObjectId
        if present:
            result = self.db.seances.update_one(
                {"_id": ObjectId(seance_id)},
                {
                    "$addToSet": {"presences": matricule},
                    "$pull": {"absences": matricule}
                }
            )
        else:
            result = self.db.seances.update_one(
                {"_id": ObjectId(seance_id)},
                {
                    "$addToSet": {"absences": matricule},
                    "$pull": {"presences": matricule}
                }
            )
        return result.modified_count > 0
    
    def terminer_seance(self, seance_id):
        """Marque une séance comme terminée"""
        from bson import ObjectId
        result = self.db.seances.update_one(
            {"_id": ObjectId(seance_id)},
            {"$set": {"statut": "terminee", "date_fin": datetime.now()}}
        )
        return result.modified_count > 0
    
    def supprimer_seance(self, seance_id):
        """Supprime une séance"""
        from bson import ObjectId
        result = self.db.seances.delete_one({"_id": ObjectId(seance_id)})
        return result.deleted_count > 0
    
    def mettre_a_jour_position_seance(self, seance_id, latitude, longitude):
        """Met à jour la position GPS de la séance (position du délégué)"""
        from bson import ObjectId
        result = self.db.seances.update_one(
            {"_id": ObjectId(seance_id)},
            {"$set": {"latitude": latitude, "longitude": longitude}}
        )
        return result.modified_count > 0
    
    # ========== OPERATIONS PRESENCES ==========
    
    def enregistrer_presence(self, seance_id, matricule, nom, device_id, 
                            latitude=None, longitude=None, statut="present"):
        """Enregistre une présence d'étudiant"""
        presence = {
            "seance_id": str(seance_id),
            "matricule": matricule,
            "nom": nom,
            "device_id": device_id,
            "latitude": latitude,
            "longitude": longitude,
            "statut": statut,
            "date_presence": datetime.now(),
            "validee": False
        }
        try:
            result = self.db.presences.insert_one(presence)
            print(f"✓ Présence enregistrée pour {nom}")
            return result.inserted_id
        except Exception as e:
            print(f"✗ Erreur lors de l'enregistrement: {e}")
            return None
    
    def valider_presence(self, presence_id, validee=True):
        """Valide ou invalide une présence"""
        from bson import ObjectId
        result = self.db.presences.update_one(
            {"_id": ObjectId(presence_id)},
            {"$set": {"validee": validee}}
        )
        return result.modified_count > 0
    
    def obtenir_presences_seance(self, seance_id):
        """Récupère toutes les présences d'une séance"""
        return list(self.db.presences.find({"seance_id": str(seance_id)}))
    
    def obtenir_presence_etudiant(self, seance_id, matricule):
        """Récupère la présence d'un étudiant pour une séance"""
        return self.db.presences.find_one({
            "seance_id": str(seance_id),
            "matricule": matricule
        })
    
    def verifier_presence_validee(self, seance_id, matricule, device_id, 
                                   lat_etudiant, lon_etudiant, rayon_max=20.0):
        """
        Vérifie si une présence peut être validée
        EXCEPTION: Les délégués peuvent enregistrer depuis n'importe quel appareil
        Retourne (True, message) si validée, (False, message) sinon
        """
        from utils import calculer_distance
        
        etudiant = self.obtenir_etudiant(matricule)
        if not etudiant:
            return False, "Étudiant non trouvé"
        
        if etudiant.get("titre") == "Delegue":
            return True, "Présence validée (Délégué)"
        
        device_id_enregistre = etudiant.get("device_id")
        if not device_id_enregistre:
            return False, "Vous devez d'abord vous VALIDER (associer cet appareil)"
        
        if device_id_enregistre != device_id:
            return False, "ID de l'appareil non reconnu. Veuillez vous valider d'abord."
        
        from bson import ObjectId
        seance = self.obtenir_seance(str(seance_id))
        if not seance:
            return False, "Séance non trouvée"
        
        lat_delegue = seance.get("latitude")
        lon_delegue = seance.get("longitude")
        
        if lat_delegue and lon_delegue and lat_etudiant and lon_etudiant:
            distance = calculer_distance(
                lat_etudiant, lon_etudiant,
                lat_delegue, lon_delegue
            )
            if distance > rayon_max:
                return False, f"Vous êtes trop loin ({distance:.0f}m). Rayon max: {rayon_max}m"
        
        return True, "Présence validée avec succès!"
    
    def close(self):
        """Ferme la connexion à MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Connexion MongoDB fermée")


# Instance globale pour utilisation dans l'application
db = MongoDB()
