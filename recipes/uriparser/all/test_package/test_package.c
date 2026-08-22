#include <uriparser/Uri.h>

#include <stdio.h>

static void printUriTextRange(const UriTextRangeA *textRange) {
    const char *ptr;
    for (ptr = textRange->first; ptr != NULL && ptr != textRange->afterLast; ++ptr) {
        putchar(*ptr);
    }
}

static void printSegments(const UriPathSegmentA *head) {
    int i = 0;
    while (head != NULL) {
        printf("segment [%d]: ", i); printUriTextRange(&head->text); putchar('\n');
        head = head->next;
        ++i;
    }
}

int main() {
    UriUriA uri;
    const char *errorPos;
    const char *const uriString = "file://username:password@home:22/user/directory/subdirectory/index.html?q=1337&b=5318008#some_fragment_index";
    printf("URI to parse is \"%s\"\n", uriString);
    if (uriParseSingleUriA(&uri, uriString, &errorPos) != URI_SUCCESS) {
        fprintf(stderr, "uriParseSingleUriA failed\n");
        return EXIT_FAILURE;
    }
    printf("scheme:   "); printUriTextRange(&uri.scheme); putchar('\n');
    printf("userInfo: "); printUriTextRange(&uri.userInfo); putchar('\n');
    printf("hostText: "); printUriTextRange(&uri.hostText); putchar('\n');
    printf("portText: "); printUriTextRange(&uri.portText); putchar('\n');
    printf("query:    "); printUriTextRange(&uri.query); putchar('\n');
    printf("fragment: "); printUriTextRange(&uri.fragment); putchar('\n');
    printSegments(uri.pathHead);
    uriFreeUriMembersA(&uri);
    return EXIT_SUCCESS;
}
