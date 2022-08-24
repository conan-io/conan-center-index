import os
import functools
import glob
from io import StringIO
from conan import ConanFile
from conans import CMake, tools
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration

from helpers import parse_proto_libraries

class GoogleAPIS(ConanFile):
    name = "googleapis"
    description = "Public interface definitions of Google APIs"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/googleapis/googleapis"
    topics = "google", "protos", "api"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False, 
        "fPIC": True
        }
    exports = "helpers.py"
    short_paths = True

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
            self.options["protobuf"].shared = True

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) <= "5":
            raise ConanInvalidConfiguration("Build with GCC 5 fails")

        if self.settings.compiler in ["Visual Studio", "msvc"] and self.options.shared:
            raise ConanInvalidConfiguration("Source code generated from protos is missing some export macro")
        if self.options.shared and not self.options["protobuf"].shared:
            raise ConanInvalidConfiguration("If built as shared, protobuf must be shared as well. Please, use `protobuf:shared=True`")

    def requirements(self):
        self.requires('protobuf/3.21.4')

    @property
    def _cmake_new_enough(self):
        try:
            import re
            output = StringIO()
            self.run("cmake --version", output=output)
            m = re.search(r'cmake version (\d+)\.(\d+)\.(\d+)', output.getvalue())
            major, minor = int(m.group(1)), int(m.group(2))
            assert major >= 3 and minor >= 20
        except:
            return False
        else:
            return True

    def build_requirements(self):
        self.build_requires('protobuf/3.21.4')
        # CMake >= 3.20 is required. There is a proto with dots in the name 'k8s.min.proto' and CMake fails to generate project files
        if not self._cmake_new_enough:
            self.build_requires('cmake/3.23.2')

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
            
        # Validate that all files exist and all dependencies are found
        all_deps = [f"{it.qname}:{it.name}" for it in proto_libraries]
        all_deps += ["protobuf::libprotobuf"]
        for it in proto_libraries:
            it.validate(self.source_folder, all_deps)

        # Mark the libraries we need recursively (C++ context)
        all_dict = {f"{it.qname}:{it.name}": it for it in proto_libraries}
        def activate_library(proto_library):
            proto_library.is_used = True
            for it_dep in proto_library.deps:
                if it_dep == "protobuf::libprotobuf":
                    continue
                activate_library(all_dict[it_dep])
            
        for it in filter(lambda u: u.is_used, proto_libraries):
            activate_library(it)

        # Tweaks
        def deactivate_library(key):
            if key in all_dict:
                all_dict[key].is_used = False
        #  - Inconvenient macro names from usr/include/sys/syslimits.h in some macOS SDKs: GID_MAX
        #    Patched here: https://github.com/protocolbuffers/protobuf/commit/f138d5de2535eb7dd7c8d0ad5eb16d128ab221fd
        #    as of 3.21.4 issue still exist
        if tools.Version(self.deps_cpp_info["protobuf"].version) <= "3.21.5" and self.settings.os == "Macos":
            deactivate_library("//google/storagetransfer/v1:storagetransfer_proto")
        #  - Inconvenient macro names from /usr/include/math.h : DOMAIN
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++") or \
            self.settings.compiler in ["Visual Studio", "msvc"]:
            deactivate_library("//google/cloud/channel/v1:channel_proto")
            deactivate_library("//google/cloud/channel/v1:channel_cc_proto")

        return proto_libraries

    def build(self):
        proto_libraries = self._parse_proto_libraries()
        with open(os.path.join(self.source_folder, "CMakeLists.txt"), "a", encoding="utf-8") as f:
            for it in filter(lambda u: u.is_used, proto_libraries):
                f.write(it.cmake_content)
        cmake = self._configure_cmake()
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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m"])
