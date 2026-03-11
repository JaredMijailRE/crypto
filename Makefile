# Cifrador/Decifrador CUDA - Línea de comando
# Requiere: nvcc (CUDA Toolkit)

NVCC = nvcc
TARGET = crypto
SRC = crypto.cu

# Opciones: ajustar según tu arquitectura GPU (ej. -arch=sm_75 para Turing)
NVCCFLAGS = -O2 -std=c++14

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(SRC)
	$(NVCC) $(NVCCFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET) *.o

run: $(TARGET)
	@echo "Ejemplo de uso:"
	./$(TARGET) -e "miclave" 3 "Hola mundo"
