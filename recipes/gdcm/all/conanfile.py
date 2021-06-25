from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"

class GDCMConan(ConanFile):
    name = "gdcm"
    topics = ("dicom", "images")
    homepage = "http://gdcm.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    description = "C++ library for DICOM medical files"
    exports_sources = "CMakeLists.txt", "patches/**"
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

    def validate(self):
        if (self.settings.compiler == "Visual Studio"
                and self.options.shared
                and str(self.settings.compiler.runtime).startswith("MT")):
            raise ConanInvalidConfiguration("shared gdcm can't be built with MT or MTd")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("expat/2.4.1")
        self.requires("openjpeg/2.4.0")
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
        self._cmake.definitions["GDCM_BUILD_DOCBOOK_MANPAGES"] = False
        self._cmake.definitions["GDCM_BUILD_SHARED_LIBS"] = self.options.shared
        # FIXME: unvendor deps https://github.com/conan-io/conan-center-index/pull/5705#discussion_r647224146
        self._cmake.definitions["GDCM_USE_SYSTEM_EXPAT"] = True
        self._cmake.definitions["GDCM_USE_SYSTEM_OPENJPEG"] = True
        self._cmake.definitions["GDCM_USE_SYSTEM_ZLIB"] = True

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
            tools.remove_files_by_mask(bin_dir, "*.pdb")
        lib_dir = os.path.join(self.package_folder, "lib")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(lib_dir, self._gdcm_subdir), "[!U]*.cmake") #leave UseGDCM.cmake untouched
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._gdcm_cmake_module_aliases_path),
            self._gdcm_libraries
        )
        self._create_cmake_variables(os.path.join(self.package_folder, self._gdcm_cmake_variables_path))

    def _create_cmake_variables(self, variables_file):
        v = tools.Version(self.version)
        content = textwrap.dedent("""\
            # The GDCM version number.
            set(GDCM_MAJOR_VERSION "{v_major}")
            set(GDCM_MINOR_VERSION "{v_minor}")
            set(GDCM_BUILD_VERSION "{v_patch}")

            get_filename_component(SELF_DIR "${{CMAKE_CURRENT_LIST_FILE}}" PATH)

            # The libraries.
            set(GDCM_LIBRARIES "")

            # The CMake macros dir.
            set(GDCM_CMAKE_DIR "")

            # The configuration options.
            set(GDCM_BUILD_SHARED_LIBS "{build_shared_libs}")

            set(GDCM_USE_VTK "OFF")

            # The "use" file.
            set(GDCM_USE_FILE ${{SELF_DIR}}/UseGDCM.cmake)

            # The VTK options.
            set(GDCM_VTK_DIR "")

            get_filename_component(GDCM_INCLUDE_ROOT "${{SELF_DIR}}/../../include/{gdcm_subdir}" ABSOLUTE)
            set(GDCM_INCLUDE_DIRS ${{GDCM_INCLUDE_ROOT}})
            get_filename_component(GDCM_LIB_ROOT "${{SELF_DIR}}/../../lib" ABSOLUTE)
            set(GDCM_LIBRARY_DIRS ${{GDCM_LIB_ROOT}})
        """.format(v_major=v.major,
                   v_minor=v.minor,
                   v_patch=v.patch,
                   build_shared_libs="ON" if self.options.shared else "OFF",
                   gdcm_subdir=self._gdcm_subdir))
        tools.save(variables_file, content)

    @staticmethod
    def _create_cmake_module_alias_targets(targets_file, libraries):
        content = "\n".join([textwrap.dedent("""\
            if(TARGET {aliased} AND NOT TARGET {alias})
                add_library({alias} INTERFACE IMPORTED)
                set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
            endif()
            """.format(alias=library, aliased="GDCM::"+library)) for library in libraries])
        tools.save(targets_file, content)

    @property 
    def _gdcm_subdir(self):
        v = tools.Version(self.version)
        return "gdcm-{}.{}".format(v.major, v.minor)

    @property
    def _gdcm_builddir(self):
        return os.path.join("lib", self._gdcm_subdir)

    @property
    def _gdcm_cmake_module_aliases_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-targets.cmake")

    @property
    def _gdcm_cmake_variables_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-variables.cmake")

    @property
    def _gdcm_build_modules(self):
        return [self._gdcm_cmake_module_aliases_path, self._gdcm_cmake_variables_path]

    @property
    def _gdcm_libraries(self):
        gdcm_libs = ["gdcmcharls",
                     "gdcmCommon",
                     "gdcmDICT",
                     "gdcmDSED",
                     "gdcmIOD",
                     "gdcmjpeg12",
                     "gdcmjpeg16",
                     "gdcmjpeg8",
                     "gdcmMEXD",
                     "gdcmMSFF",
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
        for lib in gdcm_libs:
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].includedirs = [os.path.join("include", self._gdcm_subdir)]
            self.cpp_info.components[lib].builddirs = [self._gdcm_builddir] 
            self.cpp_info.components[lib].build_modules["cmake"] = self._gdcm_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = self._gdcm_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_multi_package"] = self._gdcm_build_modules

        self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
        self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon", "expat::expat"])
        self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT", "openjpeg::openjpeg"])
        if not self.options.shared:
            self.cpp_info.components["gdcmDICT"].requires.extend(["gdcmDSED", "gdcmIOD"])
            self.cpp_info.components["gdcmMEXD"].requires.extend(["gdcmMSFF", "gdcmDICT", "gdcmDSED", "gdcmIOD", "socketxx"])
            self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmjpeg8", "gdcmjpeg12", "gdcmjpeg16", "gdcmcharls"])

            if self.settings.os == "Windows":
                self.cpp_info.components["gdcmCommon"].system_libs = ["ws2_32", "crypt32"]
                self.cpp_info.components["gdcmMSFF"].system_libs = ["rpcrt4"]
                self.cpp_info.components["socketxx"].system_libs = ["ws2_32"]
            else:
                self.cpp_info.components["gdcmMSFF"].requires.append("gdcmuuid")

                self.cpp_info.components["gdcmCommon"].system_libs = ["dl"]
                if tools.is_apple_os(self.settings.os):
                    self.cpp_info.components["gdcmCommon"].frameworks = ["CoreFoundation"]
