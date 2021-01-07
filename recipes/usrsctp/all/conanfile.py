from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os


class ConanRecipe(ConanFile):
    name = "usrsctp"
    description = "SCTP user-land implementation (usrsctp)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sctplab/usrsctp"
    license = "BSD-3-Clause"
    topics = ("usrsctp", "sctp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "programs": [True, False],
        "fuzzer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "programs": False,
        "fuzzer": False,
    }
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["sctp_build_programs"] = self.options.programs
        cmake.definitions["sctp_build_fuzzer"] = self.options.fuzzer
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "iphlpapi", "ws2_32"]
