#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <attr/libattr.h>


int main(void) {
    printf("libattr test package: attr_copy_file\n");
    attr_copy_file("file_not_exist.txt", "attr_not_exist", NULL, NULL);
    return EXIT_SUCCESS;
}
