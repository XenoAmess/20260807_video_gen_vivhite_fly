import os
import time
import requests

api_key = os.environ["MINIMAX_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}
BASE_URL = "https://api.minimaxi.com"
MODEL = "MiniMax-H2.3"


# --- 步骤 1: 发起视频生成任务 ---
# MiniMax-H3 使用多模态 content[] 结构：每个元素通过 type（text / image_url / video_url / audio_url）区分，
# 并可用 role 标注用途。以下四个函数分别对应文生视频、图生视频、首尾帧、多模态参考四种模式，
# 都会发起一个异步任务并返回唯一的 task_id。

def invoke_text_to_video() -> str:
    """（模式一）纯文本生成视频（t2va）。t2va 场景 ratio 必填且不能为 adaptive。"""
    url = f"{BASE_URL}/v2/video_generation"
    payload = {
        "model": MODEL,
        "content": [
            # type=text 为必填项，用于描述视频的动态内容。
            {"type": "text", "text": "镜头拍摄一个女性坐在咖啡馆里，女人抬头看着窗外，镜头缓缓移动拍摄到窗外的街道，画面呈现暖色调，色彩浓郁，氛围轻松惬意。"},
        ],
        "duration": 5,
        "resolution": "2K",
        "ratio": "16:9",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["task_id"]


def invoke_image_to_video() -> str:
    """（模式二）首帧图 + 文本生成视频（i2va）。"""
    url = f"{BASE_URL}/v2/video_generation"
    payload = {
        "model": MODEL,
        "content": [
            {"type": "text", "text": "Contemporary dance, the people in the picture are performing contemporary dance."},
            # role=first_frame 指定视频起始帧；图生视频场景下宽高比由输入图片决定，ratio 恒为 adaptive。
            {"type": "image_url", "image_url": {"url": "https://filecdn.minimax.chat/public/85c96368-6ead-4eae-af9c-116be878eac3.png"}, "role": "first_frame"},
        ],
        "duration": 5,
        "resolution": "2K",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["task_id"]


def invoke_start_end_to_video() -> str:
    """（模式三）首帧图 + 尾帧图 + 文本生成视频。"""
    url = f"{BASE_URL}/v2/video_generation"
    payload = {
        "model": MODEL,
        "content": [
            {"type": "text", "text": "A little girl grows up."},
            # role=first_frame 指定起始画面
            {"type": "image_url", "image_url": {"url": "https://filecdn.minimax.chat/public/fe9d04da-f60e-444d-a2e0-18ae743add33.jpeg"}, "role": "first_frame"},
            # role=last_frame 指定结束画面
            {"type": "image_url", "image_url": {"url": "https://filecdn.minimax.chat/public/97b7cd08-764e-4b8b-a7bf-87a0bd898575.jpeg"}, "role": "last_frame"},
        ],
        "duration": 5,
        "resolution": "2K",
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["task_id"]


def invoke_reference_to_video() -> str:
    """(Mode 4) Reference-to-video (r2va): combine reference images / videos / audio."""
    url = f"{BASE_URL}/v2/video_generation"
    payload = {
        "model": MODEL,
        "content": [
            {"type": "text", "text": "以视频1作为基础，保留动作，场景，神态等，只将视频中的人物替换为图1中的人物。 去除视频中底部的歌词字幕。"},
            {"type": "image_url", "image_url": {
                "url": "https://github.com/XenoAmess/20260807_video_gen_vivhite_fly/raw/refs/heads/master/raw_picture/BV1N84y1L7mh.png"},
             "role": "reference_image"},
            {"type": "video_url", "video_url": {
                "url": "https://github.com/XenoAmess/20260807_video_gen_vivhite_fly/raw/refs/heads/master/raw_video/raw_part1.mov"},
             "role": "reference_video"},
        ],
        "duration": 28,
        "resolution": "2K",
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    response.raise_for_status()
    return response.json()["task_id"]

# --- 步骤 2: 轮询查询任务状态 ---
# 视频生成是一个耗时过程，因此 API 设计为异步模式。
# 提交任务后，需使用 task_id 通过此函数进行轮询。任务成功后直接返回成片下载地址（content.url），无需再换 file_id。
def query_task_status(task_id: str) -> str:
    """根据 task_id 轮询任务状态，成功后返回成片下载地址。"""
    url = f"{BASE_URL}/v2/query/video_generation/{task_id}"
    while True:
        # 推荐的轮询间隔为 10 秒，以避免对服务器造成不必要的压力。
        time.sleep(10)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        task = response.json()["task"]
        status = task["status"]
        print(f"当前任务状态: {status}")
        # 成功时 task.content.url 即为成片下载地址。
        if status == "succeeded":
            return task["content"]["url"]
        # 终态失败：failed / cancelled。
        if status in ("failed", "cancelled"):
            raise Exception(f"视频生成未成功: status={status}, error={task.get('error')}")



# --- 步骤 3: 下载并保存视频文件 ---
# 任务成功后直接得到成片下载地址，下载内容并保存到本地即可。
def fetch_video(download_url: str):
    """下载成片并保存到本地。"""
    with open("output1.mp4", "wb") as f:
        video_response = requests.get(download_url)
        video_response.raise_for_status()
        f.write(video_response.content)
    print("视频已成功保存至 output.mp4")


# --- 主流程: 完整调用示例 ---
# 该部分演示了从发起任务到最终保存视频的完整调用链路。
if __name__ == "__main__":
    # 选择一种方式创建任务
    # task_id = invoke_text_to_video()  # 方式一：文生视频
    # task_id = invoke_image_to_video() # 方式二：图生视频
    # task_id = invoke_start_end_to_video() # 方式三: 根据首尾帧生成视频
    task_id = invoke_reference_to_video() # 方式四: 多模态参考生视频

    print(f"视频生成任务已提交，任务 ID: {task_id}")
    download_url = query_task_status(task_id)
    print(f"任务处理成功，成片地址: {download_url}")
    fetch_video(download_url)