import os

from conans import ConanFile, CMake, tools

import yaml


class SDSLLite(ConanFile):
    name = "sdsl-lite"
    libname = "sdsl"
    exports_sources = "CMakeLists.txt"
    exports = "submoduledata.yml"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    _source_subfolder = "sdsl-lite"
    _build_subfolder = "build_folder"
    version = "2.1.1"
    git_url = "https://github.com/simongog/sdsl-lite.git"
    license = "GNU GPL"
    url = "https://github.com/conan-io/conan-center-index"
    description = "SDSL - Succinct Data Structure Library"
    homepage = "https://github.com/simongog/sdsl-lite"
    topics = ("conan", "sdsl", "succint", "data structure")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

        submodule_filename = os.path.join(
            self.recipe_folder, 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"],
                    "destination": os.path.join(self._source_subfolder, submodule["destination"]),
                    "strip_root": True
                }

                tools.get(**submodule_data)
                submodule_source = os.path.join(self._source_subfolder, path)
                tools.rmdir(submodule_source)

    def build(self):
        c = CMake(self)
        c.configure()
        c.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*.h",     dst="include/", src="sdsl-lite/include")
        self.copy("*.hpp",   dst="include/", src="sdsl-lite/include")
        self.copy("*.a",     dst="lib", keep_path=False)
        self.copy("*.lib",   dst="lib", keep_path=False)
        self.copy("*.dll",   dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs.append(self.libname)
