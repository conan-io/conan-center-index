import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
)
from conan.tools.gnu import Autotools, AutotoolsToolchain

required_conan_version = ">=1.57.0"


class BlasfeoConan(ConanFile):
    name = "blasfeo"
    description = "Basic linear algebra subroutines for embedded optimization."
    topics = (
        "blasfeo",
        "blas",
        "linear-algebra",
        "matrices",
        "embedded",
        "optimization",
    )
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/giaf/blasfeo"
    settings = "os", "arch", "compiler", "build_type"

    _blasfeo_arch_targets = {
        "x86_64": [
            "X64_INTEL_SKYLAKE_X",
            "X64_INTEL_HASWELL",
            "X64_INTEL_SANDY_BRIDGE",
            "X64_INTEL_CORE",
            "X64_AMD_BULLDOZER",
        ],
        "x86": [
            "X86_AMD_JAGUAR",
            "X86_AMD_BARCELONA",
        ],
        "armv7": [
            "ARMV7A_ARM_CORTEX_A15",
            "ARMV7A_ARM_CORTEX_A9",
            "ARMV7A_ARM_CORTEX_A7",
        ],
        "armv8": [
            "ARMV8A_APPLE_M1",
            "ARMV8A_ARM_CORTEX_A76",
            "ARMV8A_ARM_CORTEX_A73",
            "ARMV8A_ARM_CORTEX_A57",
            "ARMV8A_ARM_CORTEX_A55",
            "ARMV8A_ARM_CORTEX_A53",
        ],
        "generic": ["GENERIC"],
    }

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "target": [x for list in [i for i in _blasfeo_arch_targets.values()] for x in list],
        "la": [
            "HIGH_PERFORMANCE",
            "REFERENCE",
            "EXTERNAL_BLAS_WRAPPER",
        ],
        "mf": [
            "COLMAJ",
            "PANELMAJ",
        ],
    }
    default_options = {
        "fPIC": False,
        "shared": False,
        "target": "GENERIC",
        "la": "HIGH_PERFORMANCE",
        "mf": "PANELMAJ",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        toolchain = AutotoolsToolchain(self)
        toolchain.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        blasfeo_target = str(self.options.target)
        if blasfeo_target != self._blasfeo_arch_targets["generic"][0]:
            if blasfeo_target not in self._blasfeo_arch_targets[str(self.settings.arch)]:
                raise ConanInvalidConfiguration(
                    "Invalid arch: {} and target: {} combination.".format(self.settings.arch, self.options.target)
                )
        if self.settings.os == "Windows":
            # Installation instructions do not contain Windows information.
            # There is also an open issue for Windows support: https://github.com/giaf/blasfeo/issues/101
            raise ConanInvalidConfiguration(
                "This recipe does not support {} builds of {}.".format(self.settings.os, self.name)
            )
        if self.options.shared and is_apple_os(self):
            raise ConanInvalidConfiguration(
                "{} does not support shared builds for {}.".format(self.name, self.settings.os)
            )

    def requirements(self):
        self.requires(self.tested_reference_str)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

        target = "shared_library" if self.options.shared else "static_library"
        args = [
            "TARGET={}".format(self.options.target),
            "LA={}".format(self.options.la),
            "MF={}".format(self.options.mf),
        ]
        autotools = Autotools(self)
        autotools.make(target=target, args=args)

    def package(self):
        copy(
            self,
            pattern="LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )
        copy(
            self,
            pattern="*.h*",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
            keep_path=False,
        )
        copy(
            self,
            pattern="*.a",
            src=os.path.join(self.source_folder, "lib"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            pattern="*.so",
            src=os.path.join(self.source_folder, "lib"),
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "BLASFEO")
        self.cpp_info.set_property("cmake_target_name", "BLASFEO::BLASFEO")
        self.cpp_info.set_property("pkg_config_name", "blasfeo")
        self.cpp_info.names["cmake_find_package"] = "BLASFEO"
        self.cpp_info.names["cmake_find_package_multi"] = "BLASFEO"
        self.cpp_info.libs = ["blasfeo"]
        self.cpp_info.system_libs = ["m"]
