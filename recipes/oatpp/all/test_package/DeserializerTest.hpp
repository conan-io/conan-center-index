#ifndef oatpp_test_parser_json_mapping_DeserializerTest_hpp
#define oatpp_test_parser_json_mapping_DeserializerTest_hpp

#include "oatpp-test/UnitTest.hpp"

namespace oatpp { namespace test { namespace parser { namespace json { namespace mapping {
  
class DeserializerTest : public UnitTest{
public:
  
  DeserializerTest():UnitTest("TEST[parser::json::mapping::DeserializerTest]"){}
  void onRun() override;
  
};
  
}}}}}

#endif /* oatpp_test_parser_json_mapping_DeserializerTest_hpp */
