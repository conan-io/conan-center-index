from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, save, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.53.0"


class Exiv2Conan(ConanFile):
    name = "exiv2"
    description = "Exiv2 is a C++ library and a command-line utility " \
                  "to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata."
    license = "GPL-2.0"
    topics = ("image", "exif", "xmp")
    homepage = "https://www.exiv2.org"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_xmp": [False, "bundled", "external"],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_xmp": "bundled",
        "with_curl": False,
    }

    provides = []

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_xmp == "bundled":
            # recipe has bundled xmp-toolkit-sdk of old version
            # avoid conflict with a future xmp recipe
            self.provides.append("xmp-toolkit-sdk")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        if self.options.with_png:
            self.requires("libpng/1.6.39")
            self.requires("zlib/1.2.13")
        if self.options.with_xmp == "bundled":
            self.requires("expat/2.5.0")
        if self.options.with_curl:
            self.requires("libcurl/7.87.0")

    def validate(self):
        if self.options.with_xmp == "external":
            raise ConanInvalidConfiguration("adobe-xmp-toolkit is not available on cci (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EXIV2_BUILD_SAMPLES"] = False
        tc.variables["EXIV2_BUILD_EXIV2_COMMAND"] = False
        tc.variables["EXIV2_ENABLE_PNG"] = self.options.with_png
        tc.variables["EXIV2_ENABLE_XMP"] = self.options.with_xmp == "bundled"
        tc.variables["EXIV2_ENABLE_EXTERNAL_XMP"] = self.options.with_xmp == "external"
        # NLS is used only for tool which is not built
        tc.variables["EXIV2_ENABLE_NLS"] = False
        tc.variables["EXIV2_ENABLE_WEBREADY"] = self.options.with_curl
        tc.variables["EXIV2_ENABLE_CURL"] = self.options.with_curl
        tc.variables["EXIV2_ENABLE_SSH"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        if is_msvc(self):
            tc.variables["EXIV2_ENABLE_DYNAMIC_RUNTIME"] = not is_msvc_static_runtime(self)
        # set PIC manually because of object target exiv2_int
        tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.get_safe("fPIC", True))
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        targets = {"exiv2lib": "exiv2::exiv2lib"}
        if self.options.with_xmp == "bundled":
            targets.update({"exiv2-xmp": "exiv2::exiv2-xmp"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "exiv2")
        self.cpp_info.set_property("pkg_config_name", "exiv2")

        # component exiv2lib
        self.cpp_info.components["exiv2lib"].set_property("cmake_target_name", "exiv2lib")
        self.cpp_info.components["exiv2lib"].libs = ["exiv2"]
        self.cpp_info.components["exiv2lib"].requires = [ "libiconv::libiconv"]
        if self.options.with_png:
            self.cpp_info.components["exiv2lib"].requires.extend(["libpng::libpng", "zlib::zlib"])
        if self.options.with_curl:
            self.cpp_info.components["exiv2lib"].requires.append("libcurl::libcurl")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["exiv2lib"].system_libs.extend(["pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.components["exiv2lib"].system_libs.extend(["psapi", "ws2_32"])
            self.cpp_info.components["exiv2lib"].defines.append("WIN32_LEAN_AND_MEAN")

        # component exiv2-xmp
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2-xmp"].set_property("cmake_target_name", "exiv2-xmp")
            self.cpp_info.components["exiv2-xmp"].libs = ["exiv2-xmp"]
            self.cpp_info.components["exiv2-xmp"].requires = [ "expat::expat" ]
            self.cpp_info.components["exiv2lib"].requires.append("exiv2-xmp")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
