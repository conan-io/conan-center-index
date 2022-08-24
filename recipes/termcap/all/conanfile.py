import os
from conan import ConanFile, tools
from conans import CMake
import re


required_conan_version = ">=1.33.0"


class TermcapConan(ConanFile):
    name = "termcap"
    homepage = "https://www.gnu.org/software/termcap"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Enables programs to use display terminals in a terminal-independent manner"
    license = "GPL-2.0-or-later"
    topics = ("terminal", "display", "text", "writing")
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], }
    default_options = {"shared": False, "fPIC": True, }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _extract_sources(self):
        makefile_text = open(os.path.join(self._source_subfolder, "Makefile.in")).read()
        sources = list("{}/{}".format(self._source_subfolder, src) for src in re.search("\nSRCS = (.*)\n", makefile_text).group(1).strip().split(" "))
        headers = list("{}/{}".format(self._source_subfolder, src) for src in re.search("\nHDRS = (.*)\n", makefile_text).group(1).strip().split(" "))
        autoconf_text = open(os.path.join(self._source_subfolder, "configure.in")).read()
        optional_headers = re.search(r"AC_HAVE_HEADERS\((.*)\)", autoconf_text).group(1).strip().split(" ")
        return sources, headers, optional_headers

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        sources, headers, optional_headers = self._extract_sources()
        self._cmake.definitions["TERMCAP_SOURCES"] = ";".join(sources)
        self._cmake.definitions["TERMCAP_HEADERS"] = ";".join(headers)
        self._cmake.definitions["TERMCAP_INC_OPTS"] = ";".join(optional_headers)
        self._cmake.definitions["TERMCAP_CAP_FILE"] = os.path.join(self._source_subfolder, "termcap.src").replace("\\", "/")
        self._cmake.definitions["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "bin", "etc").replace("\\", "/")
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if self.settings.os == "Windows":
            for src in self._extract_sources()[0]:
                txt = open(src).read()
                with open(src, "w") as f:
                    f.write("#include \"termcap_intern.h\"\n\n")
                    f.write(txt)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    @property
    def _termcap_path(self):
        return os.path.join(self.package_folder, "bin", "etc", "termcap")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines = ["TERMCAP_SHARED"]

        self.output.info("Setting TERMCAP environment variable: {}".format(self._termcap_path))
        self.env_info.TERMCAP = self._termcap_path
