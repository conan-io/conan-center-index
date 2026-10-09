#include <boost/locale.hpp>

int main()
{
    BOOST_NAMESPACE::locale::generator gen; gen("");
    return 0;
}
