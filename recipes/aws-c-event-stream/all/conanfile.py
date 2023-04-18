from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"

class AwsCEventStream(ConanFile):
    name = "aws-c-event-stream"
    description = "C99 implementation of the vnd.amazon.eventstream content-type"
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-event-stream"
    topics = ("aws", "eventstream", "content", )
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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-checksums/0.1.13")
        self.requires("aws-c-common/0.8.2")
        if Version(self.version) >= "0.2":
            if Version(self.version) < "0.2.11":
                self.requires("aws-c-io/0.10.20")
            else:
                self.requires("aws-c-io/0.13.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BINARIES"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-event-stream"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-event-stream")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-event-stream")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["aws-c-event-stream-lib"].libs = ["aws-c-event-stream"]
        if self.options.shared:
            self.cpp_info.components["aws-c-event-stream-lib"].defines.append("AWS_EVENT_STREAM_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-event-stream"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-event-stream"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-event-stream-lib"].names["cmake_find_package"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-event-stream-lib"].names["cmake_find_package_multi"] = "aws-c-event-stream"
        self.cpp_info.components["aws-c-event-stream-lib"].set_property("cmake_target_name", "AWS::aws-c-event-stream")
        self.cpp_info.components["aws-c-event-stream-lib"].requires = ["aws-c-common::aws-c-common", "aws-checksums::aws-checksums"]
        if Version(self.version) >= "0.2":
            self.cpp_info.components["aws-c-event-stream-lib"].requires.append("aws-c-io::aws-c-io")
