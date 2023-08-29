#include <cassandra.h>
/* Use "#include <dse.h>" when connecting to DataStax Enterpise */
#include <iostream>

int main(int argc, char* argv[]) {
  CassUuid uuid;
  cass_uuid_from_string("550e8400-e29b-41d4-a716-446655440000", &uuid);

  cass_uint64_t timestamp = cass_uuid_timestamp(uuid);

  char uuid_str[CASS_UUID_STRING_LENGTH];
  cass_uuid_string(uuid, uuid_str);

  std::cout<<"timestamp: " << timestamp << std::endl;
  std::cout<<"uuid_str: " << uuid_str << std::endl;

  return 0;
}
