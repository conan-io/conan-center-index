
#include <vsg/core/Object.h>
#include <vsg/nodes/Node.h>
#include <vsg/core/ref_ptr.h>


#include <vsg/utils/CommandLine.h>

#include <iostream>
#include <vector>

int main(int argc, char** argv)
{
    vsg::CommandLine arguments(&argc, argv);
    auto numObjects = arguments.value(100u, {"---num-objects", "-n"});
    if (arguments.errors()) return arguments.writeErrorMessages(std::cerr);

    using Objects = std::vector<vsg::ref_ptr<vsg::Object>>;
    Objects objects;
    objects.reserve(numObjects);
    for (unsigned int i = 0; i < numObjects; ++i)
    {
        objects.push_back(vsg::Node::create());
    }

    Objects copy_objects(numObjects);


    copy_objects = objects;
    copy_objects.clear();


    return 0;
}