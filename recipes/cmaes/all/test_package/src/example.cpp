#include <libcmaes/cmaes.h>   
#include <iostream>

using namespace libcmaes;

FitFunc fsphere = [](const double *x, const int N)
{
  double val = 0.0;
  for (int i=0;i<N;i++)
  {
    val += x[i]*x[i];
  }
  return val;
};

int main()
{
  int dim = 10;
  std::vector<double> x0(dim,10.0);
  double sigma = 0.1;
  double ftol = 1e-5;

  CMAParameters<> cmaparams(x0, sigma);
  cmaparams.set_algo(aCMAES);
  cmaparams.set_ftolerance(ftol);
  CMASolutions cmasols = cmaes<>(fsphere, cmaparams);

  Candidate bcand = cmasols.best_candidate();

  std::vector<double> xsol = bcand.get_x();

  std::cout << "best solution: " << cmasols << std::endl;
  std::cout << "optimization took " << cmasols.elapsed_time() / 1000.0 << " seconds\n";
  return EXIT_SUCCESS;
}
