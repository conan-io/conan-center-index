#include <iostream>
#include <libsecret/secret.h>

int main(int argc, char *argv[]) {
  const SecretSchema schema = {
      "libsecret-conan",
      SECRET_SCHEMA_NONE,
      {
          {"libsecret-conan-testpackage", SECRET_SCHEMA_ATTRIBUTE_STRING},
          {"frogarian", SECRET_SCHEMA_ATTRIBUTE_STRING},
          {NULL, SecretSchemaAttributeType(0)},
      }};
  std::cout << schema.name << std::endl;

  return 0;
}
