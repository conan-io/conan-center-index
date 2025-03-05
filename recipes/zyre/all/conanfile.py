import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class ZyreConan(ConanFile):
    name = "zyre"
    description = "Local Area Clustering for Peer-to-Peer Applications."
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/zyre"
    topics = ("czmq", "zmq", "zeromq", "message-queue", "asynchronous")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "drafts": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "drafts": False,
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
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("czmq/4.2.1", transitive_headers=True)
        self.requires("zeromq/4.3.5")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libsystemd/255")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_DRAFTS"] = self.options.drafts
        tc.variables["ZYRE_BUILD_SHARED"] = self.options.shared
        tc.variables["ZYRE_BUILD_STATIC"] = not self.options.shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        if not self.options.shared:
            tc.preprocessor_definitions["ZYRE_STATIC"] = ""
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("zeromq", "cmake_file_name", "LIBZMQ")
        deps.set_property("czmq", "cmake_file_name", "CZMQ")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_package(libzmq REQUIRED)", "find_package(LIBZMQ REQUIRED CONFIG)")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_package(czmq REQUIRED)", "find_package(CZMQ REQUIRED CONFIG)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zyre")
        self.cpp_info.set_property("cmake_target_name", "zyre" if self.options.shared else "zyre-static")
        self.cpp_info.set_property("pkg_config_name", "libzyre")

        libname = "zyre"
        if is_msvc(self) and not self.options.shared:
            libname = "libzyre"
        self.cpp_info.libs = [libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.defines = ["ZYRE_STATIC"]
