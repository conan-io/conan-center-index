#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <glib.h>
#include <json-glib/json-glib.h>

#include <json-glib/json-version.h>

int main(int argc, char * argv[])
{
    JsonObject *object = json_object_new ();

    g_assert_cmpint (json_object_get_size (object), ==, 0);
    g_assert (json_object_get_members (object) == NULL);

    json_object_unref (object);

	printf("Using json-glib version: %s", JSON_VERSION_S);

    return 0;
}
