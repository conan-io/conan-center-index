import os
import functools
import glob
from conan import ConanFile
from conans import CMake, tools
from conan.tools.files import get, copy
from conan.tools.layout import cmake_layout

from helpers import parse_proto_libraries

class GoogleAPIS(ConanFile):
    name = "googleapis"
    description = "Public interface definitions of Google APIs"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/googleapis/googleapis"
    topics = "google", "protos", "api"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False, 
        "fPIC": True
        }
    exports = "helpers.py"

    def layout(self):
        cmake_layout(self)

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], destination=self.source_folder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires('protobuf/3.21.1')

    def build_requirements(self):
        self.build_requires('protobuf/3.21.1')

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    @functools.lru_cache(1)
    def _parse_proto_libraries(self):
        # Generate the libraries to build dynamically
        proto_libraries = []
        for filename in glob.iglob(os.path.join(self.source_folder, 'google', '**', 'BUILD.bazel'), recursive=True):
            proto_libraries += parse_proto_libraries(filename, self.source_folder, self.output.error)
            
        for filename in glob.iglob(os.path.join(self.source_folder, 'grafeas', '**', 'BUILD.bazel'), recursive=True):
            proto_libraries += parse_proto_libraries(filename, self.source_folder, self.output.error)
            
        # print(json.dumps(proto_libraries, indent=4))
        all_deps = [f"{it.qname}:{it.name}" for it in proto_libraries]
        all_deps += ["protobuf::libprotobuf"]
        for it in proto_libraries:
            self.output.info(it.dumps())
            it.validate(self.source_folder, all_deps)

        return proto_libraries

    def build(self):
        proto_libraries = self._parse_proto_libraries()
        with open(os.path.join(self.source_folder, "CMakeLists.txt"), "a") as f:
            for it in proto_libraries:
                f.write(it.cmake_content)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.proto", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))
        copy(self, pattern="*.pb.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"))
        
        copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))
        copy(self, pattern="*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), symlinks=True)
        copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        proto_libraries = self._parse_proto_libraries()
        self.cpp_info.libs = [it.cmake_target for it in proto_libraries]
