#include <iostream>
#include <cstdlib>
#include <libmount/libmount.h>

int main()
{
    struct libmnt_context *ctx = mnt_new_context();
    if (!ctx) {
      std::cerr << "failed to initialize libmount\n";
      return EXIT_FAILURE;
    }
    std::cout << "path to fstab: " << mnt_get_fstab_path() << std::endl;
    mnt_free_context(ctx);
    return EXIT_SUCCESS;
}
