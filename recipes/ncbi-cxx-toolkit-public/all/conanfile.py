from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import get, copy, rmdir, save, load, apply_conandata_patches, export_conandata_patches
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
import os
import yaml

required_conan_version = ">=2.1.0"


class NcbiCxxToolkit(ConanFile):
    name = "ncbi-cxx-toolkit-public"
    description = ("NCBI C++ Toolkit -- a cross-platform application framework and "
                   "a collection of libraries for working with biological data.")
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ncbi.github.io/cxx-toolkit"
    topics = ("ncbi", "biotechnology", "bioinformatics", "genbank", "gene",
              "genome", "genetic", "sequence", "alignment", "blast",
              "biological", "toolkit", "c++")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_grpc": [True, False],
        "with_xml": [True, False],
        "with_image": [True, False],
        "with_berkeleydb": [True, False],
        "with_cassandra": [True, False],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_grpc": False,
        "with_xml": False,
        "with_image": False,
        "with_berkeleydb": False,
        "with_cassandra": False,
        "with_curl": False,
    }

    def export(self):
        copy(self, "components.yml",
             src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.rm_safe("with_berkeleydb")
        if self.settings.os in ["Windows", "Macos"]:
            self.options.rm_safe("with_cassandra")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("bzip2/1.0.8")
        self.requires("lzo/2.10")
        self.requires("zstd/[>=1.5.2 <1.6]")
        self.requires("pcre2/[>=10.42 <11]")
        self.requires("libuv/[>=1.45.0 <2]")
        self.requires("libnghttp2/[>=1.66.0 <2]")
        self.requires("libiconv/[>=1.17 <2]")
        self.requires("lmdb/[>=0.9.29 <1]")
        self.requires("sqlite3/[>=3.44.2 <4]")
        if self.settings.os == "Linux":
            self.requires("backward-cpp/[>=1.6 <2]")
            self.requires("libunwind/[>=1.6.2 <2]")
        if self.options.with_grpc:
            self.requires("grpc/[>=1.54.3 <2]")
            self.requires("protobuf/[>=3.21.12 <7]")
        if self.options.with_xml:
            self.requires("libxml2/[>=2.12.5 <3]")
            self.requires("libxslt/[>=1.1.43 <2]")
        if self.options.with_image:
            self.requires("libjpeg/[>=9e]")
            self.requires("libpng/[>=1.6 <2]")
            self.requires("giflib/[>=5.2.1 <6]")
            self.requires("libtiff/[>=4.6.0 <5]")
        if self.options.get_safe("with_berkeleydb"):
            self.requires("libdb/5.3.28")
        if self.options.get_safe("with_cassandra"):
            self.requires("cassandra-cpp-driver/[>=2.15.3 <=2.17.1]")
        if self.options.with_curl:
            self.requires("libcurl/[>=8.8.0 <9]")

    def build_requirements(self):
        if self.options.with_grpc:
            self.tool_requires("protobuf/<host_version>")
            self.tool_requires("grpc/<host_version>")

    def validate(self):
        check_min_cppstd(self, 20)
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration("This operating system is not supported")
        if is_msvc(self):
            check_min_vs(self, 192)
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross compilation is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NCBI_PTBCFG_PACKAGING"] = True
        tc.variables["NCBI_PTBCFG_PROJECT_LIST"] = "-app/netcache"
        if is_msvc(self):
            tc.variables["NCBI_PTBCFG_CONFIGURATION_TYPES"] = self.settings.build_type
        tc.variables["NCBI_PTBCFG_PROJECT_TAGS"] = "-demo;-sample"
        disabled_cmake = []
        if not self.options.with_grpc:
            disabled_cmake.append("GRPC")
        if not self.options.with_xml:
            disabled_cmake.extend(["XML", "XSLT"])
        if not self.options.with_image:
            disabled_cmake.extend(["JPEG", "PNG", "GIF", "TIFF"])
        if not self.options.get_safe("with_berkeleydb"):
            disabled_cmake.append("BerkeleyDB")
        if not self.options.get_safe("with_cassandra"):
            disabled_cmake.append("CASSANDRA")
        if not self.options.with_curl:
            disabled_cmake.append("CURL")
        if disabled_cmake:
            tc.variables["NCBI_PTBCFG_PROJECT_COMPONENTS"] = "-" + ";-".join(disabled_cmake)
        tc.generate()
        CMakeDeps(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "src", "build-system", "cmake", "modules"))
        save(self, os.path.join(self.source_folder, "CMakeLists.txt"),
             "cmake_minimum_required(VERSION 3.15)\n"
             "project(ncbi_cpp)\n"
             "include(src/build-system/cmake/CMake.NCBItoolkit.cmake)\n"
             "add_subdirectory(src)\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def _available_targets(self):
        targets = {"zlib::zlib", "bzip2::bzip2", "lzo::lzo", "zstd::zstd",
                   "pcre2::pcre2", "libuv::libuv", "libnghttp2::libnghttp2",
                   "libiconv::libiconv", "lmdb::lmdb", "sqlite3::sqlite3"}
        if self.settings.os == "Linux":
            targets.update(["backward-cpp::backward-cpp", "libunwind::libunwind"])
        if self.options.with_grpc:
            targets.update(["grpc::grpc", "protobuf::protobuf"])
        if self.options.with_xml:
            targets.update(["libxml2::libxml2", "libxslt::libxslt"])
        if self.options.with_image:
            targets.update(["libjpeg::libjpeg", "libpng::libpng",
                            "giflib::giflib", "libtiff::libtiff"])
        if self.options.get_safe("with_berkeleydb"):
            targets.add("libdb::libdb")
        if self.options.get_safe("with_cassandra"):
            targets.add("cassandra-cpp-driver::cassandra-cpp-driver")
        if self.options.with_curl:
            targets.add("libcurl::libcurl")
        return targets

    def package_info(self):
        impfile = os.path.join(self.package_folder, "res", "ncbi-cpp-toolkit.imports")
        allexports = set(load(self, impfile).split())
        components = yaml.safe_load(load(self, os.path.join(self.recipe_folder, "components.yml")))["components"]

        available = self._available_targets()
        active = {}
        for comp_name, comp_data in components.items():
            c_libs = [lib for lib in comp_data["libraries"] if lib in allexports]
            if c_libs or comp_name == "core":
                active[comp_name] = (c_libs, comp_data)

        for comp_name, (c_libs, comp_data) in active.items():
            c_reqs = [d for d in comp_data["dependencies"] if d in active]
            for ext_req in comp_data.get("requires", []):
                if ext_req in available:
                    c_reqs.append(ext_req)
            self.cpp_info.components[comp_name].libs = c_libs
            self.cpp_info.components[comp_name].requires = c_reqs

        if self.settings.os == "Windows":
            self.cpp_info.components["core"].defines.append("_UNICODE")
            self.cpp_info.components["core"].system_libs = ["ws2_32", "dbghelp"]
        elif self.settings.os == "Linux":
            self.cpp_info.components["core"].defines.extend(["_MT", "_FILE_OFFSET_BITS=64"])
            self.cpp_info.components["core"].system_libs = ["dl", "rt", "m", "pthread", "resolv"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["core"].defines.extend(["_MT", "_FILE_OFFSET_BITS=64"])
            self.cpp_info.components["core"].system_libs = ["dl", "c", "m", "pthread", "resolv"]
            self.cpp_info.components["core"].frameworks = ["ApplicationServices"]
        if self.options.shared:
            self.cpp_info.components["core"].defines.append("NCBI_DLL_BUILD")

        self.cpp_info.components["core"].builddirs.append("res")
