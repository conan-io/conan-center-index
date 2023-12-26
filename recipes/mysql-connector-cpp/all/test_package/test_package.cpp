#include <mysqlx/xdevapi.h>

#include <iostream>


void test() {
  using namespace mysqlx::abi2::r0;
  Session sess("localhost", 33060, "user", "password");
  Schema db = sess.getSchema("test");

  Collection myColl = db.getCollection("my_collection");

  DocResult myDocs = myColl.find("name like :param")
                           .limit(1)
                           .bind("param", "L%").execute();

  std::cout << myDocs.fetchOne();
}

int main() {
    return 0;
}
