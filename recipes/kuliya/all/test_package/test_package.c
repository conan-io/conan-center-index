#include <kuliya.h>

int main()
{
    kuliya_init();
    kuliya_schema *res = get_node_by_path("umkb/fst/dee/sec");
    kuliya_deinit();
}
