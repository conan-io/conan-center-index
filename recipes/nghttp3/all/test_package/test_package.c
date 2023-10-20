#include <stdio.h>

#if defined(_MSC_VER)
/* nghttp3 defaults to int */
typedef int ssize_t;
#endif
#include <nghttp3/nghttp3.h>
#include <nghttp3/version.h>

int main()
{
    const nghttp3_info* info = nghttp3_version(NGHTTP3_VERSION_NUM);
    if (info) {
        printf("nghttp3 ver=%d version=%s\n", info->version_num, info->version_str);
    } else {
        printf("nghttp3: cannot get version\n");
    }
    return 0;
}
