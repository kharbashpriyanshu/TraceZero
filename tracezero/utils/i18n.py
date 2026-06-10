"""
utils/i18n.py — TraceZero

Lightweight Internationalization (i18n) translation dictionary.
"""

import tracezero.utils.config as cfg
from tracezero.utils.logger import app_logger

# Built-in translation mappings
_TRANSLATIONS = {
    "en": {
        "nav.dashboard": "Dashboard",
        "nav.scan": "Scan && Clean",
        "nav.history": "History",
        "nav.startup": "Startup Apps",
        "nav.duplicates": "Duplicates",
        "nav.uninstaller": "Uninstaller",
        "nav.spacemap": "Space Map",
        "nav.settings": "Settings",
        
        "settings.title": "Language / Idioma",
        "settings.lbl": "Select application language (Requires Restart):"
    },
    "es": {
        "nav.dashboard": "Panel Principal",
        "nav.scan": "Escanear y Limpiar",
        "nav.history": "Historial",
        "nav.startup": "Apps de Inicio",
        "nav.duplicates": "Duplicados",
        "nav.uninstaller": "Desinstalador",
        "nav.spacemap": "Mapa de Espacio",
        "nav.settings": "Configuración",
        
        "settings.title": "Idioma / Language",
        "settings.lbl": "Seleccione el idioma (Requiere Reinicio):"
    },
    "fr": {
        "nav.dashboard": "Tableau de bord",
        "nav.scan": "Scanner et Nettoyer",
        "nav.history": "Historique",
        "nav.startup": "Applications de démarrage",
        "nav.duplicates": "Doublons",
        "nav.uninstaller": "Désinstallateur",
        "nav.spacemap": "Carte de l'espace",
        "nav.settings": "Paramètres",
        
        "settings.title": "Langue / Language",
        "settings.lbl": "Sélectionnez la langue de l'application (Nécessite un redémarrage):"
    },
    "hi": {
        "nav.dashboard": "डैशबोर्ड (Dashboard)",
        "nav.scan": "स्कैन और क्लीन",
        "nav.history": "इतिहास",
        "nav.startup": "स्टार्टअप ऐप्स",
        "nav.duplicates": "डुप्लिकेट",
        "nav.uninstaller": "अनइंस्टालर",
        "nav.spacemap": "स्पेस मैप",
        "nav.settings": "सेटिंग्स",
        
        "settings.title": "भाषा (Language)",
        "settings.lbl": "एप्लिकेशन की भाषा चुनें (Restart की आवश्यकता है):"
    }
}

def t(key: str) -> str:
    """Translates a key based on the current config language."""
    lang = cfg.get("language")
    if lang not in _TRANSLATIONS:
        lang = "en"
        
    dic = _TRANSLATIONS[lang]
    # Fallback to English if key is missing in chosen language
    if key not in dic:
        return _TRANSLATIONS["en"].get(key, key)
        
    return dic[key]

def get_available_languages() -> dict:
    """Returns a dictionary of language codes and their display names."""
    return {
        "en": "English",
        "es": "Español (Spanish)",
        "fr": "Français (French)",
        "hi": "हिंदी (Hindi)"
    }
