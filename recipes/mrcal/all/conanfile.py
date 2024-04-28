import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.54.0"


class MrcalConan(ConanFile):
    name = "mrcal"
    description = "mrcal is a generic toolkit built to solve the calibration and SFM-like problems we encounter at NASA/JPL"
    license = "Apache-2.0 AND LGPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mrcal.secretsauce.net/"
    topics = ("camera-calibration", "computer-vision")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/dkogan/libdogleg/blob/master/dogleg.h#L8
        self.requires("suitesparse-cholmod/5.2.1", transitive_headers=True, transitive_libs=True)
        self.requires("freeimage/3.18.0")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"] and not is_apple_os(self):
            raise ConanInvalidConfiguration("Unsupported OS")

    def build_requirements(self):
        self.tool_requires("re2c/3.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["mrcal"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["libdogleg"], destination="libdogleg", strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["mrbuild"], destination="mrbuild", strip_root=True)
        copy(self, "*", "mrbuild", os.path.join("libdogleg", "mrbuild"))

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        # CHOLMOD .so file is not found without the VirtualRunEnv for some reason
        env = VirtualRunEnv(self)
        env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        # TODO: add libelas to CCI
        # tc.make_args.append("USE_LIBELAS=1")
        tc.extra_cflags.append("-Ilibdogleg")
        tc.extra_ldflags.append("-Llibdogleg")
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    @property
    def _libdogleg_version(self):
        url = self.conan_data["sources"][self.version]["libdogleg"]["url"]
        return url.split("/v")[-1].replace(".tar.gz", "")

    def build(self):
        with chdir(self, os.path.join(self.source_folder, "libdogleg")):
            replace_in_file(self, "Makefile", "$(VERSION_FROM_PROJECT)", self._libdogleg_version)
            autotools = Autotools(self)
            autotools.make()
        with chdir(self, self.source_folder):
            replace_in_file(self, "Makefile", "all: ", "all: libmrcal.$(SO) libmrcal.$(SO).${ABI_VERSION} #")
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        shutil.copy(os.path.join(self.source_folder, "libdogleg", "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE.libdogleg"))
        copy(self, "*.h", os.path.join(self.source_folder, "libdogleg"), os.path.join(self.package_folder, "include"))
        for header in ["basic-geometry.h", "mrcal-image.h", "mrcal-internal.h", "mrcal-types.h", "mrcal.h", "poseutils.h", "stereo.h", "triangulation.h"]:
            copy(self, header, self.source_folder, os.path.join(self.package_folder, "include", "mrcal"))
        so_pattern = "*.dylib" if is_apple_os(self) else "*.so*"
        copy(self, so_pattern, os.path.join(self.source_folder, "libdogleg"), os.path.join(self.package_folder, "lib"))
        copy(self, so_pattern, self.source_folder, os.path.join(self.package_folder, "lib"), excludes="libdogleg/*")
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["mrcal", "dogleg"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
