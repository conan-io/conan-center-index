//
// Created by Leonid  on 2019-03-25.
//

#ifndef oatpp_test_websocket_FullAsyncTest_hpp
#define oatpp_test_websocket_FullAsyncTest_hpp

#include "oatpp-test/UnitTest.hpp"

namespace oatpp { namespace test { namespace websocket {

class FullAsyncTest : public oatpp::test::UnitTest {
public:

  FullAsyncTest() : UnitTest("TEST[FullAsyncTest]") {}

  void onRun() override;

};

}}}


#endif // oatpp_test_websocket_FullAsyncTest_hpp
