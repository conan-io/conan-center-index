// The Art of C++ / taopq
// Copyright (c) 2016-2020 Daniel Frey

#include <cstdlib>
#include <iostream>
#include <string>

#include <tao/pq.hpp>

int main()
{
   try {
      const std::string dbname = ::getenv( "TAOPQ_TEST_DATABASE" ) ? ::getenv( "TAOPQ_TEST_DATABASE" ) : "dbname=template1";
      const auto connection = tao::pq::connection::create( dbname );
      connection->execute( "DROP TABLE IF EXISTS taopq_conan_test" );
      connection->execute( "CREATE TABLE taopq_conan_test ( a INTEGER PRIMARY KEY )" );
   }
   catch( const std::runtime_error& error ) {
      // ignore connection fault
      std::cerr << error.what() << std::endl;
   }

   return EXIT_SUCCESS;
}
