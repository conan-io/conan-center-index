from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os


class QuickfixConan(ConanFile):
    name = "quickfix"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ssl":  [True, False],
               "with_postgres": [True, False],
               "shared_ptr": ["std", "tr1"],
               "unique_ptr": ["unique", "auto"]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": False,
                       "with_postgres": False,
                       "shared_ptr": "std",
                       "unique_ptr": "unique"}
    generators = "cmake"
    exports_sources = "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _unique_ptr(self):
        # auto_ptr is fully removed in C++17.
        cppstd = self.settings.get_safe("compiler.cppstd", "")
        if "17" in cppstd or "20" in cppstd:
            return "unique"

        # gcc default standard for version 5.5 is gnu++98. In the 6 series, it
        # changed to gnu++14.
        version = Version(self.settings.compiler.version)
        if self.settings.compiler == "gcc" and (
                "98" in cppstd or
                (version <= "5.5" and not cppstd)):
            return "auto"

        if self.settings.compiler == "clang" and (
                (version <= "5.0" and self.settings.compiler.libcxx == "libstdc++" and
                 not self.settings.compiler.cppstd)):
            return "auto"

        return self.options.unique_ptr

    @property
    def _shared_ptr(self):
        # libc++ doesn't know of tr1.
        if str(self.settings.compiler).find("clang") != -1:
            if self.settings.compiler.libcxx == "libc++":
                return "std"

        # gcc default standard for version 5.5 is gnu++98. In the 6 series, it
        # changed to gnu++11.
        version = Version(str(self.settings.compiler.version))
        if self.settings.compiler == "gcc" and (
                str(self.settings.compiler.cppstd).find("98") != -1 or
                (version <= "5.5" and self.settings.compiler.cppstd == "None")):
            return "tr1"

        if self.settings.compiler == "clang" and (
                (version <= "5.0" and self.settings.compiler.libcxx == "libstdc++" and
                 self.settings.compiler.cppstd == "None")):
            return "tr1"

        return self.default_options["shared_ptr"]

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["HAVE_SSL"] = self.options.with_ssl
            self._cmake.definitions["HAVE_POSTGRESQL"] = self.options.with_postgres
            self._cmake.definitions["SHARED_PTR"] = str(self.options.shared_ptr).upper()
            self._cmake.definitions["UNIQUE_PTR"] = str(self.options.unique_ptr).upper()
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1g")

        if self.options.with_postgres:
            self.requires("libpq/11.5")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        self.options.unique_ptr = self._unique_ptr

        # It's reasonable to suppose that whenever there's support to
        # std::unique_ptr, there's also to std::shared_ptr. Otherwise
        # we need to obtain it from the settings.
        self.options.shared_ptr = "std" if self.options.unique_ptr == "unique" else self._shared_ptr

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("QuickFIX cannot be built as shared lib on Windows")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("Except.h", dst="include", src=os.path.join(self._source_subfolder, "src", "C++"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.with_ssl:
            self.cpp_info.defines.append("HAVE_SSL=1")

        if self.options.with_postgres:
            self.cpp_info.defines.append("HAVE_POSTGRESQL=1")

        if self.options.shared_ptr == "std":
            self.cpp_info.defines.append("HAVE_STD_SHARED_PTR=1")
        else:
            self.cpp_info.defines.append("HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER=1")

        if self.options.unique_ptr == "unique":
            self.cpp_info.defines.append("HAVE_STD_UNIQUE_PTR=1")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread"])
