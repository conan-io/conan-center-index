#include <openblas/cblas.h>

#include <iostream>
#include <vector>

extern "C" void dgetrf_(int* dim1, int* dim2, double* a, int* lda, int* ipiv, int* info);
extern "C" void dgetrs_(char *TRANS, int *N, int *NRHS, double *A, int *LDA, int *IPIV, double *B, int *LDB, int *INFO );

int main()
{
  int i=0;
  double A[6] = {1.0,2.0,1.0,-3.0,4.0,-1.0};
  double B[6] = {1.0,2.0,1.0,-3.0,4.0,-1.0};
  double C[9] = {.5,.5,.5,.5,.5,.5,.5,.5,.5};
  cblas_dgemm(CblasColMajor, CblasNoTrans, CblasTrans,3,3,2,1,A, 3, B, 3,2,C,3);

  for(i=0; i<9; i++)
    std::cout << C[i];
  std::cout << std::endl;

  // Solving a system with lapack
  char trans = 'N';
  int dim = 2;
  int nrhs = 1;
  int LDA = dim;
  int LDB = dim;
  int info;

  std::vector<double> a, b;

  a.push_back(2);
  a.push_back(3);
  a.push_back(1);
  a.push_back(-4);

  b.push_back(7);
  b.push_back(5);

  int ipiv[3];

  dgetrf_(&dim, &dim, &*a.begin(), &LDA, ipiv, &info);
  dgetrs_(&trans, &dim, &nrhs, & *a.begin(), &LDA, ipiv, & *b.begin(), &LDB, &info);

  std::cout << "solution is:" << "[" << b[0] << ", " << b[1] << ", " << "]" << std::endl;
}
