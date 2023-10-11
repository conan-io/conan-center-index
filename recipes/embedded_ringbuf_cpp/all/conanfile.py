from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class EmbeddedRingbufcppConan(ConanFile):
    name = "embedded_ringbuf_cpp"
    description = "A simple C++ Ring (Circular) Buffer Queuing Library for Programming with Arduino's and other Embedded platforms"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wizard97/Embedded_RingBuf_CPP/"
    topics = ("ring buffer", "circular buffer", "queue", "data-structures", "header-only")
    
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        # embedded_ringbuf_cpp uses #warning preprocessor directive
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="RingBuf*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
