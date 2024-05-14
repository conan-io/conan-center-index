#undef NDEBUG

#include <kuliya.h>
#include <assert.h>
#include <string.h>

int main()
{
    kuliya_init();
    kuliya_schema *res = get_node_by_path("umkb/fst");
    assert(strcmp(res->name.en, "Faculty of Science and Technology") == 0);
    kuliya_deinit();
}
