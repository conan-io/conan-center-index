#include <stdio.h>
#include <string.h>

#include "tree_sitter/api.h"
#ifdef TREE_SITTER_SQL_OLD_PATH
#include "tree-sitter-sql.h"
#else
#include "tree_sitter/tree-sitter-sql.h"
#endif

int main() {
    TSParser *parser = ts_parser_new();
    ts_parser_set_language(parser, tree_sitter_sql());
    const char *source_code = "select * from dummy_table;\n";
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
