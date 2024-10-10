#include <iostream>
#include <memory>
#include <QtNodes/DataFlowGraphModel>
#include <QtNodes/NodeDelegateModelRegistry>

using std::cout;
using std::endl;

using std::shared_ptr;
using Registry = QtNodes::NodeDelegateModelRegistry;
using Model = QtNodes::DataFlowGraphModel;

int main(int argc, char** argv)
{

  cout << "instantiating registry and dataflow model" << endl;
  auto reg = std::make_shared<Registry>();
  Model mod(reg);
  
  

}
