import sys
import base64
import io
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from PIL import Image

IMAGE_PATH = "actors-who-voiced-played-am-from-i-have-no-mouth-and-i-must-scream-fan-casting-poster-608263-large-3095023247.jpg"
OUTPUT_PATH = "decrypted_image.jpg"
DES_KEY = b"CryptoK1"


def image_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)


def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def encrypt_des(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    padded = pad(data, DES.block_size)
    return cipher.encrypt(padded)


def decrypt_des(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, DES.block_size)


def main():
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print(f"Imagen original: {len(image_bytes)} bytes")

    bit_array = image_to_bits(image_bytes)
    print(f"Representación en bits: {len(bit_array)} bits")
    print(f"Primeros 64 bits: {bit_array[:64]}")

    encrypted = encrypt_des(image_bytes, DES_KEY)
    print(f"\nDatos cifrados: {len(encrypted)} bytes")

    b64_encoded = base64.b64encode(encrypted).decode('utf-8')
    print(f"\n{'='*60}")
    print("TEXTO CIFRADO EN BASE64:")
    print(f"{'='*60}")
    print(b64_encoded[:500])
    print(f"... ({len(b64_encoded)} caracteres en total)")
    print(f"{'='*60}")

    decoded = base64.b64decode(b64_encoded)

    decrypted = decrypt_des(decoded, DES_KEY)
    print(f"\nDatos descifrados: {len(decrypted)} bytes")
    print(f"¿Coincide con original? {image_bytes == decrypted}")

    with open(OUTPUT_PATH, "wb") as f:
        f.write(decrypted)

    print(f"Imagen descifrada guardada como '{OUTPUT_PATH}'")

    img = Image.open(io.BytesIO(decrypted))
    img.show()
    print("Imagen mostrada.")


if __name__ == "__main__":
    main()
