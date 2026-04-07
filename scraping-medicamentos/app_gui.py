import tkinter as tk
from tkinter import ttk, font
import threading
import importlib
import sys
import os
import re
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Paleta ──────────────────────────────────────────────────────────────────
BG        = "#0d0d0f"
SURFACE   = "#16161a"
SURFACE2  = "#1e1e24"
BORDER    = "#2a2a32"
TEXT      = "#f0eff4"
MUTED     = "#7c7b8a"
GREEN     = "#2ecc71"
GREEN_BG  = "#0f1f14"
BLUE      = "#5b9cf6"
RED       = "#e05a5a"
AMBER     = "#f0a848"
WHITE     = "#ffffff"

FARMACIAS = [
    {"id": "la_rebaja",  "nombre": "La Rebaja Virtual", "modulo": "la_rebaja",  "funcion": "buscar",              "especial": False},
    {"id": "pasteur",    "nombre": "Pasteur",            "modulo": "pasteur",    "funcion": "buscar",              "especial": False},
    {"id": "cruz_verde", "nombre": "Cruz Verde",         "modulo": "cruz_verde", "funcion": "buscar",              "especial": False},
    {"id": "farmatodo",  "nombre": "Farmatodo",          "modulo": "farmatodo",  "funcion": "buscar_en_farmatodo", "especial": True},
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def extraer_precio_numerico(texto):
    if not texto or texto == "Sin precio":
        return float("inf")
    n = re.sub(r"[^\d,.]", "", str(texto)).replace(".", "").replace(",", ".")
    try:
        return float(n)
    except:
        return float("inf")

def configurar_navegador():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def buscar_en_farmatodo_wrapper(driver, medicamento):
    import farmatodo
    resultados = farmatodo.buscar_via_url(driver, medicamento)
    if resultados:
        p = resultados[0]
        return {
            "farmacia": "Farmatodo",
            "nombre":   f"{p.get('marca','')} {p.get('nombre','')}".strip(),
            "precio":   p.get("precio", "Sin precio"),
        }
    return None

# ── GUI ──────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buscador de Medicamentos")
        self.configure(bg=BG)
        self.geometry("780x620")
        self.minsize(680, 540)
        self.resizable(True, True)

        self.cards = {}
        self.resultados = {}
        self._build_fonts()
        self._build_ui()

    # ── Fuentes ──────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_title  = font.Font(family="Helvetica Neue", size=20, weight="bold")
        self.f_sub    = font.Font(family="Helvetica Neue", size=11)
        self.f_label  = font.Font(family="Helvetica Neue", size=9,  weight="bold")
        self.f_name   = font.Font(family="Helvetica Neue", size=12)
        self.f_price  = font.Font(family="Helvetica Neue", size=22, weight="bold")
        self.f_price2 = font.Font(family="Helvetica Neue", size=13)
        self.f_btn    = font.Font(family="Helvetica Neue", size=12, weight="bold")
        self.f_footer = font.Font(family="Helvetica Neue", size=10)

    # ── UI principal ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=SURFACE, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💊  Buscador de Medicamentos",
                 bg=SURFACE, fg=TEXT,
                 font=self.f_title).pack(side="left", padx=24)
        tk.Label(hdr, text="Colombia · 4 farmacias",
                 bg=SURFACE, fg=MUTED,
                 font=self.f_sub).pack(side="right", padx=24)

        # ── Separador ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Cuerpo ──
        body = tk.Frame(self, bg=BG, padx=28, pady=24)
        body.pack(fill="both", expand=True)

        # Fila de búsqueda
        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", pady=(0, 22))

        self.entry = tk.Entry(row, bg=SURFACE2, fg=TEXT,
                              insertbackground=GREEN,
                              relief="flat", font=self.f_name,
                              bd=0, highlightthickness=1,
                              highlightbackground=BORDER,
                              highlightcolor=GREEN)
        self.entry.pack(side="left", fill="both", expand=True,
                        ipady=10, ipadx=12, padx=(0, 10))
        self.entry.insert(0, "Ej: ibuprofeno 400mg")
        self.entry.config(fg=MUTED)
        self.entry.bind("<FocusIn>",  self._placeholder_on)
        self.entry.bind("<FocusOut>", self._placeholder_off)
        self.entry.bind("<Return>",   lambda e: self._iniciar())

        self.btn = tk.Button(row, text="BUSCAR",
                             bg=GREEN, fg="#0a1a10",
                             activebackground="#27ae60",
                             activeforeground="#0a1a10",
                             relief="flat", font=self.f_btn,
                             cursor="hand2", padx=22, pady=10,
                             command=self._iniciar)
        self.btn.pack(side="left")

        # Grid de cards (2×2)
        self.grid_frame = tk.Frame(body, bg=BG)
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.columnconfigure(0, weight=1, minsize=300)
        self.grid_frame.columnconfigure(1, weight=1, minsize=300)

        for i, f in enumerate(FARMACIAS):
            c = CardWidget(self.grid_frame, f["nombre"], self)
            c.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            self.grid_frame.rowconfigure(i // 2, weight=1)
            self.cards[f["id"]] = c

        # Barra inferior de resumen
        self.footer = tk.Frame(self, bg=SURFACE, pady=10)
        self.footer.pack(fill="x", side="bottom")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")
        self.lbl_footer = tk.Label(self.footer,
                                   text="Escribe un medicamento y presiona Buscar",
                                   bg=SURFACE, fg=MUTED,
                                   font=self.f_footer)
        self.lbl_footer.pack()

    # ── Placeholder ──────────────────────────────────────────────────────────
    def _placeholder_on(self, _):
        if self.entry.get() == "Ej: ibuprofeno 400mg":
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT)

    def _placeholder_off(self, _):
        if not self.entry.get():
            self.entry.insert(0, "Ej: ibuprofeno 400mg")
            self.entry.config(fg=MUTED)

    # ── Iniciar búsqueda ─────────────────────────────────────────────────────
    def _iniciar(self):
        med = self.entry.get().strip()
        if not med or med == "Ej: ibuprofeno 400mg":
            return
        self.btn.config(state="disabled")
        self.resultados = {}
        self.lbl_footer.config(text="Buscando en las 4 farmacias...", fg=BLUE)

        for card in self.cards.values():
            card.set_buscando()

        for f in FARMACIAS:
            t = threading.Thread(
                target=self._buscar_farmacia,
                args=(f, med),
                daemon=True
            )
            t.start()

    # ── Hilo de búsqueda ─────────────────────────────────────────────────────
    def _buscar_farmacia(self, f, medicamento):
        driver = None
        try:
            driver = configurar_navegador()
            resultado = None

            if f["especial"] and f["funcion"] == "buscar_en_farmatodo":
                resultado = buscar_en_farmatodo_wrapper(driver, medicamento)
            else:
                mod = importlib.import_module(f["modulo"])
                fn  = getattr(mod, f["funcion"], None)
                if fn:
                    resultado = fn(driver, medicamento)

            if resultado:
                resultado["precio_numerico"] = extraer_precio_numerico(resultado["precio"])
                self.after(0, lambda r=resultado, fid=f["id"]: self._on_encontrado(fid, r))
            else:
                self.after(0, lambda fid=f["id"]: self._on_no_encontrado(fid))

        except Exception as e:
            self.after(0, lambda fid=f["id"], err=str(e): self._on_error(fid, err))
        finally:
            if driver:
                try: driver.quit()
                except: pass

    # ── Callbacks en el hilo principal ───────────────────────────────────────
    def _on_encontrado(self, fid, resultado):
        self.resultados[fid] = resultado
        self.cards[fid].set_encontrado(resultado["nombre"], resultado["precio"])
        self._actualizar_footer()
        self._check_done()

    def _on_no_encontrado(self, fid):
        self.resultados[fid] = None
        self.cards[fid].set_no_encontrado()
        self._check_done()

    def _on_error(self, fid, err):
        self.resultados[fid] = None
        self.cards[fid].set_error(err)
        self._check_done()

    def _check_done(self):
        if len(self.resultados) == len(FARMACIAS):
            self.btn.config(state="normal")
            self._marcar_mejor()

    def _marcar_mejor(self):
        con_precio = [
            (fid, r) for fid, r in self.resultados.items()
            if r and r.get("precio_numerico", float("inf")) < float("inf")
        ]
        if not con_precio:
            return
        con_precio.sort(key=lambda x: x[1]["precio_numerico"])
        mejor_fid = con_precio[0][0]
        self.cards[mejor_fid].set_mejor()

    def _actualizar_footer(self):
        con_precio = [
            r for r in self.resultados.values()
            if r and r.get("precio_numerico", float("inf")) < float("inf")
        ]
        if not con_precio:
            return
        con_precio.sort(key=lambda r: r["precio_numerico"])
        mejor = con_precio[0]
        txt = f"Mejor precio encontrado: {mejor['farmacia']}  →  {mejor['precio']}"
        if len(con_precio) > 1:
            ahorro = con_precio[-1]["precio_numerico"] - con_precio[0]["precio_numerico"]
            pct    = ahorro / con_precio[-1]["precio_numerico"] * 100
            txt   += f"   |   Ahorras ${ahorro:,.0f} ({pct:.0f}%) vs la más cara"
        self.lbl_footer.config(text=txt, fg=GREEN)


# ── Widget de card de farmacia ───────────────────────────────────────────────
class CardWidget(tk.Frame):
    def __init__(self, parent, nombre_farmacia, app):
        super().__init__(parent, bg=SURFACE, bd=0,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        self.app = app
        self._nombre_farmacia = nombre_farmacia
        self._build(nombre_farmacia)

    def _build(self, nombre):
        self.configure(padx=16, pady=14)

        # Fila superior: nombre farmacia + estado pill
        top = tk.Frame(self, bg=SURFACE)
        top.pack(fill="x")
        self.lbl_nombre = tk.Label(top, text=nombre.upper(),
                                   bg=SURFACE, fg=MUTED,
                                   font=self.app.f_label)
        self.lbl_nombre.pack(side="left")
        self.pill = tk.Label(top, text="EN ESPERA",
                             bg=SURFACE2, fg=MUTED,
                             font=self.app.f_label,
                             padx=8, pady=2)
        self.pill.pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", pady=8)

        # Nombre del producto
        self.lbl_producto = tk.Label(self, text="—",
                                     bg=SURFACE, fg=MUTED,
                                     font=self.app.f_name,
                                     wraplength=280,
                                     justify="left", anchor="w")
        self.lbl_producto.pack(fill="x")

        # Precio
        self.lbl_precio = tk.Label(self, text="",
                                   bg=SURFACE, fg=TEXT,
                                   font=self.app.f_price,
                                   anchor="w")
        self.lbl_precio.pack(fill="x", pady=(8, 0))

    # ── Estados ──────────────────────────────────────────────────────────────
    def set_buscando(self):
        self.configure(highlightbackground=BLUE, bg=SURFACE)
        self.lbl_nombre.config(bg=SURFACE)
        self.lbl_producto.config(text="Buscando...", fg=BLUE, bg=SURFACE)
        self.lbl_precio.config(text="", bg=SURFACE)
        self.pill.config(text="BUSCANDO", bg="#0d1a2e", fg=BLUE)
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(bg=SURFACE)

    def set_encontrado(self, nombre, precio):
        self.configure(highlightbackground=GREEN, bg=GREEN_BG)
        self.lbl_nombre.config(bg=GREEN_BG)
        self.lbl_producto.config(text=nombre, fg=TEXT, bg=GREEN_BG)
        self.lbl_precio.config(text=precio, fg=GREEN, bg=GREEN_BG)
        self.pill.config(text="ENCONTRADO", bg="#0f2a1a", fg=GREEN)
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(bg=GREEN_BG)

    def set_mejor(self):
        self.pill.config(text="✦ MEJOR PRECIO", bg="#0f2a1a", fg=GREEN)
        self.configure(highlightbackground=GREEN, highlightthickness=2)

    def set_no_encontrado(self):
        self.configure(highlightbackground=BORDER, bg=SURFACE)
        self.lbl_nombre.config(bg=SURFACE)
        self.lbl_producto.config(text="No encontrado", fg=MUTED, bg=SURFACE)
        self.lbl_precio.config(text="", bg=SURFACE)
        self.pill.config(text="SIN RESULTADO", bg=SURFACE2, fg=MUTED)
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(bg=SURFACE)

    def set_error(self, err=""):
        self.configure(highlightbackground=RED, bg=SURFACE)
        self.lbl_nombre.config(bg=SURFACE)
        self.lbl_producto.config(text=f"Error: {err[:60]}", fg=RED, bg=SURFACE)
        self.lbl_precio.config(text="", bg=SURFACE)
        self.pill.config(text="ERROR", bg="#1f0d0d", fg=RED)
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(bg=SURFACE)


# ── Arranque ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()