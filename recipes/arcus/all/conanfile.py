from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0"


class ArcusConan(ConanFile):
    name = "arcus"
    description = "This library contains C++ code and Python3 bindings for " \
                  "creating a socket in a thread and using this socket to send " \
                  "and receive messages based on the Protocol Buffers library."
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Ultimaker/libArcus"
    topics = ("protobuf", "socket", "cura")

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
        self.requires("protobuf/[>=4.25.0 <7]")
        self.requires("abseil/[*]")
        self.tool_requires("cmake/[>=3.23]")

    def validate(self):
        # Newer versions of protobuf require higher versions of C++ than arcus itself
        protobuf_version = Version(self.dependencies["protobuf"].ref.version)
        protobuf_release = Version(f"{protobuf_version.minor}.{protobuf_version.patch}")
        min_cpp_std = 17 if protobuf_release >= Version("30.1") else 14
        check_min_cppstd(self, min_cpp_std)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PYTHON"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        if is_msvc(self):
            tc.cache_variables["MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Arcus")
        self.cpp_info.set_property("cmake_target_name", "Arcus")
        self.cpp_info.libs = ["Arcus"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
