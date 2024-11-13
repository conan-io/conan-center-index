// https://github.com/microsoft/proxy/blob/2.1.0/samples/resource_dictionary/main.cpp
// Copyright (c) Microsoft Corporation.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE

#include <proxy/proxy.h>

#include <iostream>
#include <map>
#include <string>
#include <vector>

#ifdef PROXY_VERSION_3_LATER

PRO_DEF_MEM_DISPATCH(MemAt, at);

struct Dictionary : pro::facade_builder
    ::add_convention<MemAt, std::string(int)>
    ::build {};

// This is a function, rather than a function template
void demo_print(pro::proxy<Dictionary> dictionary) {
  std::cout << dictionary->at(1) << "\n";
}

int main() {
  static std::map<int, std::string> container1{{1, "hello"}};
  auto container2 = std::make_shared<std::vector<const char*>>();
  container2->push_back("hello");
  container2->push_back("world");
  demo_print(&container1);  // Prints: "hello"
  demo_print(container2);  // Prints: "world"
}

#else

namespace poly {

PRO_DEF_MEMBER_DISPATCH(at, std::string(int));
PRO_DEF_FACADE(Dictionary, at);

}  // namespace poly

void demo_print(pro::proxy<poly::Dictionary> dictionary) {
  std::cout << dictionary(1) << std::endl;
}

int main() {
  std::map<int, std::string> container1{{1, "hello"}};
  std::vector<std::string> container2{"hello", "world"};
  demo_print(&container1);  // print: hello\n
  demo_print(&container2);  // print: world\n
  return 0;
}
#endif
