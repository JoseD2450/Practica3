# Practica3

README.md (propuesto)
Práctica Final — Analizador y Visualizador de FEN

Curso: Lenguajes y Paradigmas de Programación
Estudiante: Jose David Acevedo
Docente: Alexander De Jesus Narvaez Berrio
Fecha: 03/11/2025

1) Descripción de la actividad

El objetivo de esta práctica es desarrollar una aplicación que:

Reciba una cadena FEN (Forsyth–Edwards Notation) que describe una posición de ajedrez.

Valide la cadena según la gramática específica del enunciado (no sólo la FEN “general”, sino con las restricciones exactas del PDF).

Clasifique errores y muestre mensajes claros:

LÉXICO: caracteres/tokens inválidos (p. ej., letras que no representan piezas).

SINTAXIS: estructura incorrecta (p. ej., conteos por fila ≠ 8, número de campos ≠ 6, etc.).

Visualice el tablero 8×8 en una interfaz gráfica, colocando las piezas en sus casillas si la FEN es válida.

Si es inválida, no pinta el tablero y muestra “FEN inválida” con el detalle del error.

Nota sobre la gramática del enunciado:
La práctica restringe el campo <Piece Placement> de forma particular: los dígitos permitidos para “huecos” son 1..7, y ‘8’ solo se acepta si la fila entera es “8” (es decir, una fila completamente vacía). Esto es más estricto que la FEN “estándar”, pero aquí seguimos exactamente la regla del PDF.

2) Requisitos funcionales (según el enunciado)

La cadena FEN debe tener 6 campos separados por espacios:

<Piece Placement>: 8 filas separadas por /.

Piezas válidas: PNBRQK (blancas) y pnbrqk (negras).

Vacíos: dígitos 1..7; 8 únicamente si toda la fila es 8.

Cada fila debe sumar 8 (piezas + vacíos).

<Side to move>: w o b.

<Castling ability>: - o combinación sin repetidos de {K, Q, k, q} (orden libre).

<En passant>: - o una casilla [a-h][3|6].

<Halfmove clock>: entero decimal ≥ 0.

<Fullmove counter>: entero decimal ≥ 1.

Errores LÉXICOS típicos:

Caracter fuera del alfabeto permitido (p. ej., C, Z, símbolos…).

En roques con letras distintas de KQkq (si no es -).

Archivo en en-passant fuera de [a-h].

Errores de SINTAXIS típicos:

Menos/más de 6 campos.

Filas que no suman 8.

Usar 8 mezclado con piezas/dígitos en la fila (recuerda: 8 solo si la fila completa es vacía).

Enroques repetidos (p. ej., KQkqq).

En-passant con rango distinto de 3 o 6.

fullmove < 1.

3) Entregables

fen_parser_gui.py: aplicación en Python + Tkinter que:

Parsea y valida la FEN conforme a las reglas de la práctica.

Distingue LÉXICO vs SINTAXIS en los errores.

Dibuja el tablero con piezas Unicode y muestra metadatos (turno, enroques, en-passant, half/full move).

Incluye botón de Ejemplos (válidos e inválidos).

Este README.md: resumen de actividad, requisitos, ejecución y pruebas.

(Opcional) Capturas de pantalla de casos válidos/ inválidos.

4) Cómo ejecutar

Requisitos: Python 3.8+ (Tkinter viene incluido por defecto en la instalación estándar).

# Clonar o copiar el proyecto
python fen_parser_gui.py


Se abre la GUI.

Pega una cadena FEN en el campo de texto.

Presiona “Validar y dibujar”.

Si es válida, se pinta el tablero y se muestran los metadatos.

Si es inválida, verás el tipo de error ([LÉXICO] o [SINTAXIS]) y una explicación detallada.

5) Ejemplos de prueba

Válidos

Del enunciado:
2r3k1/p3bqp1/Q2p3p/3Pp3/P3N3/8/5PPP/5RK1 b - - 1 27

Inicio estándar:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Inválidos (deben disparar error claro)

Carácter no permitido y/o fila que suma >8:
2r3k7/p3bqp1/Q2p3p/3Pp3/P3C3/8/5PPP/5RK1 b - - 1 27

Letra fuera del conjunto de piezas:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPZ/RNBQKBNR w KQkq - 0 1

Uso de 8 mezclado en una fila:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBN8 w KQkq - 0 1

Enroque repetido:
... w KQkqq - 0 1

En-passant con rango inválido:
... w KQkq e4 0 1

fullmove < 1:
... w KQkq - 0 0

6) Decisiones de diseño (resumen técnico)

Validación por etapas:

Conteo de 6 campos.

Parser para <Piece Placement> con la restricción de la práctica (1..7 y 8 solo si la fila es 8).

Validaciones específicas para w|b, enroques (- o KQkq sin duplicados), en-passant (- o [a-h][36]), y rangos numéricos.

Clases de error:

LexicalError: tokens/caracteres inválidos.

ParseError: estructura/conteos/gramática.

UI: Tkinter con piezas Unicode (sin dependencias externas).

7) Aclaración sobre la mención a Excel en el PDF

El PDF sugiere Excel como alternativa para visualizar o comprobar la matriz 8×8 (por ejemplo: pintar casillas, verificar rápidamente que cada fila sume 8, etc.).
En esta entrega ya hay una GUI que dibuja el tablero y valida la FEN, por lo que Excel no es obligatorio.
Si el docente pide evidencia en Excel, puedes:

Exportar la matriz 8×8 a CSV (Excel lo abre directo).

Abrir el CSV en Excel y (opcional) formatear celdas (colores para casillas, fuente grande, etc.).

Snippet para generar un CSV con la matriz (solo librerías estándar):

import csv

# board es una lista 8x8 con letras 'PNBRQKpnbrqk' o None (vacío)
def export_board_to_csv(board, path="tablero.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in board:
            w.writerow([cell if cell is not None else "" for cell in row])

# Uso típico:
# rec = parse_fen(fen)
# export_board_to_csv(rec.board, "tablero.csv")


Luego abres tablero.csv en Excel → verás la posición (una letra por pieza y celdas vacías donde no hay pieza).

Si deseas .xlsx en vez de CSV, puedes usar pandas/openpyxl, pero CSV es suficiente y compatible.

8) Extensiones opcionales (si se requiere)

Reemplazar piezas Unicode por sprites PNG.

Botón “Exportar a CSV/Excel” en la GUI.

Historial de FEN cargadas y validaciones.

Pruebas unitarias (por ejemplo, pytest) con casos válidos/ inválidos.

9) Conclusión

La solución cumple lo pedido por la práctica: valida la FEN según la gramática específica, distingue errores LÉXICO/SINTAXIS y visualiza la posición en una GUI. La referencia a Excel es opcional y se cubre con exportación a CSV si fuese requerida.
