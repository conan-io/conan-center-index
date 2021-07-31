import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


# CCI policy is to require the latest conan client
required_conan_version = ">=1.37.0"

class XlntConan(ConanFile):
    name = "xlnt"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tfussell/xlnt"
    description = "Cross-platform user-friendly xlsx library for C++11+"
    topics = ("xlsx", "spreadsheet", "excel", "cpp", "c-plus-plus", "api", "microsoft", "read", "write")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        # https://github.com/tfussell/xlnt/blob/master/docs/introduction/Installation.md#compiling-xlnt-1xx-from-source-on-ubuntu-1604-lts-xenial-xerus
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6.2":
            raise ConanInvalidConfiguration("Xlnt requires a minimum of gcc 6.2.0")
        if self.settings.compiler in ["clang", "apple-clang"]:
            # https://github.com/tfussell/xlnt/issues/486
            raise ConanInvalidConfiguration("Xlnt doesn't build with clang")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions['TESTS'] = False
        cmake.definitions['SAMPLES'] = False
        cmake.definitions['BENCHMARKS'] = False
        cmake.definitions['PYTHON'] = False
        runtime = self.settings.get_safe('compiler.runtime')
        if runtime:
            cmake.definitions['STATIC_CRT'] = 'MT' in runtime
        cmake.configure(build_folder=self._build_subfolder)
        self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["xlntd" if self.settings.build_type == "Debug" else "xlnt"]
