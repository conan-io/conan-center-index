#include <libnet.h>
#include <stdio.h>

int main()
{
    libnet_t *l = NULL;
    unsigned char enet_dst[6] = {0x0d, 0x0e, 0x0a, 0x0d, 0x00, 0x00};
    libnet_ptag_t t = libnet_autobuild_ethernet(
                        enet_dst,                   /* ethernet destination */
                        ETHERTYPE_ARP,              /* protocol type */
                        l);                         /* libnet handle */
    if (t != (-1)) {
        fprintf(stderr, "[-] Failed!\n");
        return 1;
    }

    fprintf(stderr, "[+] Passed!\n");
    return 0;
}
