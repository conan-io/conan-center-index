#include <read-excel/book.hpp>
#include <read-excel/exceptions.hpp>
#include <read-excel/compoundfile/compoundfile_exceptions.hpp>

#include <iostream>

int main(int argc, char ** argv)
{
    try {
        Excel::Book book( "non-real-file.xls" );
    }
    catch(const Excel::Exception &)
    {
        printf("Test\n");
    }
}
