import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


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
    # and that's the list of sdks. The join it to the below one
    _sdks = (
        ('AWSMigrationHub', ['1.11.352']),
        ('access-management', ['1.9.234', '1.11.352']),
        ('accessanalyzer', ['1.9.234', '1.11.352']),
        ('account', ['1.11.352']),
        ('acm', ['1.9.234', '1.11.352']),
        ('acm-pca', ['1.9.234', '1.11.352']),
        ('alexaforbusiness', ['1.9.234']),
        ('amp', ['1.9.234', '1.11.352']),
        ('amplify', ['1.9.234', '1.11.352']),
        ('amplifybackend', ['1.9.234', '1.11.352']),
        ('amplifyuibuilder', ['1.11.352']),
        ('apigateway', ['1.9.234', '1.11.352']),
        ('apigatewaymanagementapi', ['1.9.234', '1.11.352']),
        ('apigatewayv2', ['1.9.234', '1.11.352']),
        ('appconfig', ['1.9.234', '1.11.352']),
        ('appconfigdata', ['1.11.352']),
        ('appfabric', ['1.11.352']),
        ('appflow', ['1.9.234', '1.11.352']),
        ('appintegrations', ['1.9.234', '1.11.352']),
        ('application-autoscaling', ['1.9.234', '1.11.352']),
        ('application-insights', ['1.9.234', '1.11.352']),
        ('application-signals', ['1.11.352']),
        ('applicationcostprofiler', ['1.11.352']),
        ('appmesh', ['1.9.234', '1.11.352']),
        ('apprunner', ['1.11.352']),
        ('appstream', ['1.9.234', '1.11.352']),
        ('appsync', ['1.9.234', '1.11.352']),
        ('apptest', ['1.11.352']),
        ('arc-zonal-shift', ['1.11.352']),
        ('artifact', ['1.11.352']),
        ('athena', ['1.9.234', '1.11.352']),
        ('auditmanager', ['1.9.234', '1.11.352']),
        ('autoscaling', ['1.9.234', '1.11.352']),
        ('autoscaling-plans', ['1.9.234', '1.11.352']),
        ('awstransfer', ['1.9.234', '1.11.352']),
        ('b2bi', ['1.11.352']),
        ('backup', ['1.9.234', '1.11.352']),
        ('backup-gateway', ['1.11.352']),
        ('batch', ['1.9.234', '1.11.352']),
        ('bcm-data-exports', ['1.11.352']),
        ('bedrock', ['1.11.352']),
        ('bedrock-agent', ['1.11.352']),
        ('bedrock-agent-runtime', ['1.11.352']),
        ('bedrock-runtime', ['1.11.352']),
        ('billingconductor', ['1.11.352']),
        ('braket', ['1.9.234', '1.11.352']),
        ('budgets', ['1.9.234', '1.11.352']),
        ('ce', ['1.9.234', '1.11.352']),
        ('chatbot', ['1.11.352']),
        ('chime', ['1.9.234', '1.11.352']),
        ('chime-sdk-identity', ['1.11.352']),
        ('chime-sdk-media-pipelines', ['1.11.352']),
        ('chime-sdk-meetings', ['1.11.352']),
        ('chime-sdk-messaging', ['1.11.352']),
        ('chime-sdk-voice', ['1.11.352']),
        ('cleanrooms', ['1.11.352']),
        ('cleanroomsml', ['1.11.352']),
        ('cloud9', ['1.9.234', '1.11.352']),
        ('cloudcontrol', ['1.11.352']),
        ('clouddirectory', ['1.9.234', '1.11.352']),
        ('cloudformation', ['1.9.234', '1.11.352']),
        ('cloudfront', ['1.9.234', '1.11.352']),
        ('cloudfront-keyvaluestore', ['1.11.352']),
        ('cloudhsm', ['1.9.234', '1.11.352']),
        ('cloudhsmv2', ['1.9.234', '1.11.352']),
        ('cloudsearch', ['1.9.234', '1.11.352']),
        ('cloudsearchdomain', ['1.9.234', '1.11.352']),
        ('cloudtrail', ['1.9.234', '1.11.352']),
        ('cloudtrail-data', ['1.11.352']),
        ('codeartifact', ['1.9.234', '1.11.352']),
        ('codebuild', ['1.9.234', '1.11.352']),
        ('codecatalyst', ['1.11.352']),
        ('codecommit', ['1.9.234', '1.11.352']),
        ('codeconnections', ['1.11.352']),
        ('codedeploy', ['1.9.234', '1.11.352']),
        ('codeguru-reviewer', ['1.9.234', '1.11.352']),
        ('codeguru-security', ['1.11.352']),
        ('codeguruprofiler', ['1.9.234', '1.11.352']),
        ('codepipeline', ['1.9.234', '1.11.352']),
        ('codestar', ['1.9.234', '1.11.352']),
        ('codestar-connections', ['1.9.234', '1.11.352']),
        ('codestar-notifications', ['1.9.234', '1.11.352']),
        ('cognito-identity', ['1.9.234', '1.11.352']),
        ('cognito-idp', ['1.9.234', '1.11.352']),
        ('cognito-sync', ['1.9.234', '1.11.352']),
        ('comprehend', ['1.9.234', '1.11.352']),
        ('comprehendmedical', ['1.9.234', '1.11.352']),
        ('compute-optimizer', ['1.9.234', '1.11.352']),
        ('config', ['1.9.234', '1.11.352']),
        ('connect', ['1.9.234', '1.11.352']),
        ('connect-contact-lens', ['1.9.234', '1.11.352']),
        ('connectcampaigns', ['1.11.352']),
        ('connectcases', ['1.11.352']),
        ('connectparticipant', ['1.9.234', '1.11.352']),
        ('controlcatalog', ['1.11.352']),
        ('controltower', ['1.11.352']),
        ('cost-optimization-hub', ['1.11.352']),
        ('cur', ['1.9.234', '1.11.352']),
        ('customer-profiles', ['1.9.234', '1.11.352']),
        ('databrew', ['1.9.234', '1.11.352']),
        ('dataexchange', ['1.9.234', '1.11.352']),
        ('datapipeline', ['1.9.234', '1.11.352']),
        ('datasync', ['1.9.234', '1.11.352']),
        ('datazone', ['1.11.352']),
        ('dax', ['1.9.234', '1.11.352']),
        ('deadline', ['1.11.352']),
        ('detective', ['1.9.234', '1.11.352']),
        ('devicefarm', ['1.9.234', '1.11.352']),
        ('devops-guru', ['1.9.234', '1.11.352']),
        ('directconnect', ['1.9.234', '1.11.352']),
        ('discovery', ['1.9.234', '1.11.352']),
        ('dlm', ['1.9.234', '1.11.352']),
        ('dms', ['1.9.234', '1.11.352']),
        ('docdb', ['1.9.234', '1.11.352']),
        ('docdb-elastic', ['1.11.352']),
        ('drs', ['1.11.352']),
        ('ds', ['1.9.234', '1.11.352']),
        ('dynamodb', ['1.9.234', '1.11.352']),
        ('dynamodbstreams', ['1.9.234', '1.11.352']),
        ('ebs', ['1.9.234', '1.11.352']),
        ('ec2', ['1.9.234', '1.11.352']),
        ('ec2-instance-connect', ['1.9.234', '1.11.352']),
        ('ecr', ['1.9.234', '1.11.352']),
        ('ecr-public', ['1.9.234', '1.11.352']),
        ('ecs', ['1.9.234', '1.11.352']),
        ('eks', ['1.9.234', '1.11.352']),
        ('eks-auth', ['1.11.352']),
        ('elastic-inference', ['1.9.234', '1.11.352']),
        ('elasticache', ['1.9.234', '1.11.352']),
        ('elasticbeanstalk', ['1.9.234', '1.11.352']),
        ('elasticfilesystem', ['1.9.234', '1.11.352']),
        ('elasticloadbalancing', ['1.9.234', '1.11.352']),
        ('elasticloadbalancingv2', ['1.9.234', '1.11.352']),
        ('elasticmapreduce', ['1.9.234', '1.11.352']),
        ('elastictranscoder', ['1.9.234', '1.11.352']),
        ('email', ['1.9.234', '1.11.352']),
        ('emr-containers', ['1.9.234', '1.11.352']),
        ('emr-serverless', ['1.11.352']),
        ('entityresolution', ['1.11.352']),
        ('es', ['1.9.234', '1.11.352']),
        ('eventbridge', ['1.9.234', '1.11.352']),
        ('events', ['1.9.234', '1.11.352']),
        ('evidently', ['1.11.352']),
        ('finspace', ['1.11.352']),
        ('finspace-data', ['1.11.352']),
        ('firehose', ['1.9.234', '1.11.352']),
        ('fis', ['1.11.352']),
        ('fms', ['1.9.234', '1.11.352']),
        ('forecast', ['1.9.234', '1.11.352']),
        ('forecastquery', ['1.9.234', '1.11.352']),
        ('frauddetector', ['1.9.234', '1.11.352']),
        ('freetier', ['1.11.352']),
        ('fsx', ['1.9.234', '1.11.352']),
        ('gamelift', ['1.9.234', '1.11.352']),
        ('glacier', ['1.9.234', '1.11.352']),
        ('globalaccelerator', ['1.9.234', '1.11.352']),
        ('glue', ['1.9.234', '1.11.352']),
        ('grafana', ['1.11.352']),
        ('greengrass', ['1.9.234', '1.11.352']),
        ('greengrassv2', ['1.9.234', '1.11.352']),
        ('groundstation', ['1.9.234', '1.11.352']),
        ('guardduty', ['1.9.234', '1.11.352']),
        ('health', ['1.9.234', '1.11.352']),
        ('healthlake', ['1.9.234', '1.11.352']),
        ('honeycode', ['1.9.234']),
        ('iam', ['1.9.234', '1.11.352']),
        ('identity-management', ['1.9.234', '1.11.352']),
        ('identitystore', ['1.9.234', '1.11.352']),
        ('imagebuilder', ['1.9.234', '1.11.352']),
        ('importexport', ['1.9.234', '1.11.352']),
        ('inspector', ['1.9.234', '1.11.352']),
        ('inspector-scan', ['1.11.352']),
        ('inspector2', ['1.11.352']),
        ('internetmonitor', ['1.11.352']),
        ('iot', ['1.9.234', '1.11.352']),
        ('iot-data', ['1.9.234', '1.11.352']),
        ('iot-jobs-data', ['1.9.234', '1.11.352']),
        ('iot1click-devices', ['1.9.234', '1.11.352']),
        ('iot1click-projects', ['1.9.234', '1.11.352']),
        ('iotanalytics', ['1.9.234', '1.11.352']),
        ('iotdeviceadvisor', ['1.9.234', '1.11.352']),
        ('iotevents', ['1.9.234', '1.11.352']),
        ('iotevents-data', ['1.9.234', '1.11.352']),
        ('iotfleethub', ['1.9.234', '1.11.352']),
        ('iotfleetwise', ['1.11.352']),
        ('iotsecuretunneling', ['1.9.234', '1.11.352']),
        ('iotsitewise', ['1.9.234', '1.11.352']),
        ('iotthingsgraph', ['1.9.234', '1.11.352']),
        ('iottwinmaker', ['1.11.352']),
        ('iotwireless', ['1.9.234', '1.11.352']),
        ('ivs', ['1.9.234', '1.11.352']),
        ('ivs-realtime', ['1.11.352']),
        ('ivschat', ['1.11.352']),
        ('kafka', ['1.9.234', '1.11.352']),
        ('kafkaconnect', ['1.11.352']),
        ('kendra', ['1.9.234', '1.11.352']),
        ('kendra-ranking', ['1.11.352']),
        ('keyspaces', ['1.11.352']),
        ('kinesis', ['1.9.234', '1.11.352']),
        ('kinesis-video-archived-media', ['1.9.234', '1.11.352']),
        ('kinesis-video-media', ['1.9.234', '1.11.352']),
        ('kinesis-video-signaling', ['1.9.234', '1.11.352']),
        ('kinesis-video-webrtc-storage', ['1.11.352']),
        ('kinesisanalytics', ['1.9.234', '1.11.352']),
        ('kinesisanalyticsv2', ['1.9.234', '1.11.352']),
        ('kinesisvideo', ['1.9.234', '1.11.352']),
        ('kms', ['1.9.234', '1.11.352']),
        ('lakeformation', ['1.9.234', '1.11.352']),
        ('lambda', ['1.9.234', '1.11.352']),
        ('launch-wizard', ['1.11.352']),
        ('lex', ['1.9.234', '1.11.352']),
        ('lex-models', ['1.9.234', '1.11.352']),
        ('lexv2-models', ['1.9.234', '1.11.352']),
        ('lexv2-runtime', ['1.9.234', '1.11.352']),
        ('license-manager', ['1.9.234', '1.11.352']),
        ('license-manager-linux-subscriptions', ['1.11.352']),
        ('license-manager-user-subscriptions', ['1.11.352']),
        ('lightsail', ['1.9.234', '1.11.352']),
        ('location', ['1.9.234', '1.11.352']),
        ('logs', ['1.9.234', '1.11.352']),
        ('lookoutequipment', ['1.11.352']),
        ('lookoutmetrics', ['1.11.352']),
        ('lookoutvision', ['1.9.234', '1.11.352']),
        ('m2', ['1.11.352']),
        ('machinelearning', ['1.9.234', '1.11.352']),
        ('macie', ['1.9.234']),
        ('macie2', ['1.9.234', '1.11.352']),
        ('mailmanager', ['1.11.352']),
        ('managedblockchain', ['1.9.234', '1.11.352']),
        ('managedblockchain-query', ['1.11.352']),
        ('marketplace-agreement', ['1.11.352']),
        ('marketplace-catalog', ['1.9.234', '1.11.352']),
        ('marketplace-deployment', ['1.11.352']),
        ('marketplace-entitlement', ['1.9.234', '1.11.352']),
        ('marketplacecommerceanalytics', ['1.9.234', '1.11.352']),
        ('mediaconnect', ['1.9.234', '1.11.352']),
        ('mediaconvert', ['1.9.234', '1.11.352']),
        ('medialive', ['1.9.234', '1.11.352']),
        ('mediapackage', ['1.9.234', '1.11.352']),
        ('mediapackage-vod', ['1.9.234', '1.11.352']),
        ('mediapackagev2', ['1.11.352']),
        ('mediastore', ['1.9.234', '1.11.352']),
        ('mediastore-data', ['1.9.234', '1.11.352']),
        ('mediatailor', ['1.9.234', '1.11.352']),
        ('medical-imaging', ['1.11.352']),
        ('memorydb', ['1.11.352']),
        ('meteringmarketplace', ['1.9.234', '1.11.352']),
        ('mgn', ['1.11.352']),
        ('migration-hub-refactor-spaces', ['1.11.352']),
        ('migrationhub-config', ['1.9.234', '1.11.352']),
        ('migrationhuborchestrator', ['1.11.352']),
        ('migrationhubstrategy', ['1.11.352']),
        ('mobile', ['1.9.234', '1.11.352']),
        ('mobileanalytics', ['1.9.234']),
        ('monitoring', ['1.9.234', '1.11.352']),
        ('mq', ['1.9.234', '1.11.352']),
        ('mturk-requester', ['1.9.234', '1.11.352']),
        ('mwaa', ['1.9.234', '1.11.352']),
        ('neptune', ['1.9.234', '1.11.352']),
        ('neptune-graph', ['1.11.352']),
        ('neptunedata', ['1.11.352']),
        ('network-firewall', ['1.9.234', '1.11.352']),
        ('networkmanager', ['1.9.234', '1.11.352']),
        ('networkmonitor', ['1.11.352']),
        ('nimble', ['1.11.352']),
        ('oam', ['1.11.352']),
        ('omics', ['1.11.352']),
        ('opensearch', ['1.11.352']),
        ('opensearchserverless', ['1.11.352']),
        ('opsworks', ['1.9.234', '1.11.352']),
        ('opsworkscm', ['1.9.234', '1.11.352']),
        ('organizations', ['1.9.234', '1.11.352']),
        ('osis', ['1.11.352']),
        ('outposts', ['1.9.234', '1.11.352']),
        ('panorama', ['1.11.352']),
        ('payment-cryptography', ['1.11.352']),
        ('payment-cryptography-data', ['1.11.352']),
        ('pca-connector-ad', ['1.11.352']),
        ('pca-connector-scep', ['1.11.352']),
        ('personalize', ['1.9.234', '1.11.352']),
        ('personalize-events', ['1.9.234', '1.11.352']),
        ('personalize-runtime', ['1.9.234', '1.11.352']),
        ('pi', ['1.9.234', '1.11.352']),
        ('pinpoint', ['1.9.234', '1.11.352']),
        ('pinpoint-email', ['1.9.234', '1.11.352']),
        ('pinpoint-sms-voice-v2', ['1.11.352']),
        ('pipes', ['1.11.352']),
        ('polly', ['1.9.234', '1.11.352']),
        # ('polly-sample', ['1.9.234']),  # This gets generated, but is only sample code
        ('pricing', ['1.9.234', '1.11.352']),
        ('privatenetworks', ['1.11.352']),
        ('proton', ['1.11.352']),
        ('qbusiness', ['1.11.352']),
        ('qconnect', ['1.11.352']),
        ('qldb', ['1.9.234', '1.11.352']),
        ('qldb-session', ['1.9.234', '1.11.352']),
        ('queues', ['1.9.234', '1.11.352']),
        ('quicksight', ['1.9.234', '1.11.352']),
        ('ram', ['1.9.234', '1.11.352']),
        ('rbin', ['1.11.352']),
        ('rds', ['1.9.234', '1.11.352']),
        ('rds-data', ['1.9.234', '1.11.352']),
        ('redshift', ['1.9.234', '1.11.352']),
        ('redshift-data', ['1.9.234', '1.11.352']),
        ('redshift-serverless', ['1.11.352']),
        ('rekognition', ['1.9.234', '1.11.352']),
        ('repostspace', ['1.11.352']),
        ('resiliencehub', ['1.11.352']),
        ('resource-explorer-2', ['1.11.352']),
        ('resource-groups', ['1.9.234', '1.11.352']),
        ('resourcegroupstaggingapi', ['1.9.234', '1.11.352']),
        ('robomaker', ['1.9.234', '1.11.352']),
        ('rolesanywhere', ['1.11.352']),
        ('route53', ['1.9.234', '1.11.352']),
        ('route53-recovery-cluster', ['1.11.352']),
        ('route53-recovery-control-config', ['1.11.352']),
        ('route53-recovery-readiness', ['1.11.352']),
        ('route53domains', ['1.9.234', '1.11.352']),
        ('route53profiles', ['1.11.352']),
        ('route53resolver', ['1.9.234', '1.11.352']),
        ('rum', ['1.11.352']),
        ('s3', ['1.9.234', '1.11.352']),
        ('s3-crt', ['1.9.234', '1.11.352']),
        ('s3-encryption', ['1.9.234', '1.11.352']),
        ('s3control', ['1.9.234', '1.11.352']),
        ('s3outposts', ['1.9.234', '1.11.352']),
        ('sagemaker', ['1.9.234', '1.11.352']),
        ('sagemaker-a2i-runtime', ['1.9.234', '1.11.352']),
        ('sagemaker-edge', ['1.9.234', '1.11.352']),
        ('sagemaker-featurestore-runtime', ['1.9.234', '1.11.352']),
        ('sagemaker-geospatial', ['1.11.352']),
        ('sagemaker-metrics', ['1.11.352']),
        ('sagemaker-runtime', ['1.9.234', '1.11.352']),
        ('savingsplans', ['1.9.234', '1.11.352']),
        ('scheduler', ['1.11.352']),
        ('schemas', ['1.9.234', '1.11.352']),
        ('sdb', ['1.9.234', '1.11.352']),
        ('secretsmanager', ['1.9.234', '1.11.352']),
        ('securityhub', ['1.9.234', '1.11.352']),
        ('securitylake', ['1.11.352']),
        ('serverlessrepo', ['1.9.234', '1.11.352']),
        ('service-quotas', ['1.9.234', '1.11.352']),
        ('servicecatalog', ['1.9.234', '1.11.352']),
        ('servicecatalog-appregistry', ['1.9.234', '1.11.352']),
        ('servicediscovery', ['1.9.234', '1.11.352']),
        ('sesv2', ['1.9.234', '1.11.352']),
        ('shield', ['1.9.234', '1.11.352']),
        ('signer', ['1.9.234', '1.11.352']),
        ('simspaceweaver', ['1.11.352']),
        ('sms', ['1.9.234', '1.11.352']),
        ('sms-voice', ['1.9.234', '1.11.352']),
        ('snow-device-management', ['1.11.352']),
        ('snowball', ['1.9.234', '1.11.352']),
        ('sns', ['1.9.234', '1.11.352']),
        ('sqs', ['1.9.234', '1.11.352']),
        ('ssm', ['1.9.234', '1.11.352']),
        ('ssm-contacts', ['1.11.352']),
        ('ssm-incidents', ['1.11.352']),
        ('ssm-sap', ['1.11.352']),
        ('sso', ['1.9.234', '1.11.352']),
        ('sso-admin', ['1.9.234', '1.11.352']),
        ('sso-oidc', ['1.9.234', '1.11.352']),
        ('states', ['1.9.234', '1.11.352']),
        ('storagegateway', ['1.9.234', '1.11.352']),
        ('sts', ['1.9.234', '1.11.352']),
        ('supplychain', ['1.11.352']),
        ('support', ['1.9.234', '1.11.352']),
        ('support-app', ['1.11.352']),
        ('swf', ['1.9.234', '1.11.352']),
        ('synthetics', ['1.9.234', '1.11.352']),
        ('taxsettings', ['1.11.352']),
        ('text-to-speech', ['1.9.234', '1.11.352']),
        ('textract', ['1.9.234', '1.11.352']),
        ('timestream-influxdb', ['1.11.352']),
        ('timestream-query', ['1.9.234', '1.11.352']),
        ('timestream-write', ['1.9.234', '1.11.352']),
        ('tnb', ['1.11.352']),
        ('transcribe', ['1.9.234', '1.11.352']),
        ('transcribestreaming', ['1.9.234', '1.11.352']),
        ('transfer', ['1.9.234', '1.11.352']),
        ('translate', ['1.9.234', '1.11.352']),
        ('trustedadvisor', ['1.11.352']),
        ('verifiedpermissions', ['1.11.352']),
        ('voice-id', ['1.11.352']),
        ('vpc-lattice', ['1.11.352']),
        ('waf', ['1.9.234', '1.11.352']),
        ('waf-regional', ['1.9.234', '1.11.352']),
        ('wafv2', ['1.9.234', '1.11.352']),
        ('wellarchitected', ['1.9.234', '1.11.352']),
        ('wisdom', ['1.11.352']),
        ('workdocs', ['1.9.234', '1.11.352']),
        ('worklink', ['1.9.234', '1.11.352']),
        ('workmail', ['1.9.234', '1.11.352']),
        ('workmailmessageflow', ['1.9.234', '1.11.352']),
        ('workspaces', ['1.9.234', '1.11.352']),
        ('workspaces-thin-client', ['1.11.352']),
        ('workspaces-web', ['1.11.352']),
        ('xray', ['1.9.234', '1.11.352'])
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{sdk_name: [None, True, False] for sdk_name, _ in _sdks},
    }
    default_options = {
        **{
            "shared": False,
            "fPIC": True,
            "min_size": False
        },
        **{sdk_name: None for sdk_name, _ in _sdks},
        # Overrides
        "monitoring": True  # TODO: Clarify why monitoring is True by default
    }

    short_paths = True

    @property
    def _internal_requirements(self):
        # These modules and dependencies come from https://github.com/aws/aws-sdk-cpp/blob/1.11.352/cmake/sdksCommon.cmake#L147 and below
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

        # Remove all sdk options not belonging to the current version
        for sdk_name, sdk_versions in self._sdks:
            if self.version not in sdk_versions:
                self.options.rm_safe(sdk_name)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # If the user does not specify a value for a specific sdk:
        # - Set it to True if it's a dependency of a main module that is set to True
        for module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(module):
                for dependency in dependencies:
                    # Don't listen to the linter, get_safe should be compared like this to None
                    # TODO: Remove str comparison when Conan 1 is disabled
                    if str(self.options.get_safe(dependency)) == "None":
                        setattr(self.options, dependency, True)

        # - Otherwise set it to False
        # This way there are no None options past this method, and we can control default values
        # of the dependencies of the main modules but still give the user control over them
        for sdk_name, sdk_versions in self._sdks:
            # == None is true for both "was deleted" and "was not set by the user",
            # ensure we only try to set the value to false for the latter
            if self.version in sdk_versions and self.options.get_safe(sdk_name) == None:
                setattr(self.options, sdk_name, False)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # These versions come from prefetch_crt_dependency.sh,
        # dont bump them independently, check the file
        if self.version == "1.11.352":
            self.requires("aws-crt-cpp/0.26.9", transitive_headers=True)
            self.requires("aws-c-auth/0.7.16")
            self.requires("aws-c-cal/0.6.14")
            self.requires("aws-c-common/0.9.15")
            self.requires("aws-c-compression/0.2.18")  # No mention of this in the code
            self.requires("aws-c-event-stream/0.4.2")
            self.requires("aws-c-http/0.8.1")
            self.requires("aws-c-io/0.14.7")
            self.requires("aws-c-mqtt/0.10.3")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.5.5")
            self.requires("aws-c-sdkutils/0.1.15")  # No mention of this in the code
            self.requires("aws-checksums/0.1.18")
            # missing aws-lc, but only needed as openssl replacement if USE_OPENSSL is OFF
        if self.version == "1.9.234":
            self.requires("aws-crt-cpp/0.17.1a", transitive_headers=True)
            self.requires("aws-c-auth/0.6.4")
            self.requires("aws-c-cal/0.5.12")
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-compression/0.2.14")
            self.requires("aws-c-event-stream/0.2.7")
            self.requires("aws-c-http/0.6.7")
            self.requires("aws-c-io/0.10.9")
            self.requires("aws-c-mqtt/0.7.8")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.1.26")
            self.requires("aws-checksums/0.1.12")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate_build(self):
        if self._settings_build.os == "Windows" and self.settings.os == "Android":
            raise ConanInvalidConfiguration("Cross-building from Windows to Android is not supported")

        if (self.options.shared
                and self.settings.compiler == "gcc"
                and Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )

    def validate(self):
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")
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

    def _enabled_sdks(self):
        for sdk in self._sdks:
            if self.options.get_safe(sdk[0]):
                yield sdk

    def generate(self):
        tc = CMakeToolchain(self)
        # All option() are defined before project() in upstream CMakeLists,
        # therefore we must use cache_variables

        build_only = ["core"]
        for sdk_name, _ in self._enabled_sdks():
            build_only.append(sdk_name)
        tc.cache_variables["BUILD_ONLY"] = ";".join(build_only)

        tc.cache_variables["ENABLE_UNITY_BUILD"] = True
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["AUTORUN_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            tc.cache_variables["USE_OPENSSL"] = True
            tc.cache_variables["ENABLE_OPENSSL_ENCRYPTION"] = True

        tc.cache_variables["MINIMIZE_SIZE"] = self.options.min_size
        if is_msvc(self):
            tc.cache_variables["FORCE_SHARED_CRT"] = not is_msvc_static_runtime(self)

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

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable warnings as errors
        if self.version == "1.9.234":
            replace_in_file(
                self, os.path.join(self.source_folder, "cmake", "compiler_settings.cmake"),
                'list(APPEND AWS_COMPILER_WARNINGS "-Wall" "-Werror" "-pedantic" "-Wextra")', "",
            )

    def build(self):
        self._patch_sources()
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
            "toolchains/pkg-config.pc.in"
        ]
        if Version(self.version) >= "1.11.352":
            dependant_files.append("src/aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        else:
            dependant_files.append("aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
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

        if Version(self.version) >= "1.11.352":
            self.cpp_info.components["core"].requires.extend([
                "aws-c-sdkutils::aws-c-sdkutils",
            ])

        for sdk, _ in self._enabled_sdks():
            # TODO: there is no way to properly emulate COMPONENTS names for
            #       find_package(AWSSDK COMPONENTS <sdk>) in set_property()
            #       right now: see https://github.com/conan-io/conan/issues/10258
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"AWS::aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].set_property("pkg_config_name", f"aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[sdk].names["cmake_find_package"] = "aws-sdk-cpp-" + sdk
            self.cpp_info.components[sdk].names["cmake_find_package_multi"] = "aws-sdk-cpp-" + sdk
            component_alias = f"aws-sdk-cpp-{sdk}_alias"  # to emulate COMPONENTS names for find_package()
            self.cpp_info.components[component_alias].names["cmake_find_package"] = sdk
            self.cpp_info.components[component_alias].names["cmake_find_package_multi"] = sdk
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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "AWSSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "AWSSDK"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["core"].names["cmake_find_package"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "aws-sdk-cpp-core"
        self.cpp_info.components["plugin_scripts"].build_modules["cmake_find_package"] = [sdk_plugin_conf]
        self.cpp_info.components["plugin_scripts"].build_modules["cmake_find_package_multi"] = [sdk_plugin_conf]
