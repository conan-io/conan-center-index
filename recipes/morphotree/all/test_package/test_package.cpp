#include <morphotree/core/box.hpp>
#include <morphotree/adjacency/adjacency8c.hpp>
#include <morphotree/tree/mtree.hpp>
#include <morphotree/attributes/areaComputer.hpp>

#include <morphotree/core/io.hpp>

#include <iostream>
#include <memory>
#include <functional>
#include <vector>

int main(int argc, char *argv[])
{
  using uint8 = morphotree::uint8;
  using uint32 = morphotree::uint32;
  using Box = morphotree::Box;
  using Point = morphotree::UI32Point;
  using MTree = morphotree::MorphologicalTree<uint8>;
  using Adjacency8C = morphotree::Adjacency8C;
  using NodePtr = typename MTree::NodePtr;
  using AreaComputer = morphotree::AreaComputer<uint8>;
  using AreaType = typename AreaComputer::AttributeType;
  using morphotree::buildMaxTree;
  using morphotree::printImageIntoConsoleWithCast;

  std::vector<uint8> f = {
    0, 0, 0, 0, 0, 0, 0,
    0, 4, 4, 4, 7, 7, 7,
    0, 7, 7, 4, 7, 4, 7,
    0, 7, 4, 4, 7, 4, 7,
    0, 4, 4, 4, 7, 4, 7,
    0, 7, 7, 4, 7, 7, 7,
    0, 0, 0, 0, 0, 0, 0 };  

  Box domain = Box::fromSize(Point{7, 7});
  MTree tree = buildMaxTree(f, 
    std::make_shared<Adjacency8C>(domain));
  
  std::vector<AreaType> area = 
    std::make_unique<AreaComputer>()->computeAttribute(tree);

  tree.traverseByLevel([&area, &domain](NodePtr node) {
    std::cout << "node.Id= " << node->id() << "\n";
    std::cout << "node.level= " << static_cast<int>(node->level()) << "\n";
    std::cout << "node.area= " << area[node->id()] << "\n";
    printImageIntoConsoleWithCast<int>(node->reconstruct(domain), domain);
    std::cout << "\n";
  });
  
  return 0;
}

