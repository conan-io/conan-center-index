// Example implementation of an objective function class for linear regression
// and usage of the L-BFGS optimizer.
// 
// Compilation:
// g++ example.cpp -o example -O3 -larmadillo


#include <iostream>
#include <armadillo>
#include <ensmallen.hpp>


class LinearRegressionFunction
{
  public:
  
  LinearRegressionFunction(arma::mat& X, arma::vec& y) : X(X), y(y) { }
  
  double EvaluateWithGradient(const arma::mat& theta, arma::mat& gradient)
  {
    const arma::vec tmp = X.t() * theta - y;
    gradient = 2 * X * tmp;
    return arma::dot(tmp,tmp);
  }
  
  private:
  
  const arma::mat& X;
  const arma::vec& y;
};


int main(int argc, char** argv)
{
  if (argc < 3)
  {
    std::cout << "usage: " << argv[0] << " n_dims n_points" << std::endl;
    return -1;
  }
  
  int n_dims   = atoi(argv[1]);
  int n_points = atoi(argv[2]);
  
  // generate noisy dataset with a slight linear pattern
  arma::mat X(n_dims, n_points, arma::fill::randu);
  arma::vec y(        n_points, arma::fill::randu);
  
  for (size_t i = 0; i < n_points; ++i)
  {
    double a = arma::randu();
    X(1, i) += a;
    y(i)    += a;
  }
  
  LinearRegressionFunction lrf(X, y);
  
  // create a Limited-memory BFGS optimizer object with default parameters
  ens::L_BFGS opt;
  opt.MaxIterations() = 10;
  
  // initial point (uniform random)
  arma::vec theta(n_dims, arma::fill::randu);
  
  opt.Optimize(lrf, theta);
  
  // theta now contains the optimized parameters
  theta.print("theta:");
  
  return 0;
}
