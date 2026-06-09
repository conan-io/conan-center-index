import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2"


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # This list comes from tools/code-generation/api-description, which then generates the sdk sources
    # To generate for a new one, run the build once and check src/generated/src inside your build_folder, remove the common aws-sdk-cpp prefix
    # NON_GENERATED_CLIENT_LIST in src/cmake/sdks.cmake contains extra ones that should also be added here
    # and that's the list of sdks. Then join it to this one
    _sdks = (
        "AWSMigrationHub",
        "accessanalyzer",
        "account",
        "acm",
        "acm-pca",
        "aiops",
        "amp",
        "amplify",
        "amplifybackend",
        "amplifyuibuilder",
        "apigateway",
        "apigatewaymanagementapi",
        "apigatewayv2",
        "appconfig",
        "appconfigdata",
        "appfabric",
        "appflow",
        "appintegrations",
        "application-autoscaling",
        "application-insights",
        "application-signals",
        "applicationcostprofiler",
        "appmesh",
        "apprunner",
        "appstream",
        "appsync",
        "arc-region-switch",
        "arc-zonal-shift",
        "artifact",
        "athena",
        "auditmanager",
        "autoscaling",
        "autoscaling-plans",
        "awstransfer",
        "b2bi",
        "backup",
        "backup-gateway",
        "backupsearch",
        "batch",
        "bcm-dashboards",
        "bcm-data-exports",
        "bcm-pricing-calculator",
        "bcm-recommended-actions",
        "bedrock",
        "bedrock-agent",
        "bedrock-agent-runtime",
        "bedrock-agentcore",
        "bedrock-agentcore-control",
        "bedrock-data-automation",
        "bedrock-data-automation-runtime",
        "bedrock-runtime",
        "billing",
        "billingconductor",
        "braket",
        "budgets",
        "ce",
        "chatbot",
        "chime",
        "chime-sdk-identity",
        "chime-sdk-media-pipelines",
        "chime-sdk-meetings",
        "chime-sdk-messaging",
        "chime-sdk-voice",
        "cleanrooms",
        "cleanroomsml",
        "cloud9",
        "cloudcontrol",
        "clouddirectory",
        "cloudformation",
        "cloudfront",
        "cloudfront-keyvaluestore",
        "cloudhsm",
        "cloudhsmv2",
        "cloudsearch",
        "cloudsearchdomain",
        "cloudtrail",
        "cloudtrail-data",
        "codeartifact",
        "codebuild",
        "codecatalyst",
        "codecommit",
        "codeconnections",
        "codedeploy",
        "codeguru-reviewer",
        "codeguru-security",
        "codeguruprofiler",
        "codepipeline",
        "codestar-connections",
        "codestar-notifications",
        "cognito-identity",
        "cognito-idp",
        "cognito-sync",
        "comprehend",
        "comprehendmedical",
        "compute-optimizer",
        "config",
        "connect",
        "connect-contact-lens",
        "connectcampaigns",
        "connectcampaignsv2",
        "connectcases",
        "connectparticipant",
        "controlcatalog",
        "controltower",
        "cost-optimization-hub",
        "cur",
        "customer-profiles",
        "databrew",
        "dataexchange",
        "datapipeline",
        "datasync",
        "datazone",
        "dax",
        "deadline",
        "detective",
        "devicefarm",
        "devops-guru",
        "directconnect",
        "directory-service-data",
        "discovery",
        "dlm",
        "dms",
        "docdb",
        "docdb-elastic",
        "drs",
        "ds",
        "dsql",
        "dynamodb",
        "dynamodbstreams",
        "ebs",
        "ec2",
        "ec2-instance-connect",
        "ecr",
        "ecr-public",
        "ecs",
        "eks",
        "eks-auth",
        "elasticache",
        "elasticbeanstalk",
        "elasticfilesystem",
        "elasticloadbalancing",
        "elasticloadbalancingv2",
        "elasticmapreduce",
        "elastictranscoder",
        "email",
        "emr-containers",
        "emr-serverless",
        "entityresolution",
        "es",
        "eventbridge",
        "events",
        "evidently",
        "evs",
        "finspace",
        "finspace-data",
        "firehose",
        "fis",
        "fms",
        "forecast",
        "forecastquery",
        "frauddetector",
        "freetier",
        "fsx",
        "gamelift",
        "gameliftstreams",
        "geo-maps",
        "geo-places",
        "geo-routes",
        "glacier",
        "globalaccelerator",
        "glue",
        "grafana",
        "greengrass",
        "greengrassv2",
        "groundstation",
        "guardduty",
        "health",
        "healthlake",
        "iam",
        "identitystore",
        "imagebuilder",
        "importexport",
        "inspector",
        "inspector-scan",
        "inspector2",
        "internetmonitor",
        "invoicing",
        "iot",
        "iot-data",
        "iot-jobs-data",
        "iot-managed-integrations",
        "iotanalytics",
        "iotdeviceadvisor",
        "iotevents",
        "iotevents-data",
        "iotfleetwise",
        "iotsecuretunneling",
        "iotsitewise",
        "iotthingsgraph",
        "iottwinmaker",
        "iotwireless",
        "ivs",
        "ivs-realtime",
        "ivschat",
        "kafka",
        "kafkaconnect",
        "kendra",
        "kendra-ranking",
        "keyspaces",
        "keyspacesstreams",
        "kinesis",
        "kinesis-video-archived-media",
        "kinesis-video-media",
        "kinesis-video-signaling",
        "kinesis-video-webrtc-storage",
        "kinesisanalytics",
        "kinesisanalyticsv2",
        "kinesisvideo",
        "kms",
        "lakeformation",
        "lambda",
        "launch-wizard",
        "lex",
        "lex-models",
        "lexv2-models",
        "lexv2-runtime",
        "license-manager",
        "license-manager-linux-subscriptions",
        "license-manager-user-subscriptions",
        "lightsail",
        "location",
        "logs",
        "lookoutequipment",
        "m2",
        "machinelearning",
        "macie2",
        "mailmanager",
        "managedblockchain",
        "managedblockchain-query",
        "marketplace-agreement",
        "marketplace-catalog",
        "marketplace-deployment",
        "marketplace-entitlement",
        "marketplace-reporting",
        "marketplacecommerceanalytics",
        "mediaconnect",
        "mediaconvert",
        "medialive",
        "mediapackage",
        "mediapackage-vod",
        "mediapackagev2",
        "mediastore",
        "mediastore-data",
        "mediatailor",
        "medical-imaging",
        "memorydb",
        "meteringmarketplace",
        "mgn",
        "migration-hub-refactor-spaces",
        "migrationhub-config",
        "migrationhuborchestrator",
        "migrationhubstrategy",
        "monitoring",
        "mpa",
        "mq",
        "mturk-requester",
        "mwaa",
        "neptune",
        "neptune-graph",
        "neptunedata",
        "network-firewall",
        "networkflowmonitor",
        "networkmanager",
        "networkmonitor",
        "notifications",
        "notificationscontacts",
        "oam",
        "observabilityadmin",
        "odb",
        "omics",
        "opensearch",
        "opensearchserverless",
        "organizations",
        "osis",
        "outposts",
        "panorama",
        "partnercentral-selling",
        "payment-cryptography",
        "payment-cryptography-data",
        "pca-connector-ad",
        "pca-connector-scep",
        "pcs",
        "personalize",
        "personalize-events",
        "personalize-runtime",
        "pi",
        "pinpoint",
        "pinpoint-email",
        "pinpoint-sms-voice-v2",
        "pipes",
        "polly",
        "pricing",
        "proton",
        "qapps",
        "qbusiness",
        "qconnect",
        "quicksight",
        "ram",
        "rbin",
        "rds",
        "rds-data",
        "redshift",
        "redshift-data",
        "redshift-serverless",
        "rekognition",
        "repostspace",
        "resiliencehub",
        "resource-explorer-2",
        "resource-groups",
        "resourcegroupstaggingapi",
        "rolesanywhere",
        "route53",
        "route53-recovery-cluster",
        "route53-recovery-control-config",
        "route53-recovery-readiness",
        "route53domains",
        "route53profiles",
        "route53resolver",
        "rtbfabric",
        "rum",
        "s3",
        "s3-crt",
        "s3control",
        "s3outposts",
        "s3tables",
        "s3vectors",
        "sagemaker",
        "sagemaker-a2i-runtime",
        "sagemaker-edge",
        "sagemaker-featurestore-runtime",
        "sagemaker-geospatial",
        "sagemaker-metrics",
        "sagemaker-runtime",
        "savingsplans",
        "scheduler",
        "schemas",
        "sdb",
        "secretsmanager",
        "security-ir",
        "securityhub",
        "securitylake",
        "serverlessrepo",
        "service-quotas",
        "servicecatalog",
        "servicecatalog-appregistry",
        "servicediscovery",
        "sesv2",
        "shield",
        "signer",
        "simspaceweaver",
        "sms-voice",
        "snow-device-management",
        "snowball",
        "sns",
        "socialmessaging",
        "sqs",
        "ssm",
        "ssm-contacts",
        "ssm-guiconnect",
        "ssm-incidents",
        "ssm-quicksetup",
        "ssm-sap",
        "sso",
        "sso-admin",
        "sso-oidc",
        "states",
        "storagegateway",
        "sts",
        "supplychain",
        "support",
        "support-app",
        "swf",
        "synthetics",
        "taxsettings",
        "textract",
        "timestream-influxdb",
        "timestream-query",
        "timestream-write",
        "tnb",
        "transcribe",
        "transcribestreaming",
        "translate",
        "trustedadvisor",
        "verifiedpermissions",
        "voice-id",
        "vpc-lattice",
        "waf",
        "waf-regional",
        "wafv2",
        "wellarchitected",
        "wisdom",
        "workdocs",
        "workmail",
        "workmailmessageflow",
        "workspaces",
        "workspaces-instances",
        "workspaces-thin-client",
        "workspaces-web",
        "xray",
        # Extra modules that are not generated but exist upstream
        "access-management",
        "text-to-speech",
        "queues",
        "s3-encryption",
        "identity-management",
        "transfer"
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{sdk_name: [None, True, False] for sdk_name in _sdks},
    }
    default_options = {
        **{
            "shared": False,
            "fPIC": True,
            "min_size": False
        },
        **{sdk_name: None for sdk_name in _sdks},
        # Overrides
        "monitoring": True  # TODO: Clarify why monitoring is True by default
    }

    @property
    def _internal_requirements(self):
        # These modules and dependencies come from https://github.com/aws/aws-sdk-cpp/blob/1.11.691/cmake/sdksCommon.cmake#L136 and below
        # Additionally Core is added to all modules automatically
        return {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"],
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Main modules are true by default, but the user can set them to false
        for module in self._internal_requirements:
            setattr(self.options, module, True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # If the user does not specify a value for a specific sdk:
        # - Set it to True if it's a dependency of a main module that is set to True
        for module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(module):
                for dependency in dependencies:
                    # This returns a PackageOption object
                    # and checking if it's None should be done this way
                    if self.options.get_safe(dependency) == None:  # noqa
                        setattr(self.options, dependency, True)

        # - Otherwise set it to False
        # This way there are no None options past this method, and we can control default values
        # of the dependencies of the main modules but still give the user control over them
        for sdk_name in self._sdks:
            if self.options.get_safe(sdk_name) == None:  # noqa
                setattr(self.options, sdk_name, False)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # These versions come from prefetch_crt_dependency.sh,
        # don't bump them independently, check the file
        # Create the new versions for the dependencies in the order shown
        # in that script, they are mostly topo sorted
        self.requires("aws-crt-cpp/0.35.2", transitive_headers=True)
        self.requires("aws-c-auth/0.9.1")
        self.requires("aws-c-cal/0.9.8")
        self.requires("aws-c-common/0.12.5")
        self.requires("aws-c-compression/0.3.1")
        self.requires("aws-c-event-stream/0.5.7")
        self.requires("aws-c-http/0.10.5")
        self.requires("aws-c-io/0.23.2")
        self.requires("aws-c-mqtt/0.13.3")
        if self.options.get_safe("s3-crt"):
            self.requires("aws-c-s3/0.9.2")
        self.requires("aws-c-sdkutils/0.2.4")  # No mention of this in the code
        self.requires("aws-checksums/0.2.6")
        if self.settings.os != "Windows":
            # Used transitively in core/utils/crypto/openssl/CryptoImpl.h public header
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
            # Used transitively in core/http/curl/CurlHandleContainer.h public header
            self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)
        if self.settings.os == "Linux":
            # Pulseaudio -> libcap, libalsa only support linux, don't use pulseaudio on other platforms
            if self.options.get_safe("text-to-speech"):
                # Used transitively in text-to-speech/PulseAudioPCMOutputDriver.h public header
                self.requires("pulseaudio/14.2", transitive_headers=True, transitive_libs=True)
        # zlib is used if ENABLE_ZLIB_REQUEST_COMPRESSION is enabled, set ot ON by default
        self.requires("zlib/[>=1.2.11 <2]")

    def validate_build(self):
        if self.settings_build.os == "Windows" and self.settings.os == "Android":
            raise ConanInvalidConfiguration("Cross-building from Windows to Android is not supported")

        if (self.options.shared
                and self.settings.compiler == "gcc"
                and Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )

    def validate(self):
        if (is_msvc(self) and self.options.shared
                and not self.dependencies["aws-c-common"].options.shared):
            raise ConanInvalidConfiguration(f"{self.ref} with shared is not supported with aws-c-common static")

        # If the user has explicitly set a main module dependency to False,
        # error out if the main module itself is not also disabled
        for main_module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(main_module):
                for internal_requirement in dependencies:
                    if not self.options.get_safe(internal_requirement):
                        raise ConanInvalidConfiguration(f"-o={self.ref}:{main_module}=True requires -o={self.ref}:{internal_requirement}=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def _enabled_sdks(self):
        return [sdk for sdk in self._sdks
                if self.options.get_safe(sdk)]

    def generate(self):
        tc = CMakeToolchain(self)
        # All option() are defined before project() in upstream CMakeLists,
        # therefore we must use cache_variables

        build_only = ["core"] + self._enabled_sdks()
        tc.cache_variables["BUILD_ONLY"] = ";".join(build_only)

        tc.cache_variables["ENABLE_UNITY_BUILD"] = True
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["AUTORUN_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            tc.cache_variables["USE_OPENSSL"] = True
            tc.cache_variables["ENABLE_OPENSSL_ENCRYPTION"] = True

        tc.cache_variables["MINIMIZE_SIZE"] = self.options.min_size
        tc.cache_variables['AWS_STATIC_MSVC_RUNTIME_LIBRARY'] = self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime") == "static"

        if cross_building(self):
            tc.cache_variables["CURL_HAS_H2_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        if is_msvc(self):
            tc.preprocessor_definitions["_SILENCE_CXX17_OLD_ALLOCATOR_MEMBERS_DEPRECATION_WARNING"] = "1"
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _res_folder(self):
        return "res"

    def _create_project_cmake_module(self):
        # package files needed to build other components (e.g. aws-cdi-sdk) with this SDK
        dependant_files = [
            "cmake/compiler_settings.cmake",
            "cmake/initialize_project_version.cmake",
            "cmake/utilities.cmake",
            "cmake/sdk_plugin_conf.cmake",
            "toolchains/cmakeProjectConfig.cmake",
            "toolchains/pkg-config.pc.in",
            "src/aws-cpp-sdk-core/include/aws/core/VersionConfig.h"
        ]
        for file in dependant_files:
            copy(self, file, src=self.source_folder, dst=os.path.join(self.package_folder, self._res_folder))
            replace_in_file(
                self, os.path.join(self.package_folder, self._res_folder, file),
                "CMAKE_CURRENT_SOURCE_DIR", "AWS_NATIVE_SDK_ROOT",
                strict=False,
            )

        # avoid getting error from hook
        rename(self, os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConfig.cmake"),
               os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConf.cmake"))
        replace_in_file(
            self, os.path.join(self.package_folder, self._res_folder, "cmake", "utilities.cmake"),
            "cmakeProjectConfig.cmake", "cmakeProjectConf.cmake",
        )

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if is_msvc(self):
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            rm(self, "*.lib", os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_project_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AWSSDK")

        sdk_plugin_conf = os.path.join(self._res_folder, "cmake", "sdk_plugin_conf.cmake")
        self.cpp_info.set_property("cmake_build_modules", [sdk_plugin_conf])

        # core component
        self.cpp_info.components["core"].set_property("cmake_target_name", "AWS::aws-sdk-cpp-core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "aws-sdk-cpp-core")
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = [
            "aws-crt-cpp::aws-crt-cpp",
            "aws-c-auth::aws-c-auth",
            "aws-c-cal::aws-c-cal",
            "aws-c-common::aws-c-common",
            "aws-c-compression::aws-c-compression",
            "aws-c-event-stream::aws-c-event-stream",
            "aws-c-http::aws-c-http",
            "aws-c-io::aws-c-io",
            "aws-c-mqtt::aws-c-mqtt",
            "aws-checksums::aws-checksums",
            "zlib::zlib"
        ]

        self.cpp_info.components["core"].requires.extend([
            "aws-c-sdkutils::aws-c-sdkutils",
        ])

        for sdk in self._enabled_sdks():
            # TODO: We might want to set cmake_components if the targets dont match the component names
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"AWS::aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].set_property("pkg_config_name", f"aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: Remove, Conan 1 legacy, but this component now exists, it's part of the api
            component_alias = f"aws-sdk-cpp-{sdk}_alias"  # to emulate COMPONENTS names for find_package()
            self.cpp_info.components[component_alias].requires = [sdk]

        # specific system_libs, frameworks and requires of components
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs.extend([
                "winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"
            ])
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].system_libs.append("winmm")
        else:
            self.cpp_info.components["core"].requires.extend(["libcurl::curl", "openssl::openssl"])

        if self.settings.os == "Linux":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].requires.append("pulseaudio::pulseaudio")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("atomic")

        if self.options.get_safe("s3-crt"):
            self.cpp_info.components["s3-crt"].requires.append("aws-c-s3::aws-c-s3")

        if self.settings.os == "Macos":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].frameworks.extend(["CoreAudio", "AudioToolbox"])

        libcxx = stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["core"].system_libs.append(libcxx)

        self.cpp_info.components["plugin_scripts"].requires = ["core"]
        self.cpp_info.components["plugin_scripts"].builddirs.extend([
            os.path.join(self._res_folder, "cmake"),
            os.path.join(self._res_folder, "toolchains")])
