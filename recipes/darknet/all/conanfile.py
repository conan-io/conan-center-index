import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
)
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class DarknetConan(ConanFile):
    name = "darknet"
    description = "Darknet is a neural network frameworks written in C"
    license = "YOLO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pjreddie.com/darknet/"
    topics = ("neural network", "deep learning")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opencv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_opencv": False,
    }

    @property
    def _lib_to_compile(self):
        if not self.options.shared:
            return "$(ALIB)"
        else:
            return "$(SLIB)"

    @property
    def _shared_lib_extension(self):
        if self.settings.os == "Macos":
            return ".dylib"
        else:
            return ".so"

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "Makefile"),
            "SLIB=libdarknet.so",
            f"SLIB=libdarknet{self._shared_lib_extension}",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "Makefile"),
            "all: obj backup results $(SLIB) $(ALIB) $(EXEC)",
            f"all: obj backup results {self._lib_to_compile}",
        )

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_opencv:
            # Requires OpenCV 2.x
            self.requires("opencv/2.4.13.7")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.fpic = self.options.get_safe("fPIC", True)
        tc.make_args = ["OPENCV={}".format("1" if self.options.with_opencv else "0")]
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            self._patch_sources()
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(
            self,
            "LICENSE*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            "*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        for pattern in ["*.so", "*.dylib", "*.a"]:
            copy(
                self,
                pattern,
                src=self.source_folder,
                dst=os.path.join(self.package_folder, "lib"),
                keep_path=False,
            )
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["darknet"]
        if self.options.with_opencv:
            # For https://github.com/pjreddie/darknet/blob/61c9d02ec461e30d55762ec7669d6a1d3c356fb2/include/darknet.h#L757
            self.cpp_info.defines.append("OPENCV=1")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        if stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
