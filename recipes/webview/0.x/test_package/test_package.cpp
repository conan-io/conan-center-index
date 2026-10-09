#include <webview/webview.h>

int main() {
    const webview_version_info_t* info = webview_version();
    if (!info) {
        return 1;
    }
    return info->version.major == 0 && info->version.minor == 12 && info->version.patch == 0 ? 0 : 1;
}
