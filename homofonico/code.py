"""
Cifrado Homofónico con m=100 símbolos y n=26 letras (A-Z).
Cada letra se asigna a varios números; al cifrar se elige uno al azar.
Layout: el de clase (secuencial) o aleatorio (reproducible con misma semilla).
"""

import random

M = 100  # total de símbolos de cifrado (0 a 99)
N = 26   # letras del alfabeto


def _letra_a_indice(c: str) -> int:
    """Convierte una letra A-Z a índice 0-25."""
    return ord(c.upper()) - ord("A")


def _indice_a_letra(i: int) -> str:
    """Convierte índice 0-25 a letra A-Z."""
    return chr((i % N) + ord("A"))


def _preprocesar_entrada(texto: str) -> str:
    """Solo mayúsculas y letras A-Z."""
    return "".join(c.upper() for c in texto if c.isalpha())


def _construir_layout_clase() -> tuple[dict[str, list[int]], dict[int, str]]:
    """
    Layout visto en clase: reparto secuencial de 0..99 entre 26 letras.
    Primeras 22 letras (A-V): 4 números cada una.
    Últimas 4 letras (W-Z): 3 números cada una.
    22*4 + 4*3 = 100.
    """
    letra_a_numeros: dict[str, list[int]] = {}
    numero_a_letra: dict[int, str] = {}
    idx = 0
    for i in range(N):
        letra = _indice_a_letra(i)
        if i < 22:
            cantidad = 4
        else:
            cantidad = 3
        numeros = list(range(idx, idx + cantidad))
        letra_a_numeros[letra] = numeros
        for n in numeros:
            numero_a_letra[n] = letra
        idx += cantidad
    return letra_a_numeros, numero_a_letra


def _construir_layout_aleatorio(semilla: int | None = None) -> tuple[dict[str, list[int]], dict[int, str]]:
    """
    Layout aleatorio: se permutan los 100 números y se asignan sin repetición
    a las letras (22 con 4, 4 con 3). Misma semilla => mismo layout para cifrar y descifrar.
    """
    rng = random.Random(semilla)
    numeros = list(range(M))
    rng.shuffle(numeros)
    letra_a_numeros = {}
    numero_a_letra = {}
    idx = 0
    for i in range(N):
        letra = _indice_a_letra(i)
        if i < 22:
            cantidad = 4
        else:
            cantidad = 3
        asignados = numeros[idx : idx + cantidad]
        letra_a_numeros[letra] = asignados
        for n in asignados:
            numero_a_letra[n] = letra
        idx += cantidad
    return letra_a_numeros, numero_a_letra


def obtener_layout(
    aleatorio: bool = False,
    semilla: int | None = 42,
) -> tuple[dict[str, list[int]], dict[int, str]]:
    """
    Devuelve (letra -> lista de números, número -> letra).
    Si aleatorio=True, usa semilla para reproducibilidad; si aleatorio=False, ignora semilla.
    """
    if aleatorio:
        return _construir_layout_aleatorio(semilla)
    return _construir_layout_clase()


def cifrar(
    mensaje_claro: str,
    aleatorio: bool = False,
    semilla: int | None = 42,
) -> str:
    """
    Cifra el mensaje en claro con el cifrado homofónico (m=100, n=26).

    Entrada:
        mensaje_claro: texto en claro (solo se usan letras A-Z).
        aleatorio: si True, usa un layout aleatorio (reproducible con semilla).
        semilla: solo se usa si aleatorio=True; mismo valor => mismo layout.

    Salida:
        Mensaje cifrado como secuencia de números 0-99 separados por espacio
        (o sin separador según conveniencia; aquí con espacio para legibilidad).
    """
    letra_a_numeros, _ = obtener_layout(aleatorio=aleatorio, semilla=semilla)
    texto = _preprocesar_entrada(mensaje_claro)
    if not texto:
        return ""
    rng = random.Random(semilla + 1 if aleatorio else None)  # evita mismo stream que el layout
    salida = []
    for c in texto:
        opciones = letra_a_numeros[c]
        salida.append(str(rng.choice(opciones)))
    return " ".join(salida)


def descifrar(
    mensaje_cifrado: str,
    aleatorio: bool = False,
    semilla: int | None = 42,
) -> str:
    """
    Descifra el mensaje cifrado con el mismo layout homofónico.

    Entrada:
        mensaje_cifrado: números 0-99 separados por espacios (o sin espacios si son de 2 dígitos).
        aleatorio y semilla: deben coincidir con los usados al cifrar.

    Salida:
        Mensaje en claro (solo letras A-Z).
    """
    _, numero_a_letra = obtener_layout(aleatorio=aleatorio, semilla=semilla)
    # Aceptar "1 2 3" o "01 02 03" o "1 2 99"
    partes = mensaje_cifrado.split()
    if not partes:
        # Intentar leer de 2 en 2 dígitos si no hay espacios
        s = "".join(c for c in mensaje_cifrado if c.isdigit())
        partes = [s[i : i + 2] for i in range(0, len(s), 2)] if s else []
    salida = []
    for p in partes:
        try:
            n = int(p)
        except ValueError:
            continue
        if 0 <= n < M and n in numero_a_letra:
            salida.append(numero_a_letra[n])
    return "".join(salida)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # Sin argumentos: ejecutar demo
        print("=== Cifrado homofónico (m=100, n=26) — Demo ===\n")
        msg = "HOLA"
        c = cifrar(msg, aleatorio=False)
        print("Cifrar   ", repr(msg), "→", c)
        d = descifrar(c, aleatorio=False)
        print("Descifrar", repr(c), "→", d)
        print("\nUso:")
        print("  python code.py cifrar <mensaje_en_claro>")
        print("  python code.py descifrar <mensaje_cifrado>")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Uso:")
        print("  Cifrar:    python code.py cifrar <mensaje_en_claro>")
        print("  Descifrar: python code.py descifrar <mensaje_cifrado>")
        sys.exit(1)

    modo = sys.argv[1].lower()
    mensaje = " ".join(sys.argv[2:]).strip()
    if not mensaje:
        print("Debe indicar el mensaje.")
        sys.exit(1)

    if modo == "cifrar":
        resultado = cifrar(mensaje, aleatorio=False)
        print("Cifrado:", resultado)
    elif modo == "descifrar":
        resultado = descifrar(mensaje, aleatorio=False)
        print("Descifrado:", resultado)
    else:
        print("Modo debe ser 'cifrar' o 'descifrar'.")
        sys.exit(1)