#include <stddef.h>
#include <sys/types.h>

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

/* Compute absolute value */
int abs_val(int x) {
    int sign = x >> 31;  /* 0 if x>=0, -1 if x<0 */
    return (x ^ sign) - sign;
}

int main(void) {
    unsigned char input_buf[1024];
    ssize_t r = in(input_buf, 1024);
    if (r <= 0) {
        out("Input error.");
        return 0;
    }
    /* Use only the first 64 bytes */
    int used = (r > 64) ? 64 : r;
    unsigned char effective[64];
    int i;
    for (i = 0; i < used; i++) {
        effective[i] = input_buf[i];
    }
    /* If input is less than 64 bytes, pad with noise */
    for (; i < 64; i++) {
        effective[i] = (unsigned char)((i * 17 + 23) & 0xFF);
    }

    /* Compute the sum of absolute differences between symmetric bytes */
    int half = 64 / 2;  /* 32 */
    int sum = 0;
    for (int j = 0; j < half; j++) {
        int diff = (int)effective[j] - (int)effective[63 - j];
        int absdiff = abs_val(diff);
        sum += absdiff;
    }

    /* if all 64 bytes are identical, then all XOR differences are zero.
       Compute an aggregate XOR difference from effective[0] 
       safeguard against trivial palindrome where all characters are the same*/
    unsigned int allSameDiff = 0;
    for (int j = 1; j < 64; j++) {
        allSameDiff |= effective[j] ^ effective[0];
    }
    /* Compute a correction delta in a branchless way:
       If allSameDiff == 0 then delta becomes 1; otherwise, delta is 0.
       Explanation: (allSameDiff | -allSameDiff) >> 31 yields 0 when allSameDiff==0,
       and 0xFFFFFFFF (i.e. -1) when allSameDiff is nonzero.
       Then &1 yields 0 or 1, and 1 minus that yields 1 or 0. */
    int delta = 1 - (((allSameDiff | -allSameDiff) >> 31) & 1);
    sum += delta;  /* This forces sum nonzero for all-same inputs */

    /* if sum==0 then division by zero triggers a crash. */
    int dummy = 1 / sum;
    (void)dummy;

    out("Safe execution.");
    return 0;
}
