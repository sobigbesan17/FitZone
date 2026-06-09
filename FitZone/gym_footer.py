import tkinter as tk
from gym_font import ManageFont


class GymFooter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="#1A1A1A")
        self.manage_font = ManageFont()
        self._create_footer()

    def _create_footer(self):
        top_frame = tk.Frame(self, background="#1A1A1A")
        top_frame.pack(fill=tk.X, padx=20, pady=10)

        brand_label = tk.Label(
            top_frame,
            text="FitZone",
            background="#1A1A1A",
            foreground="#FFD700",
            font=self.manage_font.large_bold_heading_font,
        )
        brand_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tagline = tk.Label(
            top_frame,
            text="Ignite Your Potential. Become A Success.",
            background="#1A1A1A",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        tagline.grid(row=1, column=0, padx=10, sticky="w")

        links_frame = tk.Frame(self, background="#1A1A1A")
        links_frame.pack(fill=tk.X, padx=20, pady=5)

        links = [
            ("About Us", None),
            ("Services", None),
            ("Membership", None),
            ("Fitness Classes", None),
            ("Contact Us", None),
        ]
        for col, (text, cmd) in enumerate(links):
            lbl = tk.Label(
                links_frame,
                text=text,
                background="#1A1A1A",
                foreground="#AAAAAA",
                font=self.manage_font.smaller_letters_font,
                cursor="hand2",
            )
            lbl.grid(row=0, column=col, padx=15, pady=5)

        separator = tk.Frame(self, background="#444444", height=1)
        separator.pack(fill=tk.X, padx=20)

        bottom_frame = tk.Frame(self, background="#1A1A1A")
        bottom_frame.pack(fill=tk.X, padx=20, pady=8)

        copyright_label = tk.Label(
            bottom_frame,
            text="\u00A9 2026 FitZone. All rights reserved.",
            background="#1A1A1A",
            foreground="#888888",
            font=self.manage_font.smaller_letters_font,
        )
        copyright_label.pack(anchor="center")
