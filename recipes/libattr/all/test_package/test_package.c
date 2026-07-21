#include <sys/types.h>
#include <sys/xattr.h>

int main(int argc, char* argv[])
{
    char value[255];
    const char *path = "file_not_exist.txt";
    const char *attr = "attr_not_exist";
    getxattr(path, attr, value, sizeof(value));
    return 0;
}
