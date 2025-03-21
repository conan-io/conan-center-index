import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import replace_in_file


class libksRecipe(ConanFile):
    name = "libks2"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    author = "SignalWire sales@signalwire.com"
    url = "https://github.com/signalwire/libks"
    description = "Foundational support for signalwire C products"
    topics = ("libraries", "c")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe

    def source(self):
        git = Git(self)
        git.clone("https://github.com/signalwire/libks.git", ".", args=["--branch", self.conan_data["sources"][self.version]["branch"]])
        # This replacements make sure the changelog file (and the compressed file) are created in the CMAKE_BINARY_DIR, the original file has a mix of the current directory and the CMAKE_BINARY_DIR
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'file(WRITE changelog.Debian ${CHANGELOG_HEADER}\\n${CHANGELOG}\\n\\n${CHANGELOG_FOOTER})', 'file(WRITE ${CMAKE_BINARY_DIR}/changelog.Debian ${CHANGELOG_HEADER}\\n${CHANGELOG}\\n\\n${CHANGELOG_FOOTER})')
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'execute_process(COMMAND ${GZIP_CMD} -f -9 -n changelog.Debian)', 'execute_process(COMMAND ${GZIP_CMD} -f -9 -n ${CMAKE_BINARY_DIR}/changelog.Debian)')

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    # def requirements(self):
    #     self.requires("util-linux-libuuid/2.39.2")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ks2"]
        self.cpp_info.includedirs = ["include/libks2"]
