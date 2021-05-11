#include <read-excel/book.hpp>
#include <read-excel/exceptions.hpp>
#include <read-excel/compoundfile/compoundfile_exceptions.hpp>

int main()
{
    try {
        Excel::Book book( "../../sample.xls" );

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
