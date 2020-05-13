#include <soci/soci.h>
#include <iostream>
#if defined BACKEND_EMPTY
# include <soci/empty/soci-empty.h>
#elif defined BACKEND_SQLITE3 
# include <soci/sqlite3/soci-sqlite3.h>
#endif

int main()
{
#if defined BACKEND_EMPTY
  soci::session sql(*soci::factory_empty(), "db_empty.db");
#elif defined BACKEND_SQLITE3
  soci::session sql(*soci::factory_sqlite3(), "db_sqlite3.db");
#endif

  try
  {
    sql << "drop table sqlite3_test";
    sql.commit();
  }
  catch (const soci::soci_error& )
  {
    // ignore if error
  }

  sql <<
    "create table sqlite3_test ("
    "    id integer primary key,"
    "    name varchar(100)"
    ")";

  sql << "insert into sqlite3_test(name) values('sqlite3')";


  soci::rowid id(sql);

  std::string name = "sqlite3";
  sql << "select id from sqlite3_test where name = :name", soci::into(id), soci::use(name, "name");

  return 0;
}
