import json
import socket
import logging
from threading import Thread
from typing import Optional, Tuple, Any, Dict

api_logger = logging.getLogger('api')

class TermuxRpcClient(Thread):
    """
    Termux RPC 客户端基类
    """
    API_METHOD: Optional[str] = None  # 子类必须定义
    DEFAULT_TIMEOUT = 10  # 默认超时时间（秒）
    RECV_BUFFER_SIZE = 1024

    def __init__(self, host: str = "localhost", port: int = 80, timeout: int = DEFAULT_TIMEOUT):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._data = bytearray()
        self._result = None
        self._error: Optional[str] = None
        self._event_stop = False

    def _connect(self) -> None:
        """建立socket连接"""
        api_logger.debug(f"Connecting to {self.host}:{self.port}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self.timeout)
        self._socket.connect((self.host, self.port))

    def _send_request(self) -> None:
        """发送请求数据"""
        if self._socket:
            api_logger.debug(f"Sending request: {self.to_json()}")
            self._socket.sendall(self.to_json().encode() + b"\n")

    def to_dict(self) -> Dict:
        """转换为参数字典（子类可扩展）"""
        if not self.API_METHOD:
            raise NotImplementedError("API_METHOD must be defined in subclass")
        return {"extras": {"api_method": self.API_METHOD}}

    def to_json(self) -> str:
        """生成JSON参数"""
        return json.dumps(self.to_dict())

    def run(self) -> None:
        """主运行循环"""
        try:
            self._connect()
            self._send_request()
            self._receive_responses()
        except socket.timeout:
            self._error = "Connection timed out"
        except ConnectionRefusedError:
            self._error = "Connection refused"
        except Exception as e:
            self._error = f"Unexpected error: {str(e)}"
        finally:
            self.disconnect()

    def _receive_responses(self) -> None:
        """接收服务器响应"""
        if not self._socket:
            return

        while not self._event_stop:
            try:
                response = self._socket.recv(self.RECV_BUFFER_SIZE)
                if not response:
                    break

                for byte in response:
                    self._data.append(byte)
                    if byte == 10:  # 换行符
                        line = self._data.decode().strip()
                        self._data.clear()
                        self._process_line(line)

            except socket.timeout:
                self._error = "Receive timed out"
                break

    def _process_line(self, line: str) -> None:
        """处理单行响应"""
        try:
            data = json.loads(line)
            self._handle_response(data)
        except json.JSONDecodeError:
            self._error = f"Invalid JSON: {line}"
            api_logger.debug(f"JSON decode failed: {line}")

    def _handle_response(self, data: Dict) -> None:
        """响应处理模板方法"""
        if 'error' in data:
            self._handle_error(data['error'])
        elif 'permissions' in data:
            self._handle_permissions(data['permissions'])
        else:
            self._handle_data(data)

    def _handle_data(self, data: Dict) -> None:
        """数据处理（子类实现）"""
        raise NotImplementedError

    def _handle_error(self, error_msg: str) -> None:
        """错误处理"""
        self._error = error_msg
        api_logger.debug(f"API error: {error_msg}")
        self.disconnect()

    def _handle_permissions(self, permissions: list) -> None:
        """权限处理"""
        for perm in permissions:
            api_logger.debug(f"Permission: {perm['permission']}, Granted: {perm['granted']}")
            if not perm['granted']:
                self._error = f"Permission denied: {perm['permission']}"
                self.disconnect()

    def disconnect(self) -> None:
        """关闭连接"""
        self._event_stop = True
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                api_logger.debug(f"Close socket error: {str(e)}")
            finally:
                self._socket = None

    def execute(self) -> Tuple[Any, Optional[str]]:
        """执行命令并返回结果"""
        self.start()
        self.join(timeout=self.timeout)

        if self.is_alive():
            self._error = "Request timed out"
            self.disconnect()

        return self._result, self._error

class TermuxLocationCommand(TermuxRpcClient):
    """
    Termux 定位命令
    文档参考：https://wiki.termux.com/wiki/Termux-location
    """
    API_METHOD = "Location"
    ALLOWED_PROVIDERS = {"gps", "network", "passive"}
    ALLOWED_REQUESTS = {"once", "last", "updates"}

    def __init__(self, provider: str = "network", request: str = "once", **kwargs):
        super().__init__(**kwargs)
        self.provider = provider.lower()
        self.request = request.lower()
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """参数校验"""
        if self.provider not in self.ALLOWED_PROVIDERS:
            raise ValueError(
                f"Invalid provider: {self.provider}. "
                f"Allowed: {', '.join(self.ALLOWED_PROVIDERS)}"
            )

        if self.request not in self.ALLOWED_REQUESTS:
            raise ValueError(
                f"Invalid request: {self.request}. "
                f"Allowed: {', '.join(self.ALLOWED_REQUESTS)}"
            )

    def to_dict(self) -> Dict:
        """扩展参数字典"""
        params = super().to_dict()
        params['extras'].update({
            "provider": self.provider,
            "request": self.request
        })
        return params

    def _handle_data(self, data: Dict) -> None:
        """处理定位数据"""
        if 'latitude' in data:
            self._result = data
            self.disconnect()

class TermuxNotificationListCommand(TermuxRpcClient):
    """
    Termux 通知列表命令
    文档参考：https://wiki.termux.com/wiki/Termux-notification-list
    """
    API_METHOD = "NotificationList"

    def __init__(self, remove_keys = [], **kwargs):
        super().__init__(**kwargs)
        self._remove_keys = remove_keys

    def _handle_data(self, data: Dict) -> None:
        """处理通知列表数据"""
        self._result = data
        self.disconnect()

    def to_dict(self) -> Dict:
        """扩展参数字典"""
        params = super().to_dict()
        params['extras'].update({
            "keys": self._remove_keys
        })
        return params

class TermuxNotificationRemoveCommand(TermuxRpcClient):
    """
    Termux 通知移除命令
    文档参考：https://wiki.termux.com/wiki/Termux-notification-remove
    """
    API_METHOD = "NotificationRemove"

    def __init__(self, notification_id: str, **kwargs):
        super().__init__(**kwargs)
        self.notification_id = notification_id

    def to_dict(self) -> Dict:
        """扩展参数字典"""
        params = super().to_dict()
        params['extras']['id'] = self.notification_id
        return params

    def _handle_data(self, data: Dict) -> None:
        """处理移除响应"""
        self._result = data
        self.disconnect()
