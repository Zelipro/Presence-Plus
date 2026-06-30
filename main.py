import flet as ft
from database import db
from models import Seance, Matiere
from utils import obtenir_position_automatique, obtenir_id_appareil
from datetime import datetime


class MainPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Presence Plus"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Connexion à MongoDB
        if not db.connect():
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Erreur de connexion à la base de données!"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
        
        self.seance_active = None
        self.mode_utilisateur = None  # "delegue" ou "etudiant"
        self.utilisateur_actuel = None  # Info sur l'utilisateur connecté
        
    def choisir_mode_identification(self):
        """Workflow pour choisir si on est délégué ou étudiant"""
        print("🔵 Choix du mode d'identification")
        
        mode_choisi = ft.Ref[str]()
        
        def fermer_dialog(e):
            dialog.open = False
            self.page.update()
        
        def valider_mode(e):
            if not mode_choisi.current or not mode_choisi.current.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner un mode!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            if mode_choisi.current.value == "delegue":
                dialog.open = False
                self.page.update()
                self.authentifier_delegue()
            else:
                self.mode_utilisateur = "etudiant"
                dialog.open = False
                self.page.update()
                self.afficher_interface()
        
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
        
        delegues = db.obtenir_tous_etudiants(titre="Delegue")
        
        if not delegues:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Aucun délégué enregistré dans le système"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
            self.choisir_mode_identification()
            return
        
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
            self.choisir_mode_identification()
        
        def valider_auth(e):
            if not radio_group.value:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠️ Veuillez sélectionner votre nom!"),
                    bgcolor=ft.Colors.ORANGE
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            device_id_actuel = obtenir_id_appareil()
            delegue = db.obtenir_etudiant(radio_group.value)
            
            if delegue.get("device_id") is None:
                db.valider_etudiant(radio_group.value, device_id_actuel)
                self.mode_utilisateur = "delegue"
                self.utilisateur_actuel = delegue
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Bienvenue {delegue['nom']} (Délégué)\n\n🔐 Cet appareil est maintenant enregistré comme votre appareil autorisé."),
                    bgcolor=ft.Colors.GREEN,
                    duration=5000
                )
                self.page.snack_bar.open = True
                dialog.open = False
                self.page.update()
                self.afficher_interface()
            elif delegue.get("device_id") == device_id_actuel:
                self.mode_utilisateur = "delegue"
                self.utilisateur_actuel = delegue
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Bienvenue {delegue['nom']} (Délégué)"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                dialog.open = False
                self.page.update()
                self.afficher_interface()
            else:
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
                    "Retour",
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
    
    def afficher_interface(self):
        """Affiche l'interface selon le mode utilisateur"""
        from Page2 import page2
        from Page2_Etudiant import page2_etudiant

        # Stocker l'utilisateur courant pour que les sous-pages y accèdent
        self.page.data = {
            "utilisateur": self.utilisateur_actuel,
            "mode": self.mode_utilisateur,
        }

        self.page.clean()

        if self.mode_utilisateur == "delegue":
            p2 = page2(self.page)
            p2.build()
        else:
            p2_etudiant = page2_etudiant(self.page)
            self.page.appbar = p2_etudiant.Head()
            body = p2_etudiant.Body()
            self.page.add(body)
            self.page.update()
    
    def build(self):
        self.choisir_mode_identification()


def main(page: ft.Page):
    # Afficher d'abord Page1 (accueil avec animation)
    from Page1 import page1
    p1 = page1(page)
    p1.build()


if __name__ == "__main__":
    ft.app(target=main)
