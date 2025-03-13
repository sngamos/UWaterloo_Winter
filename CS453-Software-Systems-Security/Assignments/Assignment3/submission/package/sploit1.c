//sploit1.c

#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <sys/uio.h>

int main(void) {
    int fd = open("flag", O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    char buf[1024];
    ssize_t n = read(fd, buf, sizeof(buf));
    if (n < 0) {
        perror("read");
        close(fd);
        return 1;
    }
    close(fd);

    // Use writev to output the flag
    struct iovec iov;
    iov.iov_base = buf;
    iov.iov_len = n;

    ssize_t bytes_written = writev(STDOUT_FILENO, &iov, 1);
    if (bytes_written < 0) {
        perror("writev");
        return 1;
    }

    return 0;
}