import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Git

required_conan_version = ">=2.12.2"

class NuRaftConan(ConanFile):
    # Metadata
    name = "nuraft"
    package_type = "library"
    license = "Apache-2.0"
    description = "RAFT protocol library."
    homepage = "https://github.com/ebay/NuRaft.git"

    # generators = "CMakeDeps"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False], 
        "fPIC": [True, False],                
        "coverage": [True, False], 
        "boost_asio":[True, False],
        "build_tests": [True, False],
        "build_examples": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True, 
        "coverage": False, 
        "boost_asio": True, 
        "build_tests": True, 
        "build_examples":True
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.boost_asio:
            self.requires("boost/[>=1.8.0]")
        else:
            self.requires("asio/[>=1.22.0]")

        self.requires("openssl/[~3]")

    def layout(self):
        cmake_layout(self, generator="CMakeDeps")
        self.cpp.package.libs = [f"lib{self.name}.so" if self.options.shared else f"lib{self.name}.a"]

        # For “editable” packages, self.cpp.source describes the artifacts under self.source_folder.
        self.cpp.source.includedirs = ["include", "include/libnuraft"]

        hash = Git(self).get_commit()
        self.cpp.package.defines = self.cpp.build.defines = ["_RAFT_COMMIT_HASH=%s" % hash]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_CONAN"] = True
        tc.variables["CONAN_BUILD_COVERAGE"] = False

        tc.variables["CODE_COVERAGE"] = self.options.coverage
        tc.variables["BOOST_ASIO"] = self.options.boost_asio
        tc.variables["BUILD_TESTING"] = self.options.build_tests
        tc.variables["BUILD_EXAMPLES"] = self.options.build_examples
        tc.variables["ENABLE_RAFT_STATS"] = True


        tc.variables["CMAKE_EXPORT_COMPILE_COMMANDS"] = True
        tc.generate()

        deps=CMakeDeps(self)
        # deps.build_context_activated = ["boost", "openssl"]
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self.options.build_tests:
            cmake.ctest()
        copy(self, "compile_commands.json", self.build_folder, self.source_folder, keep_path=False)


    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
