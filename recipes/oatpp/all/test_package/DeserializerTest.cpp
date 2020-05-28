/***************************************************************************
 *
 * Project         _____    __   ____   _      _
 *                (  _  )  /__\ (_  _)_| |_  _| |_
 *                 )(_)(  /(__)\  )( (_   _)(_   _)
 *                (_____)(__)(__)(__)  |_|    |_|
 *
 *
 * Copyright 2018-present, Leonid Stryzhevskyi <lganzzzo@gmail.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ***************************************************************************/

#include "DeserializerTest.hpp"

#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "oatpp/core/macro/codegen.hpp"

namespace oatpp { namespace test { namespace parser { namespace json { namespace mapping {

namespace {

#include OATPP_CODEGEN_BEGIN(DTO)
  
typedef oatpp::data::mapping::type::Object DTO;
typedef oatpp::parser::Caret ParsingCaret;
typedef oatpp::parser::json::mapping::Serializer Serializer;
typedef oatpp::parser::json::mapping::Deserializer Deserializer;

class EmptyDto : public DTO {

  DTO_INIT(EmptyDto, DTO)

};

class Test1 : public DTO {
  
  DTO_INIT(Test1, DTO)
  
  DTO_FIELD(String, strF);
  
};
  
class Test2 : public DTO {
  
  DTO_INIT(Test2, DTO)
  
  DTO_FIELD(Int32, int32F);
  
};
  
class Test3 : public DTO {
  
  DTO_INIT(Test3, DTO)
  
  DTO_FIELD(Float32, float32F);
  
};

class Test4 : public DTO {

  DTO_INIT(Test4, DTO)

  DTO_FIELD(EmptyDto::ObjectWrapper, object);
  DTO_FIELD(List<EmptyDto::ObjectWrapper>::ObjectWrapper, list);
  DTO_FIELD(Fields<EmptyDto::ObjectWrapper>::ObjectWrapper, map);

};
  
#include OATPP_CODEGEN_END(DTO)
  
}
  
void DeserializerTest::onRun(){
  
  auto mapper = oatpp::parser::json::mapping::ObjectMapper::createShared();
  
  auto obj1 = mapper->readFromString<Test1>("{}");
  
  OATPP_ASSERT(obj1);
  OATPP_ASSERT(!obj1->strF);
  
  obj1 = mapper->readFromString<Test1>("{\"strF\":\"value1\"}");
  
  OATPP_ASSERT(obj1);
  OATPP_ASSERT(obj1->strF);
  OATPP_ASSERT(obj1->strF->equals("value1"));
  
  obj1 = mapper->readFromString<Test1>("{\n\r\t\f\"strF\"\n\r\t\f:\n\r\t\f\"value1\"\n\r\t\f}");
  
  OATPP_ASSERT(obj1);
  OATPP_ASSERT(obj1->strF);
  OATPP_ASSERT(obj1->strF->equals("value1"));
  
  auto obj2 = mapper->readFromString<Test2>("{\"int32F\": null}");
  
  OATPP_ASSERT(obj2);
  OATPP_ASSERT(!obj2->int32F);
  
  obj2 = mapper->readFromString<Test2>("{\"int32F\": 32}");
  
  OATPP_ASSERT(obj2);
  OATPP_ASSERT(obj2->int32F->getValue() == 32);
  
  obj2 = mapper->readFromString<Test2>("{\"int32F\":    -32}");
  
  OATPP_ASSERT(obj2);
  OATPP_ASSERT(obj2->int32F->getValue() == -32);
  
  auto obj3 = mapper->readFromString<Test3>("{\"float32F\": null}");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(!obj3->float32F);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": 32}");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F->getValue() == 32);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": 1.32e1}");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": 1.32e+1 }");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": 1.32e-1 }");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": -1.32E-1 }");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F);
  
  obj3 = mapper->readFromString<Test3>("{\"float32F\": -1.32E1 }");
  
  OATPP_ASSERT(obj3);
  OATPP_ASSERT(obj3->float32F);
  
  auto list = mapper->readFromString<Test1::List<Test1::Int32>>("[1, 2, 3]");
  OATPP_ASSERT(list);
  OATPP_ASSERT(list->count() == 3);
  OATPP_ASSERT(list->get(0)->getValue() == 1);
  OATPP_ASSERT(list->get(1)->getValue() == 2);
  OATPP_ASSERT(list->get(2)->getValue() == 3);

  // Empty test

  auto obj4 = mapper->readFromString<Test4>("{\"object\": {}, \"list\": [], \"map\": {}}");
  OATPP_ASSERT(obj4);
  OATPP_ASSERT(obj4->object);
  OATPP_ASSERT(obj4->list);
  OATPP_ASSERT(obj4->list->count() == 0);
  OATPP_ASSERT(obj4->map->count() == 0);

  obj4 = mapper->readFromString<Test4>("{\"object\": {\n\r\t}, \"list\": [\n\r\t], \"map\": {\n\r\t}}");
  OATPP_ASSERT(obj4);
  OATPP_ASSERT(obj4->object);
  OATPP_ASSERT(obj4->list);
  OATPP_ASSERT(obj4->list->count() == 0);
  OATPP_ASSERT(obj4->map->count() == 0);

}
  
}}}}}
