#include <string>
#include <fstream>

#include <cfg.hpp>

#include <iostream>

int main(int argc, char ** argv)
{
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return 1;
    }

    Cfg::Session cfg;

    std::ifstream stream( argv[1] );

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
