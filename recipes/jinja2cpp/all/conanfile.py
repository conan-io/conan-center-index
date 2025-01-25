from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class Jinja2cppConan(ConanFile):
    name = "jinja2cpp"
    description = "Jinja2 C++ (and for C++) almost full-conformance template engine implementation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jinja2cpp.dev/"
    topics = ("cpp14", "cpp17", "jinja2", "string templates", "templates engine")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_regex": ["std", "boost"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_regex": "boost",
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.3.2":
            del self.options.with_regex

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0")
        self.requires("expected-lite/0.6.3", transitive_headers=True)
        self.requires("optional-lite/3.5.0", transitive_headers=True)
        self.requires("rapidjson/cci.20220822")
        self.requires("string-view-lite/1.7.0", transitive_headers=True)
        self.requires("variant-lite/2.0.0", transitive_headers=True)
        if self.version == "1.1.0":
            self.requires("fmt/6.2.1") # not compatible with fmt >= 7.0.0
        else:
            self.requires("nlohmann_json/3.11.2")
            self.requires("fmt/10.2.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if Version(self.version) >= "1.3.1" and self.dependencies["boost"].options.without_json:
            raise ConanInvalidConfiguration(f"{self.ref} require Boost::json.")

    def build_requirements(self):
        if Version(self.version) >= "1.3.1":
            self.tool_requires("cmake/[>=3.23 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "1.3.2":
            tc.cache_variables["JINJA2CPP_USE_REGEX"] = self.options.with_regex
        tc.variables["JINJA2CPP_BUILD_TESTS"] = False
        tc.variables["JINJA2CPP_STRICT_WARNINGS"] = False
        tc.variables["JINJA2CPP_BUILD_SHARED"] = self.options.shared
        tc.variables["JINJA2CPP_DEPS_MODE"] = "conan-build"
        cppstd = self.settings.compiler.get_safe("cppstd")
        if cppstd:
            tc.cache_variables["JINJA2CPP_CXX_STANDARD"] = str(cppstd).replace("gnu", "")
        if is_msvc(self):
            # Runtime type configuration for Jinja2C++ should be strictly '/MT' or '/MD'
            runtime = "/MD" if "MD" in msvc_runtime_flag(self) else "/MT"
            tc.variables["JINJA2CPP_MSVC_RUNTIME_TYPE"] = runtime
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("expected-lite", "cmake_target_name", "expected-lite::expected-lite")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't force MD for shared lib, allow to honor runtime from profile
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(JINJA2CPP_MSVC_RUNTIME_TYPE \"/MD\")", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "jinja2cpp"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jinja2cpp")
        self.cpp_info.set_property("cmake_target_name", "jinja2cpp")
        self.cpp_info.libs = ["jinja2cpp"]

