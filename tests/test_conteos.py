"""
pruebas para asegurar que:
  1. la traduccion a python hace exactamente lo mismo que el codigo en c
     (se compara contra una version "literal" con while, que copia los for
     de c tal cual: inicializacion, condicion e incremento)
  2. la formula de contar_operaciones() da el mismo numero que contar a mano

uso (desde la raiz del repo):
    python -m unittest discover -s tests -v
"""

import contextlib
import io
import sys
import unittest
from pathlib import Path

# para poder importar los modulos de src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import problema1  # noqa: E402
import problema2  # noqa: E402
import problema3  # noqa: E402

# valores chiquitos para comparar (incluye pares, impares y potencias de 2,
# que son los casos donde n/2, n/3 y log2 n pueden fallar por uno)
VALORES_PRUEBA = list(range(0, 70)) + [127, 128, 129, 255, 256, 257, 300]


def contar_prints(funcion, n):
    """corre funcion(n) atrapando lo que imprime y cuenta las lineas."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        funcion(n)
    lineas = buffer.getvalue().splitlines()
    # de paso revisamos que siempre se imprima exactamente "Sequence"
    assert all(linea == "Sequence" for linea in lineas)
    return len(lineas)


# --- versiones literales del codigo en c, usando while como un for de c ---

def problema1_literal_c(n):
    counter = 0
    i = n // 2
    while i <= n:
        j = 1
        while j + n // 2 <= n:
            k = 1
            while k <= n:
                counter += 1
                k = k * 2
            j += 1
        i += 1
    return counter


def problema2_literal_c(n):
    if n <= 1:
        return 0
    veces = 0
    i = 1
    while i <= n:
        j = 1
        while j <= n:
            veces += 1  # printf
            break
        i += 1
    return veces


def problema3_literal_c(n):
    veces = 0
    i = 1
    while i <= n // 3:
        j = 1
        while j <= n:
            veces += 1  # printf
            j += 4
        i += 1
    return veces


class PruebaProblema1(unittest.TestCase):
    def test_igual_que_c(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(problema1.funcion(n), problema1_literal_c(n), f"n = {n}")

    def test_formula(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(problema1.contar_operaciones(n), problema1_literal_c(n), f"n = {n}")


class PruebaProblema2(unittest.TestCase):
    def test_igual_que_c(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(contar_prints(problema2.funcion, n), problema2_literal_c(n), f"n = {n}")

    def test_formula(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(problema2.contar_operaciones(n), problema2_literal_c(n), f"n = {n}")


class PruebaProblema3(unittest.TestCase):
    def test_igual_que_c(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(contar_prints(problema3.funcion, n), problema3_literal_c(n), f"n = {n}")

    def test_formula(self):
        for n in VALORES_PRUEBA:
            self.assertEqual(problema3.contar_operaciones(n), problema3_literal_c(n), f"n = {n}")


if __name__ == "__main__":
    unittest.main()
