import flet as ft
from database import db
from utils import obtenir_position_automatique, obtenir_id_appareil
from datetime import datetime


class page2_etudiant:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Etudiant"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.seance_active = None
        
    def Head(self):
        return ft.AppBar(
            leading=ft.Icon(
                ft.Icons.SCHOOL_ROUNDED,
                color=ft.Colors.WHITE,
                size=30
            ),
            leading_width=60,
            title=ft.Row([
                ft.Text(
                    "Presence Plus",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                ft.Container(
                    content=ft.Text(
                        "Étudiant",
                        size=14,
                        color=ft.Colors.WHITE70,
                        weight=ft.FontWeight.W_400
                    ),
                    padding=ft.padding.only(left=10, top=5)
                ),
            ]),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.PERSON_ADD,
                    icon_color=ft.Colors.WHITE,
                    icon_size=28,
                    tooltip="Se valider",
                    on_click=lambda e: self.valider_etudiant()
                )
            ],
            bgcolor=ft.Colors.BLUE_700,
            elevation=4,
            center_title=False,
        )
    
    def On_est_au_Cours(self):
        """Vérifie s'il y a une séance active"""
        seances_actives = db.obtenir_seances_actives()
        if seances_actives:
            self.seance_active = seances_actives[0]
            return True
        return False
    
    def Body(self):
        """Corps principal de la page"""
        controls = [
            # Logo en haut
            ft.Container(
                content=ft.Image(
                    src="Logo.png",
                    width=120,
                    height=120,
                    fit=ft.ImageFit.CONTAIN,
                ),
                width=140,
                height=140,
                border_radius=70,
                bgcolor=ft.Colors.WHITE,
                padding=10,
                shadow=ft.BoxShadow(
                    spread_radius=2,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_400),
                    offset=ft.Offset(0, 4),
                ),
                margin=ft.margin.only(bottom=30),
            ),
            
            # Titre de bienvenue
            ft.Text(
                "Bienvenue sur Presence Plus",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN_900,
            ),
            ft.Container(height=20),
        ]
        
        # Vérifier s'il y a une séance active
        if not self.On_est_au_Cours():
            # Aucune séance en cours
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.EVENT_BUSY, size=80, color=ft.Colors.ORANGE_400),
                        ft.Container(height=20),
                        ft.Text(
                            "Séance d'aujourd'hui pas créée",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Aucune séance n'est en cours pour le moment.\nVeuillez attendre que le délégué crée une séance.",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                    border_radius=15,
                    bgcolor=ft.Colors.ORANGE_50,
                    border=ft.border.all(2, ft.Colors.ORANGE_200),
                )
            )
        else:
            # Séance en cours - vérifier si l'étudiant a déjà marqué présent
            seance = self.seance_active
            matiere = db.obtenir_matiere(seance["matiere_code"])
            if not matiere:
                controls.append(ft.Text(
                    "Erreur: séance ou matière introuvable",
                    size=16, color=ft.Colors.RED_600
                ))
                return ft.Column(controls, alignment=ft.MainAxisAlignment.START,
                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                 scroll=ft.ScrollMode.ALWAYS, expand=True)

            # Obtenir le device_id actuel
            device_id_actuel = obtenir_id_appareil(self.page)
            
            # Chercher si ce device_id a déjà marqué présent
            deja_present = False
            nom_etudiant_present = None
            
            # Récupérer toutes les présences de cette séance
            presences = db.obtenir_presences_seance(str(self.seance_active["_id"]))
            
            for presence in presences:
                if presence.get("device_id") == device_id_actuel:
                    deja_present = True
                    nom_etudiant_present = presence.get("nom")
                    break
            
            # Informations sur la séance
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("📚 Séance en cours", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                        ft.Container(height=10),
                        ft.Text(f"Matière: {matiere['titre']}", size=15, color=ft.Colors.BLACK87),
                        ft.Text(f"Localisation: {seance['localisation']}", size=14, color=ft.Colors.BLACK54),
                        ft.Text(f"Durée: {seance['duree']} minutes", size=14, color=ft.Colors.BLACK54),
                    ]),
                    padding=20,
                    border_radius=12,
                    bgcolor=ft.Colors.GREEN_50,
                    border=ft.border.all(2, ft.Colors.GREEN_200),
                    margin=ft.margin.only(bottom=20),
                )
            )
            
            if deja_present:
                # L'étudiant a déjà marqué présent - afficher un message de confirmation
                controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=100, color=ft.Colors.GREEN_600),
                            ft.Container(height=15),
                            ft.Text(
                                "✅ Présence Confirmée",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                f"Bonjour {nom_etudiant_present}!",
                                size=18,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREEN_800,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=5),
                            ft.Text(
                                "Votre présence a déjà été enregistrée pour cette séance.",
                                size=14,
                                color=ft.Colors.BLACK54,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_600, size=20),
                                    ft.Text(
                                        "Vous pouvez fermer l'application",
                                        size=13,
                                        color=ft.Colors.BLUE_700,
                                        italic=True,
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.Colors.BLUE_50,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        border_radius=15,
                        bgcolor=ft.Colors.GREEN_50,
                        border=ft.border.all(3, ft.Colors.GREEN_300),
                        shadow=ft.BoxShadow(
                            spread_radius=2,
                            blur_radius=20,
                            color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_400),
                            offset=ft.Offset(0, 4),
                        ),
                    )
                )
            else:
                # Bouton pour marquer présence
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=30),
                            ft.Text("Marquer ma présence", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        width=300,
                        height=80,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        bgcolor=ft.Colors.GREEN_600,
                        ink=True,
                        on_click=lambda e: self.marquer_presence(),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                            offset=ft.Offset(0, 5),
                        ),
                    )
                )
        
        return ft.Column(
            controls,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )
    
    def valider_etudiant(self):
        """Dialog pour valider un étudiant (associer device_id)"""
        print("🔵 Validation étudiant")
        
        # Récupérer tous les étudiants
        etudiants = db.obtenir_tous_etudiants(titre="Etudiant")
        
        # Créer la liste avec RadioButtons
        radio_group = ft.RadioGroup(content=ft.Column())
        
        for etudiant in etudiants:
            # Vérifier si déjà validé
            est_valide = etudiant.get("device_id") is not None
            
            radio_group.content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Radio(
                            value=etudiant["matricule"],
                            label="",
                        ),
                        ft.Icon(
                            ft.Icons.VERIFIED_USER if est_valide else ft.Icons.PERSON, 
                            color=ft.Colors.GREEN_700 if est_valide else ft.Colors.BLUE_700, 
                            size=30
                        ),
                        ft.Column([
                            ft.Text(
                                etudiant["nom"], 
                                weight=ft.FontWeight.BOLD, 
                                size=16,
                                color=ft.Colors.BLACK87
                            ),
                            ft.Text(
                                f"Matricule: {etudiant['matricule']} • Niveau: {etudiant['level']}", 
                                size=13, 
                                color=ft.Colors.BLACK54
                            ),
                            ft.Text(
                                "✓ Déjà validé" if est_valide else "Non validé",
                                size=12,
                                color=ft.Colors.GREEN_600 if est_valide else ft.Colors.ORANGE_600,
                                italic=True
                            ),
                        ], spacing=2, expand=True),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREEN_200 if est_valide else ft.Colors.BLUE_200),
                    border_radius=8,
                    bgcolor=ft.Colors.GREEN_50 if est_valide else ft.Colors.WHITE,
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def valider_selection(e):
            if not radio_group.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner votre nom!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Obtenir l'ID de l'appareil
            device_id = obtenir_id_appareil(self.page)
            
            # Vérifier si ce device_id est déjà utilisé par quelqu'un d'autre
            tous_etudiants = db.obtenir_tous_etudiants()
            device_deja_utilise = False
            personne_avec_device = None
            
            for etud in tous_etudiants:
                if etud.get("device_id") == device_id and etud["matricule"] != radio_group.value:
                    device_deja_utilise = True
                    personne_avec_device = etud["nom"]
                    break
            
            if device_deja_utilise:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Cet appareil est déjà associé à {personne_avec_device}!\n\nUn appareil ne peut être utilisé que par une seule personne."),
                    bgcolor=ft.Colors.RED,
                    duration=5000
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Valider l'étudiant
            result = db.valider_etudiant(radio_group.value, device_id)
            
            if result:
                etudiant = db.obtenir_etudiant(radio_group.value)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ {etudiant['nom']}, vous êtes maintenant validé!"),
                    bgcolor=ft.Colors.GREEN
                )
                dialog.open = False
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Erreur lors de la validation"),
                    bgcolor=ft.Colors.RED
                )
            
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.VERIFIED_USER, color=ft.Colors.GREEN_700, size=30),
                ft.Text(
                    "Valider mon compte",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.GREEN_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Sélectionnez votre nom pour associer cet appareil à votre compte:",
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=10),
                    radio_group if etudiants else ft.Container(
                        content=ft.Text(
                            "Aucun étudiant disponible", 
                            italic=True, 
                            color=ft.Colors.GREY_700,
                            size=16
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    )
                ], scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=fermer_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "✓ Valider",
                    on_click=valider_selection,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def marquer_presence(self):
        """Dialog pour marquer la présence"""
        print("🔵 Marquage présence")
        
        # Récupérer tous les étudiants VALIDÉS
        tous_etudiants = db.obtenir_tous_etudiants(titre="Etudiant")
        etudiants_valides = [e for e in tous_etudiants if e.get("device_id") is not None]
        
        # Créer la liste avec RadioButtons
        radio_group = ft.RadioGroup(content=ft.Column())
        
        for etudiant in etudiants_valides:
            radio_group.content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Radio(
                            value=etudiant["matricule"],
                            label="",
                        ),
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREEN_700, size=30),
                        ft.Column([
                            ft.Text(
                                etudiant["nom"], 
                                weight=ft.FontWeight.BOLD, 
                                size=16,
                                color=ft.Colors.BLACK87
                            ),
                            ft.Text(
                                f"Matricule: {etudiant['matricule']}", 
                                size=13, 
                                color=ft.Colors.BLACK54
                            ),
                        ], spacing=2, expand=True),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def enregistrer_presence(e):
            if not radio_group.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner votre nom!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Vérifier si l'étudiant a déjà marqué présent pour cette séance
            presence_existante = db.obtenir_presence_etudiant(
                str(self.seance_active["_id"]),
                radio_group.value
            )
            
            if presence_existante:
                etudiant = db.obtenir_etudiant(radio_group.value)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ {etudiant['nom']}, vous êtes déjà présent(e)!\n\nVous ne pouvez marquer présent qu'une seule fois par séance."),
                    bgcolor=ft.Colors.ORANGE,
                    duration=5000
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Obtenir l'ID de l'appareil actuel
            device_id_actuel = obtenir_id_appareil(self.page)
            
            # Obtenir la position GPS
            lat, lon = obtenir_position_automatique(self.page, methode="ip")
            
            # Vérifier la présence (device_id + localisation)
            validee, message = db.verifier_presence_validee(
                seance_id=str(self.seance_active["_id"]),
                matricule=radio_group.value,
                device_id=device_id_actuel,
                lat_etudiant=lat,
                lon_etudiant=lon,
                rayon_max=20.0
            )
            
            if validee:
                # Enregistrer la présence
                etudiant = db.obtenir_etudiant(radio_group.value)
                db.enregistrer_presence(
                    seance_id=str(self.seance_active["_id"]),
                    matricule=radio_group.value,
                    nom=etudiant["nom"],
                    device_id=device_id_actuel,
                    latitude=lat,
                    longitude=lon,
                    statut="present"
                )
                
                # Marquer comme validée
                presence = db.obtenir_presence_etudiant(
                    str(self.seance_active["_id"]),
                    radio_group.value
                )
                if presence:
                    db.valider_presence(str(presence["_id"]), True)
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Présence enregistrée avec succès!"),
                    bgcolor=ft.Colors.GREEN
                )
                dialog.open = False
                self.page.snack_bar.open = True
                self.page.update()
                # Rafraîchir la page pour afficher la confirmation
                self.page.clean()
                self.page.appbar = self.Head()
                self.page.add(self.Body())
                self.page.update()
                return
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ {message}\n\nIl y a un problème, veuillez contacter le Délégué"),
                    bgcolor=ft.Colors.RED,
                    duration=5000
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=30),
                ft.Text(
                    "Marquer ma présence",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.GREEN_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Sélectionnez votre nom:",
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=10),
                    radio_group if etudiants_valides else ft.Container(
                        content=ft.Text(
                            "Aucun étudiant validé disponible", 
                            italic=True, 
                            color=ft.Colors.GREY_700,
                            size=16
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    )
                ], scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=fermer_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "✓ Présence",
                    on_click=enregistrer_presence,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def choisir_mode_identification(self):
        """Workflow pour choisir si on est délégué ou étudiant"""
        print("🔵 Choix du mode d'identification")
        
        mode_choisi = ft.Ref[str]()
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def valider_mode(e):
            if mode_choisi.current.value == "delegue":
                # Mode délégué - demander authentification
                dialog.open = False
                self.page.update()
                self.authentifier_delegue()
            else:
                # Mode étudiant - pas d'authentification
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=ft.Colors.BLUE_700, size=30),
                ft.Text(
                    "Mode d'identification",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.BLUE_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Veuillez choisir votre mode d'accès:",
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=20),
                    ft.RadioGroup(
                        ref=mode_choisi,
                        content=ft.Column([
                            ft.Container(
                                content=ft.Row([
                                    ft.Radio(value="etudiant", label=""),
                                    ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.BLUE_700, size=30),
                                    ft.Column([
                                        ft.Text(
                                            "Je suis un étudiant",
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                            color=ft.Colors.BLACK87
                                        ),
                                        ft.Text(
                                            "Accès standard pour marquer ma présence",
                                            size=13,
                                            color=ft.Colors.BLACK54
                                        ),
                                    ], spacing=2, expand=True),
                                ]),
                                padding=15,
                                border=ft.border.all(1, ft.Colors.BLUE_200),
                                border_radius=8,
                                bgcolor=ft.Colors.WHITE,
                                margin=ft.margin.only(bottom=10),
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Radio(value="delegue", label=""),
                                    ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=ft.Colors.ORANGE_700, size=30),
                                    ft.Column([
                                        ft.Text(
                                            "Je suis un délégué",
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                            color=ft.Colors.BLACK87
                                        ),
                                        ft.Text(
                                            "Accès privilégié - Authentification requise",
                                            size=13,
                                            color=ft.Colors.BLACK54
                                        ),
                                    ], spacing=2, expand=True),
                                ]),
                                padding=15,
                                border=ft.border.all(1, ft.Colors.ORANGE_200),
                                border_radius=8,
                                bgcolor=ft.Colors.WHITE,
                            ),
                        ])
                    ),
                ], scroll=ft.ScrollMode.AUTO),
                width=500,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=fermer_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "✓ Continuer",
                    on_click=valider_mode,
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def authentifier_delegue(self):
        """Authentification pour les délégués"""
        print("🔵 Authentification délégué")
        
        # Récupérer tous les délégués
        delegues = db.obtenir_tous_etudiants(titre="Delegue")
        
        if not delegues:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Aucun délégué enregistré dans le système"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Créer la liste avec RadioButtons
        radio_group = ft.RadioGroup(content=ft.Column())
        
        for delegue in delegues:
            radio_group.content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Radio(
                            value=delegue["matricule"],
                            label="",
                        ),
                        ft.Icon(ft.Icons.VERIFIED_USER, color=ft.Colors.ORANGE_700, size=30),
                        ft.Column([
                            ft.Text(
                                delegue["nom"],
                                weight=ft.FontWeight.BOLD,
                                size=16,
                                color=ft.Colors.BLACK87
                            ),
                            ft.Text(
                                f"Matricule: {delegue['matricule']}",
                                size=13,
                                color=ft.Colors.BLACK54
                            ),
                        ], spacing=2, expand=True),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.ORANGE_200),
                    border_radius=8,
                    bgcolor=ft.Colors.ORANGE_50,
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def valider_auth(e):
            if not radio_group.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner votre nom!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            # Obtenir l'appareil actuel
            device_id_actuel = obtenir_id_appareil(self.page)
            
            # Vérifier le délégué
            delegue = db.obtenir_etudiant(radio_group.value)
            
            # Vérifier si le délégué a déjà un device_id enregistré
            if delegue.get("device_id") is None:
                # Première connexion - enregistrer l'appareil
                db.valider_etudiant(radio_group.value, device_id_actuel)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Bienvenue {delegue['nom']} (Délégué)\n\n🔐 Cet appareil est maintenant enregistré comme votre appareil autorisé."),
                    bgcolor=ft.Colors.GREEN,
                    duration=5000
                )
                self.page.snack_bar.open = True
                dialog.open = False
                self.page.update()
            elif delegue.get("device_id") == device_id_actuel:
                # Appareil correct - autoriser l'accès
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Bienvenue {delegue['nom']} (Délégué)"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                dialog.open = False
                self.page.update()
            else:
                # Mauvais appareil - refuser l'accès
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Accès refusé!\n\nVous ne pouvez vous connecter qu'avec l'appareil enregistré.\n\nCe délégué est lié à un autre appareil."),
                    bgcolor=ft.Colors.RED,
                    duration=5000
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=ft.Colors.ORANGE_700, size=30),
                ft.Text(
                    "Authentification Délégué",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.ORANGE_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Sélectionnez votre nom pour vous authentifier:",
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=10),
                    radio_group
                ], scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=fermer_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "✓ S'authentifier",
                    on_click=valider_auth,
                    bgcolor=ft.Colors.ORANGE_600,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def build(self, skip_identification=False):
        # Afficher le workflow d'identification au démarrage (sauf si skip_identification=True)
        if not skip_identification:
            self.choisir_mode_identification()
        
        self.page.appbar = self.Head()
        body = self.Body()
        self.page.add(body)
        self.page.update()


def main(page: ft.Page):
    p2 = page2_etudiant(page)
    p2.build()


if __name__ == "__main__":
    ft.app(target=main)