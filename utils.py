"""
Utilitaires pour la géolocalisation et l'identification des appareils
"""
import uuid
import platform
from math import radians, sin, cos, sqrt, atan2
import flet as ft


def obtenir_id_appareil(page: ft.Page = None):
    """
    Génère un ID unique pour l'appareil.

    En mode web, la MAC address serait celle du serveur (identique pour
    tous les utilisateurs), donc on stocke un UUID par navigateur dans
    le client_storage. En mode desktop, on garde l'UUID basé sur la MAC.
    """
    if page is not None and getattr(page, "web", False):
        try:
            device_id = page.client_storage.get("presence_plus.device_id")
            if not device_id:
                device_id = str(uuid.uuid4())
                page.client_storage.set("presence_plus.device_id", device_id)
            return device_id
        except Exception as e:
            print(f"⚠️ client_storage indisponible, repli sur MAC: {e}")

    mac = uuid.getnode()
    device_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(mac)))
    return device_id


def calculer_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en mètres entre deux points GPS
    Utilise la formule de Haversine
    
    Args:
        lat1, lon1: Latitude et longitude du point 1
        lat2, lon2: Latitude et longitude du point 2
    
    Returns:
        Distance en mètres
    """
    R = 6371000  # Rayon de la Terre en mètres
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance


def obtenir_position_web(page: ft.Page, callback):
    """
    Obtient la position GPS via l'API de géolocalisation du navigateur (Web)
    
    Args:
        page: Page Flet
        callback: Fonction à appeler avec (latitude, longitude) ou None en cas d'erreur
    """
    js_code = """
    function getPosition() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    window.flet_gps_result = {
                        success: true,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    };
                },
                function(error) {
                    window.flet_gps_result = {
                        success: false,
                        error: error.message
                    };
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            window.flet_gps_result = {
                success: false,
                error: "Geolocation not supported"
            };
        }
    }
    getPosition();
    """
    
    try:
        page.evaluate_javascript(js_code)
        # Note: En production, il faudrait vérifier window.flet_gps_result
        # via un autre appel JavaScript ou un timer
    except Exception as e:
        print(f"Erreur géolocalisation web: {e}")
        callback(None, None)


def obtenir_position_ip():
    """
    Obtient une position approximative via l'adresse IP
    Moins précis mais fonctionne partout
    
    Returns:
        (latitude, longitude) ou (None, None) en cas d'erreur
    """
    try:
        import geocoder
        g = geocoder.ip('me')
        if g.ok:
            return g.lat, g.lng
    except ImportError:
        print("geocoder n'est pas installé. Installez avec: pip install geocoder")
    except Exception as e:
        print(f"Erreur géolocalisation IP: {e}")
    
    return None, None


def obtenir_position_automatique(page: ft.Page = None, methode="auto"):
    """
    Obtient la position GPS selon la plateforme
    
    Args:
        page: Page Flet (nécessaire pour web)
        methode: "web", "ip", ou "auto" (détection automatique)
    
    Returns:
        (latitude, longitude) ou (None, None)
    """
    if methode == "auto":
        # Détecter la plateforme
        if page and hasattr(page, 'web'):
            methode = "web"
        else:
            methode = "ip"
    
    if methode == "web" and page:
        # Pour le web, il faut utiliser un callback asynchrone
        # Cette version retourne None et utilise JavaScript
        print("Mode Web: utilisez obtenir_position_web() avec callback")
        return None, None
    
    elif methode == "ip":
        return obtenir_position_ip()
    
    else:
        print("Méthode de géolocalisation non reconnue")
        return None, None


def formater_position(latitude, longitude):
    """Formate les coordonnées GPS en chaîne lisible"""
    if latitude is None or longitude is None:
        return "Position inconnue"
    return f"{latitude:.6f}, {longitude:.6f}"


def est_dans_rayon(lat1, lon1, lat2, lon2, rayon_metres=20):
    """
    Vérifie si deux positions sont dans un rayon donné
    
    Args:
        lat1, lon1: Position 1
        lat2, lon2: Position 2
        rayon_metres: Rayon maximum en mètres (défaut: 20m)
    
    Returns:
        True si dans le rayon, False sinon
    """
    if None in [lat1, lon1, lat2, lon2]:
        return False
    
    distance = calculer_distance(lat1, lon1, lat2, lon2)
    return distance <= rayon_metres


# Informations sur la plateforme
def get_platform_info():
    """Retourne les informations sur la plateforme"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }


# ========== GÉNÉRATION PDF ==========

def generer_pdf_presences(matiere_code, mois, annee):
    """
    Génère un PDF professionnel avec les présences pour une matière et un mois donnés
    
    Args:
        matiere_code: Code de la matière
        mois: Mois (format "01" à "12")
        annee: Année (format "2024")
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from datetime import datetime, timedelta
    from calendar import monthrange
    from database import db
    import os
    
    try:
        # Récupérer la matière
        matiere = db.obtenir_matiere(matiere_code)
        if not matiere:
            return False, "Matière introuvable"
        
        # Récupérer tous les étudiants VALIDÉS
        tous_etudiants = db.obtenir_tous_etudiants(titre="Etudiant")
        etudiants_valides = [e for e in tous_etudiants if e.get("device_id") is not None]
        
        if not etudiants_valides:
            return False, "Aucun étudiant validé trouvé"
        
        # Trier par nom
        etudiants_valides.sort(key=lambda x: x["nom"])
        
        # Déterminer le dossier de téléchargement selon la plateforme
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == "Windows":
            download_folder = os.path.join(home, "Downloads")
        elif system == "Darwin":  # macOS
            download_folder = os.path.join(home, "Downloads")
        else:  # Linux et autres
            download_folder = os.path.join(home, "Downloads")
            # Alternative pour Linux
            if not os.path.exists(download_folder):
                download_folder = os.path.join(home, "Téléchargements")
        
        # Créer le dossier Presence_Plus
        presence_folder = os.path.join(download_folder, "Presence_Plus")
        os.makedirs(presence_folder, exist_ok=True)
        
        # Nom du fichier
        mois_noms = {
            "01": "Janvier", "02": "Fevrier", "03": "Mars",
            "04": "Avril", "05": "Mai", "06": "Juin",
            "07": "Juillet", "08": "Aout", "09": "Septembre",
            "10": "Octobre", "11": "Novembre", "12": "Decembre"
        }
        
        nom_fichier = f"{matiere['titre'].replace(' ', '_')}_{mois_noms[mois]}_{annee}.pdf"
        chemin_pdf = os.path.join(presence_folder, nom_fichier)
        
        # Créer le PDF en mode paysage pour plus d'espace
        doc = SimpleDocTemplate(
            chemin_pdf,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#424242'),
            spaceAfter=5,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#616161'),
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Contenu du PDF
        story = []
        
        # En-tête
        story.append(Paragraph("FICHE DE PRÉSENCE", title_style))
        story.append(Paragraph(f"{matiere['titre']}", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Informations sur la matière
        story.append(Paragraph(f"<b>Code de la matière :</b> {matiere['code']}", info_style))
        story.append(Paragraph(f"<b>Professeur :</b> {matiere['prof']}", info_style))
        story.append(Paragraph(f"<b>Période :</b> {mois_noms[mois]} {annee}", info_style))
        story.append(Paragraph(f"<b>Classe :</b> {etudiants_valides[0]['level'] if etudiants_valides else 'N/A'}", info_style))
        story.append(Paragraph(f"<b>Nombre d'étudiants :</b> {len(etudiants_valides)}", info_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Récupérer toutes les séances du mois
        premier_jour = datetime(int(annee), int(mois), 1)
        nb_jours = monthrange(int(annee), int(mois))[1]
        dernier_jour = datetime(int(annee), int(mois), nb_jours, 23, 59, 59)
        
        seances = db.obtenir_seances_matiere_periode(matiere_code, premier_jour, dernier_jour)

        if not seances:
            return False, f"Impossible d'exporter: Aucune séance trouvée pour {matiere['titre']} en {mois_noms[mois]} {annee}"
        else:
            # Créer le tableau
            # En-tête: Nom | Date1 | Date2 | Date3 | ... | Total
            dates_seances = [
                datetime.fromisoformat(s["date_creation"].replace("Z", "+00:00")).strftime("%d/%m")
                for s in seances
            ]
            header = ["N°", "Nom de l'étudiant", "Matricule"] + dates_seances + ["Total"]

            # Données du tableau
            data = [header]

            for idx, etudiant in enumerate(etudiants_valides, 1):
                row = [str(idx), etudiant["nom"], etudiant["matricule"]]

                nb_presences = 0
                for seance in seances:
                    # Vérifier si l'étudiant était présent
                    presence = db.obtenir_presence_etudiant(str(seance["_id"]), etudiant["matricule"])

                    if presence and presence.get("validee"):
                        row.append("✓")
                        nb_presences += 1
                    else:
                        row.append("✗")
                
                # Total
                row.append(f"{nb_presences}/{len(seances)}")
                data.append(row)
            
            # Créer le tableau avec style professionnel
            # repeatRows=1 répète l'en-tête sur chaque nouvelle page
            table = Table(data, repeatRows=1, splitByRow=True)
            
            # Style du tableau
            table_style = TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Corps du tableau
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (2, -1), 'LEFT'),  # Nom et matricule à gauche
                ('ALIGN', (3, 1), (-1, -1), 'CENTER'),  # Présences au centre
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                
                # Grille
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1565C0')),
                
                # Colonne Total en gras
                ('FONTNAME', (-1, 1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (-1, 0), (-1, -1), colors.HexColor('#E3F2FD')),
                
                # Alternance de couleurs pour les lignes
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ])
            
            table.setStyle(table_style)
            
            # Ajouter numérotation des pages
            def ajouter_numero_page(canvas, doc):
                """Ajoute le numéro de page en bas de chaque page"""
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.saveState()
                canvas.setFont('Helvetica', 9)
                canvas.setFillColor(colors.grey)
                canvas.drawCentredString(
                    doc.pagesize[0] / 2,
                    1*cm,
                    text
                )
                canvas.restoreState()
            
            story.append(table)
            
            # Légende
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("<b>Légende :</b> ✓ = Présent | ✗ = Absent", info_style))
        
        # Pied de page
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Presence Plus",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
        ))
        
        # Générer le PDF avec numérotation des pages
        doc.build(story, onFirstPage=ajouter_numero_page, onLaterPages=ajouter_numero_page)
        
        return True, f"PDF généré avec succès!\n\nEmplacement: {chemin_pdf}"
        
    except Exception as e:
        print(f"❌ Erreur génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Erreur lors de la génération: {str(e)}"
