#include <boost/locale.hpp>
#include <boost/range/algorithm/find.hpp>

int main(int argc, const char * const argv[])
{
    std::vector<std::string> backends = boost::locale::localization_backend_manager::global().get_all_backends();

    bool result = true;
 #ifdef USE_ICU
    result &= ( boost::find( backends, "icu" ) != backends.end() );
#endif

    return ! result;
}
