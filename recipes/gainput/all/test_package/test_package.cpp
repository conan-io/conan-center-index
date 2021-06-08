#include <gainput/gainput.h>

int main() {
    enum Button
    {
        ButtonConfirm
    };

    gainput::InputManager manager;
    manager.SetDisplaySize(800, 600);
    const gainput::DeviceId keyboardId = manager.CreateDevice<gainput::InputDeviceKeyboard>();
    const gainput::DeviceId padId = manager.CreateDevice<gainput::InputDevicePad>();
    const gainput::DeviceId touchId = manager.CreateDevice<gainput::InputDeviceTouch>();

    gainput::InputMap map(manager);
    map.MapBool(ButtonConfirm, keyboardId, gainput::KeyReturn);
    map.MapBool(ButtonConfirm, padId, gainput::PadButtonA);
    map.MapBool(ButtonConfirm, touchId, gainput::Touch0Down);

    return 0;
}
