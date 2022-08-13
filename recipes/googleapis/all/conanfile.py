from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import glob
from io import StringIO

from helpers import parse_proto_libraries

required_conan_version = ">=1.50.0"


class GoogleAPISConan(ConanFile):
    name = "googleapis"
    description = "Public interface definitions of Google APIs"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/googleapis/googleapis"
    topics = "google", "protos", "api"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports = "helpers.py"
    exports_sources = "CMakeLists.txt"
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            self.options["protobuf"].shared = True

    def requirements(self):
        self.requires("protobuf/3.21.1")

    def package_id(self):
        self.info.requires["protobuf"].full_package_mode()

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) <= "5":
            raise ConanInvalidConfiguration("Build with GCC 5 fails")

        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration("Source code generated from protos is missing some export macro")
        if self.info.options.shared and not self.dependencies.host["protobuf"].options["shared"]:
            raise ConanInvalidConfiguration("If built as shared, protobuf must be shared as well. Please, use `protobuf:shared=True`")

    @property
    def _cmake_new_enough(self):
        try:
            import re
            output = StringIO()
            self.run("cmake --version", output=output)
            m = re.search(r'cmake version (\d+)\.(\d+)\.(\d+)', output.getvalue())
            major, minor = int(m.group(1)), int(m.group(2))
            assert (major == 3 and minor >= 20) or major >= 4
        except:
            return False
        else:
            return True

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.1")
        # CMake >= 3.20 is required. There is a proto with dots in the name 'k8s.min.proto' and CMake fails to generate project files
        if not self._cmake_new_enough:
            self.tool_requires("cmake/3.23.2")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()
        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

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
        if Version(self.deps_cpp_info["protobuf"].version) <= "3.21.2" and self.settings.os == "Macos":
            deactivate_library("//google/storagetransfer/v1:storagetransfer_proto")
        #  - Inconvenient macro names from /usr/include/math.h : DOMAIN
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++") or \
            is_msvc(self):
            deactivate_library("//google/cloud/channel/v1:channel_proto")
            deactivate_library("//google/cloud/channel/v1:channel_cc_proto")

        return proto_libraries

    def _populate_cmakelists_from_bazel(self, cmakelists):
        content = ""
        proto_libraries = self._parse_proto_libraries()
        for it in filter(lambda u: u.is_used, proto_libraries):
            content += it.cmake_content
        save(self, cmakelists, content, append=True)

    def build(self):
        cmakelists_folder = os.path.join(self.source_folder, os.pardir)
        self._populate_cmakelists_from_bazel(os.path.join(cmakelists_folder, "CMakeLists.txt"))
        cmake = CMake(self)
        cmake.configure(build_script_folder=cmakelists_folder)
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

    def package_info(self):
        # We are not creating components, we can just collect the libraries
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])

        # TODO: remove this block if required_conan_version changed to 1.51.1 or higher
        #       (see https://github.com/conan-io/conan/pull/11790)
        self.cpp_info.requires = ["protobuf::protobuf"]
