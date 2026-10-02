from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, rmdir, copy, rm
import os

required_conan_version = ">=2.0"


class ZlibConan(ConanFile):
    name = "zlib"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    topics = ("zlib", "compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_zlibwapi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_zlibwapi": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.enable_zlibwapi

    def validate(self):
        if not self.options.get_safe("enable_zlibwapi"):
            return
        if not self.options.shared:
            raise ConanInvalidConfiguration(
                "-o zlib/*:enable_zlibwapi=True requires -o zlib/*:shared=True, "
                "zlibwapi has only ever existed as a DLL")
        if not self.settings.get_safe("compiler.runtime"):
            raise ConanInvalidConfiguration(
                "-o zlib/*:enable_zlibwapi=True is only supported with MSVC-like compilers. "
                "The contrib/zlib1-dll sub-project does not clear the library prefix, so MinGW "
                "would produce libzlibwapi.dll instead of zlibwapi.dll")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZLIB_BUILD_TESTING"] = False
        tc.cache_variables["ZLIB_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["ZLIB_BUILD_STATIC"] = not self.options.shared
        if self.options.get_safe("enable_zlibwapi"):
            # Builds contrib/zlib1-dll, which produces both zlib1.dll and zlibwapi.dll. This
            # has to be a cache variable: contrib/CMakeLists.txt tests it before declaring it
            # as an option.
            tc.cache_variables["ZLIB_BUILD_ZLIB1_DLL"] = True
            # Its install() would drop a second zlib1.dll into bin/ - the shared library of
            # this package is named zlib1.dll as well - and would add the minizip headers to
            # the include root. Only zlibwapi.dll is wanted, so it is packaged by hand below.
            # The option is added by the patch, see its description.
            tc.cache_variables["ZLIB1_DLL_INSTALL"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        if self.options.get_safe("enable_zlibwapi"):
            # contrib/zlib1-dll is configured with ZLIB1_DLL_INSTALL=OFF, see generate()
            copy(self, "*zlibwapi*.dll", src=self.build_folder,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*zlibwapi*.lib", src=self.build_folder,
                 dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            # zlibwapi.dll exports contrib/minizip as well. Its headers are packaged in a
            # folder of their own, to keep them out of the include root and to make it
            # impossible to mix them up with the minizip package, which is built for the
            # cdecl calling convention. This is the header list of the zlibwapi target.
            minizip = os.path.join(self.source_folder, "contrib", "minizip")
            for header in ["crypt.h", "ints.h", "ioapi.h", "mztools.h", "unzip.h", "zip.h"]:
                copy(self, header, src=minizip,
                     dst=os.path.join(self.package_folder, "include", "zlibwapi"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ZLIB")

        if self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime"):
            # The recipe patches the CMakeLists.txt to generate different filenames when CMake
            # detects MINGW (clang, gcc with compiler.runtime undefined and compiler.libcxx defined)
            libname = "zdll" if self.options.shared else "zlib"
        else:
            libname = "z"

        if not self.options.get_safe("enable_zlibwapi"):
            self.cpp_info.set_property("cmake_target_name", "ZLIB::ZLIB")
            self.cpp_info.set_property("pkg_config_name", "zlib")
            self.cpp_info.libs = [libname]
            return

        # The WINAPI/stdcall variant is packaged alongside the default library, so both are
        # exposed as components. The aggregated target is deliberately not named ZLIB::ZLIB:
        # that name belongs to the component below, and linking both libraries at once would
        # also leak ZLIB_WINAPI into consumers that want the regular cdecl ABI.
        self.cpp_info.set_property("cmake_target_name", "ZLIB::ZLIB-all-do-not-use")
        self.cpp_info.set_property("pkg_config_name", "zlib-all-do-not-use")

        self.cpp_info.components["zlib_"].set_property("cmake_target_name", "ZLIB::ZLIB")
        self.cpp_info.components["zlib_"].set_property("pkg_config_name", "zlib")
        self.cpp_info.components["zlib_"].libs = [libname]

        self.cpp_info.components["zlibwapi"].set_property("cmake_target_name", "ZLIB::zlibwapi")
        self.cpp_info.components["zlibwapi"].set_property("pkg_config_name", "zlibwapi")
        self.cpp_info.components["zlibwapi"].libs = ["zlibwapi"]
        # The minizip headers this DLL also exports, see package()
        self.cpp_info.components["zlibwapi"].includedirs = [
            "include", os.path.join("include", "zlibwapi")]
        # Consumers must define ZLIB_WINAPI as well, so that the prototypes in zlib.h and in
        # the minizip headers use the same calling convention the library was built with
        # (see win32/DLL_FAQ.txt)
        self.cpp_info.components["zlibwapi"].defines = ["ZLIB_WINAPI"]
