#include <string>
#include <fstream>

#include <cfg.hpp>

int main()
{
    Cfg::Session cfg;

    std::ifstream stream( "../../test.cfg" );

    try {
        Cfg::tag_Session< cfgfile::string_trait_t > s;

        cfgfile::read_cfgfile( s, stream, "test.cfg" );

        stream.close();

        cfg = s.get_cfg();
    }
    catch( const cfgfile::exception_t<> & x )
    {
        stream.close();

        std::cout << x.desc() << std::endl;

        return 1;
    }

    if( cfg.project() == "123" )
        return 0;
    else
        return 1;
}
