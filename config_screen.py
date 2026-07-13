"""
Écran de configuration initiale : saisie de l'URL et de la clé Supabase.
Affiché au premier lancement (façon "assistant de configuration Android"),
tant qu'aucune connexion valide n'a été enregistrée.
"""
import flet as ft

from database import db

CLE_URL = "presence_plus.supabase_url"
CLE_KEY = "presence_plus.supabase_key"


def config_deja_enregistree(page: ft.Page):
    """Vérifie si une config Supabase est déjà stockée (ou fournie par l'environnement)."""
    if db.url and db.key:
        return True
    try:
        url = page.client_storage.get(CLE_URL)
        key = page.client_storage.get(CLE_KEY)
        if url and key:
            db.configure(url, key)
            return True
    except Exception:
        pass
    return False


class ConfigScreen:
    """Assistant de première configuration : saisie URL + clé API Supabase."""

    def __init__(self, page: ft.Page, on_succes):
        self.page = page
        self.on_succes = on_succes

    def build(self):
        self.page.clean()
        self.page.title = "Presence Plus - Configuration"

        champ_url = ft.TextField(
            label="URL du projet Supabase",
            hint_text="https://xxxxxxxxxxxx.supabase.co",
            width=420,
            border_color=ft.Colors.BLUE_300,
        )
        champ_key = ft.TextField(
            label="Clé API (anon/public)",
            hint_text="eyJhbGciOi...",
            password=True,
            can_reveal_password=True,
            width=420,
            border_color=ft.Colors.BLUE_300,
        )
        texte_erreur = ft.Text("", color=ft.Colors.RED_600, size=13)
        bouton = ft.ElevatedButton(
            "Se connecter",
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            width=420,
            height=45,
        )

        def valider(e):
            url = (champ_url.value or "").strip()
            key = (champ_key.value or "").strip()

            if not url or not key:
                texte_erreur.value = "⚠️ Veuillez remplir l'URL et la clé."
                self.page.update()
                return

            bouton.disabled = True
            bouton.text = "Connexion en cours..."
            texte_erreur.value = ""
            self.page.update()

            db.configure(url, key)
            if db.connect():
                try:
                    self.page.client_storage.set(CLE_URL, url)
                    self.page.client_storage.set(CLE_KEY, key)
                except Exception as ex:
                    print(f"⚠️ Impossible d'enregistrer la config localement: {ex}")
                self.on_succes()
            else:
                bouton.disabled = False
                bouton.text = "Se connecter"
                texte_erreur.value = "❌ Connexion impossible. Vérifiez l'URL et la clé."
                self.page.update()

        bouton.on_click = valider

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.SETTINGS_INPUT_ANTENNA, size=60, color=ft.Colors.BLUE_600),
                        ft.Text(
                            "Configuration de la base de données",
                            size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900,
                        ),
                        ft.Text(
                            "Renseignez les informations de votre projet Supabase.\n"
                            "Disponibles dans Project Settings → API.",
                            size=13, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=15),
                        champ_url,
                        champ_key,
                        texte_erreur,
                        ft.Container(height=10),
                        bouton,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.alignment.center,
                padding=40,
                expand=True,
            )
        )
        self.page.update()
