#include <iostream>
#include <ufbx.h>

int main() {

    ufbx_load_opts opts = { 0 }; // Optional, pass NULL for defaults
    ufbx_scene *scene = ufbx_load_memory(nullptr, 0, &opts, nullptr);

    ufbx_free_scene(scene);
}
