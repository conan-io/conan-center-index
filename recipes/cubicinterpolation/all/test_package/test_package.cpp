#include "CubicInterpolation/Axis.h"
#include "CubicInterpolation/CubicSplines.h"
#include "CubicInterpolation/Interpolant.h"

double func(double x) { return x * x + x; }

int main(int argc, char* argv[])
{

    auto def = cubic_splines::CubicSplines<double>::Definition();
    def.f = func;
    def.axis = std::make_unique<cubic_splines::LinAxis<double>>(
        -2.f, 2.f, (size_t)10);

    auto inter
        = cubic_splines::Interpolant<cubic_splines::CubicSplines<double>>(
            std::move(def), "", "");

    auto res = inter.evaluate(1.2345f);

    return 0;
}
