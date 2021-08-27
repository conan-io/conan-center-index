self.cpp_info.components["experimental-bigquery"].requires = ["grpc_utils", "common", "cloud_bigquery_protos"]
self.cpp_info.components["experimental-bigquery"].libs = ["google_cloud_cpp_bigquery"]

self.cpp_info.components["bigtable"].requires = ["abseil::absl_memory", "bigtable_protos", "common", "grpc_utils", "grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["bigtable"].libs = ["google_cloud_cpp_bigtable"]

self.cpp_info.components["common"].requires = ["abseil::absl_any", "abseil::absl_flat_hash_map", "abseil::absl_memory", "abseil::absl_optional", "abseil::absl_time"]
self.cpp_info.components["common"].libs = ["google_cloud_cpp_common"]

self.cpp_info.components["experimental-firestore"].requires = ["common"]
self.cpp_info.components["experimental-firestore"].libs = ["google_cloud_cpp_firestore"]

self.cpp_info.components["bigtable_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "longrunning_operations_protos", "rpc_status_protos", "api_auth_protos"]
self.cpp_info.components["bigtable_protos"].libs = ["google_cloud_cpp_bigtable_protos"]

self.cpp_info.components["cloud_bigquery_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "rpc_status_protos", "api_http_protos"]
self.cpp_info.components["cloud_bigquery_protos"].libs = ["google_cloud_cpp_cloud_bigquery_protos"]

self.cpp_info.components["cloud_speech_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "longrunning_operations_protos", "rpc_status_protos"]
self.cpp_info.components["cloud_speech_protos"].libs = ["google_cloud_cpp_cloud_speech_protos"]

self.cpp_info.components["cloud_texttospeech_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos"]
self.cpp_info.components["cloud_texttospeech_protos"].libs = ["google_cloud_cpp_cloud_texttospeech_protos"]

self.cpp_info.components["iam_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos"]
self.cpp_info.components["iam_protos"].libs = ["google_cloud_cpp_iam_protos"]

self.cpp_info.components["pubsub_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos"]
self.cpp_info.components["pubsub_protos"].libs = ["google_cloud_cpp_pubsub_protos"]

self.cpp_info.components["spanner_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos", "longrunning_operations_protos", "rpc_status_protos"]
self.cpp_info.components["spanner_protos"].libs = ["google_cloud_cpp_spanner_protos"]

self.cpp_info.components["storage_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "iam_v1_iam_policy_protos", "iam_v1_policy_protos"]
self.cpp_info.components["storage_protos"].libs = ["google_cloud_cpp_storage_protos"]

self.cpp_info.components["longrunning_operations_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "rpc_status_protos"]
self.cpp_info.components["longrunning_operations_protos"].libs = ["google_cloud_cpp_longrunning_operations_protos"]

self.cpp_info.components["api_http_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_http_protos"].libs = ["google_cloud_cpp_api_http_protos"]

self.cpp_info.components["api_annotations_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_http_protos"]
self.cpp_info.components["api_annotations_protos"].libs = ["google_cloud_cpp_api_annotations_protos"]

self.cpp_info.components["api_auth_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
self.cpp_info.components["api_auth_protos"].libs = ["google_cloud_cpp_api_auth_protos"]

self.cpp_info.components["api_client_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_client_protos"].libs = ["google_cloud_cpp_api_client_protos"]

self.cpp_info.components["api_distribution_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_distribution_protos"].libs = ["google_cloud_cpp_api_distribution_protos"]

self.cpp_info.components["api_field_behavior_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_field_behavior_protos"].libs = ["google_cloud_cpp_api_field_behavior_protos"]

self.cpp_info.components["api_label_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_label_protos"].libs = ["google_cloud_cpp_api_label_protos"]

self.cpp_info.components["api_launch_stage_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_launch_stage_protos"].libs = ["google_cloud_cpp_api_launch_stage_protos"]

self.cpp_info.components["api_metric_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_launch_stage_protos", "api_label_protos"]
self.cpp_info.components["api_metric_protos"].libs = ["google_cloud_cpp_api_metric_protos"]

self.cpp_info.components["api_monitored_resource_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_launch_stage_protos", "api_label_protos"]
self.cpp_info.components["api_monitored_resource_protos"].libs = ["google_cloud_cpp_api_monitored_resource_protos"]

self.cpp_info.components["api_resource_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["api_resource_protos"].libs = ["google_cloud_cpp_api_resource_protos"]

self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_field_behavior_protos", "api_resource_protos", "rpc_status_protos"]
self.cpp_info.components["devtools_cloudtrace_v2_trace_protos"].libs = ["google_cloud_cpp_devtools_cloudtrace_v2_trace_protos"]

self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "devtools_cloudtrace_v2_trace_protos", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "rpc_status_protos"]
self.cpp_info.components["devtools_cloudtrace_v2_tracing_protos"].libs = ["google_cloud_cpp_devtools_cloudtrace_v2_tracing_protos"]

self.cpp_info.components["logging_type_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
self.cpp_info.components["logging_type_protos"].libs = ["google_cloud_cpp_logging_type_protos"]

self.cpp_info.components["logging_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_distribution_protos", "api_field_behavior_protos", "api_metric_protos", "api_monitored_resource_protos", "api_resource_protos", "logging_type_protos", "rpc_status_protos"]
self.cpp_info.components["logging_protos"].libs = ["google_cloud_cpp_logging_protos"]

self.cpp_info.components["monitoring_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_distribution_protos", "api_field_behavior_protos", "api_label_protos", "api_launch_stage_protos", "api_metric_protos", "api_monitored_resource_protos", "api_resource_protos", "rpc_status_protos", "type_calendar_period_protos"]
self.cpp_info.components["monitoring_protos"].libs = ["google_cloud_cpp_monitoring_protos"]

self.cpp_info.components["iam_v1_options_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos"]
self.cpp_info.components["iam_v1_options_protos"].libs = ["google_cloud_cpp_iam_v1_options_protos"]

self.cpp_info.components["iam_v1_policy_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "type_expr_protos"]
self.cpp_info.components["iam_v1_policy_protos"].libs = ["google_cloud_cpp_iam_v1_policy_protos"]

self.cpp_info.components["iam_v1_iam_policy_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "iam_v1_options_protos", "iam_v1_policy_protos"]
self.cpp_info.components["iam_v1_iam_policy_protos"].libs = ["google_cloud_cpp_iam_v1_iam_policy_protos"]

self.cpp_info.components["rpc_error_details_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["rpc_error_details_protos"].libs = ["google_cloud_cpp_rpc_error_details_protos"]

self.cpp_info.components["rpc_status_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "rpc_error_details_protos"]
self.cpp_info.components["rpc_status_protos"].libs = ["google_cloud_cpp_rpc_status_protos"]

self.cpp_info.components["type_calendar_period_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_calendar_period_protos"].libs = ["google_cloud_cpp_type_calendar_period_protos"]

self.cpp_info.components["type_color_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_color_protos"].libs = ["google_cloud_cpp_type_color_protos"]

self.cpp_info.components["type_date_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_date_protos"].libs = ["google_cloud_cpp_type_date_protos"]

self.cpp_info.components["type_datetime_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_datetime_protos"].libs = ["google_cloud_cpp_type_datetime_protos"]

self.cpp_info.components["type_dayofweek_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_dayofweek_protos"].libs = ["google_cloud_cpp_type_dayofweek_protos"]

self.cpp_info.components["type_expr_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_expr_protos"].libs = ["google_cloud_cpp_type_expr_protos"]

self.cpp_info.components["type_fraction_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_fraction_protos"].libs = ["google_cloud_cpp_type_fraction_protos"]

self.cpp_info.components["type_interval_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_interval_protos"].libs = ["google_cloud_cpp_type_interval_protos"]

self.cpp_info.components["type_latlng_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_latlng_protos"].libs = ["google_cloud_cpp_type_latlng_protos"]

self.cpp_info.components["type_localized_text_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_localized_text_protos"].libs = ["google_cloud_cpp_type_localized_text_protos"]

self.cpp_info.components["type_money_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_money_protos"].libs = ["google_cloud_cpp_type_money_protos"]

self.cpp_info.components["type_month_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_month_protos"].libs = ["google_cloud_cpp_type_month_protos"]

self.cpp_info.components["type_phone_number_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_phone_number_protos"].libs = ["google_cloud_cpp_type_phone_number_protos"]

self.cpp_info.components["type_postal_address_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_postal_address_protos"].libs = ["google_cloud_cpp_type_postal_address_protos"]

self.cpp_info.components["type_quaternion_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_quaternion_protos"].libs = ["google_cloud_cpp_type_quaternion_protos"]

self.cpp_info.components["type_timeofday_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf"]
self.cpp_info.components["type_timeofday_protos"].libs = ["google_cloud_cpp_type_timeofday_protos"]

self.cpp_info.components["cloud_dialogflow_v2_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "longrunning_operations_protos", "rpc_status_protos", "type_latlng_protos"]
self.cpp_info.components["cloud_dialogflow_v2_protos"].libs = ["google_cloud_cpp_cloud_dialogflow_v2_protos"]

self.cpp_info.components["cloud_dialogflow_v2beta1_protos"].requires = ["grpc::grpc++", "grpc::grpc", "protobuf::libprotobuf", "api_annotations_protos", "api_client_protos", "api_field_behavior_protos", "api_resource_protos", "longrunning_operations_protos", "rpc_status_protos", "type_latlng_protos"]
self.cpp_info.components["cloud_dialogflow_v2beta1_protos"].libs = ["google_cloud_cpp_cloud_dialogflow_v2beta1_protos"]

self.cpp_info.components["grpc_utils"].requires = ["abseil::absl_function_ref", "abseil::absl_memory", "abseil::absl_time", "rpc_status_protos", "common", "grpc::grpc++", "grpc::grpc"]
self.cpp_info.components["grpc_utils"].libs = ["google_cloud_cpp_grpc_utils"]

self.cpp_info.components["experimental-iam"].requires = ["grpc_utils", "common", "iam_protos"]
self.cpp_info.components["experimental-iam"].libs = ["google_cloud_cpp_iam"]

self.cpp_info.components["experimental-logging"].requires = ["grpc_utils", "common", "logging_protos"]
self.cpp_info.components["experimental-logging"].libs = ["google_cloud_cpp_logging"]

self.cpp_info.components["pubsub"].requires = ["grpc_utils", "common", "pubsub_protos", "abseil::absl_flat_hash_map"]
self.cpp_info.components["pubsub"].libs = ["google_cloud_cpp_pubsub"]

self.cpp_info.components["spanner"].requires = ["abseil::absl_fixed_array", "abseil::absl_memory", "abseil::absl_numeric", "abseil::absl_strings", "abseil::absl_time", "grpc_utils", "common", "spanner_protos"]
self.cpp_info.components["spanner"].libs = ["google_cloud_cpp_spanner"]

self.cpp_info.components["storage"].requires = ["abseil::absl_memory", "abseil::absl_strings", "abseil::absl_str_format", "abseil::absl_time", "abseil::absl_variant", "common", "nlohmann_json::nlohmann_json", "crc32c::crc32c", "curl::libcurl", "openssl::ssl", "openssl::crypto"]
self.cpp_info.components["storage"].libs = ["google_cloud_cpp_storage"]

