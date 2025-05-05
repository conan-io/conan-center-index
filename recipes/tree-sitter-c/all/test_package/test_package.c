#include <tree_sitter/api.h>
#include <tree_sitter_c/api.h>

#include <stdlib.h>
#include <string.h>

int main() {
    TSParser *parser = ts_parser_new();
    ts_parser_set_language(parser, tree_sitter_c());
    const char *source_code = "int a[] = {42, 1337};\n";
    TSTree *tree = ts_parser_parse_string(
        parser,
        NULL,
        source_code,
        strlen(source_code)
    );
    TSNode root_node = ts_tree_root_node(tree);

    char *string = ts_node_string(root_node);
    printf("Syntax tree: %s\n", string);
    free(string);

    ts_tree_delete(tree);
    ts_parser_delete(parser);
    return 0;
}

