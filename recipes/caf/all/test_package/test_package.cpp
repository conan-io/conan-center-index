#include <cstdlib>
#include <string>
#include <iostream>
#include <chrono>

#include "caf/all.hpp"
#include "caf/io/middleman.hpp"
#include "caf/openssl/manager.hpp"

caf::behavior mirror(caf::event_based_actor* self) {
  // return the (initial) actor behavior
  return {
    // a handler for messages containing a single std::string
    // that replies with a std::string
    [=](const std::string& what) -> std::string {
      // prints "Hello World!" via aout (thread-safe cout wrapper)
      aout(self) << what << std::endl;
      // reply "!dlroW olleH"
      return std::string(what.rbegin(), what.rend());
    }
  };
}

void hello_world(caf::event_based_actor* self, const caf::actor& buddy) {
  // send "Hello World!" to our buddy ...
  self->request(buddy, std::chrono::seconds(10), "Hello World!").then(
    // ... wait up to 10s for a response ...
    [=](const std::string& what) {
      // ... and print it
      aout(self) << what << std::endl;
    }
  );
}

void caf_main(caf::actor_system &system) {
  // create a new actor that calls 'mirror()'
  auto mirror_actor = system.spawn(mirror);
  // create another actor that calls 'hello_world(mirror_actor)';
  system.spawn(hello_world, mirror_actor);
  // system will wait until both actors are destroyed before leaving main
}

CAF_MAIN(caf::io::middleman, caf::openssl::manager)
