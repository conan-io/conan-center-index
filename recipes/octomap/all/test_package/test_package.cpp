#include <octomap/octomap.h>
#include <octomap/math/Utils.h>

#include <iostream>

void printChanges(octomap::OcTree &tree) {
  unsigned int changedOccupied = 0;
  unsigned int changedFree = 0;
  unsigned int actualOccupied = 0;
  unsigned int actualFree = 0;
  unsigned int missingChanged = 0;

  tree.expand();

  // iterate through the changed nodes
  for (octomap::KeyBoolMap::const_iterator it = tree.changedKeysBegin(); it != tree.changedKeysEnd(); ++it) {
    octomap::OcTreeNode *node = tree.search(it->first);
    if (node != NULL) {
      if (tree.isNodeOccupied(node)) {
        changedOccupied += 1;
      }
      else {
        changedFree += 1;
      }
    } else {
      missingChanged +=1;
    }
  }

  // iterate through the entire tree
  for(octomap::OcTree::tree_iterator it = tree.begin_tree(), end = tree.end_tree(); it != end; ++it) {
    if (it.isLeaf()) {
      if (tree.isNodeOccupied(*it)) {
        actualOccupied += 1;
      }
      else {
        actualFree += 1;
      }
    }
  }

  std::cout << "change detection: "
            << changedOccupied << " occ; "
            << changedFree << " free; "
            << missingChanged << " missing"
            << std::endl;
  std::cout << "actual: " << actualOccupied << " occ; " << actualFree << " free; " << std::endl;

  tree.prune();
}

int main() {
  octomap::OcTree tree(0.05);
  tree.enableChangeDetection(true);

  octomap::point3d origin(0.01f, 0.01f, 0.02f);
  octomap::point3d point_on_surface(4.01f, 0.01f, 0.01f);
  tree.insertRay(origin, point_on_surface);
  printChanges(tree);
  tree.updateNode(octomap::point3d(2.01f, 0.01f, 0.01f), 2.0f);
  printChanges(tree);
  tree.updateNode(octomap::point3d(2.01f, 0.01f, 0.01f), -2.0f);
  printChanges(tree);

  std::cout << "generating spherical scan at " << origin << " ..." << std::endl;

  for (int i = -100; i < 101; ++i) {
    octomap::Pointcloud cloud;
    for (int j = -100; j < 101; ++j) {
      octomap::point3d rotated = point_on_surface;
      rotated.rotate_IP(0, DEG2RAD(i * 0.5), DEG2RAD(j * 0.5));
      cloud.push_back(rotated);
    }
    tree.insertPointCloud(cloud, origin, -1);
  }

  printChanges(tree);

  std::cout << "done." << std::endl;

  return 0;
}
