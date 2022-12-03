#include "himalaya/HierarchyCalculator.hpp"
#include "himalaya/version.hpp"
#include <iostream>
#include <cmath>

himalaya::Parameters setup_point(double MS, double tb, double xt)
{
   himalaya::Parameters pars;

   const double MS2 = MS*MS;
   const double Xt = xt*MS;
   const double beta = std::atan(tb);
   pars.scale = MS;
   pars.mu = MS;
   pars.g1 = 0.46;
   pars.g2 = 0.65;
   pars.g3 = 1.166;
   pars.vd = 246*std::cos(beta);
   pars.vu = 246*std::sin(beta);
   pars.mq2 << MS2, 0, 0,
               0, MS2, 0,
               0, 0, MS2;
   pars.md2 << MS2, 0, 0,
               0, MS2, 0,
               0, 0, MS2;
   pars.mu2 << MS2, 0, 0,
               0, MS2, 0,
               0, 0, MS2;
   pars.ml2 << MS2, 0, 0,
               0, MS2, 0,
               0, 0, MS2;
   pars.me2 << MS2, 0, 0,
               0, MS2, 0,
               0, 0, MS2;
   pars.Au << 0, 0, 0,
              0, 0, 0,
              0, 0, Xt + pars.mu/tb;
   pars.Ad << 0, 0, 0, 0, 0, 0, 0, 0, 0;
   pars.Ae << 0, 0, 0, 0, 0, 0, 0, 0, 0;
   pars.Yu << 0, 0, 0, 0, 0, 0, 0, 0, 0.862;
   pars.Yd << 0, 0, 0, 0 ,0 ,0 ,0 ,0, 0.133;
   pars.Ye << 0, 0, 0, 0, 0, 0, 0, 0, 0.101;
   pars.MA = MS;
   pars.M1 = MS;
   pars.M2 = MS;
   pars.MG = MS;

   pars.validate(true);

   return pars;
}

int main()
{
   const auto point = setup_point(2000., 20., std::sqrt(6.));
   himalaya::HierarchyCalculator hc(point);

   try {
      // calculate the 3-loop corrections O(α_t*α_s^2)
      const auto ho = hc.calculateDMh3L(false);

      // extract 2x2 matrix with three-loop O(αt*αs^2) corrections
      const auto dMh3L = ho.getDMh(3);
      // extract three-loop O(αt*αs^2) correction to λ (DR'-bar scheme)
      const double delta_lambda_3L_DR = ho.getDLambda(3);
      // extract uncertainty estimate
      const double delta_lambda_3L_uncertainty = ho.getDLambdaUncertainty(3);
      // convert to MS-bar scheme
      const double delta_lambda_3L_MS =
         delta_lambda_3L_DR + ho.getDLambdaDRbarPrimeToMSbarShift(3);

      std::cout << "Himalaya version: "
                << Himalaya_VERSION_MAJOR << '.'
                << Himalaya_VERSION_MINOR << '.'
                << Himalaya_VERSION_RELEASE << '\n';

      std::cout << "ΔMh^2(3-loop,DR') = \n" << dMh3L << '\n'
                << "Δλ(3-loop,DR') = " << delta_lambda_3L_DR
                << " +- " << delta_lambda_3L_uncertainty << '\n'
                << "Δλ(3-loop,MS) = " << delta_lambda_3L_MS
                << " +- " << delta_lambda_3L_uncertainty << '\n';
   } catch (const std::exception& e) {
      std::cerr << "Error: " << e.what() << '\n';
   }

   return 0;
}
