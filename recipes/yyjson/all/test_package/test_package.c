#include <yyjson.h>

#include <stddef.h>
#include <stdio.h>

int main(void) {
    const char *json = "{\"name\":\"Mash\",\"star\":4,\"hits\":[2,2,1,3]}";

    yyjson_doc *doc = yyjson_read(json, strlen(json), 0);
    yyjson_val *root = yyjson_doc_get_root(doc);

    yyjson_val *name = yyjson_obj_get(root, "name");
    printf("name: %s\n", yyjson_get_str(name));
    printf("name length:%d\n", (int)yyjson_get_len(name));

    yyjson_val *star = yyjson_obj_get(root, "star");
    printf("star: %d\n", (int)yyjson_get_int(star));

    yyjson_val *hits = yyjson_obj_get(root, "hits");
    size_t idx, max;
    yyjson_val *hit;
    yyjson_arr_foreach(hits, idx, max, hit) {
        printf("hit%d: %d\n", (int)idx, (int)yyjson_get_int(hit));
    }

    yyjson_doc_free(doc);

    return 0;
}
