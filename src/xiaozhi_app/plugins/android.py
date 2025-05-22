from typing import Tuple
import json

try:
    from .. import rpc
except ImportError:
    import rpc  # Fallback for direct execution

class Uri:
    @staticmethod
    def parse(uri_str, rpc_client: rpc.GenericRpcClient = None) -> rpc.RpcObject:
        """解析URI字符串"""
        if rpc_client is None:
            rpc_client = rpc.GenericRpcClient()
        response = rpc_client.call_static_method("android.net.Uri", "parse", [uri_str])
        return rpc.RpcObject(rpc_client, response["instanceId"])

class Intent(rpc.RpcObject):
    # 预定义常用静态字段
    ACTION_VIEW = rpc.static_field("android.content.Intent", "ACTION_VIEW")
    FLAG_ACTIVITY_NEW_TASK = rpc.static_field(
        "android.content.Intent", "FLAG_ACTIVITY_NEW_TASK"
    )

    def __init__(self, action = None, rpc_client: rpc.GenericRpcClient = None):
        self.action = [action] if action else []
        super().__init__(rpc_client)

    def get_instance_id(self):
        if self.instance_id is None:
            self.instance_id = self.create_instance_id(
                "android.content.Intent", self.action
            )
        return self.instance_id

    def set_flags(self, flags):
        """设置标志位"""
        return self.call_method("setFlags", flags)

    def set_data(self, uri):
        """设置数据URI"""
        return self.call_method("setData", uri)


class FlashLight(rpc.RpcObject):
    def __init__(self, rpc_client: rpc.GenericRpcClient = None):
        super().__init__(rpc_client)

    def open(self):
        self.call_method("openFlashLight")

    def close(self):
        self.call_method("closeFlashLight")

    def set_message_loading(self, content: str):
        self.call_method("setMessageLoading", content)

    def add_message_robot(self, message: str):
        self.call_method("addMessageRobot", message)

    def send_message(self, message: str, show: bool = False):
        self.call_method("sendMessage", message, show)

    def set_state(self, state: dict) -> str:
        return self.call_method("setState", json.dumps(state))
    
    def get_current_agent(self) -> str:
        return self.call_method("getCurrentAgent")
    
    def get_agents(self) -> str:
        return self.call_method("getAgents")
    
    def get_tools(self) -> str:
        return self.call_method("getTools")
    
    def get_current_location(self, provider: str, id: str) -> str:
        return self.call_method("getCurrentLocation", provider, id)

    def get_instance_id(self):
        if self.instance_id is None:
            self.instance_id = self.get_static_field_instance_id(
                "cc.axyz.xiaozhi.rpc.model.Message", "Companion"
            )
        return self.instance_id

class AndroidApi(rpc.RpcObject):
    def __init__(self, rpc_client: rpc.GenericRpcClient = None):
        self._port = 0
        super().__init__(rpc_client)

    def start(self) -> bool:
        return self.call_method("startTermuxApi")

    def stop(self):
        self.call_method("stopTermuxApi")

    def isRunning(self) -> bool:
        return self.call_method("isTermuxApiRunning")

    def startService(self) -> Tuple[bool, str]:
        """
        启动Termux服务并解析返回的JSON数据。

        该方法调用 `startTermuxService` 方法获取JSON格式的响应字符串，
        尝试将其解析为JSON对象。如果解析成功，会提取其中的 `port` 信息并保存到类的私有属性 `_port` 中，
        同时返回服务启动是否成功的布尔值和可能的错误信息。如果解析失败，会返回 `False` 和解析错误信息。

        返回:
            Tuple[bool, str]: 一个元组，第一个元素表示服务是否成功启动，第二个元素是错误信息。
        """
        jsonStr = self.call_method("startTermuxService")
        try:
            jsonObj = json.loads(jsonStr)
            self._port = jsonObj.get("port", 0)
            return jsonObj["success"], jsonObj.get("error", "")
        except json.JSONDecodeError as e:
            return False, f"JSON解析错误: {str(e)}"

    def stopService(self) -> bool:
        """
        停止Termux服务并解析返回的JSON数据，判断服务是否成功停止。

        该方法调用 `stopTermuxService` 方法获取JSON格式的响应字符串，
        尝试将其解析为JSON对象。如果解析成功，会提取其中的 `success` 字段并返回该布尔值，
        表示服务是否成功停止。如果解析失败，会返回 `False`，表示服务停止操作可能未成功。

        返回:
            bool: 服务是否成功停止。
        """
        jsonStr = self.call_method("stopTermuxService")
        try:
            jsonObj = json.loads(jsonStr)
            return jsonObj["success"]
        except json.JSONDecodeError as e:
            return False

    @property
    def Port(self) -> int:
        return self._port

    def get_instance_id(self):
        if self.instance_id is None:
            self.instance_id = self.get_static_field_instance_id(
                "cc.axyz.xiaozhi.rpc.model.Message", "Companion"
            )
        return self.instance_id


# 定义你的RPC客户端类
class AndroidDevice(rpc.RpcObject):
    def __init__(self, rpc_client: rpc.GenericRpcClient = None):
        super().__init__(rpc_client, "activityContext")

    def open_flashlight(self):
        flash_light = FlashLight()
        flash_light.open()

    def close_flashlight(self):
        flash_light = FlashLight()
        flash_light.close()

    def set_message_loading(self, content: str):
        flash_light = FlashLight()
        flash_light.set_message_loading(content)

    def add_message_robot(self, message: str):
        flash_light = FlashLight()
        flash_light.add_message_robot(message)

    def send_message(self, message: str, show: bool = False):
        flash_light = FlashLight()
        flash_light.send_message(message, show)

    def set_state(self, state: dict) -> str:
        flash_light = FlashLight()
        return flash_light.set_state(state)
    
    def get_current_agent(self) -> str:
        flash_light = FlashLight()
        return flash_light.get_current_agent()
    
    def get_agents(self) -> str:
        flash_light = FlashLight()
        return flash_light.get_agents()
    
    def get_tools(self) -> str:
        flash_light = FlashLight()
        return flash_light.get_tools()
    
    def get_current_location(self, provider: str, id: str) -> str:
        flash_light = FlashLight()
        return flash_light.get_current_location(provider, id)

    def start_activity(self, intent: Intent):
        self.call_method("startActivity", intent)


def test_flashlight():
    # 调用方法
    try:
        device = AndroidDevice()
        device.open_flashlight()
        time.sleep(1)
        device.close_flashlight()
    except RpcError as e:
        print(f"操作失败: {e}")


def test_intent():
    device = AndroidDevice()
    # 创建ACTION_VIEW类型的Intent
    intent = Intent(Intent.ACTION_VIEW)
    # 设置标志位
    intent.set_flags(Intent.FLAG_ACTIVITY_NEW_TASK)
    # 创建URI
    uri = Uri.parse("baidumap://map/navi?query=故宫&src=andr.xiaomi.voiceassist")
    # uri = Uri.parse("baidumap://map/place/search?query=海底捞&src=andr.xiaomi.voiceassist")
    # 设置数据URI
    intent.set_data(uri)
    # 启动Activity
    device.start_activity(intent)


if __name__ == "__main__":
    import time
    import sys

    if len(sys.argv) != 2:
        print("Usage: python android.py <port>")
        exit(1)
    # test_flashlight()
    test_intent()
    # time.sleep(100)
    print("Done.")
