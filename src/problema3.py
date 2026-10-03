"""
problema 3 - laboratorio 8

programa original en c:

    void function(int n) {
        int i, j;
        for (i = 1; i <= n/3; i++) {
            for (j = 1; j <= n; j += 4) {
                printf("Sequence\n");
            }
        }
    }

complejidad: O(n^2)
  - ciclo de i: de 1 a n/3 -> floor(n/3) vueltas
  - ciclo de j: 1, 5, 9, ... mientras j <= n -> floor((n-1)/4) + 1 vueltas, ~n/4
  - total: (n/3) * (n/4) = n^2 / 12 printf -> O(n^2)
    (las constantes 1/3 y 1/4 no cambian el orden)

uso:
    python src/problema3.py
    python src/problema3.py --limite 60 --valores 1 10 100 1000
"""

import medicion


def funcion(n):
    """traduccion directa del programa en c (printf -> print)."""
    # for (i = 1; i <= n/3; i++)   (n/3 entero en c = n // 3 en python)
    for i in range(1, n // 3 + 1):
        # for (j = 1; j <= n; j += 4)   range con paso 4
        for j in range(1, n + 1, 4):
            print("Sequence")


def contar_operaciones(n):
    """
    cuantas veces se ejecuta el printf (conteo exacto).
      vueltas de i: n // 3
      vueltas de j: (n - 1) // 4 + 1 para n >= 1  (j = 1, 5, 9, ...)
    """
    if n < 1:
        return 0
    return (n // 3) * ((n - 1) // 4 + 1)


if __name__ == "__main__":
    medicion.main_problema(
        nombre="problema3",
        titulo="problema 3: tamano de input vs tiempo  -  O(n^2)",
        funcion=funcion,
        contar_operaciones=contar_operaciones,
        n_perfil=10000,
    )
