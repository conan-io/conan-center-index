#include <ql/qldefines.hpp>
#ifdef BOOST_MSVC
#include <ql/auto_link.hpp>
#endif
#include <ql/experimental/math/multidimintegrator.hpp>
#include <ql/experimental/math/multidimquadrature.hpp>
#include <ql/math/integrals/trapezoidintegral.hpp>
#include <ql/patterns/singleton.hpp>
#include <ql/functional.hpp>

#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <vector>

#if defined(QL_ENABLE_SESSIONS)
namespace QuantLib {
    ThreadKey sessionId() { return {}; }
}
#endif

// Correct value is: (e^{-.25} \sqrt{\pi})^{dimension}
struct integrand {
    QuantLib::Real operator()(const std::vector<QuantLib::Real>& arg) const {
        QuantLib::Real sum = 1.;
        for (double i : arg)
            sum *= std::exp(-i * i) * std::cos(i);
        return sum;
    }
};

int main() {
    try {
        QuantLib::Size dimension = 3;
        QuantLib::Real exactSol = std::pow(std::exp(-.25) * std::sqrt(M_PI), static_cast<QuantLib::Real>(dimension));

        QuantLib::ext::function<QuantLib::Real(const std::vector<QuantLib::Real>& arg)> f = integrand();

        QuantLib::GaussianQuadMultidimIntegrator intg(dimension, 15);
        QuantLib::Real valueQuad = intg(f);

        std::vector<QuantLib::ext::shared_ptr<QuantLib::Integrator> > integrals;
        for (QuantLib::Size i = 0; i < dimension; ++i) {
            integrals.push_back(QuantLib::ext::make_shared<QuantLib::TrapezoidIntegral<QuantLib::Default> >(1.e-4, 20));
        }
        std::vector<QuantLib::Real> a_limits(integrals.size(), -4.);
        std::vector<QuantLib::Real> b_limits(integrals.size(), 4.);
        QuantLib::MultidimIntegral testIntg(integrals);

        QuantLib::Real valueGrid = testIntg(f, a_limits, b_limits);

        std::cout << std::fixed << std::setprecision(4);
        std::cout << std::endl << "-------------- " << std::endl
                  << "Exact: " << exactSol << std::endl
                  << "Quad: " << valueQuad << std::endl
                  << "Grid: " << valueGrid << std::endl
                  << std::endl;

        return 0;

    } catch (std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "unknown error" << std::endl;
        return 1;
    }
}
