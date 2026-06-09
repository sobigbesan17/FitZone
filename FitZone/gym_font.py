import os
import ctypes
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont


class ManageFont:
    _loaded_font_paths = set()

    def __init__(self):
        self._register_custom_fonts()
        self.body_font_family = (
            self._font_available("Akt")
            or self._font_available("Akt Variable")
            or self._font_available("Akt-VariableFont_wght")
            or self._font_available("Outfit")
            or "Segoe UI"
        )

        # Body and smaller UI text uses Akt when available.
        self.small_font = (self.body_font_family, 9)
        self.smaller_letters_font = (self.body_font_family, 10)
        self.medium_letters_font = (self.body_font_family, 12)
        self.medium_bold_letters_font = (self.body_font_family, 12, "bold")
        self.medium_underline_letters_font = (self.body_font_family, 12, "underline")
        self.larger_letters_font = (self.body_font_family, 14)
        self.larger_bold_letters_font = (self.body_font_family, 14, "bold")
        self.large_letters_font = (self.body_font_family, 16)
        self.large_bold_letters_font = (self.body_font_family, 16, "bold")

        # Titles and main headings use Bebas Neue.
        self.large_italic_heading_font = ("Bebas Neue", 16, "italic")
        self.heading_font = ("Bebas Neue", 18, "bold")
        self.large_bold_heading_font = ("Bebas Neue", 20, "bold")
        self.medium_bold_heading_font = ("Bebas Neue", 13, "bold")
        self.small_bold_heading_font = ("Bebas Neue", 11, "bold")
        self.header_title_font = ("Bebas Neue", 32, "bold")

    def _register_custom_fonts(self):
        font_paths = [
            self._resolve_font_path("Akt.ttf", [Path(__file__).resolve().parent]),
            self._resolve_font_path("Akt-VariableFont_wght.ttf", [Path(__file__).resolve().parent]),
            self._resolve_font_path("BebasNeue-Regular.ttf", [Path(__file__).resolve().parent]),
            self._resolve_font_path("Outfit-Regular.ttf", [Path(__file__).resolve().parent]),
        ]
        for font_path in filter(None, font_paths):
            self._load_font(font_path)

    def _font_available(self, family):
        try:
            return family if family in tkfont.families() else None
        except Exception:
            return None

    def _resolve_font_path(self, filename, extra_dirs):
        if not filename:
            return None

        candidate_paths = []
        candidate_paths.append(Path(__file__).resolve().parent / filename)
        candidate_paths.extend(Path(dir_path) / filename for dir_path in extra_dirs if dir_path)

        for candidate in candidate_paths:
            if candidate.exists():
                return candidate
        return None

    def _load_font(self, font_path):
        font_path = Path(font_path)
        if font_path in self._loaded_font_paths:
            return

        if not font_path.exists():
            return

        if os.name == "nt":
            FR_PRIVATE = 0x10
            try:
                ctypes.windll.gdi32.AddFontResourceExW(str(font_path), FR_PRIVATE, 0)
                self._loaded_font_paths.add(font_path)
            except Exception:
                pass
        else:
            try:
                tkfont.Font(root=tk._default_root, family=font_path.stem)
                self._loaded_font_paths.add(font_path)
            except Exception:
                pass
