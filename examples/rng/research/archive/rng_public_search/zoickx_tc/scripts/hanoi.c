#include "stdio.h"

const int size = 5;

void main() {
  for(int m = 0; m < (1<<size) - 1; ++m) {
    printf("%i -> %i\n", (m & (m + 1)) % 3, ((m | (m + 1)) + 1) % 3);
  }
}
