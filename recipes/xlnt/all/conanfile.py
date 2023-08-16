from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class XlntConan(ConanFile):
    name = "xlnt"
    description = "Cross-platform user-friendly xlsx library for C++11+"
    license = "MIT"
    topics = ("excel", "xlsx", "spreadsheet", "reader", "writer")
    homepage = "https://github.com/tfussell/xlnt"
    url = "https://github.com/conan-io/conan-center-index"

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

    def requirements(self):
        self.requires("libstudxml/1.1.0-b.10+1")
        self.requires("miniz/3.0.2")
        self.requires("utfcpp/3.2.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        libstudxml_version = Version(self.dependencies["libstudxml"].ref.version)
        libstudxml_major_minor = f"{libstudxml_version.major}.{libstudxml_version.minor}"
        if Version(libstudxml_major_minor) < "1.1":
            raise ConanInvalidConfiguration(f"{self.ref} not compatible with libstudxml < 1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STATIC"] = not self.options.shared
        tc.variables["TESTS"] = False
        tc.variables["SAMPLES"] = False
        tc.variables["BENCHMARKS"] = False
        tc.variables["PYTHON"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Remove unvendored third party libs
        for third_party in ("libstudxml", "miniz", "utfcpp"):
            rmdir(self, os.path.join(self.source_folder, "third-party", third_party))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Xlnt")
        self.cpp_info.set_property("cmake_target_name", "xlnt::xlnt")
        self.cpp_info.set_property("pkg_config_name", "xlnt")
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"xlnt{suffix}"]
        if not self.options.shared:
            self.cpp_info.defines.append("XLNT_STATIC")

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "Xlnt"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Xlnt"
        self.cpp_info.names["cmake_find_package"] = "xlnt"
        self.cpp_info.names["cmake_find_package_multi"] = "xlnt"
