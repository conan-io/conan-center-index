#include <tree_sitter/api.h>
#include <tree_sitter/tree-sitter-cuda.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

char const kernel[] = "\
#include <vector>\
#include <cuda.h>\
\
__global__ void add_vectors(double *a, double *b, double *c, std::size_t N)\
{\
    int id = blockDim.x * blockIdx.x + threadIdx.x;\
    if(id < N) c[id] = a[id] + b[id];\
}\
\
int main() {\
    constexpr std::size_t N = 4;\
    std::vector<double> v1 = {1.0, 2.0, 3.0, 4.0};\
    std::vector<double> v2 = {5.0, 6.0, 7.0, 8.0};\
    std::vector<double> result(N);\
    double *v1_dev, *v2_dev, *res_dev;\
    cudaMalloc((void**)(&v1_dev), N * sizeof(double));\
    cudaMalloc((void**)(&v2_dev), N * sizeof(double));\
    cudaMalloc((void**)(&res_dev), N * sizeof(double));\
    cudaMemcpy(v1_dev, v1.data(), N * sizeof(double), cudaMemcpyHostToDevice);\
    cudaMemcpy(v2_dev, v2.data(), N * sizeof(double), cudaMemcpyHostToDevice);\
    cuda_hello<<<1,N>>>(v1_dev, v2_dev, res_dev, N);\
    cudaMemcpy(result.data(), res_dev, N * sizeof(double), cudaMemcpyDeviceToHost);\
    cudaFree(res_dev);\
    cudaFree(v2_dev);\
    cudaFree(v1_dev);\
    return 0;\
}\
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

