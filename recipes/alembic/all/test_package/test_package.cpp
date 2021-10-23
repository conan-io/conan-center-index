#include <iostream>

#include <Alembic/Abc/All.h>
#include <Alembic/AbcCoreOgawa/All.h>
#include <Alembic/AbcCollection/All.h>

void write()
{
    Alembic::Abc::OArchive archive(Alembic::AbcCoreOgawa::WriteArchive(), "Collection.abc");
    Alembic::Abc::OObject root(archive, Alembic::Abc::kTop);
    Alembic::Abc::OObject test(root, "test");
}

void read()
{
    Alembic::Abc::IArchive archive(Alembic::AbcCoreOgawa::ReadArchive(), "Collection.abc");
    Alembic::Abc::IObject test(archive.getTop(), "test");
}

int main() {
    write();
    read();
    return EXIT_SUCCESS;
}
