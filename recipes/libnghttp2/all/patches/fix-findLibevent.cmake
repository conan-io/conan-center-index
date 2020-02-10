--- cmake/FindLibevent.cmake
+++ cmake/FindLibevent.cmake
@@ -35,7 +35,7 @@
 )

 if(LIBEVENT_INCLUDE_DIR)
-  set(_version_regex "^#define[ \t]+_EVENT_VERSION[ \t]+\"([^\"]+)\".*")
+  set(_version_regex "^#define[ \t]+EVENT__VERSION[ \t]+\"([^\"]+)\".*")
   if(EXISTS "${LIBEVENT_INCLUDE_DIR}/event2/event-config.h")
     # Libevent 2.0
     file(STRINGS "${LIBEVENT_INCLUDE_DIR}/event2/event-config.h"
