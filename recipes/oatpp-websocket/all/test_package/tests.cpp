
#include "oatpp-test/UnitTest.hpp"

#include "FullAsyncTest.hpp"
#include "FullTest.hpp"

#include "oatpp/core/concurrency/SpinLock.hpp"
#include "oatpp/core/base/Environment.hpp"

#include "oatpp-websocket/Handshaker.hpp"

#include <iostream>

namespace {

class Test : public oatpp::test::UnitTest {
public:
  Test() : oatpp::test::UnitTest("MyTag")
  {}

  void onRun() override {

    oatpp::websocket::Handshaker::Headers headers;
    oatpp::websocket::Handshaker::clientsideHandshake(headers);

  }
};

void runTests() {
  //OATPP_RUN_TEST(oatpp::test::websocket::FullTest);
  OATPP_RUN_TEST(oatpp::test::websocket::FullAsyncTest);
}

}

int main() {

  oatpp::base::Environment::init();

  runTests();

  /* Print how much objects were created during app running, and what have left-probably leaked */
  /* Disable object counting for release builds using '-D OATPP_DISABLE_ENV_OBJECT_COUNTERS' flag for better performance */
  std::cout << "\nEnvironment:\n";
  std::cout << "objectsCount = " << oatpp::base::Environment::getObjectsCount() << "\n";
  std::cout << "objectsCreated = " << oatpp::base::Environment::getObjectsCreated() << "\n\n";

  OATPP_ASSERT(oatpp::base::Environment::getObjectsCount() == 0);

  oatpp::base::Environment::destroy();

  return 0;
}
