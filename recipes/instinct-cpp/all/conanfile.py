from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class InstinctCppConan(ConanFile):
    name = "instinct-cpp"
    description = ("instinct.cpp provides ready to use alternatives to OpenAI Assistant API"
                   "and built-in utilities for developing AI Agent applications (RAG, Chatbot, Code interpreter) powered by language models. "
                   "Call it langchain.cpp if you like.")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RobinQu/instinct.cpp"
    topics = ("llm", "agent", "genai")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_duckdb": [True, False],
        "with_exprtk": [True, False],
        "with_pdfium": [True, False],
        "with_duckx": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_duckdb": True,
        "with_exprtk": True,
        "with_pdfium": True,
        "with_duckx": True,
        "duckdb/*:with_httpfs": True,
        "icu/*:with_extras": True,
        "icu/*:data_packaging": "static"
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "15",
            "clang": "17",
            "gcc": "12"
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
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hash-library/8.0", transitive_headers=True)
        self.requires("bshoshany-thread-pool/4.1.0", transitive_headers=True)

        if self.options.with_duckdb:
            self.requires("duckdb/0.10.2", transitive_headers=True)

        self.requires("uriparser/0.9.7", transitive_headers=True)
        self.requires("crossguid/0.2.2", transitive_headers=True)
        self.requires("protobuf/5.27.0", transitive_headers=True)
        self.requires("reactiveplusplus/2.1.1", transitive_headers=True)
        self.requires("icu/74.1")
        self.requires("tsl-ordered-map/1.1.0", transitive_headers=True)
        self.requires("fmt/10.2.1", transitive_headers=True)
        self.requires("fmtlog/2.2.1", transitive_headers=True)
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("base64/0.5.2", transitive_headers=True)
        self.requires("libcurl/8.6.0", transitive_headers=True)
        self.requires("inja/3.4.0", transitive_headers=True)
        self.requires("concurrentqueue/1.0.4", transitive_headers=True)
        self.requires("cpptrace/0.5.4", transitive_headers=True)

        if self.options.with_pdfium:
            self.requires("pdfium/95.0.4629", transitive_headers=True)

        if self.options.with_duckx:
            self.requires("duckx/1.2.2", transitive_headers=True)

        if self.options.with_exprtk:
            self.requires("exprtk/0.0.2", transitive_headers=True)

        self.requires("llama-cpp/b3040", transitive_headers=True)
        self.requires("cpp-httplib/0.15.3", transitive_headers=True)
        self.requires("cli11/2.4.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        
        def _ensure_dep_has_option(dep, option, value):
            if self.dependencies[dep].options[option] != value:
                raise ConanInvalidConfiguration(f'{self.ref} needs -o="{dep}/*:{option}={value}"')

        _ensure_dep_has_option("duckdb", "with_httpfs", self.default_options["duckdb/*:with_httpfs"])       
        _ensure_dep_has_option("icu", "with_extras", self.default_options["icu/*:with_extras"])
        _ensure_dep_has_option("icu", "data_packaging", self.default_options["icu/*:data_packaging"])

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["WITH_DUCKDB"] = self.options.with_duckdb
        tc.variables["WITH_EXPRTK"] = self.options.with_exprtk
        tc.variables["WITH_PDFIUM"] = self.options.with_pdfium
        tc.variables["WITH_DUCKX"] = self.options.with_duckx
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()


    def package_info(self):
        self.cpp_info.libs = ["proto"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
