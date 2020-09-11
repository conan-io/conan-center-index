#include <cstdio>

#if defined(_MSC_VER)
// nghttp2 defaults to int
typedef int ssize_t;
#endif
#include <nghttp2/nghttp2.h>
#include <nghttp2/nghttp2ver.h>
#include <nghttp2/asio_http2_client.h>

int main()
{
    nghttp2_info* info = nghttp2_version(NGHTTP2_VERSION_NUM);
    if (info) {
        printf("nghttp2 ver=%d version=%s static with asio\n", info->version_num, info->version_str);
    } else {
        printf("nghttp2: cannot get version\n");
    }

    // test link order of nghttp2_static and nghttp2_asio
    boost::asio::io_context ioc;
    nghttp2::asio_http2::client::session session(ioc, "www.example.com", "80");

    return 0;
}

// vim: et ts=4 sw=4
