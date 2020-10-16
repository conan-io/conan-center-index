/*
 * Copyright 2016 Open Source Robotics Foundation
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
 *
*/
#include <iostream>
#include <sdf/sdf.hh>

/////////////////////////////////////////////////
static std::string simple_sdf()
{
  return R"(
  <?xml version='1.0'?>
  <sdf version='1.6'>
    <model name='my_model'>
      <link name='link'/>
    </model>
  </sdf>
  )";
}

int main(int argc, char **argv)
{
  // Read an SDF file, and store the result in sdf.
  auto sdf = std::make_shared<sdf::Element>();
  sdf::readString(simple_sdf(), sdf);

  if (sdf)
  {
    // Get a pointer to the model element
    sdf::ElementPtr model = sdf->GetElement("model");

    // Get the "name" attribute from the model
    std::string modelName = model->Get<std::string>("name");

    std::cout << "Model name = " << modelName << "\n";

    // Get the child "link" element, and its name
    auto link = model->GetElement("link");
    auto linkName = link->Get<std::string>("name");

    std::cout << "Link name = " << linkName << "\n";
    return 0;
  }

  return -1;
}
