"""水戸市の天気を Open-Meteo から取得し、README の WEATHER ブロックを更新する。

標準ライブラリのみ使用。APIキー不要。
実行: python3 .github/scripts/update_weather.py
"""
import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    JST = ZoneInfo("Asia/Tokyo")
except Exception:  # フォールバック (tzdata が無い環境用)
    JST = timezone(timedelta(hours=9))

LAT, LON = 36.365, 140.471  # 水戸市
README = Path(__file__).resolve().parents[2] / "README.md"

# WMO Weather Code -> (絵文字, 日本語)
WMO = {
    0: ("☀️", "快晴"),
    1: ("🌤️", "ほぼ晴れ"),
    2: ("⛅", "晴れ時々曇り"),
    3: ("☁️", "曇り"),
    45: ("🌫️", "霧"),
    48: ("🌫️", "霧氷"),
    51: ("🌧️", "弱い霧雨"),
    53: ("🌧️", "霧雨"),
    55: ("🌧️", "強い霧雨"),
    56: ("🌧️", "弱い着氷性霧雨"),
    57: ("🌧️", "着氷性霧雨"),
    61: ("🌦️", "弱い雨"),
    63: ("☔", "雨"),
    65: ("🌧️", "強い雨"),
    66: ("🌧️", "弱い着氷性雨"),
    67: ("🌧️", "着氷性雨"),
    71: ("🌨️", "弱い雪"),
    73: ("❄️", "雪"),
    75: ("❄️", "強い雪"),
    77: ("🌨️", "霧雪"),
    80: ("🌦️", "弱いにわか雨"),
    81: ("☔", "にわか雨"),
    82: ("🌧️", "激しいにわか雨"),
    85: ("🌨️", "弱いにわか雪"),
    86: ("🌨️", "にわか雪"),
    95: ("⛈️", "雷雨"),
    96: ("⛈️", "雹を伴う雷雨"),
    99: ("⛈️", "雹を伴う雷雨"),
}


def fetch() -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&timezone=Asia%2FTokyo&forecast_days=1"
    )
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def main() -> None:
    data = fetch()
    cur = data["current"]
    daily = data["daily"]

    emoji, ja = WMO.get(cur["weather_code"], ("❓", "不明"))
    d_emoji, d_ja = WMO.get(daily["weather_code"][0], ("❓", "不明"))
    now = datetime.now(JST).strftime("%m-%d %H:%M")

    block = (
        "<!-- WEATHER:START -->\n"
        f"**水戸市** — {emoji} {ja}（今日: {d_emoji} {d_ja}）\n"
        "\n"
        "| 項目 | 値 |\n"
        "|---|---|\n"
        f"| 🌡 気温 | {cur['temperature_2m']:.1f}℃（体感 {cur['apparent_temperature']:.1f}℃） |\n"
        f"| 💧 湿度 | {cur['relative_humidity_2m']}% |\n"
        f"| 💨 風速 | {cur['wind_speed_10m']:.1f} m/s |\n"
        f"| 📈 今日の最高 / 最低 | {daily['temperature_2m_max'][0]:.1f}℃ / {daily['temperature_2m_min'][0]:.1f}℃ |\n"
        f"| ☂ 降水確率 | {daily['precipitation_probability_max'][0] if daily['precipitation_probability_max'][0] is not None else '--'}% |\n"
        f"| 🕒 更新 | {now} JST |\n"
        "<!-- WEATHER:END -->"
    )

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(r"<!-- WEATHER:START -->.*?<!-- WEATHER:END -->", re.DOTALL)
    if not pattern.search(text):
        raise SystemExit("WEATHER markers not found in README.md")
    README.write_text(pattern.sub(block, text, count=1), encoding="utf-8")
    print("README weather block updated.")


if __name__ == "__main__":
    main()
