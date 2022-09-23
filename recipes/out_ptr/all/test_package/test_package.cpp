#include <ztd/out_ptr/out_ptr.hpp>

#include <cstdio>
#include <cassert>
#include <cerrno>

#ifndef _WIN32

// Some functions to achieve cross-platform parity

int fopen_s(FILE **f, const char *name, const char *mode)
{
    auto ret = 0;
    *f = std::fopen(name, mode);
    /* Can't be sure about 1-to-1 mapping of errno and MS' errno_t */
    if (!*f)
        ret = errno;
    return ret;
}

#endif // Windows

struct fclose_deleter
{
    void operator()(FILE *f) const
    {
        std::fclose(f);
    }
};

int main()
{
    std::unique_ptr<FILE, fclose_deleter> my_unique_fptr;

    // open file, stuff it in this deleter
    auto err = fopen_s(ztd::out_ptr::out_ptr<FILE *>(my_unique_fptr), "no such file", "r+b");
    assert(err != 0);
}
