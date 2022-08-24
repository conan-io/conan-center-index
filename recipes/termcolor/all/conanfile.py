import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake

required_conan_version = ">=1.33.0"

class TermcolorConan(ConanFile):
    name = "termcolor"
    description = "Termcolor is a header-only C++ library for printing colored messages to the terminal."
    topics = ("termcolor", "terminal", "color")
    license = "BSD-3-Clause"
    homepage = "https://github.com/ikalnytskyi/termcolor"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package_id(self):
        self.info.header_only()

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
