"""
Cifrado AES de imágenes: entrada arbitraria, Base64, bits, descifrado y visualización.
Uso: python main.py --bits 128|192|256 [--image RUTA]
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import sys
import textwrap
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PIL import Image

# Misma imagen que en DES (relativa al repo)
_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = _REPO_ROOT / "DES" / (
    "actors-who-voiced-played-am-from-i-have-no-mouth-and-i-must-scream-fan-casting-"
    "poster-608263-large-3095023247.jpg"
)
OUTPUT_DECRYPTED = Path(__file__).resolve().parent / "decrypted_image_aes.jpg"
OUTPUT_ENCRYPTED_RAW = Path(__file__).resolve().parent / "ciphertext_aes.bin"

# Frase base; la clave AES se deriva a 16/24/32 bytes según el nivel
PASSPHRASE = b"CryptoAESKeyExercise2024"


def derive_key(bits: int) -> bytes:
    if bits == 128:
        return hashlib.sha256(PASSPHRASE).digest()[:16]
    if bits == 192:
        return hashlib.sha384(PASSPHRASE).digest()[:24]
    if bits == 256:
        return hashlib.sha256(PASSPHRASE).digest()
    raise ValueError("bits debe ser 128, 192 o 256")


def bytes_to_bit_string(data: bytes, max_bits: int | None = None) -> str:
    s = "".join(format(b, "08b") for b in data)
    if max_bits is not None and len(s) > max_bits:
        return s[:max_bits] + f"... (+{len(s) - max_bits} bits más)"
    return s


def encrypt_aes_cbc(plaintext: bytes, key: bytes) -> bytes:
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return iv + ciphertext


def decrypt_aes_cbc(iv_plus_ct: bytes, key: bytes) -> bytes:
    iv = iv_plus_ct[: AES.block_size]
    ct = iv_plus_ct[AES.block_size :]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cifra una imagen con AES (CBC + IV), Base64, bits y descifrado."
    )
    parser.add_argument(
        "--bits",
        type=int,
        choices=(128, 192, 256),
        required=True,
        help="Tamaño de clave AES en bits (128, 192 o 256).",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help="Ruta a la imagen (cualquier formato que Pillow pueda abrir como bytes crudos).",
    )
    args = parser.parse_args()

    image_path = args.image.resolve()
    if not image_path.is_file():
        print(f"Error: no existe el archivo: {image_path}", file=sys.stderr)
        sys.exit(1)

    key = derive_key(args.bits)
    image_bytes = image_path.read_bytes()

    print("=" * 60)
    print("ENTRADA")
    print("=" * 60)
    print(f"Archivo: {image_path}")
    print(f"Tamaño (bytes): {len(image_bytes)}")
    print(f"SHA-256 (original): {hashlib.sha256(image_bytes).hexdigest()}")

    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            print(f"Formato detectado (Pillow): {im.format}")
            print(f"Dimensiones: {im.size[0]} x {im.size[1]} px, modo: {im.mode}")
    except Exception as e:
        print(f"(Pillow no pudo inspeccionar la imagen: {e})")

    print("\n" + "=" * 60)
    print("CLAVE Y PARÁMETROS AES")
    print("=" * 60)
    print(f"Nivel solicitado: {args.bits} bits")
    print(f"Longitud de clave derivada: {len(key)} bytes ({len(key) * 8} bits)")
    print(f"Clave (hex): {key.hex()}")
    print("Modo: CBC (IV aleatorio de 16 bytes, prefijado al criptograma)")

    bit_plain_preview = bytes_to_bit_string(image_bytes[:8])
    print(f"\nPrimeros 64 bits del archivo en claro: {bit_plain_preview}")

    pad_len = AES.block_size - (len(image_bytes) % AES.block_size)
    if pad_len == 0:
        pad_len = AES.block_size

    encrypted = encrypt_aes_cbc(image_bytes, key)
    ct_only = encrypted[AES.block_size :]
    num_blocks = len(ct_only) // AES.block_size

    print("\n" + "=" * 60)
    print("CIFRADO")
    print("=" * 60)
    print(f"Padding PKCS#7 añadido antes de cifrar: {pad_len} byte(s)")
    print(f"Tamaño tras padding (solo carga útil): {len(image_bytes) + pad_len} bytes")
    print(f"Tamaño criptograma (IV + datos): {len(encrypted)} bytes")
    print(
        f"Expansión vs archivo original: +{len(encrypted) - len(image_bytes)} bytes "
        f"(IV + padding)"
    )
    print(f"Bloques AES (sin contar IV): {num_blocks}")
    print(f"IV utilizado (hex, primeros 16 bytes del mensaje binario): {encrypted[: AES.block_size].hex()}")

    b64 = base64.b64encode(encrypted).decode("ascii")
    print("\n" + "=" * 60)
    print("TEXTO EN BASE64 (criptograma completo con IV, MIME 76 cols)")
    print("=" * 60)
    print("\n".join(textwrap.wrap(b64, 76)))
    print(f"--- Longitud Base64: {len(b64)} caracteres ---")

    decoded_from_b64 = base64.b64decode(b64)
    print("\n" + "=" * 60)
    print("TRAS DECODIFICAR BASE64 → BYTES → REPRESENTACIÓN EN BITS")
    print("=" * 60)
    print(f"Bytes tras Base64: {len(decoded_from_b64)} (¿coincide con cifrado? {decoded_from_b64 == encrypted})")
    first_chunk = decoded_from_b64[:24]
    bits_full = "".join(format(b, "08b") for b in first_chunk)
    print(f"Primeros {len(first_chunk) * 8} bits (IV parcial + inicio del cifrado):")
    print(bits_full)

    decrypted = decrypt_aes_cbc(decoded_from_b64, key)

    print("\n" + "=" * 60)
    print("DESCIFRADO")
    print("=" * 60)
    print(f"Bytes recuperados: {len(decrypted)}")
    print(f"¿Igual al original? {decrypted == image_bytes}")
    print(f"SHA-256 (recuperado): {hashlib.sha256(decrypted).hexdigest()}")

    OUTPUT_DECRYPTED.write_bytes(decrypted)
    OUTPUT_ENCRYPTED_RAW.write_bytes(encrypted)
    print(f"\nCriptograma (binario) guardado en: {OUTPUT_ENCRYPTED_RAW}")
    print(f"Imagen descifrada guardada en: {OUTPUT_DECRYPTED}")

    img = Image.open(io.BytesIO(decrypted))
    img.show()
    print("Imagen original recuperada mostrada en visor del sistema.")


if __name__ == "__main__":
    main()
