from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir, copy
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class TaoCPPTaopqConan(ConanFile):
    name = "taocpp-taopq"
    description = "C++ client library for PostgreSQL"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/taopq"
    topics = ("cpp17", "postgresql", "libpq", "data-base", "sql")
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

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7" if self.version < "cci.20231219" else "8",
            "clang": "6" if self.version < "cci.20231219" else "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # libpq-fe.h is included by many public headers of taocpp-taopq, and also uses some symbols of the lib (see https://github.com/conan-io/conan-center-index/pull/19825#issuecomment-1720996359)
        self.requires("libpq/15.4", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Option names changed in https://github.com/taocpp/taopq/commit/d77896ab80369f13512a7f0ba8af818a03de1cdf
        if Version(self.version) < "cci.20211017":
            tc.variables["TAOPQ_BUILD_TESTS"] = False
            tc.variables["TAOPQ_INSTALL_DOC_DIR"] = "licenses"
        else:
            tc.variables["taopq_BUILD_TESTS"] = False
            tc.variables["taopq_INSTALL_DOC_DIR"] = "licenses"
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taopq")
        self.cpp_info.set_property("cmake_target_name", "taocpp::taopq")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_taocpp-taopq"].libs = ["taopq"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_taocpp-taopq"].system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.components["_taocpp-taopq"].system_libs.append("ws2_32")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taopq"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taopq"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package_multi"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].set_property("cmake_target_name", "taocpp::taopq")
        self.cpp_info.components["_taocpp-taopq"].requires = ["libpq::libpq"]
