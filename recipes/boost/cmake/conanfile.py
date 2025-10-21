from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    export_conandata_patches,
    get,
    rm,
    rmdir,
    collect_libs,
)
import os


required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "boost"
    description = "Boost provides free peer-reviewed portable C++ source libraries"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.boost.org"
    license = "BSL-1.0"
    topics = ("libraries", "cpp")

    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("bzip2/1.0.8")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("zstd/[>=1.5 <1.6]")
        self.requires(
            "libbacktrace/cci.20210118", transitive_headers=True, transitive_libs=True
        )
        self.requires("icu/77.1")
        self.requires("libiconv/1.18")

    def validate(self):
        # Cobalt requires C++20
        # MQTT5 requires C++17
        # most others are 14 or below
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _iostreams_zstd_target(self):
        return (
            "zstd::libzstd_shared"
            if self.dependencies["zstd"].options.shared
            else "zstd::libzstd_static"
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables.update(
            {
                "BOOST_IOSTREAMS_ZSTD_TARGET": self._iostreams_zstd_target,
            }
        )
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Boost")

        for component, info in [
            ("random", {}),
            ("test", {}),
            ("coroutine", {}),
            ("chrono", {}),
            ("fiber", {}),
            (
                "iostreams",
                {
                    "deps": [
                        "zlib::zlib",
                        "bzip2::bzip2",
                        "xz_utils::xz_utils",
                        "zstd::zstd",
                    ]
                },
            ),
            ("json", {}),
            ("nowide", {}),
            ("locale", {"deps": ["icu::icu", "libiconv::libiconv"]}),
            (
                "stacktrace",
                {
                    "libs": ["boost_stacktrace_basic", "boost_stacktrace_noop"],
                    "deps": ["libbacktrace::libbacktrace"],
                },
            ),
            ("process", {}),
            ("test", {"libs": ["boost_unit_test_framework"]}),
            ("url", {}),
        ]:
            self.cpp_info.components[component].libs = info.get("libs", [f"boost_{component}"])
            self.cpp_info.components[component].requires = info.get("deps", [])
            self.cpp_info.components[component].set_property(
                "cmake_target_name", f"Boost::{component}"
            )

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
