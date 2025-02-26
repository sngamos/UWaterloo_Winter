#include <sys/types.h>
#include <stdint.h>

/* External interfaces */
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

/* count number of 1-bits in an 8-bit value */
static inline int bit_count(uint8_t b) {
    int count = 0;
    while(b) {
        count += (b & 1);
        b >>= 1;
    }
    return count;
}

int main(void) {
    uint8_t buffer[1024];
    ssize_t r = in(buffer, sizeof(buffer));
    if (r <= 0) {
        out("Input error.");
        return 0;
    }

    /* Build effective input of exactly 1024 bytes.
       For indices >= r, pad with 0xFF (all bits 1). */
    uint8_t effective[1024];
    for (int i = 0; i < 1024; i++) {
        if (i < r) {
            effective[i] = buffer[i];
        } else {
            effective[i] = 0xFF;
        }
    }

    /* Total bit length is fixed = 8192 */
    int L = 8192;
    int count = 0;
    for (int i = 0; i < 1024; i++) {
        count += bit_count(effective[i]);
    }

    /* if count equals L (i.e. every bit is 1), then denominator is 0 */
    int dummy = 1 / (L - count);
    (void)dummy;

    out("Safe execution.");
    return 0;
}