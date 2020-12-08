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

#include "P7_Trace.h"

// Test to validate Conan package generated

int main(int /*argc*/, const char * /*argv*/ []) {

  IP7_Client        *l_pClient    = NULL;
  //create P7 client object
  l_pClient = P7_Create_Client(TM("/P7.Pool=32768"));
  if (l_pClient == NULL) {
    std::cout << "Client is null.\n";
    return EXIT_FAILURE;
  }
    std::cout << "Created client successfully.\n";
  if (l_pClient)
  {
      l_pClient->Release();
      l_pClient = NULL;
  }
  return EXIT_SUCCESS;
}
