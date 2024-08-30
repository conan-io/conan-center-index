from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file, rmdir
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
        "with_components": ["ANY"]
    }
    default_options = {
        "shared":     False,
        "fPIC":       True,
        "with_targets":   "",
        "with_components": ""
    }
    short_paths = True
    _dependencies = None
    _requirements = None
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

    def _translate_req(self, key):
        if "Boost" in key:
            key = "Boost"
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        _alltargets = self._parse_option(self.options.with_targets)
        _required_components = set()
        for _t in _alltargets:
            _re = re.compile(_t)
            for _component in self._tk_dependencies["components"]:
                _libraries = self._tk_dependencies["libraries"][_component]
                for _lib in _libraries:
                    if _re.match(_lib) != None:
                        _required_components.add(_component)
                        break

        _allcomponents = self._parse_option(self.options.with_components)
        _required_components.update(_allcomponents)

        if len(_required_components) > 0:
            _todo = _required_components.copy()
            _required_components.clear()
            _next = set()
            while len(_todo) > 0:
                for _component in _todo:
                    if not _component in _required_components:
                        _required_components.add(_component)
                        if _component in self._tk_dependencies["dependencies"].keys():
                            for _n in self._tk_dependencies["dependencies"][_component]:
                                if not _n in _required_components:
                                    _next.add(_n)
                _todo = _next.copy()
                _next.clear()

        if len(_required_components) == 0:
            _required_components.update( self._tk_dependencies["components"])
        for component in _required_components:
            self._componenttargets.update(self._tk_dependencies["libraries"][component])

        requirements = set()
        for component in _required_components:
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
            if self.options.shared and is_msvc_static_runtime(self) and Version(self.version) < "28":
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
        if self.options.with_targets != "":
            tc.variables["NCBI_PTBCFG_PROJECT_TARGETS"] = self.options.with_targets
        if len(self._componenttargets) != 0:
            tc.variables["NCBI_PTBCFG_PROJECT_COMPONENTTARGETS"] = ";".join(self._componenttargets)
        if is_msvc(self):
            tc.variables["NCBI_PTBCFG_CONFIGURATION_TYPES"] = self.settings.build_type
        tc.variables["NCBI_PTBCFG_PROJECT_TAGS"] = "-demo;-sample"
        tc.generate()
        CMakeDeps(self).generate()
        VirtualBuildEnv(self).generate()
        if can_run(self):
            VirtualRunEnv(self).generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "src", "build-system", "cmake", "unused"))
        rmdir(self, os.path.join(self.source_folder, "src", "build-system", "cmake", "modules"))
        grpc = os.path.join(self.source_folder, "src", "build-system", "cmake", "CMake.NCBIptb.grpc.cmake")
        if self.settings.os == "Macos":
            replace_in_file(self, grpc,
                "COMMAND ${_cmd}",
                "COMMAND ${CMAKE_COMMAND} -E env \"DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}\" ${_cmd}")
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
            allexports = set(f.read().split()).intersection(self._componenttargets)
        absent = []
        for component in self._tk_dependencies["components"]:
            c_libs = []
            libraries = self._tk_dependencies["libraries"][component]
            for lib in libraries:
                if lib in allexports:
                    c_libs.append(lib)
            if len(c_libs) == 0 and len(libraries) != 0:
                absent.append(component)
        for component in self._tk_dependencies["components"]:
            c_libs = []
            c_reqs = []
            n_reqs = set()
            c_deps = self._tk_dependencies["dependencies"][component]
            for c in c_deps:
                if c in absent:
                    c_deps.remove(c)
            c_reqs.extend(c_deps)
            libraries = self._tk_dependencies["libraries"][component]
            for lib in libraries:
                if lib in allexports:
                    c_libs.append(lib)
                if lib in self._tk_dependencies["requirements"].keys():
                    n_reqs.update(self._tk_dependencies["requirements"][lib])
            for req in n_reqs:
                pkgs = self._translate_req(req)
                if pkgs != None:
                    for pkg in pkgs:
                        pkg = pkg[:pkg.find("/")]
                        ref = pkg + "::" + pkg
                        c_reqs.append(ref)
            if len(c_libs) != 0 or (len(libraries) == 0 and len(c_reqs) != 0):
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
        self.cpp_info.components["core"].build_modules = build_modules
        self.cpp_info.set_property("cmake_build_modules", build_modules)
