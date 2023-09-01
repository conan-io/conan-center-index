#include <EASTL/hash_map.h>
#include <EASTL/string_view.h>
#include <new>

// https://github.com/electronicarts/EASTL/blob/master/doc/FAQ.md#info15-how-hard-is-it-to-incorporate-eastl-into-my-project
void *operator new[](size_t size, const char *pName, int flags, unsigned debugFlags, const char *file, int line) {
    return new uint8_t[size];
}
void *operator new[](size_t size, size_t alignment, size_t alignmentOffset, const char *pName, int flags, unsigned debugFlags, const char *file, int line) {
    return new uint8_t[size];
}

int main() {
    EA_CPP14_CONSTEXPR eastl::string_view string = "string_view";
    eastl::hash_map<int, int> map;
    map[0] = 1;
    return 0;
}
