from conans import ConanFile, CMake, tools
import os


class LibProxyConan(ConanFile):
    name = "libproxy"
    description = "A library handling all the details of proxy configuration"
    topics = ("conan", "libproxy", "proxy", "configuration", "network")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libproxy.github.io/libproxy/"
    license = "LGPL-2.1-or-later"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"

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
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def  _build_subfolder(self):
        return "build_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libproxy-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libmodman/2.0.1")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        prefix = self.package_folder.replace("\\", "/")
        self._cmake.definitions["FORCE_SYSTEM_LIBMODMAN"] = True

        self._cmake.definitions["BIPR"] = False
        self._cmake.definitions["WITH_DOTNET"] = False
        self._cmake.definitions["WITH_GNOME"] = False
        self._cmake.definitions["WITH_GNOME2"] = False
        self._cmake.definitions["WITH_GNOME3"] = False
        self._cmake.definitions["WITH_KDE"] = False
        self._cmake.definitions["WITH_MOZJS"] = False
        self._cmake.definitions["WITH_NM"] = False
        self._cmake.definitions["WITH_PERL"] = False
        self._cmake.definitions["WITH_PYTHON2"] = False
        self._cmake.definitions["WITH_PYTHON3"] = False
        self._cmake.definitions["WITH_VALA"] = False
        self._cmake.definitions["WITH_WEBKIT"] = False
        self._cmake.definitions["WITH_WEBKIT3"] = False

        self._cmake.definitions["BIN_INSTALL_DIR"] = "{}/bin".format(prefix)
        self._cmake.definitions["LIB_INSTALL_DIR"] = "{}/lib".format(prefix)
        self._cmake.definitions["LIBEXEC_INSTALL_DIR"] = "{}/lib/libexec".format(prefix)
        self._cmake.definitions["SHARE_INSTALL_DIR"] = "{}/share".format(prefix)
        self._cmake.definitions["PYTHON2_SITEPKG_DIR"] = "{}/lib/python2/site-packages".format(prefix)
        self._cmake.definitions["PYTHON3_SITEPKG_DIR"] = "{}/lib/python3/sit-packages".format(prefix)

        self._cmake.definitions["PX_PERL_ARCH"] = "lib/perl"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # raise Exception
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    @property
    def _libcxx_libraries(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ("libstdc++", "libstdc++11"):
            return ["stdc++"]
        elif libcxx in ("libc++",):
            return ["c++"]
        else:
            return []

    def package_info(self):
        libname = "proxy"
        if self.settings.compiler == "Visual Studio":
            libname = "lib" + libname
        self.cpp_info.libs = [libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        self.cpp_info.system_libs.extend(self._libcxx_libraries)

        self.cpp_info.names["pkg_config"] = "libproxy-1.0"
        self.cpp_info.names["cmake_find_package"] = "libproxy"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
