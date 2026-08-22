/*
 * Copyright 2018 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <cstdlib>
#include <iostream>

#include "flatbuffers/flatbuffers.h"

#ifndef FLATBUFFERS_HEADER_ONLY
  #include "flatbuffers/util.h"
#endif
// Test to validate Conan package generated

int main(int /*argc*/, const char * /*argv*/ []) {

  flatbuffers::FlatBufferBuilder builder;
  const auto offset = builder.CreateString("test");
  if (!offset.IsNull()) {
    std::cout << "Offset is " << builder.CreateString("test").o << ".\n";
  } else {
    std::cout << "Offset is null.\n";
    return EXIT_FAILURE;
  }

#ifndef FLATBUFFERS_HEADER_ONLY
  const std::string filename("conanbuildinfo.txt");
  if (flatbuffers::FileExists(filename.c_str())) {
    std::cout << "File " << filename << " exists.\n";
  } else {
    std::cout << "File " << filename << " does not exist.\n";
  }
#endif

  return EXIT_SUCCESS;
}
