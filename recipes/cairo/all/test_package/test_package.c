#include <cairo.h>
#include <cairo-version.h>
#include <stdio.h>

#if CAIRO_HAS_FT_FONT && CAIRO_HAS_FC_FONT
#include <cairo-ft.h>
#endif

#if defined(WIN32) && CAIRO_HAS_WIN32_SURFACE && CAIRO_HAS_WIN32_FONT

#include <cairo-win32.h>
#include <windows.h>

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

#if CAIRO_HAS_FT_FONT && CAIRO_HAS_FC_FONT
    FcPattern *font_pattern = FcPatternCreate();
    if (font_pattern == NULL)
        return 1;

    cairo_font_face_t *font_face = cairo_ft_font_face_create_for_pattern(font_pattern);
    cairo_status_t font_status = cairo_font_face_status(font_face);
    cairo_font_face_destroy(font_face);
    FcPatternDestroy(font_pattern);
    if (font_status != CAIRO_STATUS_SUCCESS)
        return 1;
#endif

    printf("cairo version is %s\n", cairo_version_string());

    return 0;
}
