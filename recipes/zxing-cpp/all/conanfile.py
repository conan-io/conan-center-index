from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=2.1"


class ZXingCppConan(ConanFile):
    name = "zxing-cpp"
    description = "C++ port of ZXing, a barcode scanning library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zxing-cpp/zxing-cpp"
    topics = ("zxing", "barcode", "scanner", "generator")
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
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16]")

    def validate(self):
        check_min_cppstd(self, 20)

        # FIXME: This is a workaround for "The system cannot execute the specified program."
        # TODO: Validate on Windows for 3.1.1
        if Version(self.version) >= "1.3.0" and is_msvc_static_runtime(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MT + Debug.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZXING_EXAMPLES"] = False
        if is_msvc(self):
            tc.cache_variables["LINK_CPP_STATICALLY"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZXing")
        self.cpp_info.set_property("cmake_target_name", "ZXing::ZXing")
        self.cpp_info.libs = ["ZXing"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
