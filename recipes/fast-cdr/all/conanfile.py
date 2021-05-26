from conans import ConanFile, CMake, tools
import os
from conans.errors import ConanInvalidConfiguration

class FastCDRConan(ConanFile):

    name = "fast-cdr"
    license = "Apache-2.0"
    homepage = "https://github.com/eProsima/Fast-CDR"
    url = "https://github.com/conan-io/conan-center-index"
    description = "eProsima FastCDR library for serialization"
    topics = ("conan","DDS", "Middleware","Serialization")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":          [True, False],
        "fPIC":            [True, False]
    }
    default_options = {
        "shared":            False,
        "fPIC":              True
    }
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib",
            "cmake"
        )

    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _get_configured_cmake(self):
        if self._cmake:
            pass 
        else:
            self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)
    
    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = self._get_configured_cmake()
        cmake.build()

    def package(self):
        cmake = self._get_configured_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(self._pkg_cmake)
        tools.rmdir(self._pkg_share)
        tools.remove_files_by_mask(
            directory = os.path.join(self.package_folder,"lib"),
            pattern = "*.pdb"
        )
        tools.remove_files_by_mask(
            directory = os.path.join(self.package_folder,"bin"),
            pattern = "*.pdb"
        )
        
    def package_info(self):
        #FIXME: FastCDR does not install under a CMake namespace 
        # https://github.com/eProsima/Fast-CDR/blob/cff6ea98f66d5fd4d53541e183676257a42a6c23/src/cpp/CMakeLists.txt#L156
        self.cpp_info.names["cmake_find_package"] = "fastcdr"
        self.cpp_info.names["cmake_find_package_multi"] = "fastcdr"
        self.cpp_info.libs = tools.collect_libs(self)
