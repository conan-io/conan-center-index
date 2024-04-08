#include <libssh/libssh.h>

int main(int argc, char *argv[]) {
  ssh_session session = ssh_new();
  if (session == NULL) {
    return -1;
  }

  return 0;
}
