import os
from conan import ConanFile, tools
from conans import CMake

class OzzAnimationConan(ConanFile):
    name = "ozz-animation"
    description = "Open source c++ skeletal animation library and toolset."
    license = "MIT"
    topics = ("conan", "ozz", "animation", "skeletal")
    homepage = "https://github.com/guillaumeblanc/ozz-animation"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    short_paths = True

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ozz_build_fbx"] = False
        cmake.definitions["ozz_build_data"] = False
        cmake.definitions["ozz_build_samples"] = False
        cmake.definitions["ozz_build_howtos"] = False
        cmake.definitions["ozz_build_tests"] = False
        cmake.definitions["ozz_build_cpp11"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for before, after in [('string(REGEX REPLACE "/MT" "/MD" ${flag} "${${flag}}")', ""), ('string(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")', "")]:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "build-utils", "cmake", "compiler_settings.cmake"), before, after)

        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "animation", "offline", "tools", "CMakeLists.txt"), 
                              "if(NOT EMSCRIPTEN)",
                              "if(NOT CMAKE_CROSSCOMPILING)")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        os.remove(os.path.join(self.package_folder, "CHANGES.md"))
        os.remove(os.path.join(self.package_folder, "LICENSE.md"))
        os.remove(os.path.join(self.package_folder, "README.md"))
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
