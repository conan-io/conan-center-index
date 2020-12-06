/* Libnl example taken from stackoverflow:
 * https://stackoverflow.com/questions/42307658/how-to-get-ipv4-address-of-an-interface-using-libnl3-netlink-version-3-on-linu
*/

#include <netlink/netlink.h>
#include <netlink/route/link.h>
#include <netlink/route/addr.h>
#include <netlink/cache.h>
#include <netlink/route/addr.h>

#include <errno.h>



/*
gcc ipchange.c -o ipchange $(pkg-config --cflags --libs libnl-3.0 libnl-route-3.0 libnl-cli-3.0)
*/

#include <stdbool.h>

#define ADDR_STR_BUF_SIZE 80

void addr_cb(struct nl_object *p_nl_object, void *data) {

    int ifindex = (int) (intptr_t) data;  // this is the link index passed as a parm
    struct rtnl_addr *p_rtnl_addr;
    p_rtnl_addr = (struct rtnl_addr *) p_nl_object;
    int result;

    if (NULL == p_rtnl_addr) {
        /* error */
        printf("addr is NULL %d\n", errno);
        return;
    }

    // This routine is not mentioned in the doxygen help.
    // It is listed under Attributes, but no descriptive text.
    // this routine just returns p_rtnl_addr->a_ifindex
    int cur_ifindex = rtnl_addr_get_ifindex(p_rtnl_addr);
    if(cur_ifindex != ifindex) {
        // skip interaces where the index differs.
        return;
    }

    // Adding this to see if I can filter on ipv4 addr
    // this routine just returns p_rtnl_addr->a_family
    // this is not the one to use
    // ./linux/netfilter.h:    NFPROTO_IPV6   = 10,
    // ./linux/netfilter.h:    NFPROTO_IPV4   =  2,
    // this is the one to use
    // x86_64-linux-gnu/bits/socket.h
    // defines AF_INET6 = PF_INET6 = 10
    // defines AF_INET  = PF_INET  = 2
    result = rtnl_addr_get_family(p_rtnl_addr);
    // printf( "family is %d\n",result);
    if (AF_INET6 == result) {
    // early exit, I don't care about IPV6
    return;
    }

    // This routine just returns p_rtnl_addr->a_local
    struct nl_addr *p_nl_addr_local = rtnl_addr_get_local(p_rtnl_addr);
    if (NULL == p_nl_addr_local) {
        /* error */
        printf("rtnl_addr_get failed\n");
        return;
    }

    char addr_str[ADDR_STR_BUF_SIZE];
    const char *addr_s = nl_addr2str(p_nl_addr_local, addr_str, sizeof(addr_str));
    if (NULL == addr_s) {
        /* error */
        printf("nl_addr2str failed\n");
        return;
    }
    fprintf(stdout, "\naddr is: %s\n", addr_s);

}

int main(int argc, char **argv, char **envp) {

    int err, i;

    struct nl_sock *p_nl_sock;
    struct nl_cache *link_cache;
    struct nl_cache *addr_cache;

    struct rtnl_addr *p_rtnl_addr;
    struct nl_addr *p_nl_addr;
    struct nl_link *p_nl_link;
    struct rtnl_link *p_rtnl_link;

    char addr_str[ADDR_STR_BUF_SIZE];

    p_nl_sock = nl_socket_alloc();
    if (!p_nl_sock)
    {
        fprintf(stderr, "Could not allocate netlink socket.\n");
        exit(ENOMEM);
    }

    // Connect to socket
    if(err = nl_connect(p_nl_sock, NETLINK_ROUTE))
    {
        fprintf(stderr, "netlink error: %s\n", nl_geterror(err));
        p_nl_sock = NULL;
        exit(err);
    }

    // Either choice, the result below is a mac address
    err = rtnl_link_alloc_cache(p_nl_sock, AF_UNSPEC, &link_cache);
    //err = rtnl_link_alloc_cache(p_nl_sock, AF_INET, &link_cache);
    //err = rtnl_link_alloc_cache(p_nl_sock, IFA_LOCAL, &link_cache);
    if (0 != err)
    {
        /* error */
        printf("rtnl_link_alloc_cache failed: %s\n", nl_geterror(err));
        return(EXIT_FAILURE);
    }

    err = rtnl_addr_alloc_cache(p_nl_sock, &addr_cache);
    if (0 != err)
    {
        /* error */
        printf("rtnl_addr_alloc_cache failed: %s\n", nl_geterror(err));
        return(EXIT_FAILURE);
    }

    // This will iterate through the cache of ip's
    printf("Getting the list of interfaces by ip addr cache\n");
    int count = nl_cache_nitems(addr_cache);
    printf("addr_cache has %d items\n",count);
    struct nl_object *p_nl_object;
    p_nl_object = nl_cache_get_first(addr_cache);
    p_rtnl_addr = (struct rtnl_addr *) p_nl_object;
    for (i=0; i<count; i++)
    {
        // This routine just returns p_rtnl_addr->a_local
        struct nl_addr *p_nl_addr_local = rtnl_addr_get_local(p_rtnl_addr);
        if (NULL == p_nl_addr_local) {
            /* error */
            printf("rtnl_addr_get failed\n");
            return(EXIT_FAILURE);
        }

        int cur_ifindex = rtnl_addr_get_ifindex(p_rtnl_addr);
        printf("This is index %d\n",cur_ifindex);

        const char *addr_s = nl_addr2str(p_nl_addr_local, addr_str, sizeof(addr_str));
        if (NULL == addr_s)
        {
            /* error */
            printf("nl_addr2str failed\n");
            return(EXIT_FAILURE);
        }
        fprintf(stdout, "\naddr is: %s\n", addr_s);

        printf("%d\n",i);
        p_nl_object = nl_cache_get_next(p_nl_object);
        p_rtnl_addr = (struct rtnl_addr *) p_nl_object;
    }

    return(EXIT_SUCCESS);
}
