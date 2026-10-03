"""
problema 1 - laboratorio 8

programa original en c:

    void function(int n) {
        int i, j, k, counter = 0;
        for (i = n/2; i <= n; i++) {
            for (j = 1; j+n/2 <= n; j++) {
                for (k = 1; k <= n; k = k*2) {
                    counter++;
                }
            }
        }
    }

complejidad: O(n^2 log n)
  - ciclo de i: va de n/2 hasta n -> n - n/2 + 1 vueltas, o sea ~n/2
  - ciclo de j: j + n/2 <= n  es lo mismo que  j <= n - n/2 -> ~n/2 vueltas
  - ciclo de k: k se duplica (1, 2, 4, ...) hasta pasar n -> floor(log2 n) + 1 vueltas
  - total: (n/2) * (n/2) * log2(n) = (n^2 / 4) * log n -> O(n^2 log n)

uso:
    python src/problema1.py
    python src/problema1.py --limite 60 --valores 1 10 100 1000
"""

import medicion


def funcion(n):
    """
    traduccion directa del programa en c.
    en c n/2 con enteros trunca, en python eso es n // 2.
    regresa counter (en c es void, pero lo regresamos para poder comprobar
    en las pruebas que el conteo cuadra con la formula).
    """
    counter = 0
    # for (i = n/2; i <= n; i++)
    for i in range(n // 2, n + 1):
        # for (j = 1; j + n/2 <= n; j++)
        # la condicion j + n/2 <= n se despeja como j <= n - n/2,
        # entonces j va de 1 hasta n - n/2 (incluido)
        for j in range(1, n - n // 2 + 1):
            # for (k = 1; k <= n; k = k*2)
            # este se deja como while porque k se multiplica, no se suma
            k = 1
            while k <= n:
                counter += 1
                k = k * 2
    return counter


def contar_operaciones(n):
    """
    cuantas veces se ejecuta counter++ (conteo exacto, sin correr los ciclos).
      vueltas de i: n - n//2 + 1
      vueltas de j: n - n//2
      vueltas de k: floor(log2 n) + 1, que en python es n.bit_length() para n >= 1
    """
    if n < 1:
        return 0
    vueltas_i = n - n // 2 + 1
    vueltas_j = n - n // 2
    vueltas_k = n.bit_length()
    return vueltas_i * vueltas_j * vueltas_k


if __name__ == "__main__":
    medicion.main_problema(
        nombre="problema1",
        titulo="problema 1: tamano de input vs tiempo  -  O(n^2 log n)",
        funcion=funcion,
        contar_operaciones=contar_operaciones,
        n_perfil=1000,
    )
