//
// Created by Philip Decker on 08.12.21.
//


#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#include <sys/random.h>

#define min(a, b) (((a)<(b))?(a):(b))

char CURR_USER[0x32];
char RANDOM_DIR[0x16];
char *USAGE_SINGLE = "Please check your input, usage: <firstname> <lastname> <from> <to> <date>";
char *USAGE_GROUP = "Please check your input, usage: <date> <firstname> <lastname> <from> <to>";
char *DATA_DIR = "data/";

void create_rnd_dir() {
    // make sure it creates a directory
    int result = 1;
    char tmp[5 + 20 + 1 + 20];
    while (result == 1) {
        // create random string 
        size_t size = 20;
        const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        if (size) {
            --size;
            for (size_t n = 0; n < size; n++) {
                int key = rand() % (int) (sizeof charset - 1);
                RANDOM_DIR[n] = charset[key];
            }
            RANDOM_DIR[20] = '\0';
        }

        // now create the directory
        strncpy(tmp, DATA_DIR, 6);
        strcat(tmp, CURR_USER);
        strcat(tmp, "/");
        strcat(tmp, RANDOM_DIR);
        result = mkdir(tmp, 0777);
    }

    puts("Here is your secret key for obtaining the tickets later:");
    printf("%14s \n", RANDOM_DIR); // <-- 14 != 0x14 ?

}


void show_logo() {
     puts(
        "=========================================================================\n"
        "          \\  \\        \\  \\                \\  \\        \\  \\   \n"
        "   _______/  /________/  /________  ______/  /________/  /__________  \n" 
        "  /   |   _____                  | |             __      ___      __| \n"
        " /    |  / ____|                 | |             \\ \\    / \\ \\    / /|\n"
        "/     | | (___   __ _  __ _ _ __ | |  ___  ___  __\\ \\  / / \\ \\  / / |\n"
        "|_____|  \\___ \\ / _` |/ _` | '__|| | / __|/ _ \\/ __\\ \\/ /   \\ \\/ /  |\n"
        "|        ____) | (_| | (_| | |   | | \\__ |  __| (__ \\  /     \\  /   |\n"
        " \\      |_____/ \\__,_|\\__,_|_|   | | |___/\\___|\\___| \\/       \\/    |\n"
        "  \\___     _____     _____     __|#|__     _____     _____     _____|#\n"
        "  /    \\___/     \\___/     \\___/       \\___/     \\___/     \\___/   \n"
        "=========================================================================\n"
    );
    puts("Welcome to the fastest way of public transportation !!");
    return;
}

void clearScreen() {
    const char *CLEAR_SCREEN_ANSI = "\e[1;1H\e[2J";
    write(STDOUT_FILENO, CLEAR_SCREEN_ANSI, 11);

    return;
}

void printTickets(char *secretKey) {
    DIR *d;
    struct dirent *dir;
    FILE *fptr;
    char ch;
    char tmp[100];

    strncpy(tmp, DATA_DIR, 6);
    strcat(tmp, CURR_USER);
    strcat(tmp, "/");
    strcat(tmp, secretKey);
    d = opendir(tmp);
    if (d) {
        puts("Here is your ticketcode and your ticket:");
        while ((dir = readdir(d)) != NULL) {
            if (strcmp(dir->d_name, ".") && strcmp(dir->d_name, "..")) {
                char tmp2[150];
                printf("%s\n", dir->d_name);
                strncpy(tmp2, tmp, 100);
                strcat(tmp2, "/");
                strcat(tmp2, dir->d_name);
                fptr = fopen(tmp2, "r");
                if (fptr != NULL) {
                    ch = fgetc(fptr);
                    while (ch != EOF) {
                        printf("%c", ch);
                        ch = fgetc(fptr);
                    }
                    printf("\n\n");
                    fclose(fptr);
                }
            }
        }
        closedir(d);
    }
    return;
}

void storeTicket(char *ticketString, unsigned long ticketCode) {
    char tmp[6 + 50 + 21 + 2 + 5 + 5];
    FILE *fp;

    strncpy(tmp, DATA_DIR, 6);
    strcat(tmp, CURR_USER);
    strcat(tmp, "/");
    strcat(tmp, RANDOM_DIR);
    strcat(tmp, "/");

    const int n = snprintf(NULL, 0, "%lu", ticketCode);
    char tmp1[n + 1 + 5];
    snprintf(tmp1, n + 1, "%lu", ticketCode);
    strcat(tmp, tmp1);
    fp = fopen(tmp, "w+");
    fputs(ticketString, fp);
    fclose(fp);

    return;
}

typedef struct {
    size_t groupnamesize;
    char groupname[0x32];
    size_t fromsize;
    char from[0x32];
    size_t tosize;
    char to[0x32];
    size_t datesize;
    char date[11];
    size_t namesize;
    char name[0x128];
    char number[0x4];
} Ticket;



// -------------------- GROUP TICKET ------------------------

// here the process of generating a ticket should be vulnerable to a bufferoverflow
// and also this gets process gets forked

unsigned long genTicketCode(Ticket *ticketPtr)
{
    // TODO: we need a random code as start
    char tmp[144];
    size_t size = 0;
    unsigned long code = 0x12345;
    char splitter = ':';

    if (ticketPtr->groupname[0]) {
        for (size_t i = 0; i < ticketPtr->groupnamesize; i++) {
            char x = ticketPtr->groupname[i];
            code <<= 1;
            code ^= x;
            //memcpy(&tmp[size + i], &ticketPtr->groupname[i], 1);
            tmp[size++] = x;
        }

        tmp[size] = splitter;
        size++;
    }

    for (size_t i = 0; i < ticketPtr->datesize; i++) {
        char x = ticketPtr->date[i];
        code <<= 1;
        code ^= x;
        //memcpy(&tmp[size + i], &ticketPtr->date[i], 1);
        tmp[size++] = x;
    }

    tmp[size] = splitter;
    size++;

    for (size_t i = 0; i < ticketPtr->fromsize; i++) {
        char x = ticketPtr->from[i];
        code <<= 1;
        code ^= x;
        //memcpy(&tmp[size + i], &ticketPtr->from[i], 1);
        tmp[size++] = x;
    }

    tmp[size] = splitter;
    size++;

    for (size_t i = 0; i < ticketPtr->tosize; i++) {
        char x = ticketPtr->to[i];
        code <<= 1;
        code ^= x;
        //memcpy(&tmp[size + i], &ticketPtr->to[i], 1);
        tmp[size++] = x;
    }

    tmp[size] = splitter;
    size++;

    if (ticketPtr->number[0]) {
        for (size_t i = 0; i < 4; i++) {
            char x = ticketPtr->number[i];
            code <<= 1;
            code ^= x;
            //memcpy(&tmp[size + i], &ticketPtr->number[i], 1);
            tmp[size++] = x;
        }

        tmp[size] = splitter;
        size++;
    }

    for (size_t i = 0; i < ticketPtr->namesize; i++) {
        char x = ticketPtr->name[i];
        code <<= 1;
        code ^= x;
        //memcpy(&tmp[size + i], &ticketPtr->name[i], 1);
        tmp[size++] = x;
    }
    // maybe use this for logging and write it to log file
    //printf("%s",tmp);
    return code;
}


void generateTicket(Ticket *ticketPtr) {
    // generate the ticket code -> overflow now here happening
    unsigned long ticketCode = genTicketCode(ticketPtr);


    // ticket string -> make sure this does not overflow or the tmp is overflowing
    char id[0x144];
    char groupname[0x32];
    sprintf(groupname, "%s", ticketPtr->groupname);

    if (!strcmp(groupname, "")) {
        sprintf(id, "%lu:%s:%s:%s:%s", ticketCode, ticketPtr->date, ticketPtr->from, ticketPtr->to,
                ticketPtr->name);
    } else {
        sprintf(id, "%lu:%s:%s:%s:%s:%s:%s", ticketCode, ticketPtr->groupname, ticketPtr->date, ticketPtr->from,
                ticketPtr->to,
                ticketPtr->number, ticketPtr->name);
    }

    // now store the ticket  -> will not be stored anymore since crashing before hopefully
    storeTicket(id, ticketCode);

}

void buy_multiple_tickets() {
    int amount;
    int status = 0;

    pid_t child_pid, wpid, curr_pid;
    Ticket *ticketPtr;
    Ticket myTicket = {0};
    ticketPtr = &myTicket;

    // start process of generating
    puts("Great here you can buy group tickets!");
    puts("How many members has your group?");
    scanf("%3d", &amount);

    if (amount <= 10 || amount >= 260) {
        // if an error occurs amount == 0  -> will bet handled this way as well
        // hint somehow that canary is just some numbers -> otherwise overhead to bruteforce
        //
        puts("Currently just group sizes between 10 and 260 are supported");
        puts("Bye !");
        return;
    }

    printf("\nTicket for %d Persons will be generated \r\n", amount);

    // get the group name
    puts("What is your group name?");
    myTicket.groupnamesize = read(STDIN_FILENO, myTicket.groupname, 50);

    // date
    puts("\nPlease provide the travelling date: <dd.mm.yyyy>");
    // maybe add regex to check input
    myTicket.datesize = read(STDIN_FILENO, myTicket.date, 11);

    // to
    puts("\nWhere do you want to travel?");
    myTicket.tosize = read(STDIN_FILENO, myTicket.to, 50);

    // from
    puts("\nWhere do you want to start?");
    myTicket.fromsize = read(STDIN_FILENO, myTicket.from, 50);

    puts("\nNow provide all names of the group one by one");

    for (int i = 0; i < amount; i++) {
        printf("\nName of group member %d?", i + 1);
        myTicket.namesize = read(STDIN_FILENO, myTicket.name, 50);
        sprintf(myTicket.number, "%03d", i);

        // check if I am a child, then execute generateGroupTicket
        if ((curr_pid = fork()) == 0) {
            generateTicket(ticketPtr);
            exit(0);
        }else{
            memset(myTicket.name, 0, 50);
        }
        // add a sleep here so there are not 260 children running in parallel
    }
    // now wait until all forks are either crashed or exit
    while ((wpid = wait(&status)) > 0); // this way, the father waits for all the child processes 

    // generating of the tickets done -> return the generated tickets
    puts("Generating of the tickets done!");

    // print all tickets inside /random/tickets
    printTickets(RANDOM_DIR);

    puts("\nYou will get back to main Menu");
    return;

}

// --------------- SINGLE TICKET --------------------

void buy_single_ticket() {
    Ticket myTicket = {0};
    Ticket *ticketPtr;
    ticketPtr = &myTicket;

    puts("Great here you can buy a single ticket!");
    puts("Please provide the travelling date: <dd.mm.yyyy>");
    // maybe add regex to check input
    myTicket.datesize = read(STDIN_FILENO, myTicket.date, 10);

    puts("\nWhere do you want to go?");
    myTicket.tosize = read(STDIN_FILENO, myTicket.to, 50); // Read only 0x32-1 byte here for NUL-termination?

    puts("\nWhere do you want to start?");
    myTicket.fromsize = read(STDIN_FILENO, myTicket.from, 50); // Read only 0x32-1 byte here for NUL-termination?

    puts("\nWhose ticket is it?");
    myTicket.namesize = read(STDIN_FILENO, myTicket.name, 296); // Read only 0x128-1 byte here for NUL-termination?

    puts("\nYour ticket  will be generated \n");

    generateTicket(ticketPtr);
    printTickets(RANDOM_DIR);
    return;
}



// ----------------- LIST-BOOKINGS ----------------

void list_bookings() {
    char secretKey[0x32] = {0};
    puts("To read old bookings please provide the secret key");
    read(STDIN_FILENO, secretKey, 50);
    printTickets(secretKey);
    puts("\nYou will now get back to the main menu\n");
    return;
}
// ------------------- LOGIN ------------------------

void check(char *username) {
    char tmp[6 + 50];
    strncpy(tmp, DATA_DIR, 6);
    strcat(tmp, username);
    DIR *dir = opendir(tmp);
    if (dir) {
        // Directory exists. -> Username exists
        closedir(dir);
        puts("\nUsername already exists!");
        exit(0);

    } else if (ENOENT == errno) {
        puts("\nUsername is yours now!");
        return;

    } else {
        puts("\nSomething went wrong,try again later.");
        exit(0);
    }
}

void login(char *username, char *password) {
    char tmp[6 + 50 + 11];
    char tmp1[6 + 50];
    char pwd[50];
    FILE *fp;

    strncpy(tmp1, DATA_DIR, 6);
    strcat(tmp1, username);
    DIR *dir = opendir(tmp1);
    if (dir) {
        // Directory exists. -> Username exists
        strncpy(tmp, tmp1, 56);
        strcat(tmp, "/.password");
        fp = fopen(tmp, "r");
        fscanf(fp, "%50s", pwd);
        fclose(fp);

        if (strcmp(password, pwd)) {
            puts("\nPassword is wrong ;(");
            exit(0);
        } else {
            puts("\nPassword is correct, logged in!");
            closedir(dir);
            return;
        }

    } else if (ENOENT == errno) {
        puts("\nUser does not exist!");
        exit(0);

    } else {
        puts("\nSomething went wrong, try again later.");
        exit(0);
    }
}

void registerUser(char *username, char *password) {
    char tmp[5 + 50 + 11];
    char tmp2[5 + 50];
    FILE *fp;

    struct stat st = {0};
    strncpy(tmp2, DATA_DIR, 6);
    strcat(tmp2, username);
    if (stat(tmp2, &st) == -1) {
        mkdir(tmp2, 0700);
    } else {
        puts("\nSomething went wrong, try again later.");
        exit(0);
    }
    // Directory exists. -> Username exists
    strncpy(tmp, tmp2, 55);
    strcat(tmp, "/.password");
    fp = fopen(tmp, "w");
    fprintf(fp, "%50s", password);
    fclose(fp);
    return;
}

void handle_login() {
    int userInput, len = 0;
    char username[0x32] = {0}, password[0x32] = {0};

    puts("Are you already registered? \n"
         "1 - Yes \n"
         "2 - No \n");

    scanf("%1d", &userInput);
    switch (userInput) {
        case 1:
            puts("Please provide your username:");
            len = read(STDIN_FILENO, username, 50);

            puts("\nPlease provide your password:");
            read(STDIN_FILENO, password, 50);

            login(username, password);
            memcpy(CURR_USER, username, len);
            break;


        case 2:
            puts("New account will be generated! \n"
                 "Please provide a username: (20 chars max)");
            len = read(STDIN_FILENO, username, 50);
            check(username);

            puts("\nProvide a password: (20 chars max)");
            read(STDIN_FILENO, password, 50);

            // Store password
            registerUser(username, password);
            memcpy(CURR_USER, username, len);
            puts("\nSuccessfully created new account and logged in.\n");
            break;
    }
    return;
}

// ---------------- Validate Ticket ------------------

void validateTicket() {
    int userChoice, len, count = 0;
    char *ptr;
    char ticketString[0x144];
    char delimiter[] = ":";
    Ticket myTicket = {0}, *ticketPtr;
    ticketPtr = &myTicket;
    unsigned long ticketCode = 0;
    unsigned long recalculatedTicketCode;

    puts("Here you can validate one of your tickets. \n"
         "What ticket you want to validate? \n"
         " 1 - single ticket \n"
         " 2 - group ticket \n");
    scanf("%1d", &userChoice);

    puts("Please provide your ticket now.");
    scanf("%lu:%324s", &ticketCode, ticketString);

    switch (userChoice) {
        case 1:
            ptr = strtok(ticketString, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.datesize = min(strlen(ptr), 10);
            memcpy(myTicket.date, ptr, myTicket.datesize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.fromsize = min(strlen(ptr), 0x32);
            memcpy(myTicket.from, ptr, myTicket.fromsize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.tosize = min(strlen(ptr), 0x32);
            memcpy(myTicket.to, ptr, myTicket.tosize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.namesize = min(strlen(ptr), 0x32);
            memcpy(myTicket.name, ptr, myTicket.namesize);


            recalculatedTicketCode = genTicketCode(ticketPtr);
            break;

        case 2:
            ptr = strtok(ticketString, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.groupnamesize = min(strlen(ptr), 0x32);
            memcpy(myTicket.groupname, ptr, myTicket.groupnamesize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.datesize = min(strlen(ptr), 10);
            memcpy(myTicket.date, ptr, myTicket.datesize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.fromsize = min(strlen(ptr), 0x32);
            memcpy(myTicket.from, ptr, myTicket.fromsize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.tosize = min(strlen(ptr), 0x32);
            memcpy(myTicket.to, ptr, myTicket.tosize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            size_t numsize = min(strlen(ptr), 4);
            memcpy(myTicket.number, ptr, numsize);

            ptr = strtok(NULL, delimiter);
            if (ptr == NULL) {
                return;
            }
            myTicket.namesize = min(strlen(ptr), 0x32);
            memcpy(myTicket.name, ptr, myTicket.namesize);

            recalculatedTicketCode = genTicketCode(&myTicket);
            break;


        default:
            puts("Invalid input! \n"
                 "You will get back to the main menu now.");
            return;
    }

    if (recalculatedTicketCode == ticketCode) {
        puts("This ticket is successfully validated! \n\n"
             "You will get back to the main menu now.");
        return;
    } else {
        puts("This ticket is not valid ! \n\n"
             "You will get back to the main menu now.");
    }

}

// ------------------- MENU --------------------------

void main_menu() {
    int loop;
    loop = 1;


    while (loop <= 34) {
        int userChoice;
        // TODO: problem: once i did a path traversal the working directory is wrong
        // FIX: -> maybe use total path here
        puts("How can I help you? \n"
             " 1 - Buy a single ticket \n"
             " 2 - Buy a group ticket \n"
             " 3 - Check recent bookings \n"
             " 4 - Validate your Ticket \n"
             " 5 - Exit \n");

        scanf("%1d", &userChoice);
        switch (userChoice) {
            case 1:
                loop++;
                //clearScreen();
                create_rnd_dir();
                buy_single_ticket();
                //clearScreen();
                continue;

            case 2:
                loop++;
                //clearScreen();
                create_rnd_dir();
                buy_multiple_tickets();
                //clearScreen();
                continue;

            case 3:
                loop++;
                //clearScreen();
                list_bookings();
                //clearScreen();
                continue;

            case 4:
                loop++;
                //clearScreen()
                validateTicket();
                //clearScreen()
                continue;

            case 5:
                //clearScreen();
                puts("Thanks for using us, visit us again soon. Bye :)");
                exit(1);

            default:
                loop++;
                //clearScreen();
                puts("That was not valid...Try again :)");
                continue;
        }
    }
    puts("Thanks for using us, visit us soon again. Bye :)");
    exit(1);
}

// ----------------- MAIN -------------------

int main() {
    int seed = 0;
    setbuf(stdout, NULL);
    getrandom(&seed, sizeof(seed), GRND_NONBLOCK);
    srand(seed);
    show_logo();
    handle_login();
    main_menu();
}






