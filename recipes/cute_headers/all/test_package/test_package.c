#ifdef _WIN32
#include <windows.h>
#endif

#define CUTE_FILES_IMPLEMENTATION
#include <cute_files.h>

#include <stdio.h>

void print_dir(cf_file_t* file, void* udata)
{
    printf("name: %-10s\text: %-10s\tpath: %s\n", file->name, file->ext, file->path);
    *(int*)udata += 1;
}

void test_dir()
{
    int n = 0;
    cf_traverse(".", print_dir, &n);
    printf("Found %d files with cf_traverse\n\n", n);
}


int main()
{
    test_dir();
    return 0;
}
