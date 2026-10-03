"""
problema 2 - laboratorio 8

programa original en c:

    void function(int n) {
        if (n <= 1) return;
        int i, j;
        for (i = 1; i <= n; i++) {
            for (j = 1; j <= n; j++) {
                printf("Sequence\n");
                break;
            }
        }
    }

complejidad: O(n)
  - el ciclo de i da n vueltas
  - el ciclo de j parece que da n vueltas, pero el break lo corta en la
    primera, asi que solo hace 1 printf por cada i
  - total: n * 1 = n printf -> O(n)
  - si n <= 1 la funcion sale de una vez -> 0 printf

uso:
    python src/problema2.py
    python src/problema2.py --limite 60 --valores 1 10 100 1000
"""

import medicion


def funcion(n):
    """traduccion directa del programa en c (printf -> print)."""
    if n <= 1:
        return
    # for (i = 1; i <= n; i++)
    for i in range(1, n + 1):
        # for (j = 1; j <= n; j++)
        for j in range(1, n + 1):
            print("Sequence")
            # el break hace que este ciclo solo de una vuelta
            break


def contar_operaciones(n):
    """cuantas veces se ejecuta el printf: n si n > 1, si no 0."""
    return n if n > 1 else 0


if __name__ == "__main__":
    medicion.main_problema(
        nombre="problema2",
        titulo="problema 2: tamano de input vs tiempo  -  O(n)",
        funcion=funcion,
        contar_operaciones=contar_operaciones,
        n_perfil=10000,
    )
