from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.55.0"


class LeptonicaConan(ConanFile):
    name = "leptonica"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Library containing software that is broadly useful for " \
                  "image processing and image analysis applications."
    topics = ("image", "multimedia", "format", "graphics")
    homepage = "http://leptonica.org"
    license = "BSD 2-Clause"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_gif": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_openjpeg": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_gif": True,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_openjpeg": True,
        "with_webp": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if bool(self.options.with_jpeg):
            self.options["*"].jpeg = self.options.with_jpeg
            self.options["*"].with_jpeg = self.options.with_jpeg
            self.options["*"].with_libjpeg = self.options.with_jpeg

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")

    def build_requirements(self):
        if self.options.with_webp or self.options.with_openjpeg:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_PROG"] = False
        tc.variables["SW_BUILD"] = False
        if Version(self.version) >= "1.83.0":
            tc.variables["LIBWEBP_SUPPORT"] = self.options.with_webp
            tc.variables["OPENJPEG_SUPPORT"] = self.options.with_openjpeg
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        if self.options.with_webp or self.options.with_openjpeg:
            pc = PkgConfigDeps(self)
            pc.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        cmakelists_src = os.path.join(self.source_folder, "src", "CMakeLists.txt")
        cmake_configure = os.path.join(self.source_folder, "cmake", "Configure.cmake")

        # Honor options and inject dependencies definitions
        # TODO: submit a patch upstream
        ## zlib
        replace_in_file(self, cmakelists_src, "${ZLIB_LIBRARIES}", "ZLIB::ZLIB")
        if not self.options.with_zlib:
            replace_in_file(self, cmakelists_src, "if (ZLIB_LIBRARIES)", "if(0)")
            replace_in_file(self, cmake_configure, "if (ZLIB_FOUND)", "if(0)")
        ## giflib
        replace_in_file(self, cmakelists_src, "${GIF_LIBRARIES}", "GIF::GIF")
        if not self.options.with_gif:
            replace_in_file(self, cmakelists_src, "if (GIF_LIBRARIES)", "if(0)")
            replace_in_file(self, cmake_configure, "if (GIF_FOUND)", "if(0)")
        ## libjpeg
        replace_in_file(self, cmakelists_src, "${JPEG_LIBRARIES}", "JPEG::JPEG")
        if not self.options.with_jpeg:
            replace_in_file(self, cmakelists_src, "if (JPEG_LIBRARIES)", "if(0)")
            replace_in_file(self, cmake_configure, "if (JPEG_FOUND)", "if(0)")
        ## libpng
        replace_in_file(self, cmakelists_src, "${PNG_LIBRARIES}", "PNG::PNG")
        if not self.options.with_png:
            replace_in_file(self, cmakelists_src, "if (PNG_LIBRARIES)", "if(0)")
            replace_in_file(self, cmake_configure, "if (PNG_FOUND)", "if(0)")
        ## libtiff
        replace_in_file(self, cmakelists_src, "${TIFF_LIBRARIES}", "TIFF::TIFF")
        if not self.options.with_tiff:
            replace_in_file(self, cmakelists_src, "if (TIFF_LIBRARIES)", "if(0)")
            replace_in_file(self, cmake_configure, "if (TIFF_FOUND)", "if(0)")
        ## We have to be more aggressive with dependencies found with pkgconfig
        ## Injection of libdirs is ensured by conan_basic_setup()
        ## openjpeg
        replace_in_file(self, cmakelists_src, "${JP2K_LIBRARIES}", "openjp2")
        if Version(self.version) < "1.83.0":
            # pkgconfig is prefered to CMake. Disable pkgconfig so only CMake is used
            replace_in_file(self, cmakelists, "pkg_check_modules(JP2K libopenjp2>=2.0 QUIET)", "")
            # versions below 1.83.0 do not have an option toggle
            replace_in_file(self, cmakelists, "if(NOT JP2K)", "if(0)")
            if not self.options.with_openjpeg:
                replace_in_file(self, cmakelists_src, "if (JP2K_FOUND)", "if(0)")
                replace_in_file(self, cmake_configure, "if (JP2K_FOUND)", "if(0)")
        else:
            replace_in_file(self, cmakelists, "set(JP2K_INCLUDE_DIRS ${OPENJPEG_INCLUDE_DIRS})", "set(JP2K_INCLUDE_DIRS ${OpenJPEG_INCLUDE_DIRS})")
            if not self.options.with_openjpeg:
                replace_in_file(self, cmake_configure, "if (JP2K_FOUND)", "if(0)")

        ## libwebp
        if Version(self.version) < "1.83.0":
            # versions below 1.83.0 do not have an option toggle
            replace_in_file(self, cmakelists, "if(NOT WEBP)", "if(0)")
            replace_in_file(self, cmakelists, "if(NOT WEBPMUX)", "if(0)")
            if not self.options.with_webp:
                replace_in_file(self, cmakelists_src, "if (WEBP_FOUND)", "if(0)")
                replace_in_file(self, cmake_configure, "if (WEBP_FOUND)", "if(0)")
        if Version(self.version) >= "1.83.0" or self.options.with_webp:
            replace_in_file(self, cmakelists_src,
                                "if (WEBP_FOUND)",
                                "if (WEBP_FOUND)\n"
                                "target_link_directories(leptonica PRIVATE ${WEBP_LIBRARY_DIRS} ${WEBPMUX_LIBRARY_DIRS})\n"
                                "target_compile_definitions(leptonica PRIVATE ${WEBP_CFLAGS_OTHER} ${WEBPMUX_CFLAGS_OTHER})")
        replace_in_file(self, cmakelists_src, "${WEBP_LIBRARIES}", "${WEBP_LIBRARIES} ${WEBPMUX_LIBRARIES}")

        # Remove detection of fmemopen() on macOS < 10.13
        # CheckFunctionExists will find it in the link library.
        # There's no error because it's not including the header with the
        # deprecation macros.
        if self.settings.os == "Macos" and self.settings.os.version:
            if Version(self.settings.os.version) < "10.13":
                replace_in_file(self, cmake_configure,
                                      "set(functions_list\n    "
                                      "fmemopen\n    fstatat\n)",
                                      "set(functions_list\n    "
                                      "fstatat\n)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "leptonica-license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))  # since 1.81.0
        rmdir(self, os.path.join(self.package_folder, "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"leptonica": "Leptonica::Leptonica"}
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
        self.cpp_info.set_property("cmake_file_name", "Leptonica")
        self.cpp_info.set_property("cmake_target_name", "leptonica")
        self.cpp_info.set_property("pkg_config_name", "lept")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs.append(os.path.join("include", "leptonica"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Leptonica"
        self.cpp_info.names["cmake_find_package_multi"] = "Leptonica"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "lept"
