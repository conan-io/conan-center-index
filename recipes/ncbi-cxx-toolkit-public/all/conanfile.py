from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, replace_in_file, rmdir
from conan.tools.build import check_min_cppstd, cross_building, can_run
from conan.tools.scm import Version
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
import os
import yaml
import re

required_conan_version = ">=1.53.0"


class NcbiCxxToolkit(ConanFile):
    name = "ncbi-cxx-toolkit-public"
    description = "NCBI C++ Toolkit -- a cross-platform application framework and a collection of libraries for working with biological data."
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ncbi.github.io/cxx-toolkit"
    topics = ("ncbi", "biotechnology", "bioinformatics", "genbank", "gene",
              "genome", "genetic", "sequence", "alignment", "blast",
              "biological", "toolkit", "c++")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared":     [True, False],
        "fPIC":       [True, False],
        "with_targets":  ["ANY"],
        "with_components": ["ANY"],
        "without_req": ["ANY"]
    }
    default_options = {
        "shared":     False,
        "fPIC":       True,
        "with_targets":   "",
        "with_components": "",
	"without_req": ""
    }
    short_paths = True
    _dependencies = None
    _requirements = None
    _targets = set()
    _components = set()
    _componenttargets = set()

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    @property
    def _dependencies_folder(self):
        return "dependencies"

    @property
    def _dependencies_filename(self):
        return f"dependencies-{Version(self.version).major}.{Version(self.version).minor}.yml"

    @property
    def _requirements_filename(self):
        return f"requirements-{Version(self.version).major}.{Version(self.version).minor}.yml"

    @property
    def _tk_dependencies(self):
        if self._dependencies is None:
            dependencies_filepath = os.path.join(self.recipe_folder, self._dependencies_folder, self._dependencies_filename)
            if not os.path.isfile(dependencies_filepath):
                raise ConanException(f"Cannot find {dependencies_filepath}")
            with open(dependencies_filepath, "r", encoding="utf-8") as f:
                self._dependencies = yaml.safe_load(f)
        return self._dependencies

    @property
    def _tk_requirements(self):
        if self._requirements is None:
            requirements_filepath = os.path.join(self.recipe_folder, self._dependencies_folder, self._requirements_filename)
            if not os.path.isfile(requirements_filepath):
                raise ConanException(f"Cannot find {requirements_filepath}")
            with open(requirements_filepath, "r", encoding="utf-8") as f:
                self._requirements = yaml.safe_load(f)
        return self._requirements

    def _version_less(self, major):
        ver = Version(self.version).major
        return ver < major and ver > 1

    def _translate_req(self, key):
        if "Boost" in key:
            key = "Boost"
        _disabled_req = self._parse_option(self.options.without_req)
        if key in _disabled_req:
            return None
        if key == "BerkeleyDB" and conan_version.major > "1":
            return None
        if key in self._tk_requirements["disabled"].keys():
            if self.settings.os in self._tk_requirements["disabled"][key]:
                return None
        if key in self._tk_requirements["requirements"].keys():
            return self._tk_requirements["requirements"][key]
        return None

    def _parse_option(self, data):
        _res = set()
        if data != "":
            _data = str(data)
            _data = _data.replace(",", ";")
            _data = _data.replace(" ", ";")
            _res.update(_data.split(";"))
            if "" in _res:
                _res.remove("")
        return _res

    def export(self):
        copy(self, self._dependencies_filename,
            os.path.join(self.recipe_folder, self._dependencies_folder),
            os.path.join(self.export_folder, self._dependencies_folder))
        copy(self, self._requirements_filename,
            os.path.join(self.recipe_folder, self._dependencies_folder),
            os.path.join(self.export_folder, self._dependencies_folder))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _collect_dependencies(self, components):
        if len(components) > 0:
            _todo = components.copy()
            components.clear()
            _next = set()
            while len(_todo) > 0:
                for _component in _todo:
                    if not _component in components:
                        components.add(_component)
                        if _component in self._tk_dependencies["dependencies"].keys():
                            for _n in self._tk_dependencies["dependencies"][_component]:
                                if not _n in components:
                                    _next.add(_n)
                _todo = _next.copy()
                _next.clear()

    def requirements(self):
        self._targets = self._parse_option(self.options.with_targets)
        self._components = set()
        for _t in self._targets:
            _re = re.compile(_t)
            for _component in self._tk_dependencies["components"]:
                _libraries = self._tk_dependencies["libraries"][_component]
                for _lib in _libraries:
                    if _re.match(_lib) != None:
                        self._components.add(_component)
                        break

        _requested_components = self._parse_option(self.options.with_components)
        self._collect_dependencies(_requested_components)

        if len(self._components) == 0 and len(_requested_components) == 0:
            _requested_components.update( self._tk_dependencies["components"])

        if len(_requested_components) > 0:
            for component in _requested_components:
                self._componenttargets.update(self._tk_dependencies["libraries"][component])
            if len(self._targets) > 0:
                self._componenttargets.update(self._targets)
                self._targets.clear()
            self._components.update(_requested_components)

        self._collect_dependencies(self._components)
        requirements = set()
        for component in self._components:
            libraries = self._tk_dependencies["libraries"][component]
            for lib in libraries:
                if lib in self._tk_dependencies["requirements"].keys():
                    requirements.update(self._tk_dependencies["requirements"][lib])

        for req in requirements:
            pkgs = self._translate_req(req)
            if pkgs != None:
                for pkg in pkgs:
                    self.requires(pkg)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration("This operating system is not supported")
        if is_msvc(self):
            check_min_vs(self, 192)
            if self._version_less(28) and self.options.shared and is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration("This configuration is not supported")
            if self._version_less(29) and int(str(self.settings.compiler.version)) > 193:
                raise ConanInvalidConfiguration("This configuration is not supported")
        else:
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"This version of {self.settings.compiler} is not supported")
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross compilation is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NCBI_PTBCFG_PACKAGING"] = True
        if self.options.shared:
            tc.variables["NCBI_PTBCFG_ALLOW_COMPOSITE"] = True
        tc.variables["NCBI_PTBCFG_PROJECT_LIST"] = "-app/netcache"
        if len(self._targets) > 0:
            tc.variables["NCBI_PTBCFG_PROJECT_TARGETS"] = ";".join(self._targets)
        else:
            tc.variables["NCBI_PTBCFG_PROJECT_COMPONENTTARGETS"] = ";".join(self._componenttargets)
        if is_msvc(self):
            tc.variables["NCBI_PTBCFG_CONFIGURATION_TYPES"] = self.settings.build_type
        tc.variables["NCBI_PTBCFG_PROJECT_TAGS"] = "-demo;-sample"
        _disabled_req = self._parse_option(self.options.without_req)
        if len(_disabled_req) > 0:
            tc.variables["NCBI_PTBCFG_PROJECT_COMPONENTS"] = "-" + ";-".join(_disabled_req)
        tc.generate()
        CMakeDeps(self).generate()
        VirtualBuildEnv(self).generate()
        if can_run(self):
            VirtualRunEnv(self).generate(scope = "build" if self._version_less(29) else "run")

    def _patch_sources(self):
        rmdir(self, os.path.join(self.source_folder, "src", "build-system", "cmake", "unused"))
        rmdir(self, os.path.join(self.source_folder, "src", "build-system", "cmake", "modules"))
        if self._version_less(29):
            grpc = os.path.join(self.source_folder, "src", "build-system", "cmake", "CMake.NCBIptb.grpc.cmake")
            if self.settings.os == "Macos":
                replace_in_file(self, grpc,
                    "COMMAND ${_cmd}",
                    "COMMAND ${CMAKE_COMMAND} -E env \"DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}\" ${_cmd}", strict=False)
                pkg = os.path.join(self.source_folder, "src", "build-system", "cmake", "CMake.NCBIComponentsPackage.cmake")
                replace_in_file(self, pkg,"NCBI_util_disable_find_use_path()","#NCBI_util_disable_find_use_path()", strict=False)
                replace_in_file(self, pkg,"NCBI_util_enable_find_use_path()","#NCBI_util_enable_find_use_path()", strict=False)
            elif self.settings.os == "Linux":
                replace_in_file(self, grpc,
                    "COMMAND ${_cmd}",
                    "COMMAND ${CMAKE_COMMAND} -E env \"LD_LIBRARY_PATH=$<JOIN:${CMAKE_LIBRARY_PATH},:>:$ENV{LD_LIBRARY_PATH}\" ${_cmd}")
        root = os.path.join(self.source_folder, "CMakeLists.txt")
        with open(root, "w", encoding="utf-8") as f:
            f.write("cmake_minimum_required(VERSION 3.15)\n")
            f.write("project(ncbi-cpp)\n")
            f.write("include(src/build-system/cmake/CMake.NCBItoolkit.cmake)\n")
            f.write("add_subdirectory(src)\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
# Visual Studio sometimes runs "out of heap space"
#        if is_msvc(self):
#            cmake.parallel = False
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    @property
    def _module_file_rel_path(self):
        return os.path.join("res", "build-system", "cmake", "CMake.NCBIpkg.conan.cmake")

    def package_info(self):
        impfile = os.path.join(self.package_folder, "res", "ncbi-cpp-toolkit.imports")
        with open(impfile, "r", encoding="utf-8") as f:
            allexports = set(f.read().split())
        for component in self._components:
            c_libs = []
            c_reqs = []
            n_reqs = set()
            libraries = self._tk_dependencies["libraries"][component]
            for lib in libraries:
                if lib in allexports:
                    c_libs.append(lib)
                if lib in self._tk_dependencies["requirements"].keys():
                    n_reqs.update(self._tk_dependencies["requirements"][lib])
            c_reqs.extend(self._tk_dependencies["dependencies"][component])
            for req in n_reqs:
                pkgs = self._translate_req(req)
                if pkgs != None:
                    for pkg in pkgs:
                        pkg = pkg[:pkg.find("/")]
                        ref = pkg + "::" + pkg
                        c_reqs.append(ref)
            self.cpp_info.components[component].libs = c_libs
            self.cpp_info.components[component].requires = c_reqs

        if self.settings.os == "Windows":
            self.cpp_info.components["core"].defines.append("_UNICODE")
            self.cpp_info.components["core"].defines.append("_CRT_SECURE_NO_WARNINGS=1")
        else:
            self.cpp_info.components["core"].defines.append("_MT")
            self.cpp_info.components["core"].defines.append("_REENTRANT")
            self.cpp_info.components["core"].defines.append("_THREAD_SAFE")
            self.cpp_info.components["core"].defines.append("_FILE_OFFSET_BITS=64")
        if self.options.shared:
            self.cpp_info.components["core"].defines.append("NCBI_DLL_BUILD")
        if self.settings.build_type == "Debug":
            self.cpp_info.components["core"].defines.append("_DEBUG")
        else:
            self.cpp_info.components["core"].defines.append("NDEBUG")
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs = ["ws2_32", "dbghelp"]
        elif self.settings.os == "Linux":
            self.cpp_info.components["core"].system_libs = ["dl", "rt", "m", "pthread", "resolv"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["core"].system_libs = ["dl", "c", "m", "pthread", "resolv"]
            self.cpp_info.components["core"].frameworks = ["ApplicationServices"]
        self.cpp_info.components["core"].builddirs.append("res")
        build_modules = [self._module_file_rel_path]
        self.cpp_info.components["core"].build_modules["cmake"] = build_modules
        self.cpp_info.components["core"].build_modules["cmake_find_package"] = build_modules
        self.cpp_info.components["core"].build_modules["cmake_find_package_multi"] = build_modules
        self.cpp_info.set_property("cmake_build_modules", build_modules)
