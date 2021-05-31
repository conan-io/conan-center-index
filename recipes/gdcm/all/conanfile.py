from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class GDCMConan(ConanFile):
    name = "gdcm"
    topics = ("dicom", "images")
    homepage = "http://gdcm.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    description = "C++ library for DICOM medical files"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["GDCM_BUILD_DOCBOOK_MANPAGES"] = "OFF"
        self._cmake.definitions["GDCM_BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        self._cmake.definitions["GDCM_USE_SYSTEM_ZLIB"] = "ON"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows":
            bin_dir = os.path.join(self.package_folder, "bin")
            tools.remove_files_by_mask(bin_dir, "[!gs]*.dll")
        lib_dir = os.path.join(self.package_folder, "lib")
        tools.rmdir(os.path.join(lib_dir, "gdcmopenjpeg-2.3"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(lib_dir, self._gdcm_subdir), "GDCMTargets*.cmake")
        self._create_cmake_aliases(os.path.join(lib_dir, self._gdcm_subdir, "GDCMTargets.cmake"), self._gdcm_libraries)

    @staticmethod
    def _create_cmake_aliases(targets_file, libraries):
        content = "\n".join([f"""if(TARGET GDCM::{l} AND NOT TARGET {l})
  add_library({l} INTERFACE IMPORTED)
  set_property(TARGET {l} PROPERTY INTERFACE_LINK_LIBRARIES GDCM::{l})
endif()""" for l in libraries])
        tools.save(targets_file, content)

    @property 
    def _gdcm_subdir(self):
        v = tools.Version(self.version)
        return f"gdcm-{v.major}.{v.minor}"

    @property
    def _gdcm_config_cmake_path(self):
        return os.path.join("lib", self._gdcm_subdir, "GDCMConfig.cmake")

    @property
    def _gdcm_libraries(self):
        gdcm_libs = ["gdcmcharls",
                     "gdcmCommon",
                     "gdcmDICT",
                     "gdcmDSED",
                     "gdcmexpat",
                     "gdcmIOD",
                     "gdcmjpeg12",
                     "gdcmjpeg16",
                     "gdcmjpeg8",
                     "gdcmMEXD",
                     "gdcmMSFF",
                     "gdcmopenjp2",
                     "socketxx"]
        if self.settings.os == "Windows":
            gdcm_libs.append("gdcmgetopt")
        else:
            gdcm_libs.append("gdcmuuid")
        return gdcm_libs

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GDCM"
        self.cpp_info.names["cmake_find_multi_package"] = "GDCM"
        gdcm_libs = self._gdcm_libraries
        self.cpp_info.components["headers"].includedirs = [os.path.join("include", self._gdcm_subdir)]
        self.cpp_info.components["headers"].build_modules["cmake"] = [self._gdcm_config_cmake_path]
        self.cpp_info.components["headers"].build_modules["cmake_find_package"] = [self._gdcm_config_cmake_path]
        self.cpp_info.components["headers"].build_modules["cmake_find_multi_package"] = [self._gdcm_config_cmake_path]
        for lib in gdcm_libs:
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].requires = ["headers"]
            self.cpp_info.components[lib].builddirs = [os.path.join("lib", self._gdcm_subdir)]
            self.cpp_info.components[lib].build_modules["cmake"] = [self._gdcm_config_cmake_path]
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = [self._gdcm_config_cmake_path]
            self.cpp_info.components[lib].build_modules["cmake_find_multi_package"] = [self._gdcm_config_cmake_path]
            self.cpp_info.components[lib].names["cmake_find_package"] = lib
            self.cpp_info.components[lib].names["cmake_find_multi_package"] = lib
            
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.components["socketxx"].system_libs = ["ws2_32"]
                self.cpp_info.components["gdcmCommon"].system_libs = ["ws2_32", "crypt32"]
                self.cpp_info.components["gdcmDICT"].requires.extend(["gdcmDSED", "gdcmIOD"])
                self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
                self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon", "gdcmexpat"])
                self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT", "gdcmjpeg8", "gdcmjpeg12", "gdcmjpeg16", "gdcmopenjp2", "gdcmcharls"])
                self.cpp_info.components["gdcmMSFF"].system_libs = ["rpcrt4"]
                self.cpp_info.components["gdcmMEXD"].requires.extend(["gdcmMSFF", "gdcmDICT", "gdcmDSED", "gdcmIOD", "socketxx"])
            else:
                self.cpp_info.components["gdcmopenjp2"].system_libs = ["pthread"]
                self.cpp_info.components["gdcmCommon"].system_libs = ["dl"]
                if tools.is_apple_os(self.settings.os):
                    self.cpp_info.components["gdcmCommon"].frameworks = ["CoreFoundation"]
                self.cpp_info.components["gdcmDICT"].requires.extend(["gdcmDSED", "gdcmIOD"])
                self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
                self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon", "gdcmexpat"])
                self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT", "gdcmjpeg8", "gdcmjpeg12", "gdcmjpeg16", "gdcmopenjp2", "gdcmcharls", "gdcmuuid"])
                self.cpp_info.components["gdcmMEXD"].requires.extend(["gdcmMSFF", "gdcmDICT", "gdcmDSED", "gdcmIOD", "socketxx"])
        else:
            self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
            self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon"])
            self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT"])
            if self.settings.os != "Windows":
                self.cpp_info.components["gdcmopenjp2"].system_libs = ["pthread"]

