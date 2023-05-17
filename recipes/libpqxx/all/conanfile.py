from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.microsoft import check_min_vs, is_msvc, msvc_runtime_flag
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LibpqxxConan(ConanFile):
    name = "libpqxx"
    description = "The official C++ client API for PostgreSQL"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jtv/libpqxx"
    topics = ("libpqxx", "postgres", "postgresql", "database", "db")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 14 if Version(self.version) < "7.0" else "17"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "7.0":
            return {
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10"
            }
        else:
            return {
                "gcc": "7" if Version(self.version) < "7.5.0" else "8",
                "clang": "6",
                "apple-clang": "10"
            }

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

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
        self.requires("libpq/14.5")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if Version(self.version) < "7.0":
            check_min_vs(self, 190)
        elif Version(self.version) < "7.6":
            check_min_vs(self, 191)
        else:
            check_min_vs(self, 192)

        if is_msvc(self) and self.options.shared and msvc_runtime_flag(self) == "MTd":
            raise ConanInvalidConfiguration(f"{self.ref} recipes does not support build shared library with MTd runtime.")

        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        if is_apple_os(self):
            os_version = self.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_TEST"] = False
        # Set `-mmacosx-version-min` to enable C++17 standard library support.
        tc.variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = self._mac_os_minimum_required_version
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libpqxx")
        self.cpp_info.set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.set_property("pkg_config_name", "libpqxx")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["pqxx"].libs = ["pqxx"]
        if self.settings.os == "Windows":
            self.cpp_info.components["pqxx"].system_libs = ["wsock32", "ws2_32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["pqxx"].set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.components["pqxx"].set_property("pkg_config_name", "libpqxx")
        self.cpp_info.components["pqxx"].requires = ["libpq::libpq"]
