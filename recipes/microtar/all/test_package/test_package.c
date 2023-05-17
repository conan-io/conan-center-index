#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <microtar.h>

int main()
{
    mtar_t tar;
    const char *str1 = "Hello world";
    const char *str2 = "Goodbye world";
    
    /* Open archive for writing */
    mtar_open(&tar, "test.tar", "w");
    
    /* Write strings to files `test1.txt` and `test2.txt` */
    mtar_write_file_header(&tar, "test1.txt", strlen(str1));
    mtar_write_data(&tar, str1, strlen(str1));
    mtar_write_file_header(&tar, "test2.txt", strlen(str2));
    mtar_write_data(&tar, str2, strlen(str2));
    
    /* Finalize -- this needs to be the last thing done before closing */
    mtar_finalize(&tar);
    
    /* Close archive */
    mtar_close(&tar);
}
