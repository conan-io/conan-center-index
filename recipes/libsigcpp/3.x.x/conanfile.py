import glob
import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rename, replace_in_file, rmdir, save

required_conan_version = ">=1.53.0"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0-only"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("callback")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Avoid 'short_paths=True required' warning due to an unused folder
        rmdir(self, os.path.join(self.source_folder, "untracked"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "sigc++config.h.cmake"),
                                  "define SIGC_DLL 1", "undef SIGC_DLL")
        # Disable subdirs
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")
        # Enable static builds
        cmakelists = os.path.join(self.source_folder, "sigc++", "CMakeLists.txt")
        replace_in_file(self, cmakelists, " SHARED ", " ")
        # Fix install paths
        replace_in_file(self, cmakelists,
                        'LIBRARY DESTINATION "lib"',
                        "LIBRARY DESTINATION lib ARCHIVE DESTINATION lib RUNTIME DESTINATION bin")


    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-3.0", "include", "*.h")):
            dst = os.path.join(self.package_folder, "include", "sigc++-3.0", os.path.basename(header_file))
            rename(self, header_file, dst)
        for dir_to_remove in ["cmake", "pkgconfig", "sigc++-3.0"]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sigc++-3")
        self.cpp_info.set_property("cmake_target_name", "sigc-3.0")
        self.cpp_info.set_property("pkg_config_name", "sigc++-3.0")

        self.cpp_info.components["sigc++"].includedirs = [os.path.join("include", "sigc++-3.0")]
        self.cpp_info.components["sigc++"].libs = collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["sigc++"].system_libs.append("m")
