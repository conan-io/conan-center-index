from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os
import re

required_conan_version = ">=1.53.0"


class TermcapConan(ConanFile):
    name = "termcap"
    homepage = "https://www.gnu.org/software/termcap"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Enables programs to use display terminals in a terminal-independent manner"
    license = "GPL-2.0-or-later"
    topics = ("terminal", "display", "text", "writing")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_sources(self):
        makefile_text = open(os.path.join(self.source_folder, "Makefile.in")).read()
        sources = list(f"{self.source_folder}/{src}" for src in re.search("\nSRCS = (.*)\n", makefile_text).group(1).strip().split(" "))
        headers = list(f"{self.source_folder}/{src}" for src in re.search("\nHDRS = (.*)\n", makefile_text).group(1).strip().split(" "))
        autoconf_text = open(os.path.join(self.source_folder, "configure.in")).read()
        optional_headers = re.search(r"AC_HAVE_HEADERS\((.*)\)", autoconf_text).group(1).strip().split(" ")
        return sources, headers, optional_headers

    def generate(self):
        tc = CMakeToolchain(self)
        to_cmake_paths = lambda paths: ";".join([p.replace("\\", "/") for p in paths])
        sources, headers, optional_headers = self._extract_sources()
        tc.cache_variables["TERMCAP_SOURCES"] = to_cmake_paths(sources)
        tc.cache_variables["TERMCAP_HEADERS"] = to_cmake_paths(headers)
        tc.cache_variables["TERMCAP_INC_OPTS"] = to_cmake_paths(optional_headers)
        tc.cache_variables["TERMCAP_CAP_FILE"] = os.path.join(self.source_folder, "termcap.src").replace("\\", "/")
        tc.cache_variables["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "bin", "etc").replace("\\", "/")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if self.settings.os == "Windows":
            for src in self._extract_sources()[0]:
                txt = open(src).read()
                with open(src, "w") as f:
                    f.write("#include \"termcap_intern.h\"\n\n")
                    f.write(txt)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    @property
    def _termcap_path(self):
        return os.path.join(self.package_folder, "bin", "etc", "termcap")

    def package_info(self):
        self.cpp_info.libs = ["termcap"]
        if self.options.shared:
            self.cpp_info.defines = ["TERMCAP_SHARED"]

        self.runenv_info.define_path("TERMCAP", self._termcap_path)
        self.env_info.TERMCAP = self._termcap_path
