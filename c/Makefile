CC = gcc
CFLAGS = -O2 -std=c99 -Wall -Wextra
SRC = main.c dpll.c formula.c

ifeq ($(OS),Windows_NT)
BIN = dpll3.exe
else
BIN = dpll3
endif

$(BIN): $(SRC) dpll.h formula.h
	$(CC) $(CFLAGS) -o $(BIN) $(SRC) -lm

clean:
	rm -f dpll3 dpll3.exe
