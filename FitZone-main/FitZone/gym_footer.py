import tkinter as tk
from gym_font import ManageFont


class GymFooter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="#1A1A1A")
        self.manage_font = ManageFont()
        self._create_footer()

    def _create_footer(self):
        self.expanded = False

        self.detail_frame = tk.Frame(self, background="#1A1A1A")
        self.detail_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        brand_label = tk.Label(
            self.detail_frame,
            text="FitZone",
            background="#1A1A1A",
            foreground="#FFD700",
            font=self.manage_font.large_bold_heading_font,
        )
        brand_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tagline = tk.Label(
            self.detail_frame,
            text="Ignite Your Potential. Become A Success.",
            background="#1A1A1A",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        tagline.grid(row=1, column=0, padx=10, sticky="w")

        self.links_frame = tk.Frame(self.detail_frame, background="#1A1A1A")
        self.links_frame.grid(row=2, column=0, sticky="w", padx=20, pady=5)

        links = [
            ("About Us", None),
            ("Services", None),
            ("Membership", None),
            ("Fitness Classes", None),
            ("Contact Us", None),
        ]
        for col, (text, cmd) in enumerate(links):
            lbl = tk.Label(
                self.links_frame,
                text=text,
                background="#1A1A1A",
                foreground="#AAAAAA",
                font=self.manage_font.smaller_letters_font,
                cursor="hand2",
            )
            lbl.grid(row=0, column=col, padx=15, pady=5)

        self.separator = tk.Frame(self, background="#444444", height=1)
        self.separator.pack(fill=tk.X, padx=20)

        bottom_frame = tk.Frame(self, background="#1A1A1A")
        bottom_frame.pack(fill=tk.X, padx=20, pady=8)

        copyright_label = tk.Label(
            bottom_frame,
            text="\u00A9 2026 FitZone. All rights reserved.",
            background="#1A1A1A",
            foreground="#888888",
            font=self.manage_font.smaller_letters_font,
        )
        copyright_label.pack(side="left")

        self.toggle_button = tk.Button(
            bottom_frame,
            text="▼",
            command=self._toggle_footer,
            background="#1A1A1A",
            foreground="#FFFFFF",
            activebackground="#2A2A2A",
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            font=self.manage_font.small_font,
        )
        self.toggle_button.pack(side="right")

        self._update_footer_visibility()

    def _toggle_footer(self):
        self.expanded = not self.expanded
        self._update_footer_visibility()

    def _update_footer_visibility(self):
        if self.expanded:
            self.detail_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
            self.separator.pack(fill=tk.X, padx=20)
            self.toggle_button.config(text="▲")
        else:
            self.detail_frame.pack_forget()
            self.separator.pack_forget()
            self.toggle_button.config(text="▼")
