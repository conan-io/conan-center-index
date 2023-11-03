from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class ZookeeperClientCConan(ConanFile):
    name = "zookeeper-client-c"
    description = "ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zookeeper.apache.org/"
    topics = ("zookeeper", "client")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "static-library"
    options = {
        "fPIC": [True, False],
        "with_cyrus_sasl": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_cyrus_sasl": False,
        "with_openssl": False,
    }
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.27")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def build_requirements(self):
        self.tool_requires("maven/3.9.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WANT_CPPUNIT"] = False
        tc.variables["WITH_CYRUS_SASL"] = "ON" if self.options.with_cyrus_sasl else "OFF"
        tc.variables["WITH_OPENSSL"] = "ON" if self.options.with_openssl else "OFF"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        bvenv = VirtualBuildEnv(self)
        bvenv.generate()

    def build(self):
        apply_conandata_patches(self)

        # We have to install maven to generate jute files which are required by zookeeper-client
        self.run("mvn compile", cwd=os.path.join(self.source_folder, "zookeeper-jute"))

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "zookeeper-client", "zookeeper-client-c"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "zookeeper-client", "zookeeper-client-c")
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["zookeeper", "hashtable"]
        self.cpp_info.defines.append("USE_STATIC_LIB")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["rt", "pthread", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["wsock32", "ws2_32", ])
