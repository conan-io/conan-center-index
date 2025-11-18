from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SparrowRecipe(ConanFile):
    name = "sparrow"
    description = "C++20 idiomatic APIs for the Apache Arrow Columnar Format"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/man-group/sparrow"
    topics = ("arrow", "apache arrow", "columnar format", "dataframe")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_date_polyfill": [True, False],
        "export_json_reader": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "use_date_polyfill": True,
        "export_json_reader": False,
    }

    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os == "Macos":
            del self.options.use_date_polyfill

    @property
    def _uses_date_polyfill(self):
        # Not an option not to use it on Macos
        return self.options.get_safe("use_date_polyfill", True)

    def requirements(self):
        if self._uses_date_polyfill:
            self.requires("date/3.0.3", transitive_headers=True)
        if self.options.export_json_reader:
            self.requires("nlohmann_json/3.12.0")

    @property
    def _compilers_minimum_version(self):
        # Upstream has these set as the minimum versions
        # regardless of cppstd support
        return {
            "apple-clang": "16",
            "clang": "18",
            "gcc": "11" if Version(self.version) >= "0.6.0" else "13",
            "msvc": "194",
        }

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < Version(minimum_version):
            raise ConanInvalidConfiguration(f"{self.name} requires {self.settings.compiler} {minimum_version} or newer")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_DATE_POLYFILL"] = self._uses_date_polyfill
        tc.variables["SPARROW_BUILD_SHARED"] = self.options.shared
        tc.variables["CREATE_JSON_READER_TARGET"] = self.options.export_json_reader
        if is_msvc(self):
            tc.variables["USE_LARGE_INT_PLACEHOLDERS"] = True
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
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "cmake"))

    def package_info(self):
        postfix = "d" if (self.settings.build_type == "Debug" and Version(self.version) >= "1.3.0") else ""
        self.cpp_info.set_property("cmake_file_name", "sparrow")
        
        # Main sparrow component
        self.cpp_info.components["sparrow"].set_property("cmake_target_name", "sparrow::sparrow")
        self.cpp_info.components["sparrow"].libs = [f"sparrow{postfix}"]
        
        if not self.options.shared:
            self.cpp_info.components["sparrow"].defines.append("SPARROW_STATIC_LIB")
        if self._uses_date_polyfill:
            self.cpp_info.components["sparrow"].defines.append("SPARROW_USE_DATE_POLYFILL")
            self.cpp_info.components["sparrow"].requires.append("date::date")
        if is_msvc(self):
            self.cpp_info.components["sparrow"].defines.append("SPARROW_USE_LARGE_INT_PLACEHOLDERS")
    
        # Optional json_reader component
        if self.options.export_json_reader:
            self.cpp_info.components["json_reader"].set_property("cmake_target_name", "sparrow::json_reader")
            self.cpp_info.components["json_reader"].libs = [f"sparrow_json_reader{postfix}"]
            self.cpp_info.components["json_reader"].requires = ["sparrow", "nlohmann_json::nlohmann_json"]
