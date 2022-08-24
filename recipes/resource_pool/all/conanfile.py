from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
from conans.tools import check_min_cppstd
import os
import glob


class ResourcePool(ConanFile):
    name = "resource_pool"
    description = "C++ header only library purposed to create pool of some resources like keepalive connections"
    topics = ("conan", "resource pool", "resource_pool", "asio", "elsid", "c++17", "cpp17")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/elsid/resource_pool"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    requires = (
        "boost/1.75.0"
    )
    generators = "cmake_find_package"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warn("resource_pool requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("resource_pool requires a compiler that supports at least C++17")

    def validate(self):
        self._validate_compiler_settings()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst=os.path.join("include", "yamail"), src=os.path.join(self._source_subfolder, "include", "yamail"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        main_comp = self.cpp_info.components["_resource_pool"]
        main_comp.requires = ["boost::boost", "boost::system", "boost::thread"]
        main_comp.defines = ["BOOST_ASIO_USE_TS_EXECUTOR_AS_DEFAULT"]
        main_comp.names["cmake_find_package"] = "resource_pool"
        main_comp.names["cmake_find_package_multi"] = "resource_pool"

        if self.settings.os == "Windows":
            main_comp.system_libs.append("ws2_32")

        # Set up for compatibility with existing cmake configuration
        self.cpp_info.filenames["cmake_find_package"] = "resource_pool"
        self.cpp_info.filenames["cmake_find_package_multi"] = "resource_pool"
        self.cpp_info.names["cmake_find_package"] = "elsid"
        self.cpp_info.names["cmake_find_package_multi"] = "elsid"
