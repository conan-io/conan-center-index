#include <matrix>

using namespace STD_LA;

int main()
{
    STD_LA::fixed_size_matrix<double, 1, 4>  v;
    STD_LA::fixed_size_matrix<double, 4, 4>  m;
    v*m;

    return EXIT_SUCCESS;
}
