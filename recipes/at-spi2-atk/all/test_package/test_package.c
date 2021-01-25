/*
 * AT-SPI - Assistive Technology Service Provider Interface
 * (Gnome Accessibility Project; https://wiki.gnome.org/Accessibility)
 *
 * Copyright (c) 2014 Samsung Electronics Co., Ltd.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

/*
 * Testing AT-SPI requires both a test application and AT client.
 * Test applications are built using the Dummy ATK implementation: MyAtk.
 * This file contains the entry point for all test applications.
 * The test will provide its own implementation of atk_get_root,
 * and as such provide all the application state for the test.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <glib.h>
#include <atk/atk.h>
#include <atk-bridge.h>



static GMainLoop *mainloop;

int main (int argc, char *argv[])
{
  atk_bridge_adaptor_init (NULL, NULL);

  mainloop = g_main_loop_new (NULL, FALSE);

  atk_bridge_adaptor_cleanup();

  return 0;
}
