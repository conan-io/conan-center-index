from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class C4CoreConan(ConanFile):
    name = "c4core"
    description = (
        "c4core is a library of low-level C++ utilities, written with "
        "low-latency projects in mind."
    )
    topics = ("utilities", "low-latency", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/biojppm/c4core"
    license = "MIT",

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
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

    def requirements(self):
        self.requires("fast_float/3.4.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "11")

        ## clang with libc++ is not supported. It is already fixed at 2022-01-03.
        if tools.scm.Version(self, self.version) <= "0.1.8":
            if (self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++"):
                raise ConanInvalidConfiguration(
                    "{}/{} doesn't support clang with libc++".format(self.name, self.version),
                )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"), "c4/ext/fast_float_all.h", "")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "c4", "ext", "fast_float.hpp"),
            '#include "c4/ext/fast_float_all.h"',
            '#include "fast_float/fast_float.h"')

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rm(self, os.path.join(self.package_folder, "include"), "*.natvis")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "c4core")
        self.cpp_info.set_property("cmake_target_name", "c4core::c4core")
        self.cpp_info.libs = ["c4core"]
