"""
Modèles de données pour l'application Presence Plus
"""
from datetime import datetime
from typing import Optional, List

class Etudiant:
    """Modèle pour un étudiant"""
    def __init__(self, nom: str, level: str, matricule: str, email: str, titre: str = "Etudiant", device_id: str = None):
        self.nom = nom
        self.level = level
        self.matricule = matricule
        self.email = email
        self.titre = titre  # "Etudiant" ou "Delegue"
        self.device_id = device_id  # ID unique de l'appareil
        self.date_creation = datetime.now()
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour MongoDB"""
        return {
            "nom": self.nom,
            "level": self.level,
            "matricule": self.matricule,
            "email": self.email,
            "titre": self.titre,
            "device_id": self.device_id,
            "date_creation": self.date_creation
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Crée un objet Etudiant depuis un dictionnaire MongoDB"""
        if data is None:
            return None
        etudiant = Etudiant(
            nom=data.get("nom"),
            level=data.get("level"),
            matricule=data.get("matricule"),
            email=data.get("email"),
            titre=data.get("titre", "Etudiant"),
            device_id=data.get("device_id")
        )
        etudiant.date_creation = data.get("date_creation", datetime.now())
        return etudiant


class Delegue(Etudiant):
    """Modèle pour un délégué (hérite d'Etudiant)"""
    def __init__(self, nom: str, level: str, matricule: str, email: str, device_id: str = None):
        super().__init__(nom, level, matricule, email, titre="Delegue", device_id=device_id)


class Matiere:
    """Modèle pour une matière"""
    def __init__(self, titre: str, code: str, prof: str):
        self.titre = titre
        self.code = code
        self.prof = prof
        self.date_creation = datetime.now()
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour MongoDB"""
        return {
            "titre": self.titre,
            "code": self.code,
            "prof": self.prof,
            "date_creation": self.date_creation
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Crée un objet Matiere depuis un dictionnaire MongoDB"""
        if data is None:
            return None
        matiere = Matiere(
            titre=data.get("titre"),
            code=data.get("code"),
            prof=data.get("prof")
        )
        matiere.date_creation = data.get("date_creation", datetime.now())
        return matiere


class Seance:
    """Modèle pour une séance de cours"""
    def __init__(self, matiere_code: str, date: datetime, localisation: str, 
                 duree: int, delegue_matricule: str):
        self.matiere_code = matiere_code
        self.date = date
        self.localisation = localisation
        self.duree = duree  # en minutes
        self.delegue_matricule = delegue_matricule
        self.presences: List[str] = []  # Liste des matricules présents
        self.absences: List[str] = []   # Liste des matricules absents
        self.statut = "en_cours"  # "en_cours" ou "terminee"
        self.date_creation = datetime.now()
        self.date_fin: Optional[datetime] = None
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour MongoDB"""
        return {
            "matiere_code": self.matiere_code,
            "date": self.date,
            "localisation": self.localisation,
            "duree": self.duree,
            "delegue_matricule": self.delegue_matricule,
            "presences": self.presences,
            "absences": self.absences,
            "statut": self.statut,
            "date_creation": self.date_creation,
            "date_fin": self.date_fin
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Crée un objet Seance depuis un dictionnaire MongoDB"""
        if data is None:
            return None
        seance = Seance(
            matiere_code=data.get("matiere_code"),
            date=data.get("date"),
            localisation=data.get("localisation"),
            duree=data.get("duree"),
            delegue_matricule=data.get("delegue_matricule")
        )
        seance.presences = data.get("presences", [])
        seance.absences = data.get("absences", [])
        seance.statut = data.get("statut", "en_cours")
        seance.date_creation = data.get("date_creation", datetime.now())
        seance.date_fin = data.get("date_fin")
        return seance
    
    def marquer_presence(self, matricule: str, present: bool = True):
        """Marque la présence ou l'absence d'un étudiant"""
        if present:
            if matricule not in self.presences:
                self.presences.append(matricule)
            if matricule in self.absences:
                self.absences.remove(matricule)
        else:
            if matricule not in self.absences:
                self.absences.append(matricule)
            if matricule in self.presences:
                self.presences.remove(matricule)
    
    def terminer(self):
        """Termine la séance"""
        self.statut = "terminee"
        self.date_fin = datetime.now()
    
    def get_taux_presence(self) -> float:
        """Calcule le taux de présence en pourcentage"""
        total = len(self.presences) + len(self.absences)
        if total == 0:
            return 0.0
        return (len(self.presences) / total) * 100


class Presence:
    """Modèle pour une présence d'étudiant à une séance"""
    def __init__(self, seance_id: str, matricule: str, nom: str, 
                 device_id: str, latitude: float = None, longitude: float = None,
                 statut: str = "present"):
        self.seance_id = seance_id
        self.matricule = matricule
        self.nom = nom
        self.device_id = device_id
        self.latitude = latitude
        self.longitude = longitude
        self.statut = statut  # "present", "absent", "retard"
        self.date_presence = datetime.now()
        self.validee = False  # Sera True si localisation et device_id correspondent
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour MongoDB"""
        return {
            "seance_id": self.seance_id,
            "matricule": self.matricule,
            "nom": self.nom,
            "device_id": self.device_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "statut": self.statut,
            "date_presence": self.date_presence,
            "validee": self.validee
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Crée un objet Presence depuis un dictionnaire MongoDB"""
        if data is None:
            return None
        presence = Presence(
            seance_id=data.get("seance_id"),
            matricule=data.get("matricule"),
            nom=data.get("nom"),
            device_id=data.get("device_id"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            statut=data.get("statut", "present")
        )
        presence.date_presence = data.get("date_presence", datetime.now())
        presence.validee = data.get("validee", False)
        return presence
    
    def valider(self, device_id_enregistre: str, lat_delegue: float, 
                lon_delegue: float, rayon_max: float = 20.0) -> bool:
        """
        Valide la présence en vérifiant le device_id et la localisation
        Retourne True si validée, False sinon
        """
        from utils import calculer_distance
        
        # Vérifier le device_id
        if self.device_id != device_id_enregistre:
            return False
        
        # Vérifier la localisation (rayon de 20m)
        if self.latitude and self.longitude and lat_delegue and lon_delegue:
            distance = calculer_distance(
                self.latitude, self.longitude,
                lat_delegue, lon_delegue
            )
            if distance > rayon_max:
                return False
        
        self.validee = True
        return True
