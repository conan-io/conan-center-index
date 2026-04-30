from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os


required_conan_version = ">=2.1"


class LeptonicaConan(ConanFile):
    name = "leptonica"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Library containing software that is broadly useful for " \
                  "image processing and image analysis applications."
    topics = ("image", "multimedia", "format", "graphics")
    homepage = "http://leptonica.org"
    license = "BSD-2-Clause"

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
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.2 <4]")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/[>=4.1.5 <5]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_tiff:
            self.requires("libtiff/[>=4.6.0 <5]")
        if self.options.with_openjpeg:
            self.requires("openjpeg/[>=2.5.2 <3]")
        if self.options.with_webp:
            self.requires("libwebp/[>=1.3.2 <2]")

    def build_requirements(self):
        if self.options.with_webp or self.options.with_openjpeg:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PROG"] = False
        tc.variables["SW_BUILD"] = False
        tc.cache_variables["ENABLE_ZLIB"] = self.options.with_zlib
        tc.cache_variables["ENABLE_PNG"] = self.options.with_png
        tc.cache_variables["ENABLE_GIF"] = self.options.with_gif
        tc.cache_variables["ENABLE_JPEG"] = self.options.with_jpeg
        tc.cache_variables["ENABLE_TIFF"] = self.options.with_tiff
        tc.cache_variables["ENABLE_WEBP"] = self.options.with_webp
        tc.cache_variables["ENABLE_OPENJPEG"] = self.options.with_openjpeg
        tc.cache_variables["LIBWEBP_SUPPORT"] = self.options.with_webp
        tc.cache_variables["OPENJPEG_SUPPORT"] = self.options.with_openjpeg
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        if self.options.with_webp or self.options.with_openjpeg:
            pc = PkgConfigDeps(self)
            pc.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def _patch_sources(self):
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Leptonica")
        self.cpp_info.set_property("cmake_target_name", "leptonica")
        self.cpp_info.set_property("pkg_config_name", "lept")
        suffix = f"-{self.version }" if self.settings.os == "Windows" else ""
        self.cpp_info.libs = ["leptonica" + suffix]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs.append(os.path.join("include", "leptonica"))
