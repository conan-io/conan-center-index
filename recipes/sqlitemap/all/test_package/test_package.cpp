#include <iostream>

#include <bw/sqlitemap/sqlitemap.hpp>

int main()
{
    bw::sqlitemap::sqlitemap db(bw::sqlitemap::config().filename(":memory:").table("items"));
    db["a"] = "first-item";
    db["b"] = "second-item";
    db["c"] = "third-item";
    db.commit();

    std::cout << db.to_string() << std::endl;
    std::cout << db.size() << " items saved:" << std::endl;
    for (const auto &[key, value] : db)
    {
        std::cout << key << " = " << value << std::endl;
    }
    return 0;
}