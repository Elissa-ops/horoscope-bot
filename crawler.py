import requests
from bs4 import BeautifulSoup

star_url_map = {
    '牡羊座': 'https://astro.click108.com.tw/daily_0.php?iAstro=0',
    '金牛座': 'https://astro.click108.com.tw/daily_1.php?iAstro=1',
    '雙子座': 'https://astro.click108.com.tw/daily_2.php?iAstro=2',
    '巨蟹座': 'https://astro.click108.com.tw/daily_3.php?iAstro=3',
    '獅子座': 'https://astro.click108.com.tw/daily_4.php?iAstro=4',
    '處女座': 'https://astro.click108.com.tw/daily_5.php?iAstro=5',
    '天秤座': 'https://astro.click108.com.tw/daily_6.php?iAstro=6',
    '天蠍座': 'https://astro.click108.com.tw/daily_7.php?iAstro=7',
    '射手座': 'https://astro.click108.com.tw/daily_8.php?iAstro=8',
    '摩羯座': 'https://astro.click108.com.tw/daily_9.php?iAstro=9',
    '水瓶座': 'https://astro.click108.com.tw/daily_10.php?iAstro=10',
    '雙魚座': 'https://astro.click108.com.tw/daily_11.php?iAstro=11'
}

def get_horoscope_by_name(star_name, category):
    url = star_url_map.get(star_name)
    if not url:
        return {"result": "找不到星座網址"}

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://astro.click108.com.tw/'
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
    except Exception as e:
        return {"result": f"連線失敗：{e}"}

    soup = BeautifulSoup(res.text, 'html.parser')
    content = soup.select_one(".TODAY_CONTENT")
    p_list = content.select("p") if content else []
    keyword_map = {
        "整體": "整體運勢",
        "愛情": "愛情運勢",
        "事業": "事業運勢",
        "財運": "財運運勢"
    }
    keyword = keyword_map.get(category, "")
    result_text = ""
    for idx, p in enumerate(p_list):
        text = p.get_text(strip=True)
        if keyword in text:
            next_text = p_list[idx+1].get_text(strip=True) if idx + 1 < len(p_list) else ""
            result_text = f"{text}{next_text}"
            break

    daily_word = soup.select_one(".TODAY_WORD")
    daily_quote = daily_word.get_text(strip=True) if daily_word else "祝你有美好的一天！"

    return {
        "result": result_text or "查無運勢內容",
        "daily_quote": daily_quote
    }
