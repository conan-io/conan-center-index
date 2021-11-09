from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.36.0"


class ProjConan(ConanFile):
    name = "proj"
    description = "Cartographic Projections and Coordinate Transformations Library."
    license = "MIT"
    topics = ("dsp", "proj", "proj4", "projections", "gis", "geospatial")
    homepage = "https://proj.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_tiff": [True, False],
        "with_curl": [True, False],
        "build_executables": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_tiff": True,
        "with_curl": True,
        "build_executables": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "7.0.0":
            del self.options.with_tiff
            del self.options.with_curl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("nlohmann_json/3.10.4")
        self.requires("sqlite3/3.36.0")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.3.0")
        if self.options.get_safe("with_curl"):
            self.requires("libcurl/7.79.1")

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires("sqlite3/3.36.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        with tools.run_environment(self):
            cmake = self._configure_cmake()
            cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "/W4", "")
        # Trick to find sqlite3 executable for build machine
        sqlite3_exe_build_context_paths = " ".join("\"{}\"".format(path.replace("\\", "/")) for path in self.deps_env_info["sqlite3"].PATH)
        tools.replace_in_file(cmakelists,
                              "find_program(EXE_SQLITE3 sqlite3)",
                              "find_program(EXE_SQLITE3 sqlite3 PATHS {} NO_DEFAULT_PATH)".format(sqlite3_exe_build_context_paths))
        # unvendor nlohmann_json
        if tools.Version(self.version) < "8.1.0":
            tools.rmdir(os.path.join(self._source_subfolder, "include", "proj", "internal", "nlohmann"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_THREAD"] = self.options.threadsafe
        self._cmake.definitions["BUILD_CCT"] = self.options.build_executables
        self._cmake.definitions["BUILD_CS2CS"] = self.options.build_executables
        self._cmake.definitions["BUILD_GEOD"] = self.options.build_executables
        self._cmake.definitions["BUILD_GIE"] = self.options.build_executables
        self._cmake.definitions["BUILD_PROJ"] = self.options.build_executables
        self._cmake.definitions["BUILD_PROJINFO"] = self.options.build_executables
        self._cmake.definitions["PROJ_DATA_SUBDIR"] = "res"
        if tools.Version(self.version) < "7.0.0":
            self._cmake.definitions["PROJ_TESTS"] = False
            self._cmake.definitions["BUILD_LIBPROJ_SHARED"] = self.options.shared
            self._cmake.definitions["ENABLE_LTO"] = False
            self._cmake.definitions["JNI_SUPPORT"] = False
        else:
            self._cmake.definitions["ENABLE_TIFF"] = self.options.with_tiff
            self._cmake.definitions["ENABLE_CURL"] = self.options.with_curl
            self._cmake.definitions["BUILD_TESTING"] = False
            self._cmake.definitions["ENABLE_IPO"] = False
            self._cmake.definitions["BUILD_PROJSYNC"] = self.options.build_executables and self.options.with_curl
        if tools.Version(self.version) >= "8.1.0":
            self._cmake.definitions["NLOHMANN_JSON_ORIGIN"] = "external"
        self._cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False
        self._cmake.configure()
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        proj_version = tools.Version(self.version)
        cmake_config_filename = "proj" if proj_version >= "7.0.0" else "proj4"
        cmake_namespace = "PROJ" if proj_version >= "7.0.0" else "PROJ4"
        self.cpp_info.set_property("cmake_file_name", cmake_config_filename)
        self.cpp_info.set_property("cmake_target_name", cmake_namespace)
        self.cpp_info.set_property("pkg_config_name", "proj")
        self.cpp_info.components["projlib"].set_property("cmake_target_name", "proj")
        self.cpp_info.components["projlib"].set_property("pkg_config_name", "proj")
        self.cpp_info.components["projlib"].libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["projlib"].system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.components["projlib"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            if proj_version >= "7.0.0":
                self.cpp_info.components["projlib"].system_libs.append("shell32")
            if proj_version >= "7.1.0":
                self.cpp_info.components["projlib"].system_libs.append("Ole32")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["projlib"].system_libs.append(tools.stdcpp_library(self))
        self.cpp_info.components["projlib"].requires.extend(["nlohmann_json::nlohmann_json", "sqlite3::sqlite3"])
        if self.options.get_safe("with_tiff"):
            self.cpp_info.components["projlib"].requires.append("libtiff::libtiff")
        if self.options.get_safe("with_curl"):
            self.cpp_info.components["projlib"].requires.append("libcurl::libcurl")
        if tools.Version(self.version) < "8.2.0":
            if self.options.shared and self.settings.compiler == "Visual Studio":
                self.cpp_info.components["projlib"].defines.append("PROJ_MSVC_DLL_IMPORT")
        else:
            if not self.options.shared:
                self.cpp_info.components["projlib"].defines.append("PROJ_DLL=")

        res_path = os.path.join(self.package_folder, "res")
        self.output.info("Creating PROJ_LIB environment variable: {}".format(res_path))
        self.env_info.PROJ_LIB = res_path
        if self.options.build_executables:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
