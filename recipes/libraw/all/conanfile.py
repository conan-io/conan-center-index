import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"

class LibRawConan(ConanFile):
    name = "libraw"
    description = "LibRaw is a library for reading RAW files obtained from digital photo cameras (CRW/CR2, NEF, RAF, DNG, and others)."
    license = "CDDL-1.0", "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libraw.org/"
    topics = ("image", "photography", "raw")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_thread_safe": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_lcms": [True, False],
        "with_jasper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_thread_safe": False,
        "with_jpeg": "libjpeg",
        "with_lcms": True,
        "with_jasper": True,
    }
    exports_sources = ["CMakeLists.txt"]

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            del self.options.build_thread_safe

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TODO: RawSpeed dependency (-DUSE_RAWSPEED)
        # TODO: DNG SDK dependency (-DUSE_DNGSDK)
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.3")
        if self.options.with_lcms:
            self.requires("lcms/2.16")
        if self.options.with_jasper:
            self.requires("jasper/4.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
       get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RAW_LIB_VERSION_STRING"] = self.version
        tc.variables["LIBRAW_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["LIBRAW_BUILD_THREAD_SAFE"] = self.options.get_safe("build_thread_safe", False)
        tc.variables["LIBRAW_WITH_JPEG"] = bool(self.options.with_jpeg)
        tc.variables["LIBRAW_WITH_LCMS"] = self.options.with_lcms
        tc.variables["LIBRAW_WITH_JASPER"] = self.options.with_jasper
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libraw_"].set_property("pkg_config_name", "libraw")
        self.cpp_info.components["libraw_"].libs = ["raw"]
        self.cpp_info.components["libraw_"].includedirs.append(os.path.join("include", "libraw"))

        if self.settings.os == "Windows":
            self.cpp_info.components["libraw_"].system_libs.append("ws2_32")
            if not self.options.shared:
                self.cpp_info.components["libraw_"].defines.append("LIBRAW_NODLL")

        requires = []
        if self.options.with_jpeg == "libjpeg":
            requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_jpeg == "mozjpeg":
            requires.append("mozjpeg::libjpeg")
        if self.options.with_lcms:
            requires.append("lcms::lcms")
        if self.options.with_jasper:
            requires.append("jasper::jasper")
        self.cpp_info.components["libraw_"].requires = requires

        if self.options.get_safe("build_thread_safe"):
            self.cpp_info.components["libraw_r"].set_property("pkg_config_name", "libraw_r")
            self.cpp_info.components["libraw_r"].libs = ["raw_r"]
            self.cpp_info.components["libraw_r"].includedirs.append(os.path.join("include", "libraw"))
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libraw_r"].system_libs.append("pthread")
            self.cpp_info.components["libraw_r"].requires = requires

        if not self.options.shared and stdcpp_library(self):
            self.cpp_info.components["libraw_"].system_libs.append(stdcpp_library(self))
            if self.options.get_safe("build_thread_safe"):
                self.cpp_info.components["libraw_r"].system_libs.append(stdcpp_library(self))
