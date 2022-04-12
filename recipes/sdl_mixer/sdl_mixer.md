# link collection

The [project SDL_mixer](https://www.libsdl.org/projects/SDL_mixer/) page.

The SDL_net sources are in a cvs repo -- see documentation.

The [SDL_net released sources](https://www.libsdl.org/projects/SDL_mixer/release/) are available as a zip file.

The [SDL_net souce](https://github.com/libsdl-org/SDL_net) repo.

The new [bincrafters/.../sdl2_mixer](https://github.com/bincrafters/community/tree/main/recipes/sdl2_mixer) source.

The old [bincrafters/conan-sdl2_mixer](https://github.com/bincrafters/conan-sdl2_mixer) source.


The [ticket](https://github.com/conan-io/conan-center-index/issues/9018) that lead to this package.

# integration plan

Roughly speaking I will grab whatever is in the new bincrafters repo and convert it to fit the other sdl images in this repo.

There are dependencies missing on conan-center which would have to be ported down the road.

Missing dependencies are exluded through the build options and set to False per default.
