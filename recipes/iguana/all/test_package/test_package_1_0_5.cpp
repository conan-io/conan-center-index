#include <iguana/json_reader.hpp>
#include <iguana/json_writer.hpp>

namespace client {
struct person {
  std::string name;
  int64_t age;
};

REFLECTION(person, name, age);
} // namespace client

struct MyStruct {
  uint64_t a;
};
REFLECTION(MyStruct, a);

struct student {
  int id;
  std::string name;
  int age;
};
REFLECTION(student, id, name, age);

void test() {
  MyStruct p = {5566777755311};
  iguana::string_stream ss;
  iguana::to_json(p, ss);

  MyStruct p2;
  iguana::from_json(p2, ss);
  std::cout << p2.a << std::endl;
}

void test_v() {
  client::person p1 = {"tom", 20};
  client::person p2 = {"jack", 19};
  client::person p3 = {"mike", 21};

  std::vector<client::person> v{p1, p2, p3};
  iguana::string_stream ss;
  iguana::to_json(v, ss);
  std::cout << ss << std::endl;

  std::vector<client::person> v1;
  iguana::from_json(v1, ss);
}

void test_disorder() {
  student s{1, "tom", 20};
  iguana::string_stream ss;
  iguana::to_json(s, ss);
  std::cout << ss << std::endl;

  student s1{};
  std::string str = "{\"name\":\"tom\",\"id\":1,\"age\":20}";
  iguana::from_json(s1, str.data(), str.length());
  std::string str1 = "{\"name\":\"tom\",\"age\":20,\"id\":1}";
  iguana::from_json(s1, str1.data(), str1.length());

  std::string str2 = "{ \"id\":1,\"name\" : \"madoka\",\"age\" : 27 }";
  iguana::from_json(s1, str2.data(), str2.length());
}

int main(void) {
  test_disorder();
  test_v();
  test();
  client::person p = {"zombie chow", -311};
  iguana::string_stream ss;
  iguana::to_json(p, ss);

  std::cout << ss << std::endl;
  client::person p2;

  iguana::from_json(p2, ss.data(), ss.length());

  std::cout << p2.name << " - " << p2.age << std::endl;

  return 0;
}
