from conans import ConanFile

class TestPackage(ConanFile):
    
    def test(self):
        self.run("doxygen -version", run_environment=True)