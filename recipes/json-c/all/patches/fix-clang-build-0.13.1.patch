--- json_object.c.orig	2020-02-18 20:12:20 UTC
+++ json_object.c
@@ -698,9 +698,9 @@ int64_t json_object_get_int64(const struct json_object
 	case json_type_int:
 		return jso->o.c_int64;
 	case json_type_double:
-		if (jso->o.c_double >= INT64_MAX)
+		if (jso->o.c_double >= (double)INT64_MAX)
 			return INT64_MAX;
-		if (jso->o.c_double <= INT64_MIN)
+		if (jso->o.c_double <= (double)INT64_MIN)
 			return INT64_MIN;
 		return (int64_t)jso->o.c_double;
 	case json_type_boolean:
