#include <libcmaes/cmaes.h>   
#include <iostream>

using namespace libcmaes;

FitFunc fsphere = [](const double *x, const int N)
{
  double val = 0.0;
  for (int i=0;i<N;i++)
    val += x[i]*x[i];
  return val;
};

int test1()
{
  int dim = 10; // problem dimensions.
  std::vector<double> x0(dim,10.0);
  double sigma = 0.1;
  //int lambda = 100; // offsprings at each generation.
  CMAParameters<> cmaparams(x0,sigma);
  //cmaparams._algo = BIPOP_CMAES;
  CMASolutions cmasols = cmaes<>(fsphere,cmaparams);
  std::cout << "best solution: " << cmasols << std::endl;
  std::cout << "optimization took " << cmasols.elapsed_time() / 1000.0 << " seconds\n";

  Candidate bcand = cmasols.best_candidate();

  std::vector<double> xsol = bcand.get_x();
  return EXIT_SUCCESS;
}

int test2()
{
  int dim = 10; // problem dimensions.
  std::vector<double> x0(dim,10.0);
  double sigma = 0.1;
  double ftol = 1e-5;

  CMAParameters<> cmaparams(x0, sigma);
  // cmaparams.set_mt_feval(true);
  cmaparams.set_algo(aCMAES);
  // cmaparams.set_elitism(1);
  // cmaparams.set_noisy();
  cmaparams.set_ftolerance(ftol);
  CMASolutions cmasols = cmaes<>(fsphere, cmaparams);

  Candidate bcand = cmasols.best_candidate();

  std::vector<double> xsol = bcand.get_x();

  std::cout << "best solution: " << cmasols << std::endl;
  std::cout << "optimization took " << cmasols.elapsed_time() / 1000.0 << " seconds\n";
  return EXIT_SUCCESS;
}

int main()
{
  test1();
  test2();
  return EXIT_SUCCESS;
}
