import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain

required_conan_version = ">=1.43.0"


class BeautyConan(ConanFile):
    name = "beauty"
    homepage = "https://github.com/dfleury2/beauty"
    description = "HTTP Server above Boost.Beast"
    topics = ("http", "server", "boost.beast")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    requires = ("boost/[>1.70.0]@",
                "openssl/1.1.1o@")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build(target="beauty")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("version.hpp", dst=os.path.join("include", "beauty"), src=os.path.join(self.build_folder, "src", "beauty"))
        self.copy("*.lib", src="lib", dst="lib", keep_path=False)
        self.copy("*.so*", src="lib", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.a", src="lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::headers", "openssl::openssl"]
