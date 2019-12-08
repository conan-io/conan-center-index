import os
from conans import ConanFile, CMake, tools
import re
import shutil


class TermcapConan(ConanFile):
    name = "termcap"
    homepage = "https://www.gnu.org/software/termcap"
    description = "Enables programs to use display terminals in a terminal-independent manner"
    license = "GPL-2.0"
    topics = ("conan", "termcap", "terminal", "display")
    exports = ["LICENSE.md"]
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], }
    default_options = {"shared": False, "fPIC": True, }
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        archive_name = self.name + "-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

    def _extract_sources(self):
        makefile_text = open(os.path.join(self._source_subfolder, "Makefile.in")).read()
        sources = list("{}/{}".format(self._source_subfolder, src) for src in re.search("\nSRCS = (.*)\n", makefile_text).group(1).strip().split(" "))
        headers = list("{}/{}".format(self._source_subfolder, src) for src in re.search("\nHDRS = (.*)\n", makefile_text).group(1).strip().split(" "))
        autoconf_text = open(os.path.join(self._source_subfolder, "configure.in")).read()
        optional_headers = re.search(r"AC_HAVE_HEADERS\((.*)\)", autoconf_text).group(1).strip().split(" ")
        return sources, headers, optional_headers

    def _patch_sources(self):
        termcap_h = os.path.join(self._source_subfolder, "termcap.h")
        tools.replace_in_file(termcap_h, "extern", "TERMCAP_API")
        tools.replace_in_file(termcap_h,
                              "#define _TERMCAP_H 1",
                              "#define _TERMCAP_H 1\n"
                              "\n"
                              "#if defined _MSC_VER\n"
                              "#  define TERMCAP_SHARED_EXPORT_API __declspec(dllexport)\n"
                              "#  define TERMCAP_SHARED_IMPORT_API __declspec(dllimport)\n"
                              "#  define TERMCAP_STATIC_IMPORT_API extern\n"
                              "#  define TERMCAP_STATIC_EXPORT_API extern\n"
                              "#else\n"
                              "#  define TERMCAP_SHARED_EXPORT_API __attribute__((visibility(\"default\")))\n"
                              "#  define TERMCAP_SHARED_IMPORT_API __attribute__((visibility(\"default\")))\n"
                              "#  define TERMCAP_STATIC_IMPORT_API extern\n"
                              "#  define TERMCAP_STATIC_EXPORT_API extern\n"
                              "#endif\n"
                              "\n"
                              "#if defined TERMCAP_BUILDING\n"
                              "#  define TERMCAP_SHARED_API TERMCAP_SHARED_EXPORT_API\n"
                              "#  define TERMCAP_STATIC_API TERMCAP_STATIC_EXPORT_API\n"
                              "#else\n"
                              "#  define TERMCAP_SHARED_API TERMCAP_SHARED_IMPORT_API\n"
                              "#  define TERMCAP_STATIC_API TERMCAP_STATIC_IMPORT_API\n"
                              "#endif\n"
                              "\n"
                              "#if defined TERMCAP_SHARED\n"
                              "#  define TERMCAP_API TERMCAP_SHARED_API\n"
                              "#else\n"
                              "#  define TERMCAP_API TERMCAP_STATIC_API\n"
                              "#endif\n")
        termcap_intern_h = os.path.join(self._source_subfolder, "termcap_intern.h")
        shutil.copy(termcap_h, termcap_intern_h)
        tools.replace_in_file(termcap_intern_h, "const", "")
        tools.replace_in_file(termcap_intern_h, "tparam ( char *ctlstring, char *buffer, int size, ...)", "tparam ()")
        sources, _, _ = self._extract_sources()
        for src in sources:
            txt = open(src).read()
            with open(src, "w") as f:
                f.write("#include \"termcap_intern.h\"\n\n")
                f.write(txt)

    def _configure_cmake(self):
        cmake = CMake(self)
        sources, headers, optional_headers = self._extract_sources()
        cmake.definitions["TERMCAP_SOURCES"] = ";".join(sources)
        cmake.definitions["TERMCAP_HEADERS"] = ";".join(headers)
        cmake.definitions["TERMCAP_INC_OPTS"] = ";".join(optional_headers)
        cmake.verbose=True
        cmake.parallel = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.name = "Termcap"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.definitions = ["TERMCAP_SHARED"]
