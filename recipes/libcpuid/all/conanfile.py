from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibCpuidConan(ConanFile):
    name = "libcpuid"
    description = "libcpuid  is a small C library for x86 CPU detection and feature extraction"
    topics = ("conan", "libcpuid", "detec", "cpu", "intel", "amd", "x86_64")
    license = "https://github.com/anrieff/libcpuid"
    homepage = "https://github.com/anrieff/libcpuid"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("libcpuid is only available for x86 and x86_64 architecture")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_cmake()
        autotools.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_cmake()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["cpuid"]
        self.cpp_info.names["cmake_find_package"] = "cpuid"
        self.cpp_info.names["cmake_find_package_multi"] = "cpuid"
        self.cpp_info.names["pkg_config"] = "libcpuid"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
