from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class FftRealConan(ConanFile):
    name = "fft-real"
    description = (
        "C++ template class computing DFT and inverse DFT "
        "(FFT algorithm) for arrays of real numbers. Portable ISO C++."
    )
    license = "WTFPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cyrilcode/fft-real"
    topics = ("fft", "dft", "ifft", "signal-processing", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "license.txt",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        for pattern in ("*.h", "*.hpp"):
            copy(self, pattern,
                 src=os.path.join(self.source_folder, "src"),
                 dst=os.path.join(self.package_folder, "include", "ffft"),
                 excludes="test*")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fft-real")
        self.cpp_info.set_property("cmake_target_name", "fft-real::fft-real")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
