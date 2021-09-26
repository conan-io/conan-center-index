from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
import os
import stat

required_conan_version = ">=1.33.0"


class ZlibConan(ConanFile):
    name = "zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                  "(Also Free, Not to Mention Unencumbered by Patents)")
    topics = ("zlib", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.rmdir(os.path.join(self._source_subfolder, "contrib"))
        if not tools.os_info.is_windows:
            configure_file = os.path.join(self._source_subfolder, "configure")
            st = os.stat(configure_file)
            os.chmod(configure_file, st.st_mode | stat.S_IEXEC)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(build_dir=self._build_subfolder)
            cmake.build()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self)
                if self.settings.arch == "x86" or self.settings.arch == "x86_64":
                    autotools.flags.append("-mstackrealign")

                if self.settings.os == "Macos":
                    old_str = "-install_name $libdir/$SHAREDLIBM"
                    new_str = "-install_name $SHAREDLIBM"
                    tools.replace_in_file("configure", old_str, new_str)

                # Zlib configure doesnt allow this parameters (in 1.2.8)
                autotools.configure(build=False, host=False, target=False)
                autotools.make()

    @property
    def _license_text(self):
        text = tools.load(os.path.join(self._source_subfolder, "zlib.h"))
        return text[2:text.find("*/", 1)]

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include", "%s" % self._source_subfolder, keep_path=False)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            suffix = "d" if self.settings.build_type == "Debug" else ""
            self.copy(pattern="*.h", dst="include", src=self._build_subfolder, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", src=self._build_subfolder, dst="bin", keep_path=False)
                self.copy(pattern="libzlib.dll.a", src=os.path.join(self._build_subfolder, "lib"), dst="lib")
                self.copy(pattern="zlib{}.lib".format(suffix), src=os.path.join(self._build_subfolder, "lib"), dst="lib")
            else:
                self.copy(pattern="zlibstatic{}.lib".format(suffix), src=os.path.join(self._build_subfolder, "lib"), dst="lib")
                self.copy(pattern="libzlibstatic.a", src=os.path.join(self._build_subfolder, "lib"), dst="lib")

                lib_path = os.path.join(self.package_folder, "lib")
                if self.settings.compiler == "Visual Studio":
                    tools.rename(os.path.join(lib_path, "zlibstatic{}.lib".format(suffix)),
                                 os.path.join(lib_path, "zlib{}.lib".format(suffix)))
                elif self.settings.compiler == "gcc":
                    tools.rename(os.path.join(lib_path, "libzlibstatic.a"),
                                 os.path.join(lib_path, "libzlib.a"))
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", src=self._source_subfolder, dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", src=self._source_subfolder, dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", src=self._source_subfolder, dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ZLIB"
        self.cpp_info.names["cmake_find_package_multi"] = "ZLIB"
        self.cpp_info.names["pkg_config"] = "zlib"
        if self.settings.os == "Windows":
            suffix = ""
            if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
                suffix = "d"
            self.cpp_info.libs = ["zlib{}".format(suffix)]
        else:
            self.cpp_info.libs = ["z"]
