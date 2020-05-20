#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>

#include <pthread.h>
#include <stdlib.h>

static volatile UA_Boolean running = true;

void *run(void *arg) {
  UA_Server *server = (UA_Server *)arg;
  return (void *)UA_Server_run(server, &running);
}

int main(void) {

  UA_Server *server = UA_Server_new();
  UA_ServerConfig_setDefault(UA_Server_getConfig(server));

  pthread_t server_thread;
  pthread_create(&server_thread, NULL, run, (void *)server);

  sleep(1);
  running = false;
  void *returnCode;
  pthread_join(server_thread, &returnCode);
  UA_StatusCode retval = *((unsigned int *)(&returnCode));

  UA_Server_delete(server);
  return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
