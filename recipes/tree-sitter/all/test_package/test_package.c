#include <tree_sitter/api.h>
#include <stdio.h>

//More datailed example search at https://tree-sitter.github.io/tree-sitter/using-parsers#getting-started
int main() {
  TSParser *parser = ts_parser_new();
  ts_parser_delete(parser);
  printf( "Test package\n" );
  return 0;
}

