#include "sqlite_orm/sqlite_orm.h"

int main()
{
    auto storage = sqlite_orm::make_storage(":memory:");
    return 0;
}
