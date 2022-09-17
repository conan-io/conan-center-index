import os
import textwrap
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build, scm
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps
from conan.tools.layout import cmake_layout

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
        "ssl": False,
        "shm": False,
        "security": False
    }

    short_paths = True

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
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

    def export_sources(self):
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
    
    def build_requirements(self):
        self.tool_requires("cmake/3.16.2")

    def validate(self):
        compiler = self.settings.compiler
        version = scm.Version(self.settings.compiler.version)

        if ((self.options.security is True ) and (self.options.shared is False)):
            raise ConanInvalidConfiguration("Cyclone DDS currently do not support"\
                                            "static build and security on")

        if compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, 14)

        if compiler == "Visual Studio":
            # ToDo : determine windows error and find solution (at test_package)
            raise ConanInvalidConfiguration("Cyclone DDS is not (yet) supported"\
                                                "for Visual Studio compiler.")
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

    def layout(self):
        cmake_layout(self)

    def generate(self):

        tc = CMakeToolchain(self)
        # ToDo : determine how to do in conan : 
        # - idlc is a code generator that is used as tool (and so not cross compiled)
        # - other tools like ddsperf is cross compiled for target
        # - maybe separate package like cyclonedds_idlc 
        tc.variables["BUILD_IDLC"]            = False
        tc.variables["BUILD_IDLC_TESTING"]    = False
        tc.variables["BUILD_DDSPERF"]         = False
        tc.variables["BUILD_IDLC_TESTING"]    = False
        # variables which effects build
        tc.variables["BUILD_SHARED_LIBS"]     = self.options.shared
        tc.variables["ENABLE_SSL"]            = self.options.ssl 
        tc.variables["ENABLE_SHM"]            = self.options.shm
        tc.variables["ENABLE_SECURITY"]       = self.options.security
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","cmake","CycloneDDS"))

    def package_info(self):
        self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                { "CycloneDDS::ddsc" : "cyclonedds::ddsc"})
        self.cpp_info.set_property("cmake_file_name", "CycloneDDS")
        self.cpp_info.components["ddsc"].set_property("cmake_target_name", "CycloneDDS::ddsc")
        self.cpp_info.components["ddsc"].libs = ["ddsc"]
        requires = []
        if self.options.shm:
            requires.append("iceoryx::iceoryx_binding_c")
        if self.options.ssl:
            requires.append("openssl::openssl")
        self.cpp_info.components["ddsc"].requires = requires
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ddsc"].system_libs = ["pthread"]
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ddsc"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ddsc"].build_modules["cmake_find_package_multi"] = [
            self._module_file_rel_path
        ]
