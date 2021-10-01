import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class BRPCCppConan(ConanFile):
    name = "brpc"
    description = "Industrial-grade RPC framework used throughout Baidu, with 1,000,000+ instances and thousands kinds of services. `brpc` means `better RPC`."
    url = "https://github.com/apache/incubator-brpc"
    homepage = "https://brpc.apache.org/"
    topics = ("conan", "bprc", "apache", "baidu", "rpc")
    license = ("Apache License 2.0",)
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("bprc not supported Windows.")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("gflags/2.2.2")
        self.requires("leveldb/1.22")
        self.requires("protobuf/3.17.1")

    def build_requirements(self):
        self.build_requires("gflags/2.2.2")
        self.build_requires("leveldb/1.22")
        self.build_requires("protobuf/3.17.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "incubator-"+self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_source(self):
       cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
       tools.replace_in_file(cmake_path,
                    ("find_package(GFLAGS REQUIRED)"), "find_package(gflags REQUIRED)") 
       tools.replace_in_file(cmake_path,
                    ("GFLAGS_INCLUDE_PATH"), "gflags_INCLUDE_DIR") 
       tools.replace_in_file(cmake_path,
                    ("GFLAGS_LIBRARY"), "gflags_LIBS") 
       tools.replace_in_file(cmake_path,
                    ("PROTOBUF_INCLUDE"), "protobuf_INCLUDE") 
       tools.replace_in_file(cmake_path,
                    ("PROTOBUF_LIBRARIES"), "protobuf_LIBS") 
       tools.replace_in_file(cmake_path,
                    ("set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)"), "set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake)") 

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_source()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread"]
