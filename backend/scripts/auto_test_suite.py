# Auto test suite for video_tool
import time, requests, json, os

BASE_URL = os.getenv('NEXT_PUBLIC_API_URL', 'http://127.0.0.1:8000')

# Sample URLs (TikTok, YouTube)
SAMPLES = [
    {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@sampleuser/video/7201234567890123456"
    },
    {
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
]

REPORT_LINES = []

def submit_job(sample):
    if sample["platform"] == "tiktok":
        endpoint = f"{BASE_URL}/api/videos/process-reup"
        payload = {
            "source_url": sample["url"],
            "target_platform": "tiktok",
            "video_type": "short",
            "duration": 60,
            "add_subtitles": True,
            "add_ai_narration": True,
            "add_text_overlay": False,
            "remove_watermark": True,
            "add_background_music": False,
            "bgm_style": "cheerful",
            "normalize_audio": True,
            "processing_flow": "auto"
        }
    else:
        endpoint = f"{BASE_URL}/api/youtube/analyze"
        payload = {
            "youtube_url": sample["url"],
            "include_transcript": True,
            "include_channel_analysis": False,
            "min_score_threshold": 6.0,
            "target_platforms": ["youtube", "tiktok", "facebook"]
        }
    resp = requests.post(endpoint, json=payload)
    resp.raise_for_status()
    return resp.json()["job_id"]

def poll_status(job_id):
    status_url = f"{BASE_URL}/api/videos/job/{job_id}"
    while True:
        r = requests.get(status_url)
        r.raise_for_status()
        data = r.json()
        if data["status"] in ("COMPLETED", "FAILED"):
            return data
        time.sleep(5)

def run():
    for sample in SAMPLES:
        try:
            job_id = submit_job(sample)
            result = poll_status(job_id)
            quality = "✅" if result["status"] == "COMPLETED" else "❌"
            output_url = result.get("output_url", "N/A")
            REPORT_LINES.append(f"| {sample['url']} | {sample['platform']} | {result.get('steps', [])} | {output_url} | {quality} |")
        except Exception as e:
            REPORT_LINES.append(f"| {sample['url']} | {sample['platform']} | error | N/A | ❌ ({e}) |")
    report_path = os.path.join(os.getenv('GEMINI_BRAIN_PATH', ''), 'auto_test_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Auto Test Report\n\n")
        f.write("| Original URL | Platform | Steps (raw) | Output URL | Quality |\n")
        f.write("|---|---|---|---|---|\n")
        for line in REPORT_LINES:
            f.write(line + "\n")
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    run()
