from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"


class QuantlibConan(ConanFile):
    name = "quantlib"
    description = "QuantLib is a free/open-source library for modeling, trading, and risk management in real-life."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.quantlib.org"
    topics = ("quantitative-finance",)
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

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.80.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 14 if Version(self.version) >= "1.24" else 11)
        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")
        if Version(self.version) >= "1.24" and is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("MSVC DLL build is not supported by upstream")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if Version(self.version) >= "1.24":
            tc.cache_variables["QL_BUILD_BENCHMARK"] = False
            tc.cache_variables["QL_BUILD_EXAMPLES"] = False
            tc.cache_variables["QL_BUILD_TEST_SUITE"] = False
            tc.cache_variables["QL_INSTALL_BENCHMARK"] = False
            tc.cache_variables["QL_INSTALL_EXAMPLES"] = False
            tc.cache_variables["QL_INSTALL_TEST_SUITE"] = False
        else:
            # even if boost shared, the underlying upstream logic doesn't matter for conan
            tc.variables["USE_BOOST_DYNAMIC_LIBRARIES"] = False
            if is_msvc(self):
                tc.variables["MSVC_RUNTIME"] = "static" if is_msvc_static_runtime(self) else "dynamic"
            # Export symbols for msvc shared
            tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.TXT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QuantLib")
        self.cpp_info.set_property("cmake_target_name", "QuantLib::QuantLib")
        self.cpp_info.set_property("pkg_config_name", "quantlib")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.requires = ["boost::headers"]
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.shared:
            self.cpp_info.system_libs.append("m")
