#include "bpf/libbpf.h"

int main(int argc, char** argv)
{
    const char buffer[1] = { '\0' };
    struct bpf_object* obj = bpf_object__open_mem(buffer, 1, NULL);
    bpf_object__close(obj);
    return 0;
}
