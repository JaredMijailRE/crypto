import numpy as np

def crear_reticula(tamano, hoyos):
    """Crea una retícula con hoyos en las posiciones especificadas."""
    reticula = np.zeros((tamano, tamano), dtype=int)
    for fila, col in hoyos:
        reticula[fila][col] = 1
    return reticula

def rotar_reticula(reticula, sentido_horario=True):
    """Rota la retícula 90 grados."""
    if sentido_horario:
        return np.rot90(reticula, k=-1)
    else:
        return np.rot90(reticula, k=1)

def obtener_posiciones_hoyos(reticula):
    """Obtiene las posiciones donde hay hoyos (valor 1)."""
    posiciones = []
    tamano = len(reticula)
    for i in range(tamano):
        for j in range(tamano):
            if reticula[i][j] == 1:
                posiciones.append((i, j))
    return posiciones

def cifrar(mensaje, tamano, hoyos, sentido_horario=True):
    """Cifra un mensaje usando el algoritmo de Turning Grille."""
    mensaje = mensaje.replace(" ", "").upper()
    total_celdas = tamano * tamano
    
    if len(mensaje) < total_celdas:
        mensaje += 'X' * (total_celdas - len(mensaje))
    elif len(mensaje) > total_celdas:
        mensaje = mensaje[:total_celdas]
    
    matriz_resultado = np.full((tamano, tamano), '', dtype='U1')
    reticula = crear_reticula(tamano, hoyos)
    indice_mensaje = 0
    
    for _ in range(4):
        posiciones = obtener_posiciones_hoyos(reticula)
        for fila, col in posiciones:
            if indice_mensaje < len(mensaje):
                matriz_resultado[fila][col] = mensaje[indice_mensaje]
                indice_mensaje += 1
        reticula = rotar_reticula(reticula, sentido_horario)
    
    texto_cifrado = ''.join(matriz_resultado.flatten())
    return texto_cifrado, matriz_resultado

def descifrar(texto_cifrado, tamano, hoyos, sentido_horario=True):
    """Descifra un mensaje usando el algoritmo de Turning Grille."""
    texto_cifrado = texto_cifrado.replace(" ", "").upper()
    
    matriz_cifrada = np.array(list(texto_cifrado)).reshape((tamano, tamano))
    reticula = crear_reticula(tamano, hoyos)
    mensaje_descifrado = ""
    
    for _ in range(4):
        posiciones = obtener_posiciones_hoyos(reticula)
        for fila, col in posiciones:
            mensaje_descifrado += matriz_cifrada[fila][col]
        reticula = rotar_reticula(reticula, sentido_horario)
    
    return mensaje_descifrado

def imprimir_matriz(matriz):
    """Imprime una matriz de forma legible."""
    for fila in matriz:
        print(' '.join(str(c) if c != '' else '.' for c in fila))

def main():
    print("=== TURNING GRILLE CIPHER ===\n")
    
    tamano = int(input("Tamaño de la retícula (ej: 4 para 4x4): "))
    direccion = int(input("Dirección de rotación (1=horario, 0=antihorario): "))
    modo = int(input("Modo (1=cifrar, 0=descifrar): "))
    
    print(f"\nIngrese las posiciones de los hoyos (necesita {tamano*tamano//4} hoyos)")
    print("Formato: fila,columna (índices desde 0). Escriba 'fin' para terminar.")
    
    hoyos = []
    while True:
        entrada = input("Hoyo (fila,col): ").strip()
        if entrada.lower() == 'fin':
            break
        try:
            fila, col = map(int, entrada.split(','))
            if 0 <= fila < tamano and 0 <= col < tamano:
                hoyos.append((fila, col))
            else:
                print(f"Posición fuera de rango. Use valores entre 0 y {tamano-1}")
        except ValueError:
            print("Formato inválido. Use: fila,columna")
    
    mensaje = input("\nMensaje a procesar: ")
    sentido_horario = (direccion == 1)
    
    print("\n--- RESULTADO ---")
    
    if modo == 1:
        texto_cifrado, matriz = cifrar(mensaje, tamano, hoyos, sentido_horario)
        print("\nMatriz resultante:")
        imprimir_matriz(matriz)
        print(f"\nTexto cifrado: {texto_cifrado}")
    else:
        mensaje_descifrado = descifrar(mensaje, tamano, hoyos, sentido_horario)
        print(f"\nTexto descifrado: {mensaje_descifrado}")

def demo():
    """Demostración rápida del algoritmo."""
    print("=== DEMO TURNING GRILLE ===\n")
    
    tamano = 4
    hoyos = [(0, 0), (0, 2), (1, 3), (2, 1)]
    mensaje = "HOLAQUETALPUES"
    sentido_horario = True
    
    print(f"Tamaño: {tamano}x{tamano}")
    print(f"Hoyos: {hoyos}")
    print(f"Mensaje original: {mensaje}")
    print(f"Rotación: {'horaria' if sentido_horario else 'antihoraria'}")
    
    texto_cifrado, matriz = cifrar(mensaje, tamano, hoyos, sentido_horario)
    print("\nMatriz cifrada:")
    imprimir_matriz(matriz)
    print(f"Texto cifrado: {texto_cifrado}")
    
    mensaje_descifrado = descifrar(texto_cifrado, tamano, hoyos, sentido_horario)
    print(f"\nTexto descifrado: {mensaje_descifrado}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        main()
