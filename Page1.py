import flet as ft
import time
import threading


class page1:
    def __init__(self,page = ft.Page):
        self.page = page
        self.page.title = "Welcome"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 0
        self.button_hovered = False
        
        # Références pour les animations
        self.logo_container = None
        self.logo_center = None
        self.welcome_text = None
        self.app_name = None
        self.divider_line = None
        self.description = None
        self.button = None
        self.particles = None
        self.main_content = None
        
    def on_button_hover(self, e):
        if e.data == "true":
            self.button_hovered = True
            e.control.scale = 1.05
            e.control.bgcolor = ft.Colors.BLUE_500
            e.control.shadow = ft.BoxShadow(
                spread_radius=8,
                blur_radius=25,
                color=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_400),
                offset=ft.Offset(0, 10),
            )
        else:
            self.button_hovered = False
            e.control.scale = 1.0
            e.control.bgcolor = ft.Colors.with_opacity(0.9, ft.Colors.BLUE_600)
            e.control.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            )
        e.control.update()
    
    def animate_entrance(self):
        """Animation séquentielle des éléments"""
        # Attendre que la page soit complètement chargée
        time.sleep(0.2)
        
        # Phase 1: Afficher uniquement le logo centré
        self.logo_center.visible = True
        self.main_content.visible = False
        self.logo_center.opacity = 0
        self.logo_center.scale = 0.3
        
        self.page.update()
        
        # Animation du logo au centre
        time.sleep(0.5)
        self.logo_center.opacity = 1
        self.logo_center.scale = 1.2
        self.page.update()
        
        # Petit rebond du logo
        time.sleep(0.5)
        self.logo_center.scale = 1.0
        self.page.update()
        
        # Le logo reste seul au centre pendant 1.2 secondes
        time.sleep(1.2)
        
        # Phase 2: Faire disparaître le logo centré et afficher le contenu principal
        self.logo_center.opacity = 0
        self.page.update()
        
        time.sleep(0.3)
        
        # Cacher le logo centré et afficher le contenu principal
        self.logo_center.visible = False
        self.main_content.visible = True
        
        # Initialiser les éléments du contenu principal
        self.logo_container.opacity = 0
        self.logo_container.scale = 0.8
        
        self.welcome_text.opacity = 0
        self.welcome_text.offset = ft.Offset(0, -0.5)
        
        self.app_name.opacity = 0
        self.app_name.scale = 0.8
        
        self.divider_line.opacity = 0
        self.divider_line.width = 0
        
        self.description.opacity = 0
        
        self.button.opacity = 0
        self.button.offset = ft.Offset(0, 0.5)
        
        self.particles.opacity = 0
        
        self.page.update()
        
        # Animation du logo dans sa position finale
        time.sleep(0.2)
        self.logo_container.opacity = 1
        self.logo_container.scale = 1.0
        self.page.update()
        
        # Animation du texte "Welcome to"
        time.sleep(0.3)
        self.welcome_text.opacity = 1
        self.welcome_text.offset = ft.Offset(0, 0)
        self.page.update()
        
        # Animation du nom de l'app
        time.sleep(0.6)
        self.app_name.opacity = 1
        self.app_name.scale = 1.0
        self.page.update()
        
        # Animation de la ligne
        time.sleep(0.5)
        self.divider_line.opacity = 0.7
        self.divider_line.width = 250
        self.page.update()
        
        # Animation de la description
        time.sleep(0.4)
        self.description.opacity = 1
        self.page.update()
        
        # Animation de l'indicateur de chargement
        time.sleep(0.5)
        self.button.opacity = 1
        self.button.offset = ft.Offset(0, 0)
        self.page.update()
        
        # Animation des particules
        time.sleep(0.4)
        self.particles.opacity = 1
        self.page.update()
        
        # Attendre 3 secondes puis lancer automatiquement Main.py
        time.sleep(3)
        
        # Lancer automatiquement la transition vers Main.py
        try:
            print("🚀 Lancement automatique de Main.py...")
            self.page.clean()
            from main import MainPage
            mp = MainPage(self.page)
            mp.build()
        except Exception as ex:
            print(f"❌ Erreur lors du lancement automatique: {ex}")
            import traceback
            traceback.print_exc()
    
    def Content(self):
        # Logo centré (pour l'animation initiale)
        self.logo_center = ft.Container(
            content=ft.Image(
                src="Logo.png",
                width=120,
                height=120,
                fit=ft.ImageFit.COVER,
            ),
            width=120,
            height=120,
            border_radius=60,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            animate_scale=ft.Animation(800, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            scale=1.0,
            opacity=1,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.4, ft.Colors.YELLOW_400),
            ),
            visible=True,
        )
        
        # Logo avec animation (pour la mise en page finale)
        self.logo_container = ft.Container(
            content=ft.Image(
                src="Logo.png",
                width=120,
                height=120,
                fit=ft.ImageFit.COVER,
            ),
            width=120,
            height=120,
            border_radius=60,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            scale=1.0,
            opacity=1,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.4, ft.Colors.YELLOW_400),
            ),
        )
        
        # Texte "Welcome to"
        self.welcome_text = ft.Container(
            content=ft.Text(
                "Welcome on",
                size=28,
                weight=ft.FontWeight.W_300,
                color=ft.Colors.WHITE70,
                text_align=ft.TextAlign.CENTER,
            ),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=1,
        )
        
        # Nom de l'application
        self.app_name = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                        ft.Text(
                        "Presence",
                        size=55,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(
                            shadow=ft.BoxShadow(
                                spread_radius=2,
                                blur_radius=10,
                                color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                            ),
                        ),
                    ),
                    ft.Text(
                        "Plus",
                        size=55,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.YELLOW_400,
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(
                            shadow=ft.BoxShadow(
                                spread_radius=2,
                                blur_radius=15,
                                color=ft.Colors.with_opacity(0.6, ft.Colors.YELLOW_700),
                            ),
                        ),
                    ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            opacity=1,
        )
        
        # Ligne décorative
        self.divider_line = ft.Container(
            width=250,
            height=3,
            bgcolor=ft.Colors.YELLOW_400,
            border_radius=10,
            opacity=0.7,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # Description
        self.description = ft.Container(
            content=ft.Text(
                "Gérez vos présences facilement",
                size=16,
                color=ft.Colors.WHITE60,
                text_align=ft.TextAlign.CENTER,
                italic=True,
            ),
            padding=ft.padding.symmetric(horizontal=50),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=1,
        )
        
        # Indicateur de chargement (remplace le bouton)
        self.button = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=20, height=20, stroke_width=3, color=ft.Colors.BLUE_400),
                ft.Text(
                    "Chargement...",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_600,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15, tight=True),
            width=220,
            height=55,
            border_radius=30,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_100),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=1,
        )
        
        # Particules
        self.particles = ft.Row(
            [
                ft.Container(
                    width=10,
                    height=10,
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.YELLOW_400),
                    border_radius=5,
                    animate_opacity=ft.Animation(2000, ft.AnimationCurve.EASE_IN_OUT),
                ),
                ft.Container(
                    width=15,
                    height=15,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_300),
                    border_radius=7.5,
                    animate_opacity=ft.Animation(1500, ft.AnimationCurve.EASE_IN_OUT),
                ),
                ft.Container(
                    width=8,
                    height=8,
                    bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
                    border_radius=4,
                    animate_opacity=ft.Animation(1800, ft.AnimationCurve.EASE_IN_OUT),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=1,
        )
        
        # Contenu principal (tout sauf le logo centré initial)
        self.main_content = ft.Column(
            [
                ft.Container(height=20),
                self.logo_container,
                ft.Container(height=15),
                self.welcome_text,
                ft.Container(height=15),
                self.app_name,
                ft.Container(height=40),
                self.divider_line,
                ft.Container(height=10),
                self.description,
                ft.Container(height=60),
                self.button,
                ft.Container(height=50),
                self.particles,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )
        
        # Stack pour superposer le logo centré et le contenu principal
        return ft.Container(
            expand=True,
            padding=0,
            margin=0,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.BLUE_900,
                    ft.Colors.BLUE_700,
                    ft.Colors.INDIGO_600,
                    ft.Colors.PURPLE_800,
                ],
            ),
            content=ft.Stack(
                [
                    self.main_content,
                    ft.Container(
                        content=self.logo_center,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
            ),
        )
    
    def build(self):
        self.page.add(self.Content())
        # Lancer l'animation dans un thread séparé
        threading.Thread(target=self.animate_entrance, daemon=True).start()

def main(page : ft.Page):
    p1 = page1(page)
    p1.build()

if __name__ == "__main__":
    ft.app(target=main)