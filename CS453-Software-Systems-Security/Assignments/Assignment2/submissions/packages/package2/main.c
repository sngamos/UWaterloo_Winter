#include <stddef.h>
#include <sys/types.h>
#include <stdint.h>

/* External interfaces from interface.h */
ssize_t read(int fd, void *buffer, size_t count);
int puts(const char *buffer);

/* Exposed interfaces */
inline __attribute__((always_inline))
ssize_t in(void *buffer, size_t count) {
    return read(0, buffer, count);
}
inline __attribute__((always_inline))
int out(const char *buffer) {
    return puts(buffer);
}
void abort(void);

/* mix the first 60 bytes using FNV-1a and bit rotations */
uint32_t transform(const unsigned char *data, int len) {
    uint32_t h = 0x811C9DC5;  /* FNV offset basis */
    for (int i = 0; i < len; i++) {
        h ^= data[i];
        h *= 0x01000193;      /* FNV prime */
        h = (h << 5) | (h >> (32 - 5));  /* rotate left by 5 bits */
    }
    h ^= h >> 16;
    return h;
}

int main(void) {
    unsigned char buffer[64];
    ssize_t r = in(buffer, 64);
    if (r <= 0) {
        out("Input error.");
        return 0;
    }
    /* Pad any missing bytes with 1s */
    for (int i = r; i < 64; i++) {
        buffer[i] = 1;
    }
    /* Compute a 32-bit hash from the first 60 bytes */
    uint32_t hash_val = transform(buffer, 60);
    /* Interpret the last 4 bytes as a 32-bit integer (big-endian) */
    uint32_t last4 = ((uint32_t)buffer[60] << 24) |
                     ((uint32_t)buffer[61] << 16) |
                     ((uint32_t)buffer[62] << 8)  |
                     ((uint32_t)buffer[63]);
    /* Intentional bug: if hash_val equals last4, then diff==0 and division crashes */
    uint32_t diff = hash_val - last4;
    int dummy = 1 / diff;
    (void)dummy;

    out("Safe execution.");
    return 0;
}
