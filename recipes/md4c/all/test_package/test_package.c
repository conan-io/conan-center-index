#include "md4c.h"

#include <stdio.h>

int enter_block(MD_BLOCKTYPE type, void* detail, void* userdata) {
    printf("enter block\n");
}

int leave_block(MD_BLOCKTYPE type, void* detail, void* userdata) {
    printf("leave block\n");
}

int enter_span(MD_SPANTYPE type, void* detail, void* userdata) {
    printf("enter span\n");
}

int leave_span(MD_SPANTYPE type, void* detail, void* userdata) {
    printf("leave span\n");
}

int text_block(MD_TEXTTYPE type, const MD_CHAR* text, MD_SIZE size, void* usrdata) {
    printf("text block\n");
}

int main() {
    const char DATA[] =
        "# title\n"
        "\n"
        "example1\n"
        "example2\n"
        "\n"
        "example3\n"
        ;

    MD_PARSER parser;

    parser.abi_version = 0;
    parser.flags = MD_FLAG_TABLES;

    parser.enter_block = enter_block;
    parser.leave_block = leave_block;
    parser.enter_span = enter_span;
    parser.leave_span = leave_span;
    parser.text = text_block;

    md_parse(DATA, sizeof(DATA) / sizeof(DATA[0]), &parser, NULL);

    return 0;
}
