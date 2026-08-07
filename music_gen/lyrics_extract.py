import requests
import json
import os

url = "https://api.minimaxi.com/v1/music_cover_preprocess"
api_key = os.environ.get("MINIMAX_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "music-cover",
    "audio_url": "https://github.com/XenoAmess/20260807_video_gen_vivhite_fly/raw/refs/heads/master/raw_music/original.m4a"
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

# 保存 cover_feature_id 并查看提取的歌词
cover_feature_id = result["cover_feature_id"]
formatted_lyrics = result["formatted_lyrics"]

print(f"特征 ID: {cover_feature_id}")
print(f"提取的歌词:\n{formatted_lyrics}")
