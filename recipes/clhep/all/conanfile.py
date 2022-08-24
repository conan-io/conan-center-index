from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class ClhepConan(ConanFile):
    name = "clhep"
    description = "Class Library for High Energy Physics."
    license = "LGPL-3.0-only"
    topics = ("clhep", "cern", "hep", "high energy", "physics", "geometry", "algebra")
    homepage = "http://proj-clhep.web.cern.ch/proj-clhep"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("CLHEP doesn't properly build its shared libs with Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CLHEP_SINGLE_THREAD"] = False
        self._cmake.definitions["CLHEP_BUILD_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=os.path.join(self._source_subfolder, "CLHEP"))
        cmake = self._configure_cmake()
        cmake.install()

    @property
    def _clhep_components(self):
        def libm():
            return ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        return [
            {"name": "Vector", "system_libs": libm() + pthread()},
            {"name": "Evaluator", "system_libs": libm() + pthread()},
            {"name": "GenericFunctions", "system_libs": libm() + pthread()},
            {"name": "Geometry", "system_libs": libm() + pthread(), "requires": ["vector"]},
            {"name": "Random", "system_libs": libm() + pthread()},
            {"name": "Matrix", "system_libs": libm() + pthread(), "requires": ["random", "vector"]},
            {"name": "RandomObjects", "system_libs": libm(), "requires": ["random", "matrix", "vector"]},
            {"name": "Cast", "system_libs": pthread()},
            {"name": "RefCount", "system_libs": pthread()},
            {"name": "Exceptions", "requires": ["cast", "refcount"]},
        ]

    def package_info(self):
        suffix = "" if self.options.shared else "S"

        self.cpp_info.set_property("cmake_file_name", "CLHEP")
        self.cpp_info.set_property("cmake_target_name", "CLHEP::CLHEP{}".format(suffix))
        self.cpp_info.set_property("pkg_config_name", "clhep")

        for component in self._clhep_components:
            name = component["name"]
            conan_comp = name.lower()
            cmake_target = "{}{}".format(name, suffix)
            pkg_config_name = "clhep-{}".format(name.lower())
            lib_name = "CLHEP-{}-{}".format(name, self.version)
            system_libs = component.get("system_libs", [])
            requires = component.get("requires", [])

            self.cpp_info.components[conan_comp].set_property("cmake_target_name", "CLHEP::{}".format(cmake_target))
            self.cpp_info.components[conan_comp].set_property("pkg_config_name", pkg_config_name)
            self.cpp_info.components[conan_comp].libs = [lib_name]
            self.cpp_info.components[conan_comp].system_libs = system_libs
            self.cpp_info.components[conan_comp].requires = requires

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[conan_comp].names["cmake_find_package"] = cmake_target
            self.cpp_info.components[conan_comp].names["cmake_find_package_multi"] = cmake_target
            self.cpp_info.components[conan_comp].names["pkg_config"] = pkg_config_name
            self.cpp_info.components["clheplib"].requires.append(conan_comp)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CLHEP"
        self.cpp_info.names["cmake_find_package_multi"] = "CLHEP"
        self.cpp_info.names["pkg_config"] = "clhep"
        self.cpp_info.components["clheplib"].names["cmake_find_package"] = "CLHEP{}".format(suffix)
        self.cpp_info.components["clheplib"].names["cmake_find_package_multi"] = "CLHEP{}".format(suffix)
        self.cpp_info.components["clheplib"].set_property("cmake_target_name", "CLHEP::CLHEP{}".format(suffix))
        self.cpp_info.components["clheplib"].names["pkg_config"] = "clhep"
        self.cpp_info.components["clheplib"].set_property("pkg_config_name", "clhep")
