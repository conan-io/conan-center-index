from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class OatppPostgresqlConan(ConanFile):
    name = "oatpp-postgresql"
    license = "Apache-2.0"
    homepage = "https://github.com/oatpp/oatpp-postgresql"
    url = "https://github.com/conan-io/conan-center-index"
    description = "oat++ PostgreSQL library"
    topics = ("oat", "postgresql", "orm", "database")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("oatpp-postgresql can not be built as shared library on Windows")

        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("oatpp-postgresql requires GCC >=5")

    def requirements(self):
        self.requires("oatpp/{}".format(self.version))
        self.requires("libpq/13.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["OATPP_BUILD_TESTS"] = False
        self._cmake.definitions["OATPP_MODULES_LOCATION"] = "INSTALLED"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-postgresql"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-postgresql"
        self.cpp_info.set_property("cmake_file_name", "oatpp-postgresql")
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.set_property("cmake_target_name", "oatpp::oatpp-postgresql")
        self.cpp_info.components["_oatpp-postgresql"].names["cmake_find_package"] = "oatpp-postgresql"
        self.cpp_info.components["_oatpp-postgresql"].names["cmake_find_package_multi"] = "oatpp-postgresql"
        self.cpp_info.components["_oatpp-postgresql"].set_property("cmake_target_name", "oatpp::oatpp-postgresql")
        self.cpp_info.components["_oatpp-postgresql"].includedirs = [
            os.path.join("include", "oatpp-{}".format(self.version), "oatpp-postgresql")
        ]
        self.cpp_info.components["_oatpp-postgresql"].libdirs = [os.path.join("lib", "oatpp-{}".format(self.version))]
        self.cpp_info.components["_oatpp-postgresql"].libs = ["oatpp-postgresql"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_oatpp-postgresql"].system_libs = ["pthread"]
        self.cpp_info.components["_oatpp-postgresql"].requires = ["oatpp::oatpp", "libpq::libpq"]
