#include <tesults_gtest/tesults_gtest.h>

#include <iostream>

int main() {
    tesults_gtest::TesultsListener::Config cfg;
    cfg.target = "token";
    std::cout << "tesults-gtest: listener config ready\n";
    return 0;
}
