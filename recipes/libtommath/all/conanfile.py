import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, download, replace_in_file, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libtom.net/"
    topics = ("math", "multi-precision")

    package_type = "library"
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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if is_msvc(self) and self.settings.build_type == "Debug":
            # libtommath requires at least /O1 on MSVC for dead code elimination
            # https://github.com/libtom/libtommath/blob/42b3fb07e7d504f61a04c7fca12e996d76a25251/s_mp_rand_platform.c#L120-L138
            self.output.warning("Debug builds on MSVC are not supported, switching to RelWithDebInfo")
            self.settings.build_type = "RelWithDebInfo"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        if Version(self.version) >= "1.3":
            get(self, **self.conan_data["sources"][self.version], strip_root=True)
        else:
            get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
            download(self, **self.conan_data["sources"][self.version]["cmakelists"], filename="CMakeLists.txt")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        if Version(self.version) < "1.3":
            save(self, os.path.join(self.source_folder, "sources.cmake"),
                 "file(GLOB SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/*.c)\n"
                 "file(GLOB HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/*.h)\n")
            # Disable installation of docs, which is not valid for < 1.3
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "# Windows uses a different help sytem.\nif(", "if(0 AND")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libtommath")
        self.cpp_info.set_property("cmake_target_name", "libtommath")
        self.cpp_info.set_property("pkg_config_name", "libtommath")

        self.cpp_info.libs = ["tommath"]
        if Version(self.version) < "1.3":
            self.cpp_info.includedirs.append(os.path.join("include", "libtommath"))
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["advapi32", "crypt32"]
