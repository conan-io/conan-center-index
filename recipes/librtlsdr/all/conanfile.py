from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


class LibRtlSdrConan(ConanFile):
    name = "librtlsdr"
    description = "Software to turn the RTL2832U into an SDR"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr"
    license = "GPL-2.0"
    topics = ("conan", "sdr", "rtl-sdr")
    generators = ("cmake", "cmake_find_package")
    exports_sources = ["patches/**"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("libusb/1.0.24")
        if self.settings.compiler == "Visual Studio":
            self.requires("pthreads4w/3.0.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(
            args=[
                "-DCMAKE_BUILD_TYPE={}".format(self.settings.build_type),
                "-DCMAKE_VERBOSE_MAKEFILE=ON",
            ],
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder,
        )
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        os.rename("Findlibusb.cmake", "Findlibusb_.cmake")
        cmake = self._configure_cmake()
        # Do not build tools
        cmake.build(target="rtlsdr_shared" if self.options.shared else "rtlsdr_static")

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.h", dst="include", src=os.path.join(self._source_subfolder, "include")
        )
        self.copy("*.lib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy("*.dll", src=self._build_subfolder, dst="bin", keep_path=False)
        self.copy(
            "*.so*",
            src=self._build_subfolder,
            dst="lib",
            keep_path=False,
            symlinks=True,
        )
        self.copy("*.dylib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy("*.a", src=self._build_subfolder, dst="lib", keep_path=False)
        for name in ("shared", "static"):
            for extension in (".lib", ".so", ".dylib", ".a"):
                try:
                    tools.rename(
                        os.path.join(
                            self.package_folder,
                            "lib/rtlsdr_{}{}".format(name, extension),
                        ),
                        os.path.join(
                            self.package_folder, "lib/librtlsdr{}".format(extension)
                        ),
                    )
                except:
                    pass
            try:
                tools.rename(
                    os.path.join(self.package_folder, "bin/rtlsdr_{}.dll".format(name)),
                    os.path.join(self.package_folder, "bin/librtlsdr.dll"),
                )
            except:
                pass

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ("Linux", "FreeBSD", "SunOS"):
            self.cpp_info.system_libs.extend(["pthread", "m"])
        if self.options.shared:
            self.cpp_info.defines.extend(["rtlsdr_SHARED=1"])
        else:
            self.cpp_info.defines.extend(["rtlsdr_STATIC=1"])
