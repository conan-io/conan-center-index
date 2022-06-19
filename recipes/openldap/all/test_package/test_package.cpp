/* ldapurl -- a tool for generating LDAP URLs */
/* $OpenLDAP$ */
/* This work is part of OpenLDAP Software <http://www.openldap.org/>.
 *
 * Copyright 2008-2021 The OpenLDAP Foundation.
 * Portions Copyright 2008 Pierangelo Masarati, SysNet
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted only as authorized by the OpenLDAP
 * Public License.
 *
 * A copy of this license is available in the file LICENSE in the
 * top-level directory of the distribution or, alternatively, at
 * <http://www.OpenLDAP.org/license.html>.
 */
/* Portions Copyright (c) 1992-1996 Regents of the University of Michigan.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms are permitted
 * provided that this notice is preserved and that due credit is given
 * to the University of Michigan at Ann Arbor.  The name of the
 * University may not be used to endorse or promote products derived
 * from this software without specific prior written permission.  This
 * software is provided ``as is'' without express or implied warranty.
 */
/* ACKNOWLEDGEMENTS:
 * This work was originally developed by Pierangelo Masarati
 * for inclusion in OpenLDAP software.
 */

#include <stdio.h>
#include <cstdlib>
#include "openldap.h"

static int do_uri_create(LDAPURLDesc *lud) {
  char *uri;

  if (lud->lud_scheme == NULL) {
    lud->lud_scheme = "ldap";
  }

  if (lud->lud_port == -1) {
    if (strcasecmp(lud->lud_scheme, "ldap") == 0) {
      lud->lud_port = LDAP_PORT;

    } else if (strcasecmp(lud->lud_scheme, "ldaps") == 0) {
      lud->lud_port = LDAPS_PORT;

    } else if (strcasecmp(lud->lud_scheme, "ldapi") == 0) {
      lud->lud_port = 0;

    } else {
      /* forgiving... */
      lud->lud_port = 0;
    }
  }

  if (lud->lud_scope == -1) {
    lud->lud_scope = LDAP_SCOPE_DEFAULT;
  }

  uri = ldap_url_desc2str(lud);

  if (uri == NULL) {
    fprintf(stderr, "unable to generate URI\n");
    exit(EXIT_FAILURE);
  }

  printf("%s\n", uri);
  free(uri);

  return 0;
}

int main() {
  LDAPURLDesc lud = {0};

  lud.lud_port = -1;
  lud.lud_scope = -1;

  return do_uri_create(&lud);
}
