from conans import ConanFile, CMake, tools
import os, shutil

class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "crossplateform", "amazon", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False]
        }
    default_options = {
            "shared": False,
            "fPIC": True,
            "min_size": False
        }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("aws-c-common/0.4.25")
        self.requires("aws-c-event-stream/0.1.5")
        self.requires("zlib/1.2.11")
        if self.settings.os != "Windows":
            self.requires("libcurl/7.71.1")
        if not self.settings.os in ["Windows", "Macos"]:
            self.requires("openssl/1.1.1i")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)
        # Keeping these unused folders make the source copy fail on Windows
        shutil.rmtree(self._source_subfolder + "/code-generation/generator")
        shutil.rmtree(self._source_subfolder + "/aws-cpp-sdk-core-tests")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_DEPS"] = False
        self._cmake.definitions["ENABLE_UNITY_BUILD"] = True
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["AUTORUN_UNIT_TESTS"] = False

        self._cmake.definitions["MINIMIZE_SIZE"] = self.options.min_size
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["FORCE_SHARED_CRT"] = "MD" in self.settings.compiler.runtime

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs.extend(["aws-cpp-sdk-core", "aws-c-event-stream", "aws-c-common", "aws-checksums"])
        sdks = ("access-management",
                "acm",
                "alexaforbusiness"
                "amplify"
                "apigateway",
                "application-autoscaling",
                "appstream",
                "appsync",
                "athena",
                "autoscaling",
                "batch",
                "budgets",
                "chime",
                "cloud9",
                "clouddirectory",
                "cloudformation",
                "cloudfront",
                "cloudhsmv2",
                "cloudsearch",
                "cloudtrail",
                "codebuild",
                "codecommit",
                "codedeploy",
                "codepipeline",
                "codestar",
                "cognito-identity",
                "cognito-idp",
                "cognito-sync",
                "comprehend",
                "config",
                "cur",
                "datapipeline",
                "dax",
                "devicefarm",
                "directconnect",
                "discovery",
                "dlm",
                "dms",
                "docdb",
                "ds",
                "dynamodb",
                "dynamodbstreams",
                "ec2",
                "ecr",
                "ecs",
                "eks",
                "elasticache",
                "elasticbeanstalk",
                "elasticfilesystem",
                "elasticloadbalancing",
                "elasticloadbalancingv2",
                "elasticmapreduce",
                "elastictranscoder",
                "email",
                "es",
                "events",
                "firehose",
                "fms",
                "fsx",
                "gamelift",
                "glacier",
                "globalaccelerator",
                "glue",
                "greengrass",
                "guardduty",
                "health",
                "iam",
                "identity-management",
                "importexport",
                "inspector",
                "iot-data",
                "iot-jobs-data",
                "iot",
                "kafka",
                "kinesis",
                "kinesisanalytics",
                "kinesisvideo",
                "kms",
                "lambda",
                "lex",
                "lightsail",
                "logs",
                "machinelearnings",
                "macie",
                "marketplace-entitlement",
                "marketplacecommerceanalytics",
                "mediaconvert",
                "medialive",
                "mediapackage",
                "mediastore",
                "mediatailor",
                "meteringmarketplace",
                "mobileanalytics",
                "monitoring",
                "mq",
                "mturk-requester",
                "neptune",
                "opsworks",
                "opsworkscm",
                "organizations",
                "pinpoint",
                "polly",
                "pricing",
                "queues",
                "quicksight",
                "ram",
                "rds",
                "redshift",
                "recognition",
                "resource-groups",
                "robomaker"
                "route53",
                "route53domains",
                "s3",
                "sagemaker",
                "sdb",
                "serverlessrepo"
                "servicecatalog",
                "servicediscovery",
                "shield",
                "signer",
                "sms",
                "snowball",
                "sns",
                "sqs",
                "ssm",
                "states",
                "storagegateway",
                "sts",
                "support",
                "swf",
                "text-to-speech",
                "texttract",
                "transcribe",
                "transfer",
                "translate",
                "waf",
                "workdocs",
                "worklink",
                "workmail",
                "workspaces",
                "xray"
               )
        for sdk in self.sdks:
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]
            self.cpp_info.components[sdk].includedirs = ["aws-cpp-sdk-" + sdk + "/include"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"])

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("atomic")

        lib_stdcpp = tools.stdcpp_library(self)
        if lib_stdcpp:
            self.cpp_info.system_libs.append(lib_stdcpp)
