from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import load
import os
import tarfile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tarfile.open("test.tar", "w", format=tarfile.GNU_FORMAT) as f:
            import io
            bio = io.BytesIO()
            bio.write(b"secret text\n")
            tarinfo = tarfile.TarInfo("hello_world")
            tarinfo.size = bio.tell()
            import time
            tarinfo.mtime = time.time()
            bio.seek(0)
            f.addfile(tarinfo, bio)

        if can_run(self):
            if os.path.exists("hello_world"):
                raise ConanException("file extracted by tar archive should not exist yet")
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(f"{bin_path} test.tar", env="conanrun")
            if not os.path.exists("hello_world"):
                raise ConanException("file not extracted")
            extracted_text = load(self, "hello_world")
            if extracted_text != "secret text\n":
                raise ConanException(f"File not loaded correctly. Got \"{repr(extracted_text)}\"")

            self.run("libtar -t test.tar", env="conanrun")
