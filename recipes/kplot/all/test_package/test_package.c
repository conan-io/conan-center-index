// Both are required by kplot.h
#include <cairo.h>
#include <unistd.h>

#include <kplot.h>

int main() {
    struct kpair points1[50];
    struct kdata* d1 = kdata_array_alloc(points1, 50);
    kdata_destroy(d1);
}
