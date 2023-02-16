#include <parson.h>

#include <stdio.h>

int main() {
    JSON_Value *root_value = json_value_init_object();
    JSON_Object *root_object = json_value_get_object(root_value);
    json_object_set_string(root_object, "name", "John Smith");
    json_object_set_number(root_object, "age", 25);
    json_object_dotset_string(root_object, "address.city", "Cupertino");
    json_object_dotset_value(root_object, "contact.emails", json_parse_string("[\"email@example.com\",\"email2@example.com\"]"));
    char *serialized_string = json_serialize_to_string_pretty(root_value);
    printf("%s\n", serialized_string);

    json_free_serialized_string(serialized_string);
    json_value_free(root_value);

    return 0;
}
