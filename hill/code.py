"""
Cifrado de Hill con matriz 2×2 en módulo 26.
Validación: det(K) ≠ 0 (mod 26) y gcd(det(K), 26) = 1.
"""

import math

_MOD = 26


def _letra_a_num(c: str) -> int:
    """Convierte una letra A-Z a número 0-25."""
    return ord(c.upper()) - ord("A")


def _num_a_letra(n: int) -> str:
    """Convierte un número 0-25 a letra A-Z."""
    return chr((n % _MOD) + ord("A"))


def _preprocesar(mensaje: str) -> str:
    """Mayúsculas, solo A-Z, relleno 'X' si longitud impar."""
    s = "".join(c.upper() for c in mensaje if c.isalpha())
    if len(s) % 2 != 0:
        s += "X"
    return s


def _normalizar_matriz(K: list) -> list:
    """Asegura que la clave sea 2×2 con entradas en 0..25."""
    if len(K) != 2 or len(K[0]) != 2 or len(K[1]) != 2:
        raise ValueError("La clave debe ser una matriz 2×2")
    return [[int(K[i][j]) % _MOD for j in range(2)] for i in range(2)]


def det_2x2(K: list) -> int:
    """
    Determinante de una matriz 2×2 en Z_26.
    K = [[a, b], [c, d]] => det = (a*d - b*c) mod 26.
    """
    K = _normalizar_matriz(K)
    a, b, c, d = K[0][0], K[0][1], K[1][0], K[1][1]
    return (a * d - b * c) % _MOD


def _validar_clave(K: list) -> None:
    """Lanza ValueError si la matriz no tiene inversa modular (det=0 o gcd(det,26)≠1)."""
    d = det_2x2(K)
    if d == 0:
        raise ValueError(
            "La matriz no es válida para Hill: el determinante es 0 (mod 26)."
        )
    if math.gcd(d, _MOD) != 1:
        raise ValueError(
            f"La matriz no es válida para Hill: gcd(det, 26) = gcd({d}, 26) ≠ 1."
        )


def inv_2x2_mod26(K: list) -> list:
    """
    Inversa de la matriz 2×2 K en Z_26.
    K^{-1} = (det K)^{-1} * [[d, -b], [-c, a]] (mod 26).
    """
    _validar_clave(K)
    K = _normalizar_matriz(K)
    a, b, c, d = K[0][0], K[0][1], K[1][0], K[1][1]
    det = (a * d - b * c) % _MOD
    det_inv = pow(det, -1, _MOD)
    # Adjunta: [[d, -b], [-c, a]]
    inv = [
        [(d * det_inv) % _MOD, (-b * det_inv) % _MOD],
        [(-c * det_inv) % _MOD, (a * det_inv) % _MOD],
    ]
    return inv


def _matriz_por_vector(M: list, v: tuple) -> tuple:
    """M (2×2) por vector (x, y); resultado mod 26."""
    x, y = v[0] % _MOD, v[1] % _MOD
    r0 = (M[0][0] * x + M[0][1] * y) % _MOD
    r1 = (M[1][0] * x + M[1][1] * y) % _MOD
    return (r0, r1)


def cifrar(mensaje_claro: str, clave: list) -> str:
    """
    Cifra el mensaje en claro con la clave (matriz 2×2).

    Entrada:
        mensaje_claro: texto en claro (solo se usan letras A-Z; resto se ignora).
        clave: matriz 2×2 de enteros, [[a,b],[c,d]].

    Salida:
        Mensaje cifrado (string). Si la longitud era impar, se añade 'X' al final antes de cifrar.
    """
    _validar_clave(clave)
    K = _normalizar_matriz(clave)
    s = _preprocesar(mensaje_claro)
    out = []
    for i in range(0, len(s), 2):
        p1, p2 = _letra_a_num(s[i]), _letra_a_num(s[i + 1])
        c1, c2 = _matriz_por_vector(K, (p1, p2))
        out.append(_num_a_letra(c1))
        out.append(_num_a_letra(c2))
    return "".join(out)


def descifrar(mensaje_cifrado: str, clave: list) -> str:
    """
    Descifra el mensaje cifrado con la clave (matriz 2×2).

    Entrada:
        mensaje_cifrado: texto cifrado (solo letras A-Z; longitud par tras preproceso).
        clave: matriz 2×2 de enteros (la misma que para cifrar).

    Salida:
        Mensaje en claro (string).
    """
    K_inv = inv_2x2_mod26(clave)
    s = _preprocesar(mensaje_cifrado)
    out = []
    for i in range(0, len(s), 2):
        c1, c2 = _letra_a_num(s[i]), _letra_a_num(s[i + 1])
        p1, p2 = _matriz_por_vector(K_inv, (c1, c2))
        out.append(_num_a_letra(p1))
        out.append(_num_a_letra(p2))
    return "".join(out)


if __name__ == "__main__":
    # Clave válida: det = 11, gcd(11, 26) = 1
    clave = [[3, 2], [5, 7]]
    mensaje = "HOLA"
    cifrado = cifrar(mensaje, clave)
    claro = descifrar(cifrado, clave)
    print("Mensaje claro:  ", mensaje)
    print("Clave (2×2):    ", clave)
    print("Cifrado:       ", cifrado)
    print("Descifrado:    ", claro)
    print("Verificación:  ", "OK" if claro == _preprocesar(mensaje) else "Error")
