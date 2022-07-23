#include <assert.h>
#include <gperftools/tcmalloc.h>

int main()
{
    void *p1 = tc_malloc(10);
    assert(p1 != NULL);

    tc_free(p1);

    return 0;
}

