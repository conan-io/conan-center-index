from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class PerfettoConan(ConanFile):
    name = "perfetto"
    license = "Apache-2.0"
    homepage = "https://perfetto.dev"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Performance instrumentation and tracing for Android, Linux and Chrome"
    topics = ("linux", "profiling", "tracing")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_logging": [True, False], # switches PERFETTO_DISABLE_LOG
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_logging": False,
    }

    short_paths = True

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
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
        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < 7:
            raise ConanInvalidConfiguration ("perfetto requires gcc >= 7")
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PERFETTO_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["PERFETTO_DISABLE_LOGGING"] = self.options.disable_logging
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["perfetto"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

