#include <consteig/consteig.hpp>

int main()
{
    static constexpr consteig::Matrix<double, 2, 2> A{{{1.0, 0.0}, {0.0, 2.0}}};
    static constexpr auto eigs = consteig::eigenvalues(A);
    (void)eigs;
    return 0;
}
