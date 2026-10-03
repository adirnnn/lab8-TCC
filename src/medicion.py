"""
modulo compartido para medir los tiempos de los 3 problemas.

aqui puse todo lo que se repite entre problemas para no copiar y pegar:
  - correr la funcion en un proceso aparte con limite de tiempo
  - sacar el perfil con cProfile (el profiler que trae python)
  - estimar el tiempo de los n que serian demasiado lentos de correr
  - guardar la tabla (csv y markdown), la grafica (png) y el reporte de cProfile

cada problemaX.py solo define su funcion, su conteo exacto de operaciones
y llama a main_problema() de aqui.
"""

import argparse
import contextlib
import cProfile
import csv
import io
import multiprocessing as mp
import os
import platform
import pstats
import sys
import time
from pathlib import Path

# los valores de n que pide el enunciado
VALORES_N = [1, 10, 100, 1000, 10000, 100000, 1000000]

# limite por defecto (en segundos) para una sola corrida
LIMITE_DEFAULT = 300

# todo lo que se genera se guarda en <repo>/resultados/<problema>/
CARPETA_RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"

# colores para la grafica (azul = medido, naranja = estimado)
COLOR_MEDIDO = "#2a78d6"
COLOR_ESTIMADO = "#eb6834"


# ---------------------------------------------------------------------------
# medicion de tiempo
# ---------------------------------------------------------------------------

def _trabajador(funcion, n, repeticiones, cola):
    """
    esto corre dentro de un proceso hijo.

    se manda stdout a devnull para que los printf ("Sequence") no salgan en
    la terminal: imprimir en consola es lentisimo y terminariamos midiendo
    la consola y no el algoritmo. el print igual se ejecuta completo, solo
    que el texto se va a la "basura" del sistema.
    """
    tiempos = []
    with open(os.devnull, "w") as nulo, contextlib.redirect_stdout(nulo):
        for _ in range(repeticiones):
            inicio = time.perf_counter()
            funcion(n)
            tiempos.append(time.perf_counter() - inicio)
            # si una corrida ya se tardo mas de 1 segundo el ruido es minimo,
            # no vale la pena repetirla
            if tiempos[-1] > 1.0:
                break
    # nos quedamos con el minimo, igual que hace timeit: el minimo es la
    # corrida con menos interferencia del sistema operativo
    cola.put(min(tiempos))


def medir_con_limite(funcion, n, limite, repeticiones=5):
    """
    mide el tiempo de funcion(n) en un proceso aparte.
    regresa el tiempo en segundos, o None si se paso del limite
    (en ese caso se mata el proceso).
    """
    cola = mp.Queue()
    proceso = mp.Process(target=_trabajador, args=(funcion, n, repeticiones, cola))
    proceso.start()
    proceso.join(limite)
    if proceso.is_alive():
        # se tardo demasiado, lo matamos
        proceso.terminate()
        proceso.join()
        return None
    return cola.get()


# ---------------------------------------------------------------------------
# profiling con cProfile
# ---------------------------------------------------------------------------

def perfil_cprofile(funcion, n, lineas=15):
    """
    corre funcion(n) una vez bajo cProfile y regresa el reporte como texto.
    sirve para ver en que se va el tiempo y cuantas veces se llama cada cosa
    (por ejemplo cuantas veces se llamo print en los problemas 2 y 3).
    ojo: cProfile agrega overhead por cada llamada, por eso la tabla de tiempos
    se saca con perf_counter sin el profiler activado.
    """
    perfil = cProfile.Profile()
    with open(os.devnull, "w") as nulo, contextlib.redirect_stdout(nulo):
        perfil.enable()
        funcion(n)
        perfil.disable()
    buffer = io.StringIO()
    pstats.Stats(perfil, stream=buffer).sort_stats("cumulative").print_stats(lineas)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# formato
# ---------------------------------------------------------------------------

def tiempo_legible(segundos):
    """pasa segundos a algo que se entienda rapido (us, ms, s, min, h, dias, anios)."""
    if segundos < 1e-3:
        return f"{segundos * 1e6:.2f} us"
    if segundos < 1:
        return f"{segundos * 1e3:.2f} ms"
    if segundos < 60:
        return f"{segundos:.2f} s"
    if segundos < 3600:
        return f"{segundos / 60:.2f} min"
    if segundos < 86400:
        return f"{segundos / 3600:.2f} h"
    if segundos < 86400 * 365:
        return f"{segundos / 86400:.2f} dias"
    return f"{segundos / (86400 * 365):.2f} anios"


# ---------------------------------------------------------------------------
# experimento completo
# ---------------------------------------------------------------------------

def correr_experimento(funcion, contar_operaciones, valores_n, limite):
    """
    recorre todos los n y regresa una lista de filas con:
    n, operaciones (conteo exacto), tiempo en segundos y si fue medido o estimado.

    como estimamos los n que no se pueden correr:
      si el algoritmo hace f(n) operaciones, el tiempo es mas o menos c * f(n).
      sacamos c = tiempo / operaciones del n mas grande que si se pudo medir
      (el mas grande porque ahi el overhead fijo de llamar la funcion ya no pesa)
      y con eso calculamos c * f(n) para los demas.
    antes de correr un n revisamos cuanto se tardaria segun c; si la
    prediccion ya se pasa del limite ni lo corremos (seria esperar por gusto).
    """
    filas = []
    c = None  # segundos por operacion, se actualiza con cada medicion buena

    for n in valores_n:
        ops = contar_operaciones(n)
        prediccion = c * ops if c is not None else None

        if prediccion is not None and prediccion > limite:
            print(f"  n = {n:>8}: se predicen {tiempo_legible(prediccion)}, "
                  f"mas que el limite de {limite} s -> se estima")
            filas.append({"n": n, "operaciones": ops, "tiempo": prediccion, "tipo": "estimado"})
            continue

        print(f"  n = {n:>8}: midiendo...", end=" ", flush=True)
        tiempo = medir_con_limite(funcion, n, limite)

        if tiempo is None:
            # se paso del limite de verdad; si no hay c todavia no podemos estimar
            if c is None:
                raise RuntimeError("se paso del limite sin tener ninguna medicion para estimar")
            print(f"se paso de {limite} s -> se estima")
            filas.append({"n": n, "operaciones": ops, "tiempo": c * ops, "tipo": "estimado"})
            continue

        print(tiempo_legible(tiempo))
        filas.append({"n": n, "operaciones": ops, "tiempo": tiempo, "tipo": "medido"})
        if ops > 0:
            c = tiempo / ops

    return filas


def guardar_csv(filas, ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["n", "operaciones", "tiempo_s", "tipo"])
        for fila in filas:
            escritor.writerow([fila["n"], fila["operaciones"], f"{fila['tiempo']:.6e}", fila["tipo"]])


def tabla_markdown(filas):
    lineas = [
        "| n | operaciones (conteo exacto) | tiempo (s) | tiempo legible | tipo |",
        "|---:|---:|---:|---:|:---:|",
    ]
    for fila in filas:
        lineas.append(
            f"| {fila['n']:,} | {fila['operaciones']:,} | {fila['tiempo']:.3e} "
            f"| {tiempo_legible(fila['tiempo'])} | {fila['tipo']} |"
        )
    return "\n".join(lineas)


def guardar_grafica(filas, titulo, ruta):
    """
    grafica tamano de input vs tiempo en escala log-log.
    se usa log-log porque n va de 1 a 1,000,000 y el tiempo de microsegundos
    a horas; en escala normal todo se veria pegado al cero menos el ultimo punto.
    ademas en log-log la pendiente de la recta es el exponente de n.
    """
    # se importa aqui para que los procesos hijos no tengan que cargar matplotlib
    import matplotlib
    matplotlib.use("Agg")  # sin ventana, solo guardar el png
    import matplotlib.pyplot as plt

    medidos = [f for f in filas if f["tipo"] == "medido"]
    estimados = [f for f in filas if f["tipo"] == "estimado"]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    ax.plot([f["n"] for f in medidos], [f["tiempo"] for f in medidos],
            color=COLOR_MEDIDO, linewidth=2, marker="o", markersize=7,
            label="medido (perf_counter)")

    if estimados:
        # la linea punteada arranca desde el ultimo punto medido para que se vea la continuidad
        xs = [medidos[-1]["n"]] + [f["n"] for f in estimados]
        ys = [medidos[-1]["tiempo"]] + [f["tiempo"] for f in estimados]
        ax.plot(xs, ys, color=COLOR_ESTIMADO, linewidth=2, linestyle="--")
        ax.plot([f["n"] for f in estimados], [f["tiempo"] for f in estimados],
                linestyle="none", marker="o", markersize=7, markerfacecolor="#fcfcfb",
                markeredgecolor=COLOR_ESTIMADO, markeredgewidth=2,
                label="estimado (c * operaciones)")

    # etiqueta solo en el ultimo punto, para no llenar la grafica de numeros
    ultimo = filas[-1]
    ax.annotate(tiempo_legible(ultimo["tiempo"]), (ultimo["n"], ultimo["tiempo"]),
                textcoords="offset points", xytext=(-10, 8), ha="right",
                fontsize=9, color="#0b0b0b")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("tamano de input n", color="#52514e")
    ax.set_ylabel("tiempo de ejecucion (s)", color="#52514e")
    ax.set_title(titulo, loc="left", color="#0b0b0b")
    ax.grid(True, which="major", color="#e4e3df", linewidth=0.8)
    for borde in ("top", "right"):
        ax.spines[borde].set_visible(False)
    for borde in ("left", "bottom"):
        ax.spines[borde].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e")
    ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(ruta, facecolor=fig.get_facecolor())
    plt.close(fig)


def main_problema(nombre, titulo, funcion, contar_operaciones, n_perfil):
    """
    punto de entrada que usan problema1.py, problema2.py y problema3.py.
    nombre: nombre de la carpeta de resultados (ej. "problema1")
    titulo: titulo para la grafica
    n_perfil: el n con el que se saca el reporte de cProfile (uno que corra rapido)
    """
    parser = argparse.ArgumentParser(description=f"profiling de {nombre}")
    parser.add_argument("--limite", type=float, default=LIMITE_DEFAULT,
                        help=f"segundos maximos por corrida (default {LIMITE_DEFAULT})")
    parser.add_argument("--valores", type=int, nargs="+", default=VALORES_N,
                        help="valores de n a probar (default: los del enunciado)")
    args = parser.parse_args()

    carpeta = CARPETA_RESULTADOS / nombre
    carpeta.mkdir(parents=True, exist_ok=True)

    print(f"== {nombre} ==")
    print(f"python {platform.python_version()} en {platform.system()} {platform.release()}")
    filas = correr_experimento(funcion, contar_operaciones, args.valores, args.limite)

    # reporte de cProfile
    print(f"  sacando perfil con cProfile para n = {n_perfil}...")
    reporte = perfil_cprofile(funcion, n_perfil)
    (carpeta / "perfil_cprofile.txt").write_text(
        f"reporte de cProfile para {nombre} con n = {n_perfil}\n{reporte}", encoding="utf-8")

    # tabla y grafica
    tabla = tabla_markdown(filas)
    guardar_csv(filas, carpeta / "tabla.csv")
    (carpeta / "tabla.md").write_text(
        f"# {titulo}\n\n"
        f"python {platform.python_version()}, {platform.system()} {platform.release()}, "
        f"{platform.processor() or platform.machine()}\n\n"
        f"limite por corrida: {args.limite:g} s\n\n{tabla}\n",
        encoding="utf-8")
    guardar_grafica(filas, titulo, carpeta / "grafica.png")

    print()
    print(tabla)
    print(f"\nresultados guardados en {carpeta}")
    return filas


# por si alguien corre este archivo directo
if __name__ == "__main__":
    print("este modulo no se corre solo, usa problema1.py, problema2.py o problema3.py")
    sys.exit(1)
