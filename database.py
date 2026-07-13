import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def _avec_id_mongo(ligne):
    """Ajoute une clé '_id' (alias de 'id') pour rester compatible avec le
    code existant qui manipulait des documents Mongo."""
    if ligne is None:
        return None
    ligne = dict(ligne)
    ligne["_id"] = ligne.get("id")
    return ligne


class SupabaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseDB, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = None
        self.initialized = True

    def configure(self, url, key):
        """Définit l'URL et la clé Supabase (utilisé par l'écran de configuration)."""
        self.url = url
        self.key = key
        self.client = None  # force une reconnexion avec les nouvelles infos

    def connect(self):
        """Établit la connexion à Supabase"""
        if self.client is not None:
            return True
        if not self.url or not self.key:
            print("✗ SUPABASE_URL / SUPABASE_KEY manquants")
            return False
        try:
            self.client = create_client(self.url, self.key)
            # Test de connexion
            self.client.table("etudiants").select("id").limit(1).execute()
            print("✓ Connexion à Supabase réussie!")
            return True
        except Exception as e:
            print(f"✗ Erreur de connexion à Supabase: {e}")
            self.client = None
            return False

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
        }
        try:
            result = self.client.table("etudiants").insert(etudiant).execute()
            print(f"✓ {titre} ajouté: {nom}")
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"✗ Erreur lors de l'ajout: {e}")
            return None

    def obtenir_etudiant(self, matricule):
        """Récupère un étudiant par matricule"""
        result = self.client.table("etudiants").select("*").eq("matricule", matricule).limit(1).execute()
        return _avec_id_mongo(result.data[0]) if result.data else None

    def obtenir_tous_etudiants(self, titre=None):
        """Récupère tous les étudiants ou filtre par titre (Etudiant/Delegue)"""
        query = self.client.table("etudiants").select("*")
        if titre:
            query = query.eq("titre", titre)
        result = query.execute()
        return [_avec_id_mongo(r) for r in result.data]

    def modifier_etudiant(self, matricule, updates):
        """Modifie un étudiant"""
        result = self.client.table("etudiants").update(updates).eq("matricule", matricule).execute()
        return len(result.data) > 0

    def supprimer_etudiant(self, matricule):
        """Supprime un étudiant"""
        result = self.client.table("etudiants").delete().eq("matricule", matricule).execute()
        return len(result.data) > 0

    def valider_etudiant(self, matricule, device_id):
        """Associe un device_id à un étudiant (validation)"""
        result = self.client.table("etudiants").update({"device_id": device_id}).eq("matricule", matricule).execute()
        return len(result.data) > 0

    # ========== OPERATIONS MATIERES ==========

    def ajouter_matiere(self, titre, code, prof):
        """Ajoute une matière"""
        matiere = {"titre": titre, "code": code, "prof": prof}
        try:
            result = self.client.table("matieres").insert(matiere).execute()
            print(f"✓ Matière ajoutée: {titre}")
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"✗ Erreur lors de l'ajout de la matière: {e}")
            return None

    def obtenir_matiere(self, code):
        """Récupère une matière par code"""
        result = self.client.table("matieres").select("*").eq("code", code).limit(1).execute()
        return _avec_id_mongo(result.data[0]) if result.data else None

    def obtenir_toutes_matieres(self):
        """Récupère toutes les matières"""
        result = self.client.table("matieres").select("*").execute()
        return [_avec_id_mongo(r) for r in result.data]

    def modifier_matiere(self, code, updates):
        """Modifie une matière"""
        result = self.client.table("matieres").update(updates).eq("code", code).execute()
        return len(result.data) > 0

    def supprimer_matiere(self, code):
        """Supprime une matière"""
        result = self.client.table("matieres").delete().eq("code", code).execute()
        return len(result.data) > 0

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
        }
        try:
            result = self.client.table("seances").insert(seance).execute()
            print(f"✓ Séance créée pour {matiere_code}")
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"✗ Erreur lors de la création de la séance: {e}")
            return None

    def obtenir_seance(self, seance_id):
        """Récupère une séance par ID"""
        result = self.client.table("seances").select("*").eq("id", seance_id).limit(1).execute()
        return _avec_id_mongo(result.data[0]) if result.data else None

    def obtenir_seances_actives(self):
        """Récupère toutes les séances en cours et non expirées"""
        result = self.client.table("seances").select("*").eq("statut", "en_cours").execute()
        seances_actives = []

        for seance in result.data:
            date_creation = datetime.fromisoformat(seance["date_creation"].replace("Z", "+00:00"))
            temps_ecoule = datetime.now(date_creation.tzinfo) - date_creation
            duree_totale = timedelta(minutes=seance["duree"])

            if temps_ecoule < duree_totale:
                seances_actives.append(_avec_id_mongo(seance))
            else:
                self.client.table("seances").update({"statut": "terminee"}).eq("id", seance["id"]).execute()

        return seances_actives

    def obtenir_toutes_seances(self):
        """Récupère toutes les séances"""
        result = self.client.table("seances").select("*").execute()
        return [_avec_id_mongo(r) for r in result.data]

    def obtenir_seances_matiere_periode(self, matiere_code, debut, fin):
        """Récupère les séances d'une matière créées entre deux dates (inclusives)"""
        result = (
            self.client.table("seances")
            .select("*")
            .eq("matiere_code", matiere_code)
            .gte("date_creation", debut.isoformat())
            .lte("date_creation", fin.isoformat())
            .order("date_creation")
            .execute()
        )
        return [_avec_id_mongo(r) for r in result.data]

    def marquer_presence(self, seance_id, matricule, present=True):
        """Marque la présence ou l'absence d'un étudiant dans les listes de la séance"""
        seance = self.obtenir_seance(seance_id)
        if not seance:
            return False

        presences = set(seance.get("presences") or [])
        absences = set(seance.get("absences") or [])

        if present:
            presences.add(matricule)
            absences.discard(matricule)
        else:
            absences.add(matricule)
            presences.discard(matricule)

        result = (
            self.client.table("seances")
            .update({"presences": list(presences), "absences": list(absences)})
            .eq("id", seance_id)
            .execute()
        )
        return len(result.data) > 0

    def terminer_seance(self, seance_id):
        """Marque une séance comme terminée"""
        result = (
            self.client.table("seances")
            .update({"statut": "terminee", "date_fin": datetime.now().isoformat()})
            .eq("id", seance_id)
            .execute()
        )
        return len(result.data) > 0

    def supprimer_seance(self, seance_id):
        """Supprime une séance"""
        result = self.client.table("seances").delete().eq("id", seance_id).execute()
        return len(result.data) > 0

    def mettre_a_jour_position_seance(self, seance_id, latitude, longitude):
        """Met à jour la position GPS de la séance (position du délégué)"""
        result = (
            self.client.table("seances")
            .update({"latitude": latitude, "longitude": longitude})
            .eq("id", seance_id)
            .execute()
        )
        return len(result.data) > 0

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
            "validee": False,
        }
        try:
            result = self.client.table("presences").insert(presence).execute()
            print(f"✓ Présence enregistrée pour {nom}")
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"✗ Erreur lors de l'enregistrement: {e}")
            return None

    def valider_presence(self, presence_id, validee=True):
        """Valide ou invalide une présence"""
        result = self.client.table("presences").update({"validee": validee}).eq("id", presence_id).execute()
        return len(result.data) > 0

    def obtenir_presences_seance(self, seance_id):
        """Récupère toutes les présences d'une séance"""
        result = self.client.table("presences").select("*").eq("seance_id", str(seance_id)).execute()
        return [_avec_id_mongo(r) for r in result.data]

    def obtenir_presence_etudiant(self, seance_id, matricule):
        """Récupère la présence d'un étudiant pour une séance"""
        result = (
            self.client.table("presences")
            .select("*")
            .eq("seance_id", str(seance_id))
            .eq("matricule", matricule)
            .limit(1)
            .execute()
        )
        return _avec_id_mongo(result.data[0]) if result.data else None

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
        """Ferme la connexion à Supabase (rien à fermer explicitement)"""
        self.client = None


# Instance globale pour utilisation dans l'application
db = SupabaseDB()
