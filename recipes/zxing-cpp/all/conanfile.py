from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

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
        "enable_encoders": [True, False],
        "enable_decoders": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoders": True,
        "enable_decoders": True,
    }

    @property
    def _compiler_cpp_support(self):
        return {
            "14" : {
                "gcc": "5",
                "Visual Studio": "14",
                "msvc": "190",
                "clang": "3.4",
                "apple-clang": "3.4",
            },
            "17" : {
                "gcc": "7" if Version(self.version) < "2.0.0" else "8",
                "Visual Studio": "16",
                "msvc": "192",
                "clang": "5" if Version(self.version) < "2.0.0" else "7",
                "apple-clang": "5" if Version(self.version) < "2.0.0" else "12",
            }
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        cpp_version = 17 if Version(self.version) >= "1.2.0" else 14

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, cpp_version)
        min_version = self._compiler_cpp_support.get(str(cpp_version)).get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"This compiler is too old. {self.ref} needs a compiler with c++{cpp_version} support")

        # FIXME: This is a workaround for "The system cannot execute the specified program."
        if Version(self.version) >= "1.3.0" and is_msvc_static_runtime(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MT + Debug.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if Version(self.version) < "1.1":
            tc.variables["ENABLE_ENCODERS"] = self.options.enable_encoders
            tc.variables["ENABLE_DECODERS"] = self.options.enable_decoders
            tc.variables["BUILD_SHARED_LIBRARY"] = self.options.shared
        else:
            tc.variables["BUILD_WRITERS"] = self.options.enable_encoders
            tc.variables["BUILD_READERS"] = self.options.enable_decoders
            tc.variables["BUILD_EXAMPLES"] = False
            tc.variables["BUILD_BLACKBOX_TESTS"] = False
        if is_msvc(self):
            tc.variables["LINK_CPP_STATICALLY"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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
        self.cpp_info.set_property("pkg_config_name", "zxing")
        self.cpp_info.libs = ["ZXingCore" if Version(self.version) < "1.1" else "ZXing"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "ZXing"
        self.cpp_info.names["cmake_find_package_multi"] = "ZXing"
        self.cpp_info.names["pkg_config"] = "zxing"
