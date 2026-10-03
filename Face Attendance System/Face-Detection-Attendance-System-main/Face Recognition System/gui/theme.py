"""
GUI Styles and Theme Module
Defines colors, fonts, and styles for the GUI
"""

from config import (
    BG_COLOR, SIDEBAR_COLOR, ACCENT_COLOR, ACCENT_LIGHT,
    TEXT_COLOR, TEXT_SECONDARY, DANGER_COLOR, SUCCESS_COLOR,
    WARNING_COLOR, BORDER_COLOR, MAIN_FONT, TITLE_FONT, BUTTON_FONT
)

class Theme:
    """
    Theme configuration for the application GUI.
    """
    
    # Colors
    BG = BG_COLOR
    SIDEBAR = SIDEBAR_COLOR
    ACCENT = ACCENT_COLOR
    ACCENT_LIGHT = ACCENT_LIGHT
    TEXT = TEXT_COLOR
    TEXT_SECONDARY = TEXT_SECONDARY
    DANGER = DANGER_COLOR
    SUCCESS = SUCCESS_COLOR
    WARNING = WARNING_COLOR
    BORDER = BORDER_COLOR
    
    # Fonts
    MAIN_FONT_NAME = MAIN_FONT
    TITLE_FONT_NAME = TITLE_FONT
    BUTTON_FONT_NAME = BUTTON_FONT
    
    # Sizes
    PADDING = 15
    BORDER_RADIUS = 10
    
    @staticmethod
    def button_style():
        """Get button style configuration."""
        return {
            'font': Theme.BUTTON_FONT_NAME,
            'bg': Theme.ACCENT,
            'fg': Theme.TEXT,
            'activebackground': Theme.ACCENT_LIGHT,
            'activeforeground': Theme.TEXT,
            'bd': 0,
            'padx': 15,
            'pady': 10,
            'cursor': 'hand2'
        }
    
    @staticmethod
    def danger_button_style():
        """Get danger button style configuration."""
        return {
            'font': Theme.BUTTON_FONT_NAME,
            'bg': Theme.DANGER,
            'fg': Theme.TEXT,
            'activebackground': '#c0392b',
            'activeforeground': Theme.TEXT,
            'bd': 0,
            'padx': 15,
            'pady': 10,
            'cursor': 'hand2'
        }
    
    @staticmethod
    def label_style():
        """Get label style configuration."""
        return {
            'bg': Theme.BG,
            'fg': Theme.TEXT,
            'font': Theme.MAIN_FONT_NAME
        }
    
    @staticmethod
    def title_label_style():
        """Get title label style configuration."""
        return {
            'bg': Theme.BG,
            'fg': Theme.ACCENT,
            'font': Theme.TITLE_FONT_NAME
        }
    
    @staticmethod
    def entry_style():
        """Get entry field style configuration."""
        return {
            'bg': Theme.SIDEBAR,
            'fg': Theme.TEXT,
            'font': Theme.MAIN_FONT_NAME,
            'insertbackground': Theme.ACCENT,
            'bd': 1,
            'relief': 'solid'
        }
    
    @staticmethod
    def frame_style():
        """Get frame style configuration."""
        return {
            'bg': Theme.BG
        }
    
    @staticmethod
    def sidebar_frame_style():
        """Get sidebar frame style configuration."""
        return {
            'bg': Theme.SIDEBAR
        }


# Style presets for quick use
BUTTON_STYLE = Theme.button_style()
DANGER_BUTTON_STYLE = Theme.danger_button_style()
LABEL_STYLE = Theme.label_style()
TITLE_LABEL_STYLE = Theme.title_label_style()
ENTRY_STYLE = Theme.entry_style()
FRAME_STYLE = Theme.frame_style()
SIDEBAR_FRAME_STYLE = Theme.sidebar_frame_style()
