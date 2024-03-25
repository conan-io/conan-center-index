import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import rename, get, rmdir, save, copy, replace_in_file, rm
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.55.0"


class MysqlConnectorCppConan(ConanFile):
    name = "mysql-connector-cpp"
    description = "MySQL database connector for C++ applications"
    license = "GPL-2.0-only WITH Universal-FOSS-exception-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dev.mysql.com/doc/connector-cpp/en/"
    topics = ("mysql", "sql", "connector", "database")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True], # fPIC is required by internal libraries
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "5",
            "clang": "6",
        }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # None of the dependencies are used transitively
        self.requires("libmysqlclient/8.2.0")
        self.requires("lz4/1.9.4")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("rapidjson/cci.20230929")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5")
        self.requires("protobuf/3.21.12")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer")

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        # Unvendor dependencies
        for subdir in ["lz4", "protobuf", "rapidjson", "zlib", "zstd"]:
            rmdir(self, os.path.join(self.source_folder, "cdk", "extra", subdir))
            save(self, os.path.join(self.source_folder, "cdk", "extra", subdir, "CMakeLists.txt"), "")

        # Dependencies are found by conan_deps.cmake, adjust modules accordingly
        for find_module in self.source_path.joinpath("cdk", "cmake").rglob("DepFind*.cmake"):
            if "SSL" not in find_module.name:
                replace_in_file(self, find_module, "if(TARGET ", "if(0) # if(TARGET ", strict=False)
                replace_in_file(self, find_module, "add_ext_targets", "message(TRACE #", strict=False)
        save(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindCompression.cmake"), "")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"),
                        "ext::protoc", "protoc")

        # Buggy and not required for the build
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set_target_properties(${T} PROPERTIES FOLDER "CDK")', "")

        # Link against protobuf instead of protobuf-lite, if necessary
        if not self.dependencies["protobuf"].options.lite:
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "core", "CMakeLists.txt"),
                            "ext::protobuf-lite", "ext::protobuf")
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"),
                            "set(use_full_protobuf ${WITH_TESTS})", "set(use_full_protobuf 1)")

    def generate(self):
        VirtualBuildEnv(self).generate()
        VirtualRunEnv(self).generate(scope="build")

        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_MySQL_CONCPP_INCLUDE"] = os.path.join(self.source_folder, "conan_deps.cmake")
        tc.cache_variables["BUNDLE_DEPENDENCIES"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["STATIC_MSVCRT"] = is_msvc_static_runtime(self)
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["WITH_SSL"] = "system"
        tc.cache_variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libmysqlclient", "cmake_file_name", "MySQL")
        deps.set_property("libmysqlclient", "cmake_target_name", "MySQL::client")
        deps.set_property("lz4", "cmake_target_name", "ext::lz4")
        deps.set_property("protobuf::libprotobuf", "cmake_target_name", "ext::protobuf")
        deps.set_property("protobuf::libprotobuf-lite", "cmake_target_name", "ext::protobuf-lite")
        deps.set_property("rapidjson", "cmake_target_name", "RapidJSON::rapidjson")
        deps.set_property("zlib", "cmake_target_name", "ext::z")
        deps.set_property("zstd", "cmake_target_name", "ext::zstd")
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.package_path.joinpath("lib64").exists():
            rename(self, self.package_path.joinpath("lib64"), self.package_path.joinpath("lib"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        major_ver = Version(self.version).major
        lib = f"mysqlcppconn{major_ver}"
        if not self.options.shared:
            lib += "-static"
        self.cpp_info.libs = [lib]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("dnsapi")
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os != "FreeBSD":
            self.cpp_info.system_libs.append("resolv")
        if self.settings.os == "SunOS":
            self.cpp_info.system_libs.append("socket")
            self.cpp_info.system_libs.append("nsl")
