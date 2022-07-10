#include "gm2calc/gm2_1loop.hpp"
#include "gm2calc/gm2_2loop.hpp"
#include "gm2calc/gm2_error.hpp"
#include "gm2calc/gm2_uncertainty.hpp"
#include "gm2calc/gm2_version.h"
#include "gm2calc/MSSMNoFV_onshell.hpp"
#include <iostream>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

gm2calc::MSSMNoFV_onshell setup() {
   gm2calc::MSSMNoFV_onshell model;

   const Eigen::Matrix<double,3,3> UnitMatrix
      = Eigen::Matrix<double,3,3>::Identity();

   // fill SM parameters
   model.set_alpha_MZ(0.00775531);              // 1L
   model.set_alpha_thompson(0.00729735);        // 2L
   model.set_g3(std::sqrt(4 * M_PI * 0.1184));  // 2L
   model.get_physical().MFt   = 173.34;         // 2L
   model.get_physical().MFb   = 4.18;           // 2L, mb(mb) MS-bar
   model.get_physical().MFm   = 0.1056583715;   // 1L
   model.get_physical().MFtau = 1.777;          // 2L
   model.get_physical().MVWm  = 80.385;         // 1L
   model.get_physical().MVZ   = 91.1876;        // 1L

   // fill pole masses
   model.get_physical().MSvmL   =  5.18860573e+02; // 1L
   model.get_physical().MSm(0)  =  5.05095249e+02; // 1L
   model.get_physical().MSm(1)  =  5.25187016e+02; // 1L
   model.get_physical().MChi(0) =  2.01611468e+02; // 1L
   model.get_physical().MChi(1) =  4.10040273e+02; // 1L
   model.get_physical().MChi(2) = -5.16529941e+02; // 1L
   model.get_physical().MChi(3) =  5.45628749e+02; // 1L
   model.get_physical().MCha(0) =  4.09989890e+02; // 1L
   model.get_physical().MCha(1) =  5.46057190e+02; // 1L
   model.get_physical().MAh(1)  =  1.50000000e+03; // 2L

   // fill DR-bar parameters
   model.set_TB(40);                        // 1L
   model.set_Mu(500);                       // initial guess
   model.set_MassB(200);                    // initial guess
   model.set_MassWB(400);                   // initial guess
   model.set_MassG(2000);                   // 2L
   model.set_mq2(7000 * 7000 * UnitMatrix); // 2L
   model.set_ml2(0, 0, 500 * 500);          // 2L
   model.set_ml2(1, 1, 500 * 500);          // irrelevant
   model.set_ml2(2, 2, 500 * 500);          // 2L
   model.set_md2(7000 * 7000 * UnitMatrix); // 2L
   model.set_mu2(7000 * 7000 * UnitMatrix); // 2L
   model.set_me2(0, 0, 500 * 500);          // 2L
   model.set_me2(1, 1, 500 * 500);          // initial guess
   model.set_me2(2, 2, 500 * 500);          // 2L
   model.set_Au(2, 2, 0);                   // 2L
   model.set_Ad(2, 2, 0);                   // 2L
   model.set_Ae(1, 1, 0);                   // 1L
   model.set_Ae(2, 2, 0);                   // 2L
   model.set_scale(1000);                   // 2L

   // convert DR-bar parameters to on-shell
   model.convert_to_onshell();

   // check for warnings
   if (model.get_problems().have_warning())
     std::cout << model.get_problems().get_warnings()  << '\n';

   // check for problems
   if (model.get_problems().have_problem())
     std::cout << model.get_problems().get_problems()  << '\n';

   return model;
}

int main() {
   std::cout << "GM2Calc " << GM2CALC_VERSION << '\n';

   try {
      gm2calc::MSSMNoFV_onshell model(setup());

      const double amu =
         + gm2calc::calculate_amu_1loop(model)
         + gm2calc::calculate_amu_2loop(model);

      const double delta_amu =
         gm2calc::calculate_uncertainty_amu_2loop(model);

      std::cout << "amu = " << amu << " +- " << delta_amu << std::endl;
   } catch (const gm2calc::Error& e) {
      std::cout << e.what() << std::endl;
   }

   return 0;
}
