#include <iostream>
#include <ufbx.h>

int main() {
    std::string content = R"(
# ufbx:bad_uvs
# This file uses centimeters as units for non-parametric coordinates.

g default
v -10.000005 0.000000 10.000005
v 10.000005 0.000000 10.000005
v -10.000005 0.000000 -10.000005
v 10.000005 0.000000 -10.000005
v -10.000005 20.000010 10.000005
v 10.000005 20.000010 10.000005
v -10.000005 20.000010 -10.000005
v 10.000005 20.000010 -10.000005
vn -0.577350 -0.577350 0.577350
vn -0.577350 -0.577350 -0.577350
vn 0.577350 -0.577350 -0.577350
vn 0.577350 -0.577350 0.577350
vn -0.577350 0.577350 0.577350
vn 0.577350 0.577350 0.577350
vn 0.577350 0.577350 -0.577350
vn -0.577350 0.577350 -0.577350
s 1
g Box01
f 1//1 3//2 4//3 2//4
f 5//5 6//6 8//7 7//8
f 1//1 2//4 6//6 5//5
f 2//4 4//3 8//7 6//6
f 4//3 3//2 7//8 8//7
f 3//2 1//1 5//5 7//8
)";
    ufbx_load_opts opts = { 0 }; // Optional, pass NULL for defaults
    ufbx_error error; // Optional, pass NULL if you don't care about errors
    ufbx_scene *scene = ufbx_load_memory(content.c_str(), content.size(), &opts, &error);
    if (!scene) {
        fprintf(stderr, "Failed to load: %s\n", error.description.data);
        exit(1);
    }

    // Use and inspect `scene`, it's just plain data!

    // Let's just list all objects within the scene for example:
    for (size_t i = 0; i < scene->nodes.count; i++) {
        ufbx_node *node = scene->nodes.data[i];
        if (node->is_root) continue;

        printf("Object: %s\n", node->name.data);
        if (node->mesh) {
            printf("-> mesh with %zu faces\n", node->mesh->faces.count);
        }
    }

    ufbx_free_scene(scene);
}