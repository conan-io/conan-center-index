#include <libssh/libssh.h>

int main(int argc, char *argv[]) {
  ssh_init();
  ssh_session session = ssh_new();
  if (session == NULL)
    return -1;

  const char* host = "localhost";
  ssh_options_set(session, SSH_OPTIONS_HOST, host);
  ssh_options_set(session, SSH_OPTIONS_USER, "user");
  int rc = ssh_connect(session);
  return 0;
}
