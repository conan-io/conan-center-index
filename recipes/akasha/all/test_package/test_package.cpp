#include <akasha.hpp>
#include <iostream>
#include <cassert>
#include <string>
#include <cstdio>

int main() {
    std::cout << "Akasha version: " << akasha::version() << std::endl;

    // Functional test: create Store, save and read a value
    akasha::Store store;

    const std::string dataset = "testdata";
    const std::string file = "test_akasha.mmap";

    // Remove the file if it already exists
    std::remove(file.c_str());

    auto status = store.load(dataset, file, akasha::FileOptions::create_if_missing);
    assert(status == akasha::Status::ok);

    // Save a value
    std::string key = dataset + ".key";
    std::string value = "hello_conan";

    status = store.set<std::string>(key, value);
    assert(status == akasha::Status::ok);

    // Read the value
    auto read = store.get<std::string>(key);
    assert(read.has_value());
    assert(read.value() == value);

    std::cout << "Read value: " << read.value() << std::endl;

    // Clean up temporary file
    auto unload_status = store.unload(dataset);
    assert(unload_status == akasha::Status::ok);
    std::remove(file.c_str());

    std::cout << "Akasha functional test OK" << std::endl;
    return 0;
}
