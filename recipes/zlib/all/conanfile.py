from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, load, replace_in_file, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.46.0"


class ZlibConan(ConanFile):
    name = "zlib"
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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SKIP_INSTALL_ALL"] = False
        tc.variables["SKIP_INSTALL_LIBRARIES"] = False
        tc.variables["SKIP_INSTALL_HEADERS"] = False
        tc.variables["SKIP_INSTALL_FILES"] = True
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        is_apple_clang12 = self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) >= "12.0"
        if not is_apple_clang12:
            for filename in ['zconf.h', 'zconf.h.cmakein', 'zconf.h.in']:
                filepath = os.path.join(self.source_folder, filename)
                replace_in_file(self, filepath,
                                      '#ifdef HAVE_UNISTD_H    '
                                      '/* may be set to #if 1 by ./configure */',
                                      '#if defined(HAVE_UNISTD_H) && (1-HAVE_UNISTD_H-1 != 0)')
                replace_in_file(self, filepath,
                                      '#ifdef HAVE_STDARG_H    '
                                      '/* may be set to #if 1 by ./configure */',
                                      '#if defined(HAVE_STDARG_H) && (1-HAVE_STDARG_H-1 != 0)')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_license(self):
        tmp = load(self, os.path.join(self.source_folder, "zlib.h"))
        license_contents = tmp[2:tmp.find("*/", 1)]
        return license_contents

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ZLIB")
        self.cpp_info.set_property("cmake_target_name", "ZLIB::ZLIB")
        self.cpp_info.set_property("pkg_config_name", "zlib")
        if is_msvc(self) or self._is_clang_cl:
            libname = "zdll" if self.options.shared else "zlib"
        else:
            libname = "z"
        self.cpp_info.libs = [libname]

        self.cpp_info.names["cmake_find_package"] = "ZLIB"
        self.cpp_info.names["cmake_find_package_multi"] = "ZLIB"
