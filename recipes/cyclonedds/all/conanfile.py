import os
import textwrap
from conan import ConanFile
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build, scm

required_conan_version = ">=1.43.0"


class CycloneDDSConan(ConanFile):
    name = "cyclonedds"
    license = "EPL-2.0"
    homepage = "https://cyclonedds.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse Cyclone DDS - An implementation"\
                  " of the OMG Data Distribution Service (DDS) specification"
    topics = ("dds", "ipc", "ros", "middleware")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "shm" : [True, False],
        "security" : [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "shm": True,
        "security": False
    }

    generators = ["cmake", "cmake_find_package_multi"]
    _cmake = None
    short_paths = True

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.shm:
            self.requires("iceoryx/2.0.0")
        if self.options.ssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        compiler = self.settings.compiler
        version = scm.Version(self.settings.compiler.version)

        if ((self.options.security is True ) and (self.options.shared is False)):
            raise ConanInvalidConfiguration("Cyclone DDS currently do not support"\
                                            "static build and security on")

        if compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, 14)

        if compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("Cyclone DDS is just supported"\
                                                "for Visual Studio 2019 and higher.")
            if self.options.shared:
                raise ConanInvalidConfiguration(
                    'Using Cyclone DDS with Visual Studio currently just possible'\
                    'with "shared=False"')
        elif compiler == "gcc":
            if version < "6":
                raise ConanInvalidConfiguration("Using Cyclone DDS with gcc requires"\
                                                " gcc 6 or higher.")
            if version < "9" and compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("gcc < 9 with libstdc++ not supported")
            if version == "6":
                self.output.warn("Cyclone DDS package is compiled with gcc 6, it is"\
                                 " recommended to use 7 or higher")
                self.output.warn("GCC 6 will build with warnings.")
        elif compiler == "clang":
            if compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("clang with libstdc++ not supported")
            if version == "7.0" and compiler.get_safe("libcxx") == "libc++" and \
               self.options.shared and self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("shared Debug with clang 7.0 and"\
                                                " libc++ not supported")

    def source(self):
        files.get(self,**self.conan_data["sources"][self.version], strip_root=True,
                 destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self,**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_IDLC"] = False
        self._cmake.definitions["BUILD_DDSPERF"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_IDLC_TESTING"] = False
        # ToDo : check how to build static + security
        self._cmake.definitions["ENABLE_SECURITY"] = self.options.security
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["ENABLE_SSL"] = self.options.ssl
        self._cmake.definitions["ENABLE_SHM"] = self.options.shm
        self._cmake.configure()
        return self._cmake

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        files.save(self, module_file, content)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","cmake","CycloneDDS"))

    def package_info(self):
        self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                { "CycloneDDS::ddsc" : "cyclone-dds::ddsc"})
        self.cpp_info.set_property("cmake_file_name", "CycloneDDS")
        self.cpp_info.components["ddsc"].set_property("cmake_target_name", "CycloneDDS::ddsc")
        self.cpp_info.components["ddsc"].libs = ["ddsc"]
        requires = []
        if self.options.shm:
            requires.append("iceoryx::iceoryx_binding_c")
        if self.options.ssl:
            requires.append("openssl::openssl")
        self.cpp_info.components["ddsc"].requires = requires
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ddsc"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ddsc"].build_modules["cmake_find_package_multi"] = [
            self._module_file_rel_path
        ]
