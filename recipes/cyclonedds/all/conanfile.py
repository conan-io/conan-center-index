import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build, scm
from conan.tools.microsoft import is_msvc
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps
from conan.tools.layout import cmake_layout

required_conan_version = ">=1.51.3"

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
        "with_ssl": [True, False],
        "with_shm" : [True, False],
        "enable_security" : [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
        "with_shm": False,
        "enable_security": False
    }

    short_paths = True

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if self.options.with_shm:
            self.requires("iceoryx/2.0.0")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1q")

    def build_requirements(self):
        self.tool_requires("cmake/3.16.2")

    def validate(self):
        compiler = self.info.settings.compiler
        version = scm.Version(self.info.settings.compiler.version)

        if self.options.enable_security and not self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} currently do not support"\
                                            "static build and security on")

        if compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, 14)

        if is_msvc(self):
            # TODO : determine windows error and find solution (at test_package)
            raise ConanInvalidConfiguration(f"{self.ref} is not (yet) supported"\
                                                "for Visual Studio compiler.")
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and scm.Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++"\
                f"{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        files.get(self,**self.conan_data["sources"][self.version], strip_root=True,
                 destination=self.source_folder)

    def layout(self):
        cmake_layout(self,src_folder="src")

    def generate(self):

        tc = CMakeToolchain(self)
        # TODO : determine how to do in conan :
        # - idlc is a code generator that is used as tool (and so not cross compiled)
        # - other tools like ddsperf is cross compiled for target
        # - maybe separate package like cyclonedds_idlc
        tc.variables["BUILD_IDLC"]            = False
        tc.variables["BUILD_IDLC_TESTING"]    = False
        tc.variables["BUILD_DDSPERF"]         = False
        tc.variables["BUILD_IDLC_TESTING"]    = False
        # variables which effects build
        tc.variables["ENABLE_SSL"]            = self.options.with_ssl
        tc.variables["ENABLE_SHM"]            = self.options.with_shm
        tc.variables["ENABLE_SECURITY"]       = self.options.enable_security
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("LICENSE", src=self.source_folder, dst="licenses")
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "lib","cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cyclonedds")
        self.cpp_info.filenames["cmake_find_package"] = "cyclonedds"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cyclonedds"
        self.cpp_info.names["cmake_find_package"] = "CycloneDDS"
        self.cpp_info.names["cmake_find_package_multi"] = "CycloneDDS"
        self.cpp_info.components["CycloneDDS"].names["cmake_find_package"] = "ddsc"
        self.cpp_info.components["CycloneDDS"].names["cmake_find_package_multi"] = "ddsc"
        self.cpp_info.components["CycloneDDS"].libs = ["ddsc"]
        self.cpp_info.components["CycloneDDS"].set_property("cmake_target_name",
                    "CycloneDDS::ddsc")
        requires = []
        if self.options.with_shm:
            requires.append("iceoryx::iceoryx_binding_c")
        if self.options.with_ssl:
            requires.append("openssl::openssl")
        self.cpp_info.components["ddsc"].requires = requires
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ddsc"].system_libs = ["pthread"]
