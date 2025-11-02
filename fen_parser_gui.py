#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FEN Parser + Validador + Tablero GUI (Tkinter)
Autor: ChatGPT (asistente)
Compatibilidad: Python 3.8+ (Tkinter incluido)
Uso:
  - Ejecuta: python fen_parser_gui.py
  - Pega una cadena FEN válida y pulsa "Validar y dibujar".
  - Si es inválida, verás un mensaje de error con el tipo (léxico/sintaxis) y detalle.

Notas de la rúbrica y decisiones de diseño (alineadas con la práctica):
- Se implementa un "lexer" implícito para la parte de <Piece Placement> que
  detecta caracteres no válidos (errores léxicos).
- Se implementa un parser con validaciones sintácticas y semánticas mínimas
  (conteo de columnas por fila, número de filas, campos obligatorios).
- La gramática del PDF establece que en <ranki> los dígitos permitidos son '1'..'7'
  y '8' solo cuando la fila completa es '8'. La implementación respeta esta regla.
- Se valida: 6 campos, 8 filas, suma=8 por fila, 'w'|'b', enroques con {KQkq} o '-', 
  en passant '-' o [a-h][36], halfmove entero >=0, fullmove entero >=1.
- Interfaz: Tkinter, tablero 8x8 con casillas claras/oscuro y piezas Unicode.

Valor agregado:
- Botón “Ejemplos” con FEN válidos y uno inválido del enunciado.
- Mensajes de error explicativos (con etiqueta de tipo de error: LÉXICO / SINTAXIS).
- Conversión inmediata de FEN a matriz para la GUI.

Licencia: Uso académico.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import tkinter as tk
from tkinter import messagebox, ttk

# ==============================
# Excepciones específicas
# ==============================

class FenError(Exception):
    """Error base para problemas con FEN."""
    kind: str = "FEN_ERROR"

    def __init__(self, message: str, *, kind: Optional[str] = None):
        super().__init__(message)
        if kind is not None:
            self.kind = kind

class LexicalError(FenError):
    """Caracteres o tokens inválidos al 'tokenizar' (lexer)."""
    def __init__(self, message: str):
        super().__init__(f"[LÉXICO] {message}", kind="LEXICAL")

class ParseError(FenError):
    """Estructura o conteos inválidos (parser)."""
    def __init__(self, message: str):
        super().__init__(f"[SINTAXIS] {message}", kind="PARSE")

# ==============================
# Modelo de datos
# ==============================

UNICODE_WHITE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔'
}
UNICODE_BLACK = {
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}
ALL_PIECES = set(UNICODE_WHITE.keys()) | set(UNICODE_BLACK.keys())
DIGITS_1_7 = set("1234567")

@dataclass
class FenRecord:
    board: List[List[Optional[str]]]  # 8x8; None=celda vacía; si no, una de PNBRQKpnbrqk
    side_to_move: str                 # 'w' o 'b'
    castling: str                     # '-', o combinación de 'KQkq' sin repetidos
    en_passant: str                   # '-' o [a-h][36]
    halfmove_clock: int               # >= 0
    fullmove_number: int              # >= 1

# ==============================
# Funciones de validación
# ==============================

def _validate_fields_count(parts: List[str]) -> None:
    if len(parts) != 6:
        raise ParseError(
            f"Se esperaban 6 campos separados por espacios, pero se recibieron {len(parts)}."
        )

def _parse_piece_placement(placement: str) -> List[List[Optional[str]]]:
    ranks = placement.split('/')
    if len(ranks) != 8:
        raise ParseError(
            f"El campo <Piece Placement> debe tener 8 filas separadas por '/', pero tiene {len(ranks)}."
        )

    board: List[List[Optional[str]]] = []

    for i, rank in enumerate(ranks, start=1):
        # Regla de la práctica:
        # <ranki> ::= [<digit17>]<piece> { [<digit17>]<piece> } [<digit17>] | '8'
        # Es decir: '8' solo si la fila completa es '8'. No se permite '...8...' mezclada.
        if rank == '8':
            board.append([None] * 8)
            continue

        row: List[Optional[str]] = []
        j = 0
        while j < len(rank):
            ch = rank[j]

            if ch in ALL_PIECES:
                row.append(ch)
                j += 1
                continue

            if ch in DIGITS_1_7:
                # Se permite 1..7 como espacios consecutivos
                count = int(ch)
                row.extend([None] * count)
                j += 1
                continue

            if ch == '8':
                # Según la gramática provista, '8' solo es válido si la fila es exactamente "8"
                raise ParseError(
                    f"En la fila {i}, '8' solo es válido si la fila completa es '8'. "
                    "No puede aparecer mezclado con otras piezas/dígitos."
                )

            # Cualquier otro carácter es léxico inválido
            raise LexicalError(
                f"Carácter no permitido '{ch}' en la fila {i} del <Piece Placement>."
            )

        if len(row) != 8:
            raise ParseError(
                f"La fila {i} suma {len(row)} columnas; deben ser exactamente 8."
            )
        board.append(row)

    return board

def _parse_side_to_move(side: str) -> str:
    if side not in ('w', 'b'):
        raise ParseError("El campo <Side to move> debe ser 'w' o 'b'.")
    return side

def _parse_castling(castling: str) -> str:
    if castling == '-':
        return castling

    valid = set("KQkq")
    seen = set()
    for ch in castling:
        if ch not in valid:
            raise LexicalError(f"Carácter de enroque inválido '{ch}'. Solo se permiten K, Q, k, q o '-'.")
        if ch in seen:
            raise ParseError(f"Enroque repetido: '{ch}'. No se permiten duplicados en <Castling ability>.")
        seen.add(ch)

    # Cualquier orden es válido
    return castling

def _parse_en_passant(ep: str) -> str:
    if ep == '-':
        return ep
    if len(ep) != 2:
        raise ParseError("El campo <En passant target square> debe ser '-' o una casilla como 'e3'/'e6'.")
    file_, rank = ep[0], ep[1]
    if file_ not in 'abcdefgh':
        raise LexicalError(f"Archivo en en passant inválido '{file_}'. Debe estar en [a-h].")
    if rank not in '36':
        raise ParseError(f"Rango de en passant inválido '{rank}'. Según el enunciado, solo '3' o '6'.")
    return ep

def _parse_halfmove_clock(hm: str) -> int:
    if not hm.isdigit():
        raise LexicalError("El campo <Halfmove clock> debe ser un número decimal no negativo.")
    val = int(hm)
    if val < 0:
        # No ocurrirá por isdigit, pero se deja por claridad
        raise ParseError("El <Halfmove clock> no puede ser negativo.")
    return val

def _parse_fullmove_number(fn: str) -> int:
    if not fn.isdigit():
        raise LexicalError("El campo <Fullmove counter> debe ser un número entero decimal >= 1.")
    val = int(fn)
    if val < 1:
        raise ParseError("El <Fullmove counter> debe ser >= 1.")
    return val

def parse_fen(fen: str) -> FenRecord:
    """
    Parsea y valida una cadena FEN completa según la especificación de la práctica.
    Retorna un FenRecord o lanza LexicalError/ParseError con mensajes claros.
    """
    parts = fen.strip().split()
    _validate_fields_count(parts)

    placement, side, castling, ep, halfmove, fullmove = parts

    board = _parse_piece_placement(placement)
    side = _parse_side_to_move(side)
    castling = _parse_castling(castling)
    ep = _parse_en_passant(ep)
    hm = _parse_halfmove_clock(halfmove)
    fn = _parse_fullmove_number(fullmove)

    return FenRecord(
        board=board,
        side_to_move=side,
        castling=castling,
        en_passant=ep,
        halfmove_clock=hm,
        fullmove_number=fn
    )

# ==============================
# GUI (Tkinter)
# ==============================

class FenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador FEN - Validador y Tablero")
        self.geometry("930x660")
        self.minsize(900, 640)

        self._build_ui()

    def _build_ui(self):
        # Frame de entrada
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Cadena FEN:").pack(side=tk.LEFT)
        self.fen_var = tk.StringVar()
        self.entry = ttk.Entry(top, textvariable=self.fen_var, width=100)
        self.entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)

        ttk.Button(top, text="Validar y dibujar", command=self.on_validate).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Ejemplos", command=self.on_examples).pack(side=tk.LEFT)

        # Panel informativo
        info = ttk.Frame(self, padding=10)
        info.pack(side=tk.TOP, fill=tk.X)
        self.lbl_status = ttk.Label(info, text="Listo.", foreground="#333")
        self.lbl_status.pack(side=tk.LEFT)

        # Panel tablero + datos
        mid = ttk.Frame(self, padding=10)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Tablero
        self.board_frame = ttk.Frame(mid)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Datos adicionales
        right = ttk.Frame(mid, padding=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.side_lbl = ttk.Label(right, text="Turno: -")
        self.castling_lbl = ttk.Label(right, text="Enroques: -")
        self.ep_lbl = ttk.Label(right, text="En passant: -")
        self.half_lbl = ttk.Label(right, text="Halfmove clock: -")
        self.full_lbl = ttk.Label(right, text="Fullmove #: -")

        for w in (self.side_lbl, self.castling_lbl, self.ep_lbl, self.half_lbl, self.full_lbl):
            w.pack(anchor="w", pady=2)

        sep = ttk.Separator(right, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=8)

        self.notes = tk.Text(right, height=12, wrap="word")
        self.notes.insert("1.0",
            "Notas:\n"
            "- Usa piezas Unicode para dibujar el tablero.\n"
            "- '8' solo es válido si la fila completa es '8' (regla de la práctica).\n"
            "- Enroque: usa '-', o letras entre {K,Q,k,q} sin duplicados (orden libre).\n"
            "- En passant: '-' o casilla [a-h][3|6].\n"
            "- 'Halfmove' ≥ 0 y 'Fullmove' ≥ 1.\n"
        )
        self.notes.configure(state="disabled")
        self.notes.pack(fill=tk.BOTH, expand=True)

        # Construye una grilla vacía inicial
        self._build_empty_board()

    def _build_empty_board(self):
        # Elimina widgets previos
        for child in self.board_frame.winfo_children():
            child.destroy()

        size = 60  # px por celda
        font = ("DejaVu Sans", 28)  # tipografía con soporte Unicode para piezas

        for r in range(8):
            for c in range(8):
                bg = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"  # claro/oscuro estilo lichess/chess.com
                cell = tk.Label(self.board_frame, text="", width=2, height=1,
                                font=font, bg=bg, fg="#111")
                cell.grid(row=r, column=c, ipadx=10, ipady=10, sticky="nsew")

        for i in range(8):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

    def draw_board(self, board: List[List[Optional[str]]]):
        self._build_empty_board()
        font = ("DejaVu Sans", 28)

        for r in range(8):
            for c in range(8):
                ch = board[r][c]
                if ch is None:
                    continue
                piece = None
                if ch in UNICODE_WHITE:
                    piece = UNICODE_WHITE[ch]
                    fg = "#000000"  # negro para piezas blancas (mejor contraste)
                elif ch in UNICODE_BLACK:
                    piece = UNICODE_BLACK[ch]
                    fg = "#111111"
                else:
                    # No debería pasar
                    piece = "?"
                    fg = "#ff0000"

                cell = self.board_frame.grid_slaves(row=r, column=c)[0]
                cell.config(text=piece, font=font, fg=fg)

    def on_validate(self):
        fen = self.fen_var.get().strip()
        if not fen:
            messagebox.showinfo("Información", "Por favor ingresa una cadena FEN.")
            return
        try:
            rec = parse_fen(fen)
            self.lbl_status.config(text="FEN válida ✓", foreground="green")
            self.draw_board(rec.board)
            # Actualiza panel derecho
            self.side_lbl.config(text=f"Turno: {'Blancas' if rec.side_to_move=='w' else 'Negras'} ({rec.side_to_move})")
            self.castling_lbl.config(text=f"Enroques: {rec.castling}")
            self.ep_lbl.config(text=f"En passant: {rec.en_passant}")
            self.half_lbl.config(text=f"Halfmove clock: {rec.halfmove_clock}")
            self.full_lbl.config(text=f"Fullmove #: {rec.fullmove_number}")
        except FenError as e:
            self.lbl_status.config(text=str(e), foreground="red")
            messagebox.showerror("FEN inválida", str(e))
        except Exception as ex:
            self.lbl_status.config(text=f"Error inesperado: {ex}", foreground="red")
            messagebox.showerror("Error inesperado", repr(ex))

    def on_examples(self):
        menu = tk.Toplevel(self)
        menu.title("Ejemplos FEN")
        menu.geometry("820x260")

        examples = [
            ("Ejemplo válido (del enunciado)",
             "2r3k1/p3bqp1/Q2p3p/3Pp3/P3N3/8/5PPP/5RK1 b - - 1 27"),
            ("Posición inicial estándar",
             "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
            ("FEN inválido (primer fila >8, y tiene 'C')",
             "2r3k7/p3bqp1/Q2p3p/3Pp3/P3C3/8/5PPP/5RK1 b - - 1 27"),
        ]

        def put(idx: int):
            self.fen_var.set(examples[idx][1])
            menu.destroy()

        for i, (title, fen) in enumerate(examples):
            btn = ttk.Button(menu, text=title, command=lambda i=i: put(i))
            btn.pack(anchor="w", padx=12, pady=6)

        txt = tk.Text(menu, height=7, wrap="word")
        txt.insert("1.0",
            "Sugerencias:\n"
            "- Pruébalo con cadenas válidas para confirmar el dibujo.\n"
            "- Pruébalo con errores para ver mensajes (por ejemplo, '8' mezclado, caracteres inválidos, sumas por fila ≠ 8, etc.).\n"
        )
        txt.configure(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

def main():
    app = FenApp()
    app.mainloop()

if __name__ == "__main__":
    main()
