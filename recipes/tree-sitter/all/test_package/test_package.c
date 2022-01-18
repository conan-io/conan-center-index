#include <tree_sitter/api.h>

//More detailed example search at https://tree-sitter.github.io/tree-sitter/using-parsers#getting-started
int main() {
    TSParser *parser = ts_parser_new();
    ts_parser_delete(parser);
    return 0;
}
