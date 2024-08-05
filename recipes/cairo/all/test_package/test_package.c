#include <cairo.h>
#include <cairo-version.h>
#include <stdio.h>

#if defined(WIN32) && CAIRO_HAS_WIN32_SURFACE && CAIRO_HAS_WIN32_FONT

#include <cairo-win32.h>
#include <Windows.h>

#endif

int main()
{
#if defined(WIN32) && CAIRO_HAS_WIN32_SURFACE && CAIRO_HAS_WIN32_FONT

    HDC hDC = GetDC(0);
    if (hDC)
    {
        cairo_surface_t * surface = cairo_win32_surface_create(hDC);
        if (surface)
        {
            HFONT hFont = (HFONT)GetStockObject(SYSTEM_FONT);
            cairo_font_face_t* font = cairo_win32_font_face_create_for_hfont(hFont);
            if (font)
                cairo_font_face_destroy(font);

            cairo_surface_destroy(surface);
        }
        ReleaseDC(0, hDC);
    }
#endif

    printf("cairo version is %s\n", cairo_version_string());

    return 0;
}
