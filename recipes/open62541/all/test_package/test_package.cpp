#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#endif

#include <stdlib.h>
#include <thread>

int main(void) {

  UA_Server *server = UA_Server_new();
  UA_ServerConfig_setDefault(UA_Server_getConfig(server));
  UA_Boolean running = true;
  UA_StatusCode return_code;

  std::thread server_thread(
      [&]() { return_code = UA_Server_run(server, &running); });

  std::this_thread::sleep_for(std::chrono::milliseconds(1));
  running = false;

  server_thread.join();
  UA_Server_delete(server);

  return return_code == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
