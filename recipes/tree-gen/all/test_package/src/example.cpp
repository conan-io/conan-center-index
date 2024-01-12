#include "tree-annotatable.hpp"

#include <iostream>  // cout
#include <sstream>  // ostringstream
#include <string>


struct TestA {
    int a;
    std::string b;
};

void serialize_test_a(const TestA &obj, tree::cbor::MapWriter &map) {
    map.append_int("a", obj.a);
    map.append_string("b", obj.b);
}

TestA deserialize_test_a(const tree::cbor::MapReader &map) {
    return TestA {
        (int) map.at("a").as_int(),
        map.at("b").as_string()
    };
}

struct TestB : public tree::annotatable::Serializable {
    bool a{};
    double b{};

    TestB(bool a, double b) : a(a), b(b) {}

    void serialize(tree::cbor::MapWriter &map) const override {
        map.append_bool("a", a);
        map.append_float("b", b);
    }

    explicit TestB(const tree::cbor::MapReader &map) {
        a = map.at("a").as_bool();
        b = map.at("b").as_float();
    }
};

int main() {
    // Register serdes types
    tree::annotatable::serdes_registry.add<TestA>(serialize_test_a, deserialize_test_a);
    tree::annotatable::serdes_registry.add<TestB>();

    // Create an annotated object
    tree::annotatable::Annotatable a;
    a.set_annotation<TestA>(TestA{3, "hello world"});
    a.set_annotation<TestB>(TestB{true, 3.1415});

    // Serialize that object's annotations
    std::ostringstream ss{};
    {
        tree::cbor::Writer writer{ss};
        auto map = writer.start();
        a.serialize_annotations(map);
    }
    std::string encoded = ss.str();

    // Deserialize them into another object
    tree::annotatable::Annotatable b;
    b.deserialize_annotations(tree::cbor::Reader(encoded).as_map());

    // Check the annotations
    if (b.get_annotation<TestA>().a == 3 &&
        b.get_annotation<TestA>().b == "hello world" &&
        b.get_annotation<TestB>().a == true &&
        b.get_annotation<TestB>().b == 3.1415) {

        std::cout << "Success: example OK\n";
    } else {
        std::cout << "Error: example failed\n";

    }
}
