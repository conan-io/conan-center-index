#include <consteig/consteig.hpp>

int main(void) {
    static constexpr auto matrix = consteig::make_matrix<double, 2, 2>(
        0.0, 1.0,
        2.0, 3.0
    );
    static constexpr auto eigs = consteig::eigenvalues(matrix);
    return 0;
}
