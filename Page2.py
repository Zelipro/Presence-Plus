import flet as ft
from database import db
from models import Seance, Matiere
from datetime import datetime


class page2:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Delegue"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.seance_active = None
        
    def Head(self):
        return ft.AppBar(
            leading=ft.Icon(
                ft.Icons.LOCATION_ON_ROUNDED,
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
                        "Délégué",
                        size=14,
                        color=ft.Colors.WHITE70,
                        weight=ft.FontWeight.W_400
                    ),
                    padding=ft.padding.only(left=10, top=5)
                ),
            ]),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.PICTURE_AS_PDF,
                    icon_color=ft.Colors.WHITE,
                    icon_size=28,
                    tooltip="Exporter en PDF",
                    on_click=lambda e: self.exporter_pdf()
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_color=ft.Colors.WHITE,
                    icon_size=28,
                    tooltip="Menu Délégué",
                    items=[
                        ft.PopupMenuItem(
                            text="➕ Ajouter un délégué",
                            icon=ft.Icons.PERSON_ADD,
                            on_click=lambda e: self.ajouter_delegue()
                        ),
                        ft.PopupMenuItem(
                            text="👥 Liste des délégués",
                            icon=ft.Icons.PEOPLE,
                            on_click=lambda e: self.afficher_delegues()
                        ),
                    ],
                )
            ],
            bgcolor=ft.Colors.BLUE_700,
            elevation=4,
            center_title=False,
        )
    
    def On_est_au_Cours(self):
        # Vérifie s'il y a une séance active
        seances_actives = db.obtenir_seances_actives()
        if seances_actives:
            self.seance_active = seances_actives[0]
            return True
        return False
    
    def Body(self):
        # Bouton principal avec style amélioré
        def handle_click(e):
            print("🟢 CLIC DÉTECTÉ!")
            self.creer_seance(e)
        
        create_session_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=30),
                ft.Text("Créer une séance", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            width=280,
            height=80,
            border_radius=15,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREEN_600,
            ink=True,
            on_click=handle_click,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        seance_en_cours = self.On_est_au_Cours()

        if seance_en_cours:
            create_session_btn.bgcolor = ft.Colors.GREY_400
            create_session_btn.on_click = None
            create_session_btn.ink = False

        # Construire la liste des contrôles
        controls = [
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
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_400),
                    offset=ft.Offset(0, 4),
                ),
                margin=ft.margin.only(bottom=30),
            ),
            ft.Text(
                "Bienvenue sur Presence Plus",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_900,
            ),
            ft.Container(height=10),
            create_session_btn,
            ft.Container(height=20),
        ]
        
        if not seance_en_cours:
            controls.append(ft.Text(
                "Aucune séance en cours",
                size=16,
                color=ft.Colors.GREY_600,
                italic=True
            ))
        else:
            from bson import ObjectId
            seance = db.obtenir_seance(str(self.seance_active["_id"]))
            matiere = db.obtenir_matiere(seance["matiere_code"])
            
            from datetime import datetime, timedelta
            temps_ecoule = datetime.now() - seance["date_creation"]
            duree_totale = timedelta(minutes=seance["duree"])
            temps_restant = duree_totale - temps_ecoule
            
            if temps_restant.total_seconds() > 0:
                heures = int(temps_restant.total_seconds() // 3600)
                minutes = int((temps_restant.total_seconds() % 3600) // 60)
                secondes = int(temps_restant.total_seconds() % 60)
                
                if heures > 0:
                    temps_str = f"{heures}h {minutes}m {secondes}s"
                elif minutes > 0:
                    temps_str = f"{minutes}m {secondes}s"
                else:
                    temps_str = f"{secondes}s"
                
                temps_couleur = ft.Colors.GREEN_700 if temps_restant.total_seconds() > 300 else ft.Colors.ORANGE_700
            else:
                temps_str = "Terminée"
                temps_couleur = ft.Colors.RED_700
            
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.BLUE_700, size=24),
                            ft.Text(
                                "Séance en cours",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_900
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        ft.Container(height=10),
                        ft.Text(
                            f"📚 {matiere['titre']}",
                            size=15,
                            color=ft.Colors.BLACK87,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            f"📍 {seance['localisation']}",
                            size=13,
                            color=ft.Colors.BLACK54,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "⏱️ Temps restant",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLACK87,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Text(
                                    temps_str,
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=temps_couleur,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            padding=15,
                            border_radius=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border=ft.border.all(2, ft.Colors.BLUE_200),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=20,
                    border_radius=15,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(2, ft.Colors.BLUE_300),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_400),
                        offset=ft.Offset(0, 3),
                    ),
                    margin=ft.margin.only(top=10),
                )
            )
        
        return ft.Column(
            controls,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )
    
    def on_hover_button(self, e, container):
        if e.data == "true":
            container.scale = 1.05
        else:
            container.scale = 1.0
        container.update()
    
    def ajouter_delegue(self):
        """Affiche la liste des étudiants pour choisir qui promouvoir en délégué"""
        print("🔵 Sélection étudiant pour délégué")
        
        etudiants = db.obtenir_tous_etudiants(titre="Etudiant")
        etudiant_selectionne = {"matricule": None}
        etudiant_list = []
        radio_group = ft.RadioGroup(content=ft.Column())
        
        for etudiant in etudiants:
            radio_group.content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Radio(
                            value=etudiant["matricule"],
                            label="",
                        ),
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700, size=30),
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
                                etudiant["email"], 
                                size=12, 
                                italic=True, 
                                color=ft.Colors.BLACK45
                            ),
                        ], spacing=2, expand=True),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def promouvoir_delegue(e):
            if not radio_group.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner un étudiant!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            result = db.modifier_etudiant(
                matricule=radio_group.value,
                updates={"titre": "Delegue"}
            )
            
            if result:
                etudiant = db.obtenir_etudiant(radio_group.value)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ {etudiant['nom']} est maintenant délégué!"),
                    bgcolor=ft.Colors.GREEN
                )
                dialog.open = False
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Erreur lors de la promotion"),
                    bgcolor=ft.Colors.RED
                )
            
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PERSON_ADD, color=ft.Colors.BLUE_700, size=30),
                ft.Text(
                    "Promouvoir un étudiant en délégué",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.BLUE_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Sélectionnez un étudiant à promouvoir:",
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
                    "✓ Promouvoir",
                    on_click=promouvoir_delegue,
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
    
    def afficher_delegues(self):
        """Affiche la liste des délégués"""
        print("🔵 Affichage liste délégués")
        
        delegues = db.obtenir_tous_etudiants(titre="Delegue")
        delegue_list = []
        for delegue in delegues:
            delegue_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700, size=30),
                        ft.Column([
                            ft.Text(
                                delegue["nom"], 
                                weight=ft.FontWeight.BOLD, 
                                size=18,
                                color=ft.Colors.BLUE_900
                            ),
                            ft.Text(
                                f"Matricule: {delegue['matricule']} • Niveau: {delegue['level']}", 
                                size=14, 
                                color=ft.Colors.BLACK87
                            ),
                            ft.Text(
                                delegue["email"], 
                                size=13, 
                                italic=True, 
                                color=ft.Colors.BLACK54
                            ),
                        ], spacing=4, expand=True),
                    ]),
                    padding=15,
                    border=ft.border.all(2, ft.Colors.BLUE_300),
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.only(bottom=10),
                )
            )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE_700, size=30),
                ft.Text(
                    "Liste des délégués", 
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.BLUE_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column(
                    delegue_list if delegue_list else [
                        ft.Container(
                            content=ft.Text(
                                "Aucun délégué trouvé", 
                                italic=True, 
                                color=ft.Colors.GREY_700,
                                size=16
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=450,
                height=350,
                padding=10,
            ),
            actions=[
                ft.ElevatedButton(
                    "Fermer",
                    on_click=fermer_dialog,
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
    
    def creer_seance(self, e):
        print("🔵 Fonction creer_seance appelée")
        
        from utils import obtenir_position_automatique, obtenir_id_appareil
        
        print("🔵 Récupération des matières...")
        matieres = db.obtenir_toutes_matieres()
        print(f"🔵 {len(matieres)} matières trouvées")
        options_matieres = [ft.dropdown.Option(m["code"], f"{m['code']} - {m['titre']}") for m in matieres]
    
        date_actuelle = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        print("🔵 Récupération de la localisation...")
        lat, lon = obtenir_position_automatique(self.page, methode="ip")
        localisation_auto = f"GPS: {lat:.6f}, {lon:.6f}" if lat and lon else "Position non disponible"
        print(f"🔵 Localisation: {localisation_auto}")
        
        date_field = ft.TextField(
            label="📅 Date et heure",
            value=date_actuelle,
            read_only=True,
            filled=True,
            border_color=ft.Colors.BLUE_200,
        )
        
        matiere_dropdown = ft.Dropdown(
            label="📚 Matière",
            hint_text="Choisissez une matière",
            options=options_matieres,
            filled=True,
            border_color=ft.Colors.BLUE_200,
        )
        
        localisation_field = ft.TextField(
            label="📍 Localisation",
            value=localisation_auto,
            read_only=True,
            filled=True,
            border_color=ft.Colors.BLUE_200,
        )
        
        duree_field = ft.TextField(
            label="⏱️ Durée (minutes)",
            hint_text="Ex: 120",
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            border_color=ft.Colors.BLUE_200,
            value="120"
        )
        
        # Récupérer le matricule du délégué connecté depuis page.data
        delegue_matricule_auto = ""
        if self.page.data and self.page.data.get("utilisateur"):
            delegue_matricule_auto = self.page.data["utilisateur"].get("matricule", "")

        delegue_field = ft.TextField(
            label="👤 Matricule du délégué",
            hint_text="Ex: DEL001",
            value=delegue_matricule_auto,
            read_only=bool(delegue_matricule_auto),
            filled=True,
            border_color=ft.Colors.BLUE_200,
        )
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def sauvegarder_seance(e):
            if not matiere_dropdown.value or not duree_field.value or not delegue_field.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez remplir tous les champs!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            try:
                seance_id = db.creer_seance(
                    matiere_code=matiere_dropdown.value,
                    date=datetime.now(),
                    localisation=localisation_auto,
                    duree=int(duree_field.value),
                    delegue_matricule=delegue_field.value
                )
                
                if seance_id and lat and lon:
                    db.mettre_a_jour_position_seance(seance_id, lat, lon)
                
                if seance_id:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("✅ Séance créée avec succès!"),
                        bgcolor=ft.Colors.GREEN
                    )
                    dialog.open = False
                    self.page.clean()
                    self.build()
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("❌ Erreur lors de la création de la séance"),
                        bgcolor=ft.Colors.RED
                    )
            except ValueError:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ La durée doit être un nombre!"),
                    bgcolor=ft.Colors.ORANGE
                )
            
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=ft.Colors.BLUE, size=35),
                            ft.Text(
                                "Créer une nouvelle séance", 
                                size=15, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_900
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.only(bottom=20)
                    ),
                    date_field,
                    ft.Container(height=10),
                    matiere_dropdown,
                    ft.Container(height=10),
                    localisation_field,
                    ft.Container(height=10),
                    duree_field,
                    ft.Container(height=10),
                    delegue_field,
                ], 
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Annuler", 
                    on_click=fermer_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "Créer la séance",
                    on_click=sauvegarder_seance,
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
        
        print("🔵 Ajout du dialog à overlay...")
        self.page.overlay.append(dialog)
        dialog.open = True
        print("🔵 Dialog ajouté et ouvert")
        self.page.update()
        print("🔵 Page mise à jour")
    
    def exporter_pdf(self):
        """Dialog pour exporter les présences en PDF"""
        print("🔵 Export PDF")
        
        toutes_seances = db.obtenir_toutes_seances()
        
        if not toutes_seances:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Aucune séance n'a été créée. Impossible de générer un PDF."),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        codes_matieres_avec_seances = list(set([s["matiere_code"] for s in toutes_seances]))
        
        matieres_disponibles = []
        for code in codes_matieres_avec_seances:
            matiere = db.obtenir_matiere(code)
            if matiere:
                matieres_disponibles.append(matiere)
        
        if not matieres_disponibles:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Aucune matière avec séances disponible"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        matiere_dropdown = ft.Dropdown(
            label="Sélectionner la matière",
            hint_text="Choisissez une matière",
            options=[
                ft.dropdown.Option(key=m["code"], text=f"{m['titre']} ({m['code']})") 
                for m in matieres_disponibles
            ],
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            width=450,
        )
        
        mois_noms = {
            "01": "Janvier", "02": "Février", "03": "Mars",
            "04": "Avril", "05": "Mai", "06": "Juin",
            "07": "Juillet", "08": "Août", "09": "Septembre",
            "10": "Octobre", "11": "Novembre", "12": "Décembre"
        }
        
        mois_dropdown = ft.Dropdown(
            label="Sélectionner le mois",
            hint_text="Sélectionnez d'abord une matière",
            options=[],
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            width=450,
            disabled=True,
        )
        
        annee_dropdown = ft.Dropdown(
            label="Sélectionner l'année",
            hint_text="Sélectionnez d'abord un mois",
            options=[],
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            width=450,
            disabled=True,
        )
        
        def update_mois_disponibles(e):
            if not matiere_dropdown.value:
                return
            
            seances_matiere = [s for s in toutes_seances if s["matiere_code"] == matiere_dropdown.value]
            
            mois_annees = {}
            for seance in seances_matiere:
                date = seance["date_creation"]
                annee = str(date.year)
                mois = date.strftime("%m")
                
                if annee not in mois_annees:
                    mois_annees[annee] = set()
                mois_annees[annee].add(mois)
            
            mois_disponibles = set()
            for annee in mois_annees:
                mois_disponibles.update(mois_annees[annee])
            
            mois_disponibles = sorted(list(mois_disponibles))
            
            mois_dropdown.options = [
                ft.dropdown.Option(key=mois, text=mois_noms[mois])
                for mois in mois_disponibles
            ]
            mois_dropdown.disabled = False
            mois_dropdown.hint_text = "Choisissez un mois"
            mois_dropdown.value = None
            
            annee_dropdown.value = None
            annee_dropdown.options = []
            annee_dropdown.disabled = True
            annee_dropdown.hint_text = "Sélectionnez d'abord un mois"
            
            matiere_dropdown.data = mois_annees
            self.page.update()
        
        def update_annees_disponibles(e):
            if not mois_dropdown.value or not matiere_dropdown.value:
                return
            
            mois_annees = matiere_dropdown.data
            
            annees_disponibles = []
            for annee, mois_set in mois_annees.items():
                if mois_dropdown.value in mois_set:
                    annees_disponibles.append(annee)
            
            annees_disponibles.sort()
            
            annee_dropdown.options = [
                ft.dropdown.Option(key=annee, text=annee)
                for annee in annees_disponibles
            ]
            annee_dropdown.disabled = False
            annee_dropdown.hint_text = "Choisissez une année"
            annee_dropdown.value = annees_disponibles[0] if annees_disponibles else None
            self.page.update()
        
        matiere_dropdown.on_change = update_mois_disponibles
        mois_dropdown.on_change = update_annees_disponibles
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def generer_pdf(e):
            if not matiere_dropdown.value or not mois_dropdown.value or not annee_dropdown.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez remplir tous les champs!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            from utils import generer_pdf_presences
            
            success, message = generer_pdf_presences(
                matiere_code=matiere_dropdown.value,
                mois=mois_dropdown.value,
                annee=annee_dropdown.value
            )
            
            dialog.open = False
            self.page.update()
            
            if success:
                def fermer_succes(e):
                    dialog_succes.open = False
                    self.page.update()
                
                dialog_succes = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=40),
                        ft.Text(
                            "PDF généré avec succès !",
                            weight=ft.FontWeight.BOLD,
                            size=20,
                            color=ft.Colors.GREEN_900
                        ),
                    ]),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Votre fichier PDF a été créé et enregistré.",
                                size=15,
                                color=ft.Colors.BLACK87,
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Container(height=15),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.BLUE_700, size=24),
                                        ft.Text(
                                            "Emplacement :",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_900
                                        ),
                                    ], spacing=8),
                                    ft.Container(height=8),
                                    ft.Text(
                                        message.split("Emplacement: ")[1] if "Emplacement: " in message else message,
                                        size=12,
                                        color=ft.Colors.BLACK87,
                                        selectable=True,
                                    ),
                                ]),
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.BLUE_50,
                                border=ft.border.all(2, ft.Colors.BLUE_200),
                            ),
                        ]),
                        width=500,
                    ),
                    actions=[
                        ft.ElevatedButton(
                            "OK",
                            on_click=fermer_succes,
                            bgcolor=ft.Colors.GREEN_600,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            )
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.CENTER,
                    shape=ft.RoundedRectangleBorder(radius=15),
                )
                
                self.page.overlay.append(dialog_succes)
                dialog_succes.open = True
                self.page.update()
            else:
                def fermer_erreur(e):
                    dialog_erreur.open = False
                    self.page.update()
                
                dialog_erreur = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_700, size=40),
                        ft.Text(
                            "Erreur lors de la génération",
                            weight=ft.FontWeight.BOLD,
                            size=20,
                            color=ft.Colors.RED_900
                        ),
                    ]),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Une erreur s'est produite lors de la création du PDF.",
                                size=15,
                                color=ft.Colors.BLACK87,
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Container(height=15),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.RED_700, size=24),
                                        ft.Text(
                                            "Détails de l'erreur :",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.RED_900
                                        ),
                                    ], spacing=8),
                                    ft.Container(height=8),
                                    ft.Text(
                                        message,
                                        size=13,
                                        color=ft.Colors.BLACK87,
                                    ),
                                ]),
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.RED_50,
                                border=ft.border.all(2, ft.Colors.RED_200),
                            ),
                        ]),
                        width=500,
                    ),
                    actions=[
                        ft.ElevatedButton(
                            "Fermer",
                            on_click=fermer_erreur,
                            bgcolor=ft.Colors.RED_600,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            )
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.CENTER,
                    shape=ft.RoundedRectangleBorder(radius=15),
                )
                
                self.page.overlay.append(dialog_erreur)
                dialog_erreur.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.RED_700, size=30),
                ft.Text(
                    "Exporter en PDF",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.BLUE_900
                ),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Sélectionnez les paramètres d'export:",
                        size=14,
                        color=ft.Colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=15),
                    matiere_dropdown,
                    ft.Container(height=10),
                    mois_dropdown,
                    ft.Container(height=10),
                    annee_dropdown,
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_600, size=18),
                            ft.Text(
                                "Le PDF sera enregistré dans le dossier Téléchargements",
                                size=12,
                                color=ft.Colors.BLUE_700,
                                italic=True,
                            ),
                        ], spacing=5),
                        padding=10,
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                ]),
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
                    "📄 Générer PDF",
                    on_click=generer_pdf,
                    bgcolor=ft.Colors.RED_600,
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
    
    def build(self):
        self.page.appbar = self.Head()
        body = self.Body()
        self.page.add(body)
        self.page.update()

def main(page: ft.Page):
    p2 = page2(page)
    p2.build()

if __name__ == "__main__":
    ft.app(target=main)
