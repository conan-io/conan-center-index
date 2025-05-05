#include <cmath>
#include <iostream>

#include "msg.pb.h"
#include <libprotobuf-mutator/src/libfuzzer/libfuzzer_macro.h>

DEFINE_PROTO_FUZZER(const libfuzzer_example::Msg& message) {
  protobuf_mutator::protobuf::FileDescriptorProto file;

  // Emulate a bug.
  if (message.optional_uint64() == std::hash<std::string>{}(message.optional_string()) &&
      message.optional_string() == "abcdefghijklmnopqrstuvwxyz" &&
      !std::isnan(message.optional_float()) &&
      std::fabs(message.optional_float()) > 1000 &&
      message.any().UnpackTo(&file) && !file.name().empty())
  {
    std::cerr << message.DebugString() << "\n";
  }
}

int main() {
    return 0;
}
