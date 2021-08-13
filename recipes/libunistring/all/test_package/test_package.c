#include <unistr.h>

#include <stdio.h>
#include <string.h>
#include <wchar.h>

int main(int argc, char * argv[]) {
    const char *text = "This is some text";
    if (u8_check(text, strlen(text)) != NULL) {
        printf("u8_check failed on input string\n");
        return 1;
    }
    uint16_t resultbuf[64];
    size_t resultSize = 64;
    u8_to_u16(text, strlen(text)+1, resultbuf, &resultSize);
    if (u16_check(resultbuf, resultSize) != NULL) {
        printf("u16_check failed\n");
        return 1;
    }
    printf(  "char array:      '%s'\n", text);
    wprintf(L"wide char array: '%s'\n", resultbuf);
    return 0;
}
