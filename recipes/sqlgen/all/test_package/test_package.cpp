#include <cstdlib>
#include <iostream>
#include <sqlgen/sqlite.hpp>
#include <string>
#include <vector>

struct User {
    std::string name;
    int age;
};

int main() {
    const auto conn = sqlgen::sqlite::connect();

    const auto user = User{.name = "John", .age = 30};
    sqlgen::write(conn, user);

    const auto users = sqlgen::read<std::vector<User>>(conn).value();

    for (const auto& u : users) {
        std::cout << u.name << " is " << u.age << " years old\n";
    }

    return EXIT_SUCCESS;
}

