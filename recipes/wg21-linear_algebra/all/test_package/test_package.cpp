#include <linear_algebra.hpp>

using namespace STD_LA;

int main()
{
    STD_LA::vector<fs_vector_engine<double, 4>>     v;
    STD_LA::matrix<fs_matrix_engine<double, 4, 4>>  m;
    v*m;

    return EXIT_SUCCESS;
}
