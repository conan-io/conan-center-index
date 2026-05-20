import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git, Version
from conan.tools.files import apply_conandata_patches, get, replace_in_file, patch, copy, export_conandata_patches, mkdir, rename, replace_in_file, rmdir, save, rm


class uhdRecipe(ConanFile):
    name = "uhd"

    # Optional metadata
    license = "GPL-3.0-only"
    author = "EttusResearch"
    url = "https://github.com/EttusResearch/uhd"
    description = "UHD is the USRP Hardware Driver, a software driver for Ettus Research's Universal Software Radio Peripheral (USRP) hardware."
    topics = ("UHD", "SDR", "USRP", "Ettus", "Software Radio", "Driver")
    no_copy_source = True
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    package_type = "library"


    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "*"

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def requirements(self):
        for deps in self.conan_data["dependencies"][self.version].get("dependency", []):
            self.run("echo 'Adding dependency: {}'".format(deps))
            self.requires(deps)

    def system_requirements(self):
        import pip
        if hasattr(pip, "main"):
            pip.main(["install", "Mako"])
        else:
            from pip._internal import main
            main(['install', "Mako"])

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="host", cli_args=[
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
            "-DENABLE_LIBUHD=ON",
            "-DENABLE_C_API=ON",
            "-DENABLE_PYTHON_API=OFF",
            "-DENABLE_EXAMPLES=OFF",
            "-DENABLE_TESTS=OFF",
            "-DENABLE_PYMOD_UTILS=OFF",
            "-DENABLE_USB=ON",
            "-DENABLE_B100=OFF",
            "-DENABLE_B200=ON",
            "-DENABLE_USRP1=OFF",
            "-DENABLE_USRP2=ON",
            "-DENABLE_X300=OFF",
            "-DENABLE_MPMD=OFF",
            "-DENABLE_SIM=OFF",
            "-DENABLE_N300=OFF",
            "-DENABLE_N320=OFF",
            "-DENABLE_E300=OFF",
            "-DENABLE_OCTOCLOCK=OFF",
            "-DENABLE_DPDK=OFF"])
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Binaries to link
        self.cpp_info.libs = ["uhd"]  # The libs to link against
        # Directories
        self.cpp_info.includedirs = ['include']  # Ordered list of include paths
        self.cpp_info.libdirs = ['lib']  # Directories where libraries can be found
        self.cpp_info.bindirs = ['bin']  # Directories where executables and shared libs can be found
        self.cpp_info.set_property("cmake_find_mode", "both")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
 
        lib_path = os.path.join(self.package_folder, "lib")
        self.output.info(f"Appending LD_LIBRARY_PATH environment variable: {lib_path}")
        self.env_info.LD_LIBRARY_PATH.append(lib_path)
