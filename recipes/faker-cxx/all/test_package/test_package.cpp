#include <format>
#include <iostream>
#include "faker-cxx/Internet.h"
#include "faker-cxx/String.h"
#include "faker-cxx/Date.h"

int main()
{
    const auto id = faker::String::uuid();
    const auto email = faker::Internet::email();
    const auto password = faker::Internet::password();
    const auto createdAt = faker::Date::pastDate(5, faker::Date::DateFormat::ISO);
    const auto updatedAt = faker::Date::recentDate(2, faker::Date::DateFormat::ISO);

    std::cout << std::format("id: {}, email: {}, password: {}, createdAt: {}, updatedAt: {}", id, email, password,
                             createdAt, updatedAt);

    return 0;
}
