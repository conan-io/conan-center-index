// This include fixes the following error on MSVC2019/static/MD with boost/1.73.0:
// error C2027: use of undefined type 'std::basic_ios<char,std::char_traits<char>>'
#include <ios>

#include <boost/nowide/args.hpp>


#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main(int argc,char **argv)
{
    boost::nowide::args a(argc,argv); // Fix arguments - make them UTF-8
    return 0;
}
