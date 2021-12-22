#include "DeserializerTest.hpp"

#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "oatpp/core/macro/codegen.hpp"

namespace oatpp { namespace test { namespace parser { namespace json { namespace mapping {

namespace {

#include OATPP_CODEGEN_BEGIN(DTO)

class EmptyDto : public oatpp::DTO {

  DTO_INIT(EmptyDto, DTO)

};

class SampleDto : public DTO {

  DTO_INIT(SampleDto, DTO);

  DTO_FIELD(String, strF);
  DTO_FIELD(Int32, int32F);
  DTO_FIELD(Float32, float32F);
  DTO_FIELD(Object<EmptyDto>, object);
  DTO_FIELD(List<Object<EmptyDto>>, list);

};

#include OATPP_CODEGEN_END(DTO)

}

void DeserializerTest::onRun(){

  auto mapper = oatpp::parser::json::mapping::ObjectMapper::createShared();

  auto obj = mapper->readFromString<oatpp::Object<SampleDto>>("{ \"strF\": \"value1\", \"int32F\": 30, \"float32F\": 32.4, \"object\": {}\"list\": [] }");

  OATPP_ASSERT(obj);
  OATPP_ASSERT(obj->strF->equals("value1"));
  OATPP_ASSERT(obj->int32F == 30);
  OATPP_ASSERT(obj->float32F);
  OATPP_ASSERT(obj->object);
  OATPP_ASSERT(obj->list->size() == 0);

}

}}}}}
