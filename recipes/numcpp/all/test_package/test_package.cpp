#include "NumCpp.hpp"

#include <cstdlib>
#include <iostream>

using FunctionType = std::function<double(const nc::NdArray<double>&, const nc::NdArray<double>&)>;

void wikipediaExample()
{
    // https://en.wikipedia.org/wiki/Gauss%E2%80%93Newton_algorithm

    // In a biology experiment studying the relation between substrate concentration [S] and reaction rate in
    // an enzyme-mediated reaction, the data in the following table were obtained.
    nc::NdArray<double> sMeasured = { 0.038, 0.194, 0.425, 0.626, 1.253, 2.5, 3.74 };
    nc::NdArray<double> rateMeasured = { 0.05, 0.127, 0.094, 0.2122, 0.2729, 0.2665, 0.3317 };

    // It is desired to find a curve (model function) of the form
    FunctionType function = [](const nc::NdArray<double>& coordinates, const nc::NdArray<double>& betas) -> double
    {
        const double s = coordinates.at(0);
        const double beta1 = betas.at(0);
        const double beta2 = betas.at(1);

        return (beta1 * s) / (beta2 + s);
    };

    // partial derivative of function with respect to beta1
    FunctionType delFdelBeta1 = [](const nc::NdArray<double>& coordinates, const nc::NdArray<double>& betas) -> double
    {
        const double s = coordinates.at(0);
        const double beta2 = betas.at(1);

        return s / (beta2 + s);
    };

    // partial derivative of function with respect to beta2
    FunctionType delFdelBeta2 = [](const nc::NdArray<double>& coordinates, const nc::NdArray<double>& betas) -> double
    {
        const double s = coordinates.at(0);
        const double beta1 = betas.at(0);
        const double beta2 = betas.at(1);

        return -(beta1 * s) / nc::square(beta2 + s);
    };

    // starting with the initial estimates of beta1Guess and beta2Guess and calculating after 5 iterations
    const nc::uint32 numIterations = 5;
    const double beta1Guess = 0.9;
    const double beta2Guess = 0.2;

#ifdef __cpp_structured_bindings
    auto [betas, rms] = nc::linalg::gaussNewtonNlls(numIterations, sMeasured.transpose(), rateMeasured,
        function, {delFdelBeta1, delFdelBeta2}, beta1Guess, beta2Guess);
#else
    auto results = nc::linalg::gaussNewtonNlls(numIterations, sMeasured.transpose(), rateMeasured,
        function, {delFdelBeta1, delFdelBeta2}, beta1Guess, beta2Guess);
    auto& betas = results.first;
    auto& rms = results.second;
#endif

    std::cout << "==========Wikipedia Example==========\n";
    std::cout << "beta values = " << betas;
    std::cout << "RMS = " << rms << '\n';
}

int main()
{
    wikipediaExample();
    return EXIT_SUCCESS;
}
