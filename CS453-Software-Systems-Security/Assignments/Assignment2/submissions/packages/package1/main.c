#include <stddef.h>
#include <sys/types.h>

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

/* Simple hash function: computes a polynomial hash with factor 31 */
int hash_bytes(const unsigned char *data, int len) {
    int h = 0;
    for (int i = 0; i < len; i++) {
        h = h * 31 + data[i];
    }
    return h;
}

int main(void) {
    unsigned char buffer[64];
    ssize_t r = in(buffer, 64);
    /* If fewer than 64 bytes are provided, pad remaining bytes with 1 */
    for (int i = (int)r; i < 64; i++) {
        buffer[i] = 1;
    }
    
    /* Constant sample input of exactly 64 bytes.
       This is our "target" that causes the bug. */
    const unsigned char sample[64] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@";
    
    int target_hash = hash_bytes(sample, 64);
    int user_hash = hash_bytes(buffer, 64);
    int diff = target_hash - user_hash;
    
    /* Intentional bug: if user input exactly matches the sample, then diff == 0,
       causing a division by zero crash. */
    int dummy = 1 / diff;
    (void)dummy;
    
    out("Safe execution.");
    return 0;
}
