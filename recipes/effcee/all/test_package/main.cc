// Copyright 2017 The Effcee Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <iostream>
#include <sstream>

#include "effcee/effcee.h"

// Checks standard input against the list of checks provided as command line
// arguments.
//
// Example:
//    cat <<EOF >sample_data.txt
//    Bees
//    Make
//    Delicious Honey
//    EOF
//    effcee-example <sample_data.txt "CHECK: Bees" "CHECK-NOT:Sting" "CHECK: Honey"
int main(int argc, char* argv[]) {
  // Read the command arguments as a list of check rules.
  std::ostringstream checks_stream;
  for (int i = 1; i < argc; ++i) {
    checks_stream << argv[i] << "\n";
  }
  // Read stdin as the input to match.
  std::stringstream input_stream;
  std::cin >> input_stream.rdbuf();

  // Attempt to match.  The input and checks arguments can be provided as
  // std::string or pointer to char.
  auto result = effcee::Match(input_stream.str(), checks_stream.str(),
                              effcee::Options().SetChecksName("checks"));

  return 0;
}
