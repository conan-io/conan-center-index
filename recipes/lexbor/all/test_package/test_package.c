#include <lexbor/core/base.h>
#include <lexbor/core/types.h>
#include <lexbor/html/parser.h>
#include <lexbor/html/serialize.h>

int main() {
    lxb_html_document_t* document = lxb_html_document_create();
    lxb_html_document_destroy(document);

    return 0;
}
