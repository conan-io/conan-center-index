#include <read-excel/book.hpp>
#include <read-excel/exceptions.hpp>
#include <read-excel/compoundfile/compoundfile_exceptions.hpp>

#include <iostream>

int main(int argc, char ** argv)
{
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return 1;
    }

    try {
        Excel::Book book( argv[1] );

        Excel::Sheet * sheet = book.sheet( 0 );

        if(sheet->cell( 0, 0 ).getString() == L"This is a string.")
            return 0;

        return 1;
    }
    catch(const Excel::Exception &)
    {
        return 1;
    }
    catch(const CompoundFile::Exception &)
    {
        return 1;
    }
    catch(const std::exception &)
    {
        return 1;
    }
}
