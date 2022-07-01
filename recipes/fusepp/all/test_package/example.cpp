#include "Fuse.h"
#include "Fuse-impl.h"

class MyFilesystem : public Fusepp::Fuse<MyFilesystem> {
};

int main() {
    MyFilesystem();
}
