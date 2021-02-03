CC = gcc
CFLAGS = -g -Wall -Wextra -Wpedantic -Wshadow -pthread
TARGET = loadbalancer

all: $(TARGET)

$(TARGET): $(TARGET).o
	$(CC) $(CFLAGS) -o $(TARGET) $(TARGET).o

$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c

clean:
	rm $(TARGET).o

spotless:
	rm $(TARGET).o $(TARGET)