#include <Windows.h>

static LRESULT CALLBACK WndProc(HWND hwnd,
    UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    LRESULT res = 1;
    switch (uMsg)
    {
    case WM_DESTROY:
        ::PostQuitMessage (0);
        break;
    default:
        res = ::DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    return res;
}

bool init_context()
{
    static const wchar_t * class_name = L"ConanOpenGL";
    static const wchar_t * window_name = L"Conan OpenGL";
    WNDCLASSEXW wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = ::GetModuleHandle(NULL);
    wc.hIcon = ::LoadIcon(0, IDI_APPLICATION);
    wc.hCursor = ::LoadCursor(0, IDC_ARROW);
    wc.hbrBackground = (HBRUSH) ::GetStockObject(WHITE_BRUSH);
    wc.lpszClassName = class_name;
    if (!::RegisterClassExW(&wc))
        return false;
    HWND hWnd = ::CreateWindowExW(0, class_name, window_name,
        WS_OVERLAPPEDWINDOW, 0, 0, 0, 0, NULL, NULL, wc.hInstance, NULL);
    if (!hWnd)
        return false;
    HDC hDC = ::GetDC(hWnd);
    if (!hDC)
        return false;
    PIXELFORMATDESCRIPTOR pfd = {0};
    pfd.nSize = sizeof(PIXELFORMATDESCRIPTOR);
    pfd.nVersion = 1;
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA;
    pfd.dwLayerMask = PFD_MAIN_PLANE;
    pfd.cColorBits = 32;
    pfd.cDepthBits = 16;
    int pixel_format = ::ChoosePixelFormat(hDC, &pfd);
    if(0 == pixel_format)
        return false;
    if (!::SetPixelFormat(hDC, pixel_format, &pfd))
        return false;
    HGLRC hGLRC = ::wglCreateContext(hDC);
    if (!hGLRC)
        return false;
    ::wglMakeCurrent(hDC, hGLRC);
    return true;
}
