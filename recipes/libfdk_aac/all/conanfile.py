from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class LibFDKAACConan(ConanFile):
    name = "libfdk_aac"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A standalone library of the Fraunhofer FDK AAC code from Android"
    license = "https://github.com/mstorsjo/fdk-aac/blob/master/NOTICE"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    topics = ("multimedia", "audio", "fraunhofer", "aac", "decoder", "encoding", "decoding")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _use_cmake(self):
        return Version(self.version) >= "2.0.2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self._use_cmake:
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def build_requirements(self):
        if not self._use_cmake and not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self._use_cmake:
            tc = CMakeToolchain(self)
            tc.variables["BUILD_PROGRAMS"] = False
            tc.variables["FDK_AAC_INSTALL_CMAKE_CONFIG_MODULE"] = False
            tc.variables["FDK_AAC_INSTALL_PKGCONFIG_MODULE"] = False
            tc.generate()
        elif is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if self._use_cmake:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        elif is_msvc(self):
            makefile_vc = os.path.join(self.source_folder, "Makefile.vc")
            replace_in_file(self, makefile_vc, "CFLAGS   = /nologo /W3 /Ox /MT", "CFLAGS   = /nologo")
            replace_in_file(self, makefile_vc, "MKDIR_FLAGS = -p", "MKDIR_FLAGS =")
            # Build either shared or static, and don't build utility (it always depends on static lib)
            replace_in_file(self, makefile_vc, "copy $(PROGS) $(bindir)", "")
            replace_in_file(self, makefile_vc, "copy $(LIB_DEF) $(libdir)", "")
            if self.options.shared:
                replace_in_file(
                    self, makefile_vc,
                    "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                    "all: $(LIB_DEF) $(SHARED_LIB) $(IMP_LIB)",
                )
                replace_in_file(self, makefile_vc, "copy $(STATIC_LIB) $(libdir)", "")
            else:
                replace_in_file(
                    self, makefile_vc,
                    "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                    "all: $(STATIC_LIB)",
                )
                replace_in_file(self, makefile_vc, "copy $(IMP_LIB) $(libdir)", "")
                replace_in_file(self, makefile_vc, "copy $(SHARED_LIB) $(bindir)", "")
            with chdir(self, self.source_folder):
                self.run("nmake -f Makefile.vc")
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            if self.settings.os == "Android" and self._settings_build.os == "Windows":
                # remove escape for quotation marks, to make ndk on windows happy
                replace_in_file(
                    self, os.path.join(self.source_folder, "configure"),
                    "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g",
                )
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self._use_cmake:
            cmake = CMake(self)
            cmake.install()
        elif is_msvc(self):
            with chdir(self, self.source_folder):
                self.run(f"nmake -f Makefile.vc prefix=\"{self.package_folder}\" install")
            if self.options.shared:
                rename(self, os.path.join(self.package_folder, "lib", "fdk-aac.dll.lib"),
                             os.path.join(self.package_folder, "lib", "fdk-aac.lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fdk-aac")
        self.cpp_info.set_property("cmake_target_name", "FDK-AAC::fdk-aac")
        self.cpp_info.set_property("pkg_config_name", "fdk-aac")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["fdk-aac"].libs = ["fdk-aac"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["fdk-aac"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "fdk-aac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.names["cmake_find_package"] = "FDK-AAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FDK-AAC"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].set_property("cmake_target_name", "FDK-AAC::fdk-aac")
