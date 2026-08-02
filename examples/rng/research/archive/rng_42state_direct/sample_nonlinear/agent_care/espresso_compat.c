#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "misc/util/abc_global.h"

ABC_NAMESPACE_IMPL_START

char *util_optarg = NULL;
int util_optind = 0;
static const char *scan = NULL;

char *MMalloc(long size) {
    char *result = (char *)malloc((size_t)(size > 0 ? size : 1));
    if (result == NULL) {
        fprintf(stderr, "out of memory allocating %ld bytes\n", size);
        exit(1);
    }
    return result;
}

char *MMrealloc(char *object, long size) {
    char *result = (char *)realloc(object, (size_t)(size > 0 ? size : 1));
    if (result == NULL) {
        fprintf(stderr, "out of memory reallocating %ld bytes\n", size);
        exit(1);
    }
    return result;
}

abctime Extra_CpuTime(void) {
    return (abctime)((double)clock() * 1000.0 / CLOCKS_PER_SEC);
}

int Extra_GetSoftDataLimit(void) {
    return 1024 * 1024 * 1024;
}

static void out_of_memory(long size) {
    fprintf(stderr, "out of memory allocating %ld bytes\n", size);
    exit(1);
}

void (*Extra_UtilMMoutOfMemory)(long size) = out_of_memory;

void util_getopt_reset(void) {
    util_optarg = NULL;
    util_optind = 0;
    scan = NULL;
}

int util_getopt(int argc, char **argv, char *options) {
    const char *match;
    util_optarg = NULL;
    if (scan == NULL || *scan == '\0') {
        if (util_optind == 0) {
            ++util_optind;
        }
        if (util_optind >= argc || argv[util_optind][0] != '-' || argv[util_optind][1] == '\0') {
            return EOF;
        }
        if (strcmp(argv[util_optind], "--") == 0) {
            ++util_optind;
            return EOF;
        }
        scan = argv[util_optind++] + 1;
    }
    {
        int option = (unsigned char)*scan++;
        match = strchr(options, option);
        if (match == NULL || option == ':') {
            fprintf(stderr, "%s: unknown option %c\n", argv[0], option);
            return '?';
        }
        if (match[1] == ':') {
            if (*scan != '\0') {
                util_optarg = (char *)scan;
                scan = NULL;
            } else if (util_optind < argc) {
                util_optarg = argv[util_optind++];
                scan = NULL;
            } else {
                fprintf(stderr, "%s: %c requires an argument\n", argv[0], option);
                return '?';
            }
        }
        return option;
    }
}

char *util_print_time(long milliseconds) {
    static char buffer[40];
    snprintf(buffer, sizeof(buffer), "%ld.%02ld sec", milliseconds / 1000,
             (milliseconds % 1000) / 10);
    return buffer;
}

char *util_strsav(char *text) {
    size_t length;
    char *copy;
    if (text == NULL) {
        return NULL;
    }
    length = strlen(text);
    copy = MMalloc((long)length + 1);
    memcpy(copy, text, length + 1);
    return copy;
}

ABC_NAMESPACE_IMPL_END
