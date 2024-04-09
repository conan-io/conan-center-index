#include <stdio.h>
#include <string.h>
#include <jwt/jwt.h>

int
main(int argc, char ** argv)
{
    const char res[] = "eyJhbGciOiJub25lIn0.eyJpYXQiOjE0NzU5ODA1NDUsIml"
                       "zcyI6ImZpbGVzLm1hY2xhcmEtbGxjLmNvbSIsInJlZiI6IlhYWFgtWVlZW"
                       "S1aWlpaLUFBQUEtQ0NDQyIsInN1YiI6InVzZXIwIn0.";
    jwt_t *jwt = NULL;
    char *out;
    int ret = jwt_new(&jwt);
    if(ret != 0){
        printf("failed to alloc jwt: %d", ret);
        return -1;
    }
    ret = jwt_add_grant(jwt, "iss", "files.maclara-llc.com");
    if(ret != 0){
        printf("failed to jwt_add_grant: %d", ret);
        return -1;
    }
    ret = jwt_add_grant(jwt, "sub", "user0");
    if(ret != 0){
        printf("failed to jwt_add_grant: %d", ret);
        return -1;
    }

    ret = jwt_add_grant(jwt, "ref", "XXXX-YYYY-ZZZZ-AAAA-CCCC");
    if(ret != 0){
        printf("failed to jwt_add_grant: %d", ret);
        return -1;
    }
    ret = jwt_add_grant_int(jwt, "iat", 1475980545L);
    if(ret != 0){
        printf("failed to jwt_add_grant: %d", ret);
        return -1;
    }
    out = jwt_encode_str(jwt);
    if(strcmp(out, res)){
        printf("except \"%s\", but got \"%s\"", res, out);
        return -1;
    }
    jwt_free_str(out);

    jwt_free(jwt);
    return 0;
}
