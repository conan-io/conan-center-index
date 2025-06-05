import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import replace_in_file, get, rmdir, copy
from conan.tools.apple import is_apple_os
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfigDeps


class LibksConan(ConanFile):
    name = "libks"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalwire/libks"
    license = "MIT"
    description = "Foundational support for signalwire C products"
    topics = ("libraries", "c")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True
    }

    implements = ["auto_shared_fpic"]

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # libks2/libks/ks_ssl.h:25:10: fatal error: openssl/ssl.h: No such file or directory
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            # libks2/libks/ks_types.h:163:18: fatal error: uuid/uuid.h: No such file or directory
            self.requires("util-linux-libuuid/2.39.2", transitive_headers=True)

    def validate(self):
        if is_apple_os(self):
            raise ConanInvalidConfiguration("This is not apple compatible, https://github.com/signalwire/libks/issues/204")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows do not use CMake")

    def generate(self):
        deps = CMakeDeps(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            deps.set_property("util-linux-libuuid", "cmake_target_name", "LIBUUID::LIBUUID")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'include(cmake/FindUUID.cmake)',
                        'find_package(libuuid CONFIG REQUIRED)') # Use conan to find uuid
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'add_subdirectory(tests)',
                        '') # Do not build tests
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'if("${CMAKE_OS_NAME}" STREQUAL "Debian")',
                        'if(FALSE)') # Do not generate .deb
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "include", "libks2", "libks", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["ks2"]
        self.cpp_info.includedirs = ["include/libks2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
