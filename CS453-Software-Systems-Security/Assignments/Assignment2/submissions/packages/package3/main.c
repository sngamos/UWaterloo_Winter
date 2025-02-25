#include <stddef.h>
#include <sys/types.h>

/* External interfaces (as provided) */
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

int main(void) {
    unsigned char buf[64];
    ssize_t r = in(buf, 64);
    if (r <= 0) {
        out("Input error.");
        return 0;
    }
    /* Pad missing bytes with 1 */
    for (int i = r; i < 64; i++) {
        buf[i] = 1;
    }
    /* Check if the array is sorted in ascending order.
       For each adjacent pair, compute diff = buf[i+1]-buf[i].
       For nonnegative diff, (diff >> 31) is 0 so ((diff >> 31)+1)==1.
       For a negative diff, (diff >> 31) is -1, so ((diff >> 31)+1)==0.
       Multiply these together into flag. If all differences are nonnegative,
       flag remains 1; if any difference is negative, flag becomes 0. */
    int flag = 1;
    for (int i = 0; i < 63; i++) {
        int diff = (int)buf[i+1] - (int)buf[i];
        int cond = ((diff >> 31) + 1);  /* 1 if diff>=0, 0 if diff<0 */
        flag *= cond;
    }
    /* Crash if sorted: if flag==1 then (flag-1)==0, so division by zero */
    int dummy = 1 / (flag - 1);
    (void)dummy;
    out("Safe execution.");
    return 0;
}
