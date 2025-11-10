from conan import ConanFile
from conan.tools.build import check_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir, save, load, apply_conandata_patches
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=2.0.9"

class CouchbaseCxxClientConan(ConanFile):
    name = "couchbase_cxx_client"
    description = "Couchbase C++ SDK"
    license = "Apache-2.0"
    url = "https://github.com/couchbase/couchbase-cxx-client"
    homepage = "https://github.com/couchbase/couchbase-cxx-client"
    topics = ("couchbase", "database", "nosql", "sdk")
    package_type = "library"
    exports_sources = "*.patch"
    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def requirements(self):
        # these should match https://github.com/couchbase/couchbase-cxx-client/blob/main/couchbase-sdk-cxx-black-duck-manifest.yaml
        # as best as possible
        self.requires("spdlog/[~1.15.0]")
        self.requires("ms-gsl/4.0.0")
        self.requires("snappy/[~1.2.1]") # 1.2.2 not in conancenter yet
        self.requires("asio/1.31.0") 
        self.requires("hdrhistogram-c/0.11.8")
        self.requires("taocpp-json/1.0.0-beta.14")
        self.requires("llhttp/9.3.0")
        self.requires("openssl/[>=1.1 <4]")
    
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19.0 <4.0]")

    def layout(self):
        cmake_layout(self)

    def validate(self):
        # couchbase-cxx-client requires C++17 or newer
        check_min_cppstd(self, 17)
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()
        # point to our custom ThirdPartyDependencies.cmake that connects to conan dependencies
        # also fix bug in original file where it assumes it will always be building snappy from source
        apply_conandata_patches(self)
    
    def export_sources(self):
        # provide our custom ThirdPartyDependencies.cmake into the cmake folder to use later in patching
        copy(self, "ConanThirdPartyDependencies.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "cmake"))

    def _patch_sources(self):
        # couchbase uses spdlog's bundled fmt rather than having fmt as a separate dependency. 
        # Conancenter does not have a spdlog recipe that includes the bundled fmt lib. 
        # Thus we need to rewrite the code to use the external fmt.
        # there are too many files to patch individually, so do a bulk search/replace
        for root, _, files in os.walk(self.source_folder):
            for file in files:
                if os.path.splitext(file)[1] in (".cxx", ".hxx", ".h"):
                    full_path = os.path.join(root, file)
                    data = load(self, full_path)
                    data = re.sub(r"spdlog/fmt/bundled", "fmt", data)
                    save(self, full_path, data)

    def generate(self):
        deps = CMakeDeps(self)

        # Couchbase uses CPM.cmake to manage dependencies, which expects certain target names.
        # Provide aliases expected by couchbase-cxx-client ThirdPartyDependencies.cmake
        deps.set_property("hdrhistogram-c", "cmake_target_aliases", ["hdr_histogram_static", "hdr_histogram"])
        deps.set_property("snappy", "cmake_target_aliases", ["snappy"])
        deps.set_property("asio", "cmake_target_aliases", ["asio", "asio::asio"])
        deps.set_property("taocpp-json", "cmake_target_aliases", ["taocpp::json", "json"])
        deps.set_property("llhttp", "cmake_target_aliases", ["llhttp::llhttp", "llhttp"])
        deps.set_property("ms-gsl", "cmake_target_aliases", ["Microsoft.GSL::GSL", "gsl"])
        deps.set_property("spdlog", "cmake_target_aliases", ["spdlog::spdlog", "spdlog"])

        deps.generate()

        tc = CMakeToolchain(self)

        tc.variables["COUCHBASE_CXX_CLIENT_COLUMNAR"] = "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_BUILD_TESTS"] = "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_BUILD_EXAMPLES"] =  "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_BUILD_TOOLS"] = "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_BUILD_DOCS"] = "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_INSTALL"] = "ON"
        tc.variables["COUCHBASE_CXX_CLIENT_CLANG_TIDY"] = False

        if self.options.shared:
            tc.variables["COUCHBASE_CXX_CLIENT_BUILD_SHARED"] = "ON"
            tc.variables["COUCHBASE_CXX_CLIENT_BUILD_STATIC"] = "OFF"
        else:
            tc.variables["COUCHBASE_CXX_CLIENT_BUILD_SHARED"] = "OFF"
            tc.variables["COUCHBASE_CXX_CLIENT_BUILD_STATIC"] = "ON"

        tc.variables["COUCHBASE_CXX_CLIENT_STATIC_BORINGSSL"] = "OFF"
        tc.variables["COUCHBASE_CXX_CLIENT_POST_LINKED_OPENSSL"] = "OFF"

        # Ensure CPM finds packages only from Conan
        tc.variables["CPM_LOCAL_PACKAGES_ONLY"] = True

        # Force try_compile checks to use the current single-config build type to avoid looking for missing *_DEBUG imported targets
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)

        tc.generate()

    def validate(self):
        check_min_cppstd(self, 17)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # couchbase has different library names for shared vs static builds
        if self.options.shared:
            self.cpp_info.libs = ["couchbase_cxx_client"]
        else:
            self.cpp_info.libs = ["couchbase_cxx_client_static"]

        # Provide canonical CMake target name for consumers
        self.cpp_info.set_property("cmake_target_name", "couchbase_cxx_client::couchbase_cxx_client")
