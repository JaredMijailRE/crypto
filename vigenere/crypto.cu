/*
 * Cifrador/Decifrador en CUDA - Modo línea de comando
 * Uso:
 *   Cifrar:  ./crypto -e <clave> <t> <mensaje>
 *   Decifrar: ./crypto -d <clave> <t> <texto_cifrado>
 *
 * Parámetro t: desplazamiento del alineamiento de la clave (entero).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cuda_runtime.h>

#define CHECK_CUDA(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error en %s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(err)); \
        exit(EXIT_FAILURE); \
    } \
} while(0)

/* Kernel de cifrado: out[i] = (data[i] + key[(i + t) % keyLen]) % 256 */
__global__ void kernel_cifrar(const unsigned char *data, unsigned char *out,
                              const unsigned char *key, int keyLen, int t, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        int keyIdx = (i + t) % keyLen;
        out[i] = (data[i] + key[keyIdx]) % 256;
    }
}

/* Kernel de decifrado: out[i] = (data[i] - key[(i + t) % keyLen] + 256) % 256 */
__global__ void kernel_decifrar(const unsigned char *data, unsigned char *out,
                                const unsigned char *key, int keyLen, int t, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        int keyIdx = (i + t) % keyLen;
        out[i] = (data[i] - key[keyIdx] + 256) % 256;
    }
}

/* Cifra en GPU */
void cifrar_gpu(const unsigned char *mensaje, int len, const unsigned char *clave, int clave_len, int t,
                unsigned char *cifrado) {
    unsigned char *d_in = NULL, *d_out = NULL, *d_key = NULL;

    CHECK_CUDA(cudaMalloc(&d_in, len));
    CHECK_CUDA(cudaMalloc(&d_out, len));
    CHECK_CUDA(cudaMalloc(&d_key, clave_len));

    CHECK_CUDA(cudaMemcpy(d_in, mensaje, len, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(d_key, clave, clave_len, cudaMemcpyHostToDevice));

    int blockSize = 256;
    int gridSize = (len + blockSize - 1) / blockSize;
    kernel_cifrar<<<gridSize, blockSize>>>(d_in, d_out, d_key, clave_len, t, len);
    CHECK_CUDA(cudaGetLastError());
    CHECK_CUDA(cudaDeviceSynchronize());

    CHECK_CUDA(cudaMemcpy(cifrado, d_out, len, cudaMemcpyDeviceToHost));

    cudaFree(d_in);
    cudaFree(d_out);
    cudaFree(d_key);
}

/* Decifra en GPU */
void decifrar_gpu(const unsigned char *cifrado, int len, const unsigned char *clave, int clave_len, int t,
                  unsigned char *mensaje) {
    unsigned char *d_in = NULL, *d_out = NULL, *d_key = NULL;

    CHECK_CUDA(cudaMalloc(&d_in, len));
    CHECK_CUDA(cudaMalloc(&d_out, len));
    CHECK_CUDA(cudaMalloc(&d_key, clave_len));

    CHECK_CUDA(cudaMemcpy(d_in, cifrado, len, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(d_key, clave, clave_len, cudaMemcpyHostToDevice));

    int blockSize = 256;
    int gridSize = (len + blockSize - 1) / blockSize;
    kernel_decifrar<<<gridSize, blockSize>>>(d_in, d_out, d_key, clave_len, t, len);
    CHECK_CUDA(cudaGetLastError());
    CHECK_CUDA(cudaDeviceSynchronize());

    CHECK_CUDA(cudaMemcpy(mensaje, d_out, len, cudaMemcpyDeviceToHost));

    cudaFree(d_in);
    cudaFree(d_out);
    cudaFree(d_key);
}

/* Imprime bytes como texto (ASCII) o hex si hay caracteres no imprimibles */
void imprimir_salida(const unsigned char *buf, int len, int es_cifrado) {
    int i;
    if (es_cifrado) {
        /* Cifrado: imprimir en hex para poder copiar/pegar sin problemas de encoding */
        for (i = 0; i < len; i++)
            printf("%02x", buf[i]);
        printf("\n");
    } else {
        /* Texto claro: imprimir tal cual */
        fwrite(buf, 1, len, stdout);
        printf("\n");
    }
}

void uso(const char *prog) {
    fprintf(stderr, "Uso:\n");
    fprintf(stderr, "  Cifrado:    %s -e <clave> <t> <mensaje>\n", prog);
    fprintf(stderr, "  Decifrado:  %s -d <clave> <t> <texto_cifrado_hex>\n", prog);
    fprintf(stderr, "\n");
    fprintf(stderr, "  clave:  cadena de caracteres (sin espacios si va entre comillas)\n");
    fprintf(stderr, "  t:      entero (parámetro de desplazamiento)\n");
    fprintf(stderr, "  mensaje / texto_cifrado_hex:  texto a cifrar o cadena hex a decifrar\n");
    fprintf(stderr, "\nEjemplo cifrado:    %s -e \"miclave\" 3 \"Hola mundo\"\n", prog);
    fprintf(stderr, "Ejemplo decifrado:  %s -d \"miclave\" 3 <salida_hex>\n", prog);
}

/* Convierte cadena hex (ej. "4a5b6c") a bytes. Devuelve longitud en *out_len. */
unsigned char *hex_a_bytes(const char *hex, int *out_len) {
    size_t hexlen = strlen(hex);
    if (hexlen % 2 != 0) {
        fprintf(stderr, "Error: el texto cifrado en hex debe tener longitud par.\n");
        return NULL;
    }
    *out_len = (int)(hexlen / 2);
    unsigned char *buf = (unsigned char *)malloc(*out_len);
    if (!buf) return NULL;
    for (int i = 0; i < *out_len; i++) {
        unsigned int x;
        if (sscanf(hex + 2 * i, "%2x", &x) != 1) {
            fprintf(stderr, "Error: caracteres no hex en posición %d.\n", 2 * i);
            free(buf);
            return NULL;
        }
        buf[i] = (unsigned char)x;
    }
    return buf;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        uso(argv[0]);
        return 1;
    }

    int cifrar;
    if (strcmp(argv[1], "-e") == 0)
        cifrar = 1;
    else if (strcmp(argv[1], "-d") == 0)
        cifrar = 0;
    else {
        fprintf(stderr, "Error: primer argumento debe ser -e (cifrar) o -d (decifrar).\n");
        uso(argv[0]);
        return 1;
    }

    const char *clave_str = argv[2];
    int t = atoi(argv[3]);
    const char *entrada = argv[4];

    int clave_len = (int)strlen(clave_str);
    if (clave_len == 0) {
        fprintf(stderr, "Error: la clave no puede estar vacía.\n");
        return 1;
    }

    unsigned char *clave = (unsigned char *)malloc(clave_len);
    if (!clave) {
        fprintf(stderr, "Error: memoria.\n");
        return 1;
    }
    memcpy(clave, clave_str, clave_len);

    if (cifrar) {
        int len = (int)strlen(entrada);
        if (len == 0) {
            fprintf(stderr, "Error: mensaje vacío.\n");
            free(clave);
            return 1;
        }
        unsigned char *cifrado = (unsigned char *)malloc(len);
        if (!cifrado) {
            free(clave);
            return 1;
        }
        cifrar_gpu((const unsigned char *)entrada, len, clave, clave_len, t, cifrado);
        imprimir_salida(cifrado, len, 1);
        free(cifrado);
    } else {
        int len;
        unsigned char *bytes = hex_a_bytes(entrada, &len);
        if (!bytes) {
            free(clave);
            return 1;
        }
        unsigned char *mensaje = (unsigned char *)malloc(len);
        if (!mensaje) {
            free(bytes);
            free(clave);
            return 1;
        }
        decifrar_gpu(bytes, len, clave, clave_len, t, mensaje);
        imprimir_salida(mensaje, len, 0);
        free(mensaje);
        free(bytes);
    }

    free(clave);
    return 0;
}
