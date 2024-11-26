#include <boost/locale.hpp>


#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main()
{
    boost::locale::generator gen; gen("");
    return 0;
}
