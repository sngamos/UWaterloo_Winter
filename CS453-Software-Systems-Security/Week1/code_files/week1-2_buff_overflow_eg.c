#include <stdio.h>
#include <string.h>

int main(void) {
char buff[8];
int pass = 0;

printf("Enter the password: ");
gets(buff);

if(strcmp(buff, "warriors")) {
printf("Wrong password\n");
} else {
printf("Correct password\n");
pass = 1;
}

if(pass) {
printf ("Root privileges granted\n");
}
return 0;
}
