from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=1.53.0"


class NiftiClibConan(ConanFile):
    name = "nifti_clib"
    description = "C libraries for NIFTI support"
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NIFTI-Imaging/nifti_clib"
    topics = ("image")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_nifti2": [True, False],
        "use_cifti": [True, False],
        "use_fslio": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_nifti2": True,
        "use_cifti": False,  # seems to be beta?
        "use_fslio": False  # Note in CMakeLists.txt: "If OFF, The copyright of this code is questionable for inclusion with nifti."
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if is_msvc(self) and self.options.shared:
            # not supported due to not having dllexport definitions
            raise ConanInvalidConfiguration(f"{self.ref} does not support -o {self.ref}:shared=True with MSVC compiler.")
        if not self.options.use_nifti2 and self.options.use_cifti:
            raise ConanInvalidConfiguration(f"{self.ref} -o '&:use_cifti=True' requires -o '&:use_nifti2=True'")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.use_cifti:
            self.requires("expat/[>=2.6.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NIFTI_INSTALL_NO_DOCS"] = True
        tc.variables["USE_NIFTI2_CODE"] = self.options.use_nifti2
        tc.variables["USE_CIFTI_CODE"] = self.options.use_cifti
        tc.variables["USE_FSL_CODE"] = self.options.use_fslio
        tc.variables["NIFTI_BUILD_TESTING"] = False  # disable building tests
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
            tc.preprocessor_definitions["_CRT_SECURE_NO_WARNINGS"] = 1
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nifti")
        self.cpp_info.set_property("cmake_target_name", "NIFTI::NIFTI")
        self.cpp_info.set_property("pkg_config_name", "nifti")
        self.cpp_info.includedirs += [ os.path.join("include", "nifti") ]

        sys_libs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            sys_libs += ["m"]

        self.cpp_info.required_components = ["ZLIB::ZLIB"]
        if self.options.use_cifti:
            self.cpp_info.required_components += ["EXPAT::EXPAT"]

        self.cpp_info.components["znz"].libs = ["znz"]
        self.cpp_info.components["znz"].set_property("pkg_config_name", "znz")
        self.cpp_info.components["znz"].set_property("cmake_target_name", "NIFTI::znz")
        self.cpp_info.components["znz"].includedirs += [os.path.join("include", "nifti")]
        self.cpp_info.components["znz"].system_libs += sys_libs

        # inside the niftilib folder
        self.cpp_info.components["niftiio"].libs = ["niftiio"]
        self.cpp_info.components["niftiio"].set_property("pkg_config_name", "niftiio")
        self.cpp_info.components["niftiio"].set_property("cmake_target_name", "NIFTI::niftiio")
        self.cpp_info.components["niftiio"].includedirs += [os.path.join("include", "nifti")]
        self.cpp_info.components["niftiio"].system_libs += sys_libs

        self.cpp_info.components["nifticdf"].libs = ["nifticdf"]
        self.cpp_info.components["nifticdf"].requires = ["niftiio"]
        self.cpp_info.components["nifticdf"].set_property("pkg_config_name", "nifticdf")
        self.cpp_info.components["nifticdf"].set_property("cmake_target_name", "NIFTI::nifticdf")
        self.cpp_info.components["nifticdf"].includedirs += [os.path.join("include", "nifti")]
        self.cpp_info.components["nifticdf"].system_libs += sys_libs

        if self.options.use_nifti2:
            self.cpp_info.components["nifti2"].libs = ["nifti2"]
            self.cpp_info.components["nifti2"].requires = ["znz"]
            self.cpp_info.components["nifti2"].set_property("pkg_config_name", "nifti2")
            self.cpp_info.components["nifti2"].set_property("cmake_target_name", "NIFTI::nifti2")
            self.cpp_info.components["nifti2"].includedirs += [os.path.join("include", "nifti")]
            self.cpp_info.components["nifti2"].system_libs += sys_libs

        if self.options.use_cifti:
            self.cpp_info.components["cifti"].libs = ["cifti"]
            self.cpp_info.components["cifti"].requires = ["nifti2"]
            self.cpp_info.components["cifti"].set_property("pkg_config_name", "cifti")
            self.cpp_info.components["cifti"].set_property("cmake_target_name", "NIFTI::cifti")
            self.cpp_info.components["cifti"].includedirs += [os.path.join("include", "nifti")]
            self.cpp_info.components["cifti"].system_libs += sys_libs

        if self.options.use_fslio:
            self.cpp_info.components["fslio"].libs = ["fslio"]
            self.cpp_info.components["fslio"].requires = ["nifti2"]
            self.cpp_info.components["fslio"].set_property("pkg_config_name", "fslio")
            self.cpp_info.components["fslio"].set_property("cmake_target_name", "NIFTI::fslio")
            self.cpp_info.components["fslio"].includedirs += [os.path.join("include", "nifti")]
            self.cpp_info.components["fslio"].system_libs += sys_libs
