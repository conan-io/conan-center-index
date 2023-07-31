from conan import ConanFile
from conan.tools.files import get, copy, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LibRawConan(ConanFile):
    name = "libraw"
    description = "LibRaw is a library for reading RAW files obtained from digital photo cameras (CRW/CR2, NEF, RAF, DNG, and others)."
    license = "CDDL-1.0", "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libraw.org/"
    topics = ["image", "photography", "raw"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_lcms": [True, False],
        "with_jasper": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "with_lcms": True,
        "with_jasper": True
    }
    exports_sources = ["CMakeLists.txt"]

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
            self.requires("libjpeg-turbo/2.1.5")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
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
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("WIN32")
            self.cpp_info.system_libs.append("ws2_32")

        if not self.options.shared:
            self.cpp_info.defines.append("LIBRAW_NODLL")
