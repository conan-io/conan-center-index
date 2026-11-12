#include <tree_sitter/api.h>
#include <tree_sitter/tree-sitter-cuda.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

char const kernel[] = "\
__global__ void my_kernel(int *data) {\
    data[0] = 1;\
}\
int main() { return 0; }\
";

#define ASSERT_TRUE(var, msg) if ((var) != true) { printf("%d::%s\n", __LINE__, (msg)); exit(1);}
#define ASSERT_NOT_NULL(var, msg) if ((var) == NULL) { printf("%d::%s\n", __LINE__, (msg)); exit(1);}

int main() {
  TSParser *parser = ts_parser_new();
  ASSERT_NOT_NULL(parser, "parser is NULL");
  const TSLanguage * lang = tree_sitter_cuda();
  ASSERT_NOT_NULL(lang, "lang is NULL");
  bool result = ts_parser_set_language(parser, lang);
  ASSERT_TRUE(result, "cannot set language");
  TSTree *tree =
    ts_parser_parse_string(parser, NULL, kernel, strlen(kernel));
  ASSERT_NOT_NULL(tree, "tree is NULL");
  TSNode root_node = ts_tree_root_node(tree);  
  char *string = ts_node_string(root_node);
  ASSERT_NOT_NULL(string, "string is NULL");
  printf("Syntax tree: %s\n", string);
  free(string);

  ts_tree_delete(tree);
  ts_parser_delete(parser);
  printf("========\nsuccess!\n========\n");
  return 0;
}

