import os
from conan import ConanFile
from conan.tools.files import copy, get, rm, apply_conandata_patches, replace_in_file
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class OpenvrConan(ConanFile):
    name = "openvr"
    description = "API and runtime that allows access to VR hardware from applications have specific knowledge of the hardware they are targeting."
    topics = ("conan", "openvr", "vr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ValveSoftware/openvr"
    license = "BSD-3-Clause"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Honor fPIC=False
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "-fPIC", "")
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_UNIVERSAL"] = False

        runtime = self.settings.get_safe("compiler.libcxx")
        if runtime != None and runtime != "libc++":
            tc.variables["USE_LIBCXX"] = False

        if self.options.shared:
            tc.variables["BUILD_SHARED"] = True
        else:
            tc.variables["BUILD_SHARED"] = False
        tc.generate()    

    def build(self):        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "openvr_*.dll", src=os.path.join(self.package_folder,
             "lib"), dst=os.path.join(self.package_folder, "bin"))
        rm(self, "openvr_*.dll", folder=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "openvr")
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["openvr_api64"]
        else:
            self.cpp_info.libs = ["openvr_api"]
        self.cpp_info.includedirs.append(os.path.join("include", "openvr"))
        if not self.options.shared:
            self.cpp_info.defines.append("OPENVR_BUILD_STATIC")
            self.cpp_info.defines.append("OPENVR_API_NODLL")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Foundation")
