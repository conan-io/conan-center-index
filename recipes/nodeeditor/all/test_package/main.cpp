#include <cstdlib>
#include <memory>
#include <QtNodes/DataFlowGraphModel>
#include <QtNodes/NodeDelegateModelRegistry>


int main(int argc, char** argv)
{
    auto reg = std::make_shared<QtNodes::NodeDelegateModelRegistry>();
    QtNodes::DataFlowGraphModel mod(reg);
    return EXIT_SUCCESS;
}
