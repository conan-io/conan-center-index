from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os

required_conan_version = ">=1.29.1"


class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    topics = ("conan", "geographiclib", "geodesic")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["float", "double", "extended", "quadruple", "variable"],
        "tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "tools": True
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
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
        if self.options.precision not in ["float", "double"]:
            # FIXME: add support for extended, quadruple and variable precisions
            # (may require external libs: boost multiprecision for quadruple, mpfr for variable)
            raise ConanInvalidConfiguration("extended, quadruple and variable precisions not yet supported in this recipe")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "GeographicLib-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # it does not work on Windows but is not needed
        tools.replace_in_file(cmakelists, "add_subdirectory (js)", "")
        # Don't install system libs
        tools.replace_in_file(cmakelists, "include (InstallRequiredSystemLibraries)", "")
        # Don't build tools if asked
        if not self.options.tools:
            tools.replace_in_file(cmakelists, "add_subdirectory (tools)", "")
            tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "CMakeLists.txt"),
                                  "${TOOLS}", "")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["GEOGRAPHICLIB_LIB_TYPE"] = "SHARED" if self.options.shared else "STATIC"
            self._cmake.definitions["GEOGRAPHICLIB_PRECISION"] = self._cmake_option_precision
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _cmake_option_precision(self):
        return {
            "float": 1,
            "double": 2,
            "extended": 3,
            "quadruple": 4,
            "variable": 5,
        }.get(str(self.options.precision))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for folder in ["share", os.path.join("lib", "python"), os.path.join("lib", "pkgconfig"),
                       os.path.join("lib", "cmake"), "sbin", "python", "matlab", "doc", "cmake"]:
            tools.rmdir(os.path.join(os.path.join(self.package_folder, folder)))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        self._create_cmake_module_targets(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file),
            libs={"GeographicLib": "GeographicLib::GeographicLib"}, # "GeographicLib and GeographicLib::GeographicLib are both official targets
            executables=self._executables
        )

    @staticmethod
    def _create_cmake_module_targets(module_file, libs={}, executables={}):
        content = ""
        for alias, aliased in libs.items():
            content += (
                "if(TARGET {aliased} AND NOT TARGET {alias})\n"
                "    add_library({alias} INTERFACE IMPORTED)\n"
                "    target_link_libraries({alias} INTERFACE {aliased})\n"
                "endif()\n"
            ).format(alias=alias, aliased=aliased)
        for target, executable in executables.items():
            # Geographic lib provides both namespaced and non-namespaced imported targets
            content += (
                "if(NOT TARGET {target} OR NOT TARGET GeographicLib::{target})\n"
                "    get_filename_component(GeographicLib_{target}_IMPORTED_LOCATION \"${{CMAKE_CURRENT_LIST_DIR}}/../../bin/{exec}\" ABSOLUTE)\n"
                "    message(STATUS \"GeographicLib component {target} found: ${{GeographicLib_{target}_IMPORTED_LOCATION}}\")\n"
                "    set(GeographicLib_{target}_FOUND ON)\n"
                "    if(NOT TARGET {target})\n"
                "        add_executable({target} IMPORTED)\n"
                "        set_property(TARGET {target} PROPERTY IMPORTED_LOCATION ${{GeographicLib_{target}_IMPORTED_LOCATION}})\n"
                "    endif()\n"
                "    if(NOT TARGET GeographicLib::{target})\n"
                "        add_executable(GeographicLib::{target} IMPORTED)\n"
                "        set_property(TARGET GeographicLib::{target} PROPERTY IMPORTED_LOCATION ${{GeographicLib_{target}_IMPORTED_LOCATION}})\n"
                "    endif()\n"
                "endif()\n"
            ).format(target=target, exec=executable)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    @property
    def _executables(self):
        def exec_name(name):
            return os.path.basename(glob.glob(os.path.join(self.package_folder, "bin", name + "*"))[0])

        executables = {}
        if self.options.tools:
            executables.update({
                "CartConvert": exec_name("CartConvert"),
                "ConicProj": exec_name("ConicProj"),
                "GeodesicProj": exec_name("GeodesicProj"),
                "GeoConvert": exec_name("GeoConvert"),
                "GeodSolve": exec_name("GeodSolve"),
                "GeoidEval": exec_name("GeoidEval"),
                "Gravity": exec_name("Gravity"),
                "MagneticField": exec_name("MagneticField"),
                "Planimeter": exec_name("Planimeter"),
                "RhumbSolve": exec_name("RhumbSolve"),
                "TransverseMercatorProj": exec_name("TransverseMercatorProj"),
            })
        return executables

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.build_modules = [os.path.join(self._module_subfolder, self._module_file)]

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
