import os
import glob
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class RTTRConan(ConanFile):
    name = "rttr"
    description = "Run Time Type Reflection library"   
    topics = ("conan", "reflection", "rttr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rttrorg/rttr"
    license = "MIT"

    exports_sources = "CMakeLists.txt", "patches/*.patch",
    generators = "cmake",

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtti": False,
    }

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        
        cmake.definitions["BUILD_DOCUMENTATION"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        cmake.definitions["BUILD_WITH_RTTI"] = self.options.with_rtti
        cmake.definitions["BUILD_PACKAGE"] = False

        if self.options.shared:
            cmake.definitions["BUILD_RTTR_DYNAMIC"] = True
            cmake.definitions["BUILD_STATIC"] = False
        else:
            cmake.definitions["BUILD_STATIC"] = True
            cmake.definitions["BUILD_RTTR_DYNAMIC"] = False

        cmake.configure()
        
        return cmake

    def _patch_sources(self):
        tools.patch(patch_file="patches/001_fix_build_without_RTTI.patch", base_path=self._source_subfolder)
        tools.patch(patch_file="patches/002_fix_license_installer.patch", base_path=self._source_subfolder)

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        pdb_files = glob.glob(os.path.join(self.package_folder, 'bin', '*.pdb'), recursive=True)
        for pdb in pdb_files:
            os.unlink(pdb)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])