#include "md4c.h"

#include <stdio.h>
#include <string.h>

int enter_block(MD_BLOCKTYPE type, void* detail, void* userdata) {
    printf("enter block\n");
    return 0;
}

int leave_block(MD_BLOCKTYPE type, void* detail, void* userdata) {
    printf("leave block\n");
    return 0;
}

int enter_span(MD_SPANTYPE type, void* detail, void* userdata) {
    printf("enter span\n");
    return 0;
}

int leave_span(MD_SPANTYPE type, void* detail, void* userdata) {
    printf("leave span\n");
    return 0;
}

int text_block(MD_TEXTTYPE type, const MD_CHAR* text, MD_SIZE size, void* usrdata) {
    printf("text block\n");
    return 0;
}

int main() {
    const char DATA[] =
        "# title\n"
        "\n"
        "example1\n"
        "`example2`\n"
        "\n"
        "> example3\n"
        "\n"
        ;

    printf("%s\n", DATA);

    MD_PARSER parser;

    parser.abi_version = 0;
    parser.flags = MD_FLAG_TABLES;
    parser.enter_block = enter_block;
    parser.leave_block = leave_block;
    parser.enter_span = enter_span;
    parser.leave_span = leave_span;
    parser.text = text_block;

    md_parse(DATA, strlen(DATA), &parser, NULL);

    return 0;
}
