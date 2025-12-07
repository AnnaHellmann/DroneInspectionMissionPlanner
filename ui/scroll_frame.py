# ui/scroll_frame.py
import tkinter as tk
from tkinter import ttk


class ScrollFrame(tk.Frame):
    """
    Kontener z przewijalną zawartością:
    [Canvas][ScrollBar]
      └── inside_frame (tu pakujesz swoje widgety)
    """

    def __init__(self, parent, bg="#e0e0e0", *args, **kwargs):
        super().__init__(parent, bg=bg, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Wewnętrzna ramka
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # Aktualizacja scrollregionu
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Scroll kółkiem myszy
        self.inner.bind("<Enter>", self._bind_mousewheel)
        self.inner.bind("<Leave>", self._unbind_mousewheel)

    # ---------- obsługa kółka myszy ----------
    def _on_mousewheel(self, event):
        # Windows / macOS
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")
        # Linux
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def get_frame(self):
        """Zwraca wewnętrzny frame, do którego pakujemy formularze."""
        return self.inner
