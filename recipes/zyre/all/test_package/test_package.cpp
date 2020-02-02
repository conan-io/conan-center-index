#include <iostream>
#include <zyre.h>
#include <zyre_library.h>

int main(void) {
  std::cout << "Hello, World\n";
  return 0;

  //  Create two nodes
  zyre_t *node1 = zyre_new("node1");
  assert(node1);
  assert(streq(zyre_name(node1), "node1"));
  zyre_set_header(node1, "X-HELLO", "World");

  //  Set inproc endpoint for this node
  int rc = zyre_set_endpoint(node1, "inproc://zyre-node1");
  assert(rc == 0);
  //  Set up gossip network for this node
  zyre_gossip_bind(node1, "inproc://gossip-hub");
  rc = zyre_start(node1);
  assert(rc == 0);

  zyre_t *node2 = zyre_new("node2");
  assert(node2);
  assert(streq(zyre_name(node2), "node2"));

  //  Set inproc endpoint for this node
  //  First, try to use existing name, it'll fail
  rc = zyre_set_endpoint(node2, "inproc://zyre-node1");
  assert(rc == -1);
  //  Now use available name and confirm that it succeeds
  rc = zyre_set_endpoint(node2, "inproc://zyre-node2");
  assert(rc == 0);

  //  Set up gossip network for this node
  zyre_gossip_connect(node2, "inproc://gossip-hub");
  rc = zyre_start(node2);
  assert(rc == 0);
  assert(strneq(zyre_uuid(node1), zyre_uuid(node2)));

  zyre_join(node1, "GLOBAL");
  zyre_join(node2, "GLOBAL");

  //  Give time for them to interconnect
  zclock_sleep(250);

  zlist_t *peers = zyre_peers(node1);
  assert(peers);
  assert(zlist_size(peers) == 1);
  zlist_destroy(&peers);

  zyre_join(node1, "node1 group of one");
  zyre_join(node2, "node2 group of one");

  // Give them time to join their groups
  zclock_sleep(250);

  zlist_t *own_groups = zyre_own_groups(node1);
  assert(own_groups);
  assert(zlist_size(own_groups) == 2);
  zlist_destroy(&own_groups);

  zlist_t *peer_groups = zyre_peer_groups(node1);
  assert(peer_groups);
  assert(zlist_size(peer_groups) == 2);
  zlist_destroy(&peer_groups);

  char *value = zyre_peer_header_value(node2, zyre_uuid(node1), "X-HELLO");
  assert(streq(value, "World"));
  zstr_free(&value);

  //  One node shouts to GLOBAL
  zyre_shouts(node1, "GLOBAL", "Hello, World");

  //  Second node should receive ENTER, JOIN, and SHOUT
  zmsg_t *msg = zyre_recv(node2);
  assert(msg);
  char *command = zmsg_popstr(msg);
  assert(streq(command, "ENTER"));
  zstr_free(&command);
  assert(zmsg_size(msg) == 4);
  char *peerid = zmsg_popstr(msg);
  char *name = zmsg_popstr(msg);
  assert(streq(name, "node1"));
  zstr_free(&name);
  zframe_t *headers_packed = zmsg_pop(msg);

  char *address = zmsg_popstr(msg);
  char *endpoint = zyre_peer_address(node2, peerid);
  assert(streq(address, endpoint));
  zstr_free(&peerid);
  zstr_free(&endpoint);
  zstr_free(&address);

  assert(headers_packed);
  zhash_t *headers = zhash_unpack(headers_packed);
  assert(headers);
  zframe_destroy(&headers_packed);
  assert(streq((char *)zhash_lookup(headers, "X-HELLO"), "World"));
  zhash_destroy(&headers);
  zmsg_destroy(&msg);

  msg = zyre_recv(node2);
  assert(msg);
  command = zmsg_popstr(msg);
  assert(streq(command, "JOIN"));
  zstr_free(&command);
  assert(zmsg_size(msg) == 3);
  zmsg_destroy(&msg);

  msg = zyre_recv(node2);
  assert(msg);
  command = zmsg_popstr(msg);
  assert(streq(command, "JOIN"));
  zstr_free(&command);
  assert(zmsg_size(msg) == 3);
  zmsg_destroy(&msg);

  msg = zyre_recv(node2);
  assert(msg);
  command = zmsg_popstr(msg);
  assert(streq(command, "SHOUT"));
  zstr_free(&command);
  zmsg_destroy(&msg);

  zyre_stop(node2);

  msg = zyre_recv(node2);
  assert(msg);
  command = zmsg_popstr(msg);
  assert(streq(command, "STOP"));
  zstr_free(&command);
  zmsg_destroy(&msg);

  zyre_stop(node1);

  zyre_destroy(&node1);
  zyre_destroy(&node2);
  return 0;
}
