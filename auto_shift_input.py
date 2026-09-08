import ctypes
import sys
import threading
from ctypes import wintypes

import pystray
from PIL import Image, ImageDraw

user32 = ctypes.WinDLL("user32", use_last_error=True)
imm32 = ctypes.WinDLL("imm32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_INPUTLANGCHANGEREQUEST = 0x0050
WM_QUIT = 0x0012

VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
LLKHF_INJECTED = 0x0010

IME_CMODE_NATIVE = 0x0001
WM_IME_CONTROL = 0x0283
IMC_SETCONVERSIONMODE = 0x0002
IMC_SETOPENSTATUS = 0x0006
KLF_ACTIVATE = 0x00000001
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

class KeyboardHookData(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class GuiThreadInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]


LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class KeyboardInput(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class InputUnion(ctypes.Union):
    _fields_ = [("ki", KeyboardInput)]


class Input(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("input", InputUnion),
    ]

user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = wintypes.LPARAM
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, LowLevelKeyboardProc, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
user32.GetKeyboardLayout.restype = wintypes.HKL
user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
user32.LoadKeyboardLayoutW.restype = wintypes.HKL
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GuiThreadInfo)]
user32.GetGUIThreadInfo.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.SendMessageW.restype = wintypes.LPARAM
user32.PostMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.PostMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
user32.SendInput.argtypes = [
    wintypes.UINT,
    ctypes.POINTER(Input),
    ctypes.c_int,
]
user32.SendInput.restype = wintypes.UINT

kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

imm32.ImmGetContext.argtypes = [wintypes.HWND]
imm32.ImmGetContext.restype = wintypes.HANDLE
imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
imm32.ImmGetConversionStatus.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD),
]
imm32.ImmSetConversionStatus.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
]
imm32.ImmSetOpenStatus.argtypes = [wintypes.HANDLE, wintypes.BOOL]
imm32.ImmSetOpenStatus.restype = wintypes.BOOL
imm32.ImmGetDefaultIMEWnd.argtypes = [wintypes.HWND]
imm32.ImmGetDefaultIMEWnd.restype = wintypes.HWND


def is_notepad_window(window: wintypes.HWND) -> bool:
    process_id = wintypes.DWORD()
    if not user32.GetWindowThreadProcessId(window, ctypes.byref(process_id)):
        return False

    process = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION, False, process_id.value
    )
    if not process:
        return False

    try:
        path_buffer = ctypes.create_unicode_buffer(32768)
        path_length = wintypes.DWORD(len(path_buffer))
        if not kernel32.QueryFullProcessImageNameW(
            process, 0, path_buffer, ctypes.byref(path_length)
        ):
            return False
        return path_buffer.value.casefold().endswith("\\notepad.exe")
    finally:
        kernel32.CloseHandle(process)


def request_keyboard_layout(window: wintypes.HWND, to_chinese: bool) -> bool:
    layout_name = "00000404" if to_chinese else "00000409"
    target_layout = user32.LoadKeyboardLayoutW(layout_name, KLF_ACTIVATE)
    if not target_layout:
        print(f"無法載入鍵盤配置：{layout_name}。", file=sys.stderr)
        return False
    return bool(
        user32.PostMessageW(
            window,
            WM_INPUTLANGCHANGEREQUEST,
            0,
            target_layout,
        )
    )


def inject_shift(vk: int, key_up: bool) -> None:
    keyboard_input = Input()
    keyboard_input.type = INPUT_KEYBOARD
    keyboard_input.input.ki.wVk = vk
    keyboard_input.input.ki.dwFlags = KEYEVENTF_KEYUP if key_up else 0
    user32.SendInput(1, ctypes.byref(keyboard_input), ctypes.sizeof(Input))


def create_tray_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (32, 96, 160, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(245, 245, 245, 255))
    draw.text((18, 13), "A", fill=(32, 96, 160, 255))
    draw.text((18, 32), "中", fill=(32, 96, 160, 255))
    return image


def run_tray(main_thread_id: int, shutdown_event: threading.Event) -> None:
    def stop(icon, _item) -> None:
        shutdown_event.set()
        icon.stop()
        user32.PostThreadMessageW(main_thread_id, WM_QUIT, 0, 0)

    menu = pystray.Menu(
        pystray.MenuItem("Auto Shift Input", None, enabled=False),
        pystray.MenuItem("結束程式", stop),
    )
    icon = pystray.Icon(
        "auto_shift_input",
        create_tray_image(),
        "Auto Shift Input",
        menu,
    )
    icon.run()

def switch_language(to_chinese: bool) -> bool:
    # 左右Shift相反 改這裡
    switch_keyboard_layout = to_chinese
    to_chinese = bool(not to_chinese)

    
    foreground_window = user32.GetForegroundWindow()
    if not foreground_window:
        print("無法取得前景視窗。", file=sys.stderr)
        return False

    # 新版記事本使用 TSF；用鍵盤配置請求切換，避免走 IMM 相容路徑。
    if is_notepad_window(foreground_window):
        #print("偵測到新版記事本，使用鍵盤配置請求切換。")
        return request_keyboard_layout(foreground_window, switch_keyboard_layout)

    process_id = wintypes.DWORD()
    thread_id = user32.GetWindowThreadProcessId(
        foreground_window, ctypes.byref(process_id)
    )
    keyboard_layout = user32.GetKeyboardLayout(thread_id)
    language_id = keyboard_layout & 0xFFFF
    if language_id not in {0x0404, 0x0C04, 0x1404}:
        return request_keyboard_layout(foreground_window, switch_keyboard_layout)

    gui_info = GuiThreadInfo()
    gui_info.cbSize = ctypes.sizeof(gui_info)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_info)):
        print("無法取得 GUI 執行緒資訊。", file=sys.stderr)
        return False

    window = gui_info.hwndFocus or foreground_window
    context = imm32.ImmGetContext(window)
    if not context:
        #print("無法取得輸入法上下文。", file=sys.stderr)
        ime_window = imm32.ImmGetDefaultIMEWnd(foreground_window)
        if not ime_window:
            return False

        if to_chinese:
            user32.SendMessageW(
                ime_window, WM_IME_CONTROL, IMC_SETOPENSTATUS, 1
            )
            conversion_mode = IME_CMODE_NATIVE
            #print("已切換為中文輸入法。")
        else:
            conversion_mode = 0
        user32.SendMessageW(
            ime_window,
            WM_IME_CONTROL,
            IMC_SETCONVERSIONMODE,
            conversion_mode,
        )
        #print("已切換語言狀態。")
        return True

    conversion_mode = wintypes.DWORD()
    sentence_mode = wintypes.DWORD()
    try:
        if not imm32.ImmGetConversionStatus(
            context, ctypes.byref(conversion_mode), ctypes.byref(sentence_mode)
        ):
            return False

        if not imm32.ImmSetOpenStatus(context, True):
            return False

        current_native = bool(conversion_mode.value & IME_CMODE_NATIVE)
        if current_native == to_chinese:
            print("已經是目標語言狀態，無需切換。")
            return True

        if to_chinese:
            new_conversion_mode = conversion_mode.value | IME_CMODE_NATIVE
        else:
            new_conversion_mode = conversion_mode.value & ~IME_CMODE_NATIVE
        return bool(
            imm32.ImmSetConversionStatus(
                context, new_conversion_mode, sentence_mode.value
            )
        )
    finally:
        imm32.ImmReleaseContext(window, context)

# 追蹤 Shift 狀態
lshift_pressed = False
rshift_pressed = False
other_key_pressed = False
handled_lshift = False
handled_rshift = False

@LowLevelKeyboardProc
def keyboard_hook(code: int, message: int, data_pointer: int) -> int:
    global lshift_pressed, rshift_pressed, other_key_pressed
    global handled_lshift, handled_rshift

    if code >= 0:
        data = ctypes.cast(data_pointer, ctypes.POINTER(KeyboardHookData)).contents
        vk = data.vkCode

        if data.flags & LLKHF_INJECTED:
            return user32.CallNextHookEx(None, code, message, data_pointer)

        if message in {WM_KEYDOWN, WM_SYSKEYDOWN}:
            if vk == VK_LSHIFT:
                #print("Left Shift")
                if not lshift_pressed:
                    lshift_pressed = True
                    other_key_pressed = False
                    handled_lshift = False
                if is_notepad_window(user32.GetForegroundWindow()):
                    return 1
                
            elif vk == VK_RSHIFT:
                #print("Right Shift")
                if not rshift_pressed:
                    rshift_pressed = True
                    other_key_pressed = False
                    handled_rshift = False
                if is_notepad_window(user32.GetForegroundWindow()):
                    return 1
            else:
                # 當 Shift 按下期間按了其他鍵，標記為組合鍵（例如 Shift + A）
                #print(f"Other key pressed: {vk}")
                if lshift_pressed or rshift_pressed:
                    other_key_pressed = True
                    #inject_shift(VK_LSHIFT if lshift_pressed else VK_RSHIFT, False)

        elif message in {WM_KEYUP, WM_SYSKEYUP}:
            if vk == VK_LSHIFT:
                if lshift_pressed and not other_key_pressed:
                    #print("L Shift, process")
                    # 左 Shift 獨立按下並放開 -> 強制切換為中文
                    handled_lshift = switch_language(to_chinese=True)
                    #print(f"切換為英文: {bIsPass}")
                lshift_pressed = False
                handled_lshift = False
            elif vk == VK_RSHIFT:
                if rshift_pressed and not other_key_pressed:
                    #print("R Shift, process")
                    # 右 Shift 獨立按下並放開 -> 強制切換為英文
                    handled_rshift = switch_language(to_chinese=False)
                    #print(f"切換為中文: {bIsPass}")
                rshift_pressed = False
                handled_rshift = False

    # 永遠返回 CallNextHookEx，不阻斷正常的 Shift 按鍵功能（解決組合鍵失效問題）
    return user32.CallNextHookEx(None, code, message, data_pointer)

def main() -> int:
    if sys.platform != "win32":
        print("此工具只能在 Windows 執行。", file=sys.stderr)
        return 1

    # 保持對 callback 的引用，防止被 Python 垃圾回收
    global hook_proc
    hook_proc = keyboard_hook

    hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, hook_proc, None, 0)
    if not hook:
        error = ctypes.get_last_error()
        print(f"無法安裝鍵盤攔截器，Windows 錯誤碼：{error}", file=sys.stderr)
        return 1

    main_thread_id = kernel32.GetCurrentThreadId()
    shutdown_event = threading.Event()
    tray_thread = threading.Thread(
        target=run_tray,
        args=(main_thread_id, shutdown_event),
        daemon=True,
    )
    tray_thread.start()
    print("已啟用：單獨按【左 Shift】切換中文，單獨按【右 Shift】切換英文。")
    print("程式已在背景執行，請從右下角系統匣圖示選擇「結束程式」。")
    try:
        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWindowsHookEx(hook)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())