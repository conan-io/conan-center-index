#include <tree_sitter/api.h>
#include <tree-sitter-cql.h>

int main() {
    TSParser *parser = ts_parser_new();
    ts_parser_set_language(parser, tree_sitter_cql());
    ts_parser_delete(parser);
    return 0;
}

