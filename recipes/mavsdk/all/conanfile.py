import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class MavsdkConan(ConanFile):
    name = "mavsdk"
    description = "C++ library to interface with MAVLink systems"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mavsdk.mavlink.io/"
    topics = ("mavlink", "drones")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "regenerate_protobuf": [True, False],
        "build_server": [True, False],
        "enable_reflection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "regenerate_protobuf": False,
        "build_server": False,
        "enable_reflection": False,
    }
    implements = ["auto_shared_fpic"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.build_server:
            # The .proto files were processed with protobuf v4, which is not compatible with
            # the gRPC protobuf version on CCI, so we need to regenerate them.
            del self.options.regenerate_protobuf
        else:
            del self.options.enable_reflection

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("mavlink/1.0.12.cci.20240530", transitive_headers=True)
        self.requires("jsoncpp/1.9.6")
        self.requires("tinyxml2/10.0.0")
        self.requires("libcurl/[>=7.86 <9]")
        self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.build_server:
            self.requires("grpc/1.67.1")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        if self.options.get_safe("regenerate_protobuf", True):
            if self.options.build_server:
                self.tool_requires("grpc/<host_version>")
                self.tool_requires("protobuf/<host_version>")
            else:
                self.tool_requires("grpc/1.67.1")
                self.tool_requires("protobuf/5.27.0")
            if self.settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["proto"], strip_root=True, destination="proto")
        # Let Conan handle the C++ standard
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 17)", "")
        # Fix version string for SOVERSION, since it cannot be derived from a git tag.
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(VERSION_STR "0.0.0")',
                        f'set(VERSION_STR "v{self.version}")')

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) <= "2.13.0":
            tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["SUPERBUILD"] = False
        tc.cache_variables["MAVLINK_DIALECT"] = self.dependencies["mavlink"].options.dialect
        tc.cache_variables["BUILD_MAVSDK_SERVER"] = self.options.build_server
        tc.cache_variables["BUILD_WITH_PROTO_REFLECTION"] = self.options.get_safe("enable_reflection", False)
        # The project uses CMake policy version < 3.12 in several places
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if self.options.get_safe("regenerate_protobuf", True):
            # No need to re-generate Jinja templates
            replace_in_file(self, os.path.join(self.source_folder, "tools", "generate_from_protos.sh"),
                            "python3 ${script_dir}/grpc_server_jinja.py",
                            "# python3 ${script_dir}/grpc_server_jinja.py")
            self.run(f"tools/generate_from_protos.sh -b {self.build_folder}", cwd=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MAVSDK")

        postfix = ""
        if is_msvc(self) and self.settings.build_type == "Debug":
            postfix = "d"

        mavsdk = self.cpp_info.components["mavsdk"]
        mavsdk.set_property("cmake_target_name", "MAVSDK::mavsdk")
        mavsdk.set_property("pkg_config_name", "mavsdk")
        mavsdk.libs = ["mavsdk" + postfix]
        mavsdk.includedirs.append(os.path.join("include", "mavsdk"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            mavsdk.system_libs = ["m", "pthread", "dl"]
        elif self.settings.os == "Windows":
            mavsdk.system_libs = ["ws2_32"]
        elif self.settings.os == "iOS":
            mavsdk.frameworks = ["Foundation", "Security"]
        elif self.settings.os == "Android":
            mavsdk.system_libs = ["log"]
        if str(self.settings.compiler.libcxx) in ["libstdc++", "libstdc++11"] or str(self.settings.arch).startswith("arm"):
            mavsdk.system_libs.append("atomic")
        mavsdk.requires = [
            "mavlink::mavlink",
            "jsoncpp::jsoncpp",
            "tinyxml2::tinyxml2",
            "libcurl::libcurl",
            "xz_utils::xz_utils",
        ]

        if self.options.build_server:
            mavsdk_server = self.cpp_info.components["mavsdk_server"]
            mavsdk_server.set_property("cmake_target_name", "MAVSDK::mavsdk_server")
            mavsdk_server.set_property("pkg_config_name", "mavsdk_server")
            mavsdk_server.libs = ["mavsdk_server"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                mavsdk_server.system_libs = ["dl"]
            if str(self.settings.compiler.libcxx) in ["libstdc++", "libstdc++11"] or str(self.settings.arch).startswith("arm"):
                mavsdk_server.system_libs.append("atomic")
            mavsdk_server.requires = ["grpc::grpc++"]
            if self.options.enable_reflection:
                mavsdk_server.requires.append("grpc::grpc++_reflection")
