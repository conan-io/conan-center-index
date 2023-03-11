import os
import functools
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, collect_libs, copy

from helpers import parse_proto_libraries


class GRPCProto(ConanFile):
    name = "grpc-proto"
    package_type = "library"
    description = "gRPC-defined protobufs for peripheral services such as health checking, load balancing, etc"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc-proto"
    topics = "google", "protos", "api"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True
        }
    exports = "helpers.py"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], destination=self.source_folder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["protobuf"].shared = True
            self.options["googleapis"].shared = True

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        if self.options.shared and (not self.dependencies["protobuf"].options.shared or not self.dependencies["googleapis"].options.shared):
            raise ConanInvalidConfiguration("If built as shared, protobuf and googleapis must be shared as well. Please, use `protobuf:shared=True` and `googleapis:shared=True`")

    def generate(self):
        tc = CMakeToolchain(self)
        googleapis_resdirs = self.dependencies["googleapis"].cpp_info.aggregated_components().resdirs
        tc.cache_variables["GOOGLEAPIS_PROTO_DIRS"] = ";".join([p.replace("\\", "/") for p in googleapis_resdirs])
        tc.generate()

    def requirements(self):
        self.requires('protobuf/3.21.4', transitive_headers=True)
        self.requires('googleapis/cci.20221108')

    def build_requirements(self):
        self.build_requires('protobuf/3.21.4')

    @functools.lru_cache(1)
    def _parse_proto_libraries(self):
        # Generate the libraries to build dynamically
        proto_libraries = parse_proto_libraries(os.path.join(self.source_folder, 'BUILD.bazel'), self.source_folder, self.output.error)

        # Validate that all files exist and all dependencies are found
        all_deps = [it.cmake_target for it in proto_libraries]
        all_deps += ["googleapis::googleapis", "protobuf::libprotobuf"]
        for it in proto_libraries:
            it.validate(self.source_folder, all_deps)

        # Mark the libraries we need recursively (C++ context)
        all_dict = {it.cmake_target: it for it in proto_libraries}
        def activate_library(proto_library):
            proto_library.is_used = True
            for it_dep in proto_library.deps:
                if it_dep in ["googleapis::googleapis", "protobuf::libprotobuf"]:
                    continue
                activate_library(all_dict[it_dep])

        for it in filter(lambda u: u.is_used, proto_libraries):
            activate_library(it)

        return proto_libraries

    def build(self):
        proto_libraries = self._parse_proto_libraries()
        with open(os.path.join(self.source_folder, "CMakeLists.txt"), "a", encoding="utf-8") as f:
            for it in filter(lambda u: u.is_used, proto_libraries):
                f.write(it.cmake_content)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.proto", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))
        copy(self, pattern="*.pb.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"))

        copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_id(self):
        self.info.requires["protobuf"].full_package_mode()

    def package_info(self):
        # We are not creating components, we can just collect the libraries
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.resdirs = ["res"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m"])
