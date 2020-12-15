#include <boost/nowide/args.hpp>
#include <boost/nowide/fstream.hpp>
#include <boost/nowide/iostream.hpp>
int main(int argc,char **argv)
{
    boost::nowide::args a(argc,argv); // Fix arguments - make them UTF-8
    if(argc!=2) {
        boost::nowide::cerr << "Usage: file_name" << std::endl; // Unicode aware console
        return 1;
    }
    boost::nowide::ifstream f(argv[1]); // argv[1] - is UTF-8
    if(!f) {
        // the console can display UTF-8
        boost::nowide::cerr << "Can't open " << argv[1] << std::endl;
        return 1;
    }
    int total_lines = 0;
    while(f) {
        if(f.get() == '\n')
            total_lines++;
    }
    f.close();
    // the console can display UTF-8
    boost::nowide::cout << "File " << argv[1] << " has " << total_lines << " lines" << std::endl;
    return 0;
}
