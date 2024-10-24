import os
import textwrap

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibtiffConan(ConanFile):
    name = "libtiff"
    description = "Library for Tag Image File Format (TIFF)"
    url = "https://github.com/conan-io/conan-center-index"
    license = "libtiff"
    homepage = "http://www.simplesystems.org/libtiff"
    topics = ("tiff", "image", "bigtiff", "tagged-image-file-format")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lzma": [True, False],
        "jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "zlib": [True, False],
        "lerc": [True, False],
        "libdeflate": [True, False],
        "zstd": [True, False],
        "jbig": [True, False],
        "webp": [True, False],
        "cxx":  [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lzma": True,
        "jpeg": "libjpeg",
        "zlib": True,
        "lerc": False,
        "libdeflate": True,
        "zstd": True,
        "jbig": True,
        "webp": True,
        "cxx":  True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) <= "4.5.0":
            # test_package.cpp segfaults with older libtiff versions
            del self.options.cxx

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("cxx"):
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.libdeflate:
            self.requires("libdeflate/1.19")
        if self.options.lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.jbig:
            self.requires("jbig/20160605")
        if self.options.zstd:
            self.requires("zstd/1.5.5")
        if self.options.webp:
            self.requires("libwebp/1.3.2")
        if self.options.lerc:
            self.requires("lerc/4.0.4")

    def validate(self):
        if self.options.libdeflate and not self.options.zlib:
            raise ConanInvalidConfiguration("libtiff:libdeflate=True requires libtiff:zlib=True")

    def build_requirements(self):
        if Version(self.version) >= "4.5.1":
            # https://github.com/conan-io/conan/issues/3482#issuecomment-662284561
            self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["lzma"] = self.options.lzma
        tc.variables["jpeg"] = bool(self.options.jpeg)
        tc.variables["jpeg12"] = False
        tc.variables["jbig"] = self.options.jbig
        tc.variables["zlib"] = self.options.zlib
        tc.variables["libdeflate"] = self.options.libdeflate
        tc.variables["zstd"] = self.options.zstd
        tc.variables["webp"] = self.options.webp
        tc.variables["lerc"] = self.options.lerc
        if Version(self.version) >= "4.5.0":
            # Disable tools, test, contrib, man & html generation
            tc.variables["tiff-tools"] = False
            tc.variables["tiff-tests"] = False
            tc.variables["tiff-contrib"] = False
            tc.variables["tiff-docs"] = False
        tc.variables["cxx"] = self.options.get_safe("cxx", False)
        # BUILD_SHARED_LIBS must be set in command line because defined upstream before project()
        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()
        deps = CMakeDeps(self)
        if Version(self.version) >= "4.5.1":
            deps.set_property("jbig", "cmake_target_name", "JBIG::JBIG")
            deps.set_property("xz_utils", "cmake_target_name", "liblzma::liblzma")
            deps.set_property("libdeflate", "cmake_file_name", "Deflate")
            deps.set_property("libdeflate", "cmake_target_name", "Deflate::Deflate")
        deps.set_property("lerc", "cmake_target_name", "LERC::LERC")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # remove FindXXXX for conan dependencies
        for module in self.source_path.joinpath("cmake").glob("Find*.cmake"):
            if module.name != "FindCMath.cmake":
                module.unlink()

        # Export symbols of tiffxx for msvc shared
        replace_in_file(self, os.path.join(self.source_folder, "libtiff", "CMakeLists.txt"),
                              "set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION})",
                              "set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION} WINDOWS_EXPORT_ALL_SYMBOLS ON)")

        # Disable tools, test, contrib, man & html generation
        if Version(self.version) < "4.5.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "add_subdirectory(tools)\nadd_subdirectory(test)\nadd_subdirectory(contrib)\nadd_subdirectory(build)\n"
                                  "add_subdirectory(man)\nadd_subdirectory(html)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        license_file = "COPYRIGHT" if Version(self.version) < "4.5.0" else "LICENSE.md"
        copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        if conan_version.major == 1:
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {
                    "TIFF::TIFF": "libtiff::tiff",
                    "TIFF::CXX": "libtiff::tiffxx",
                }
            )

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

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

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "TIFF")

        self.cpp_info.components["tiff"].set_property("cmake_target_name", "TIFF::TIFF")
        self.cpp_info.components["tiff"].set_property("pkg_config_name", f"libtiff-{Version(self.version).major}")
        suffix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        self.cpp_info.components["tiff"].libs.append(f"tiff{suffix}")
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.components["tiff"].system_libs.append("m")

        self.cpp_info.requires = []
        if self.options.zlib:
            self.cpp_info.components["tiff"].requires.append("zlib::zlib")
        if self.options.libdeflate:
            self.cpp_info.components["tiff"].requires.append("libdeflate::libdeflate")
        if self.options.lzma:
            self.cpp_info.components["tiff"].requires.append("xz_utils::xz_utils")
        if self.options.jpeg == "libjpeg":
            self.cpp_info.components["tiff"].requires.append("libjpeg::libjpeg")
        elif self.options.jpeg == "libjpeg-turbo":
            self.cpp_info.components["tiff"].requires.append("libjpeg-turbo::jpeg")
        elif self.options.jpeg == "mozjpeg":
            self.cpp_info.components["tiff"].requires.append("mozjpeg::libjpeg")
        if self.options.jbig:
            self.cpp_info.components["tiff"].requires.append("jbig::jbig")
        if self.options.zstd:
            self.cpp_info.components["tiff"].requires.append("zstd::zstd")
        if self.options.webp:
            self.cpp_info.components["tiff"].requires.append("libwebp::webp")
        if self.options.lerc:
            self.cpp_info.components["tiff"].requires.append("lerc::lerc")

        if self.options.get_safe("cxx"):
            self.cpp_info.components["tiffxx"].libs.append(f"tiffxx{suffix}")
            # https://cmake.org/cmake/help/latest/module/FindTIFF.html#imported-targets
            # https://github.com/libsdl-org/libtiff/blob/v4.6.0/libtiff/CMakeLists.txt#L229
            self.cpp_info.components["tiffxx"].set_property("cmake_target_name", "TIFF::CXX")
            # Note: the project does not export tiffxx as a pkg-config component, this is unofficial
            self.cpp_info.components["tiffxx"].set_property("pkg_config_name", f"libtiffxx-{Version(self.version).major}")
            self.cpp_info.components["tiffxx"].requires = ["tiff"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        if conan_version.major == 1:
            self.cpp_info.filenames["cmake_find_package"] = "TIFF"
            self.cpp_info.filenames["cmake_find_package_multi"] = "TIFF"
            self.cpp_info.components["tiff"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["tiff"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
