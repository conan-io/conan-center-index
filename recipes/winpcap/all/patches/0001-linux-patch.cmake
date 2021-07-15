--- wpcap/libpcap/pcap-linux.c
+++ wpcap/libpcap/pcap-linux.c
@@ -129,10 +129,10 @@
 #ifdef HAVE_REMOTE
 #include <pcap-remote.h>
 #endif
+#ifdef NEED_LINUX_SOCKIOS_H
+#include <linux/sockios.h>
+#endif
-
 /*
- * If PF_PACKET is defined, we can use {SOCK_RAW,SOCK_DGRAM}/PF_PACKET
- * sockets rather than SOCK_PACKET sockets.
  *
  * To use them, we include <linux/if_packet.h> rather than
  * <netpacket/packet.h>; we do so because
