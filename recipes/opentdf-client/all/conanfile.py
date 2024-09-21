import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OpenTDFConan(ConanFile):
    name = "opentdf-client"
    description = "openTDF core c++ client library for creating and accessing TDF protected data"
    license = "BSD-3-Clause-Clear"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.virtru.com"
    topics = ("opentdf", "tdf", "virtru")

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
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7.5",
            "clang": "12",
            "apple-clang": "12",
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
        # Uses openssl 3.x for 1.5.0 and newer
        if Version(self.version) >= "1.5.0":
            self.requires("openssl/[>=3.1 <4]")
        else:
            self.requires("openssl/1.1.1w")
        # Uses magic_enum for 1.4.0 and newer
        if Version(self.version) >= "1.4.0":
            self.requires("magic_enum/0.8.2")
        self.requires("ms-gsl/2.1.0")
        self.requires("nlohmann_json/3.11.3")
        self.requires("jwt-cpp/0.4.0")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("boost/1.83.0")
        self.requires("libxml2/2.11.6")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        # check minimum version of compiler
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
            )
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires {self.settings.compiler} {self.settings.compiler.version} "
                    f"but found {min_version}"
                )
        # Disallow MT and MTd
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.name} can not be built with MT or MTd at this time")

        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.name} does not currently support shared library on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not self.settings.get_safe("compiler.cppstd"):
            tc.variables["CMAKE_CXX_STANDARD"] = 17
        tc.cache_variables["CMAKE_PROJECT_opentdf_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*",
            dst=os.path.join(self.package_folder, "lib"),
            src=os.path.join(os.path.join(self.source_folder, "tdf-lib-cpp"), "lib"),
            keep_path=False)
        copy(self, "*",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(os.path.join(self.source_folder, "tdf-lib-cpp"), "include"),
            keep_path=False)
        copy(self, "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
            ignore_case=True,
            keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "opentdf-client")
        self.cpp_info.set_property("cmake_target_name", "opentdf-client::opentdf-client")
        self.cpp_info.set_property("pkg_config_name", "opentdf-client")

        self.cpp_info.components["libopentdf"].libs = ["opentdf_static"] if not self.options.shared else ["opentdf"]
        self.cpp_info.components["libopentdf"].set_property("cmake_target_name", "copentdf-client::opentdf-client")
        self.cpp_info.components["libopentdf"].names["cmake_find_package"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["cmake_find_package_multi"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].requires = [
            "openssl::openssl",
            "boost::boost",
            "ms-gsl::ms-gsl",
            "libxml2::libxml2",
            "jwt-cpp::jwt-cpp",
            "nlohmann_json::nlohmann_json",
            "zlib::zlib"
        ]
        if Version(self.version) >= "1.4.0":
            self.cpp_info.components["libopentdf"].requires.append("magic_enum::magic_enum")
        if Version(self.version) >= "1.4.0":
            self.cpp_info.components["libopentdf"].requires.append("magic_enum::magic_enum")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
