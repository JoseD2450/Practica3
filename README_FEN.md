# Analizador FEN (Tkinter)

**Cómo ejecutar**

```bash
python fen_parser_gui.py
```

Pega una cadena FEN y pulsa **Validar y dibujar**. Si la cadena no cumple la gramática de la práctica, verás un error claro (LÉXICO o SINTAXIS).

**Requisitos**: Python 3.8+ con Tkinter (incluido en instalaciones estándar).

**Nota**: Este tablero usa piezas Unicode. Si deseas sprites PNG, puedes reemplazar las etiquetas por `PhotoImage` fácilmente (no requerido por la práctica).

**Ejemplos de prueba**

- Válido: `2r3k1/p3bqp1/Q2p3p/3Pp3/P3N3/8/5PPP/5RK1 b - - 1 27`
- Válido (inicio): `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
- Inválido: `2r3k7/p3bqp1/Q2p3p/3Pp3/P3C3/8/5PPP/5RK1 b - - 1 27`
