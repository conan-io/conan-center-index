import os
import re

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, load, save, replace_in_file
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "rdma-core"
    description = ("RDMA core userspace libraries and daemons. "
                   "Provides userspace components for the Linux Kernel's drivers/infiniband subsystem.")
    license = ("GPL-2.0", "Linux-OpenIB", "BSD-2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linux-rdma/rdma-core"
    topics = ("linux-kernel", "rdma", "infiniband", "iwarp", "roce", "kernel-rdma-drivers",
              "libefa", "libibmad", "libibnetdisc", "libibumad", "libibverbs", "libmana",
              "libmlx4", "libmlx5", "librdmacm")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libnl/3.7.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libudev/system")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()
        tc = CMakeToolchain(self)
        # Shared libraries are built by default and even if ENABLE_STATIC is turned on,
        # the static libraries still have dependencies on the shared libraries.
        # tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["NO_PYVERBS"] = True
        tc.variables["NO_MAN_PAGES"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Build only the libraries and disable everything else
        allowed_subdirs = ["ccan", "kernel-boot", "kernel-headers", "libibmad", "libibnetdisc", "libibumad", "libibverbs",
                           "librdmacm", "providers/efa", "providers/mana", "providers/mlx4", "providers/mlx5", "util"]
        cmakelists_path = os.path.join(self.source_folder, "CMakeLists.txt")
        cmakelists_content = load(self, cmakelists_path)
        patched_content = re.sub(r"add_subdirectory\((?!({})\)).+\)".format("|".join(allowed_subdirs)), r"", cmakelists_content)
        save(self, cmakelists_path, patched_content)
        # Adjust the pkg-config target for libnl
        replace_in_file(self, cmakelists_path, "libnl-3.0 libnl-route-3.0", "libnl")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        for lib in ["libefa", "libibmad", "libibnetdisc", "libibumad",
                    "libibverbs", "libmana", "libmlx4", "libmlx5", "librdmacm"]:
            component = self.cpp_info.components[lib]
            component.libs = [lib.replace("lib", "")]
            component.requires = ["libudev::libudev", "libnl::libnl"]
            component.set_property("pkg_config_name", lib)

        for lib in ["libefa", "libmana", "libmlx4", "libmlx5", "librdmacm"]:
            self.cpp_info.components[lib].requires += ["libibverbs"]
        self.cpp_info.components["libibmad"].requires += ["libibumad"]
        self.cpp_info.components["libibnetdisc"].requires += ["libibmad", "libibumad"]
        for lib in ["libefa", "libibverbs", "libmana", "libmlx4", "libmlx5", "librdmacm"]:
            self.cpp_info.components[lib].system_libs = ["pthread"]
