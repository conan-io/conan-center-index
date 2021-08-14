#include <boost/python/numpy.hpp>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

namespace p = boost::python;
namespace np = boost::python::numpy;

int main(int argc, char **argv)
{
    Py_Initialize();
    np::initialize();

    p::tuple shape = p::make_tuple(3, 3);
    np::dtype dtype = np::dtype::get_builtin<float>();
    np::ndarray a = np::zeros(shape, dtype);

    np::ndarray b = np::empty(shape,dtype);

    std::cout << "Original array:\n" << p::extract<char const *>(p::str(a)) << std::endl;

    // Reshape the array into a 1D array
    a = a.reshape(p::make_tuple(9));
    // Print it again.
    std::cout << "Reshaped array:\n" << p::extract<char const *>(p::str(a)) << std::endl;
}
