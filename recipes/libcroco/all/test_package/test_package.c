#include <libcroco/libcroco.h>
#include <string.h>

int main() {
    const char* css = "body { color: red; }";
    CRStyleSheet *stylesheet = NULL;
    enum CRStatus status = cr_om_parser_simply_parse_buf(css, strlen(css), CR_ASCII, &stylesheet);
}
