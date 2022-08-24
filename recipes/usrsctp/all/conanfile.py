from conan import ConanFile, tools
from conans import CMake
import os


class UsrsctpConan(ConanFile):
    name = "usrsctp"
    license = "BSD-3-Clause"
    homepage = "https://github.com/sctplab/usrsctp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "network", "sctp")
    description = " A portable SCTP userland stack"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    _cmake = None

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
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "usrsctp-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["sctp_debug"] = False
        self._cmake.definitions["sctp_werror"] = False
        self._cmake.definitions["sctp_build_shared_lib"] = self.options.shared
        self._cmake.definitions["sctp_build_programs"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "usrsctp"
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(['ws2_32', 'iphlpapi'])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['pthread'])
        suffix = "_import" if self.settings.os == "Windows" and self.options.shared else ""
        self.cpp_info.libs = ["usrsctp" + suffix]
