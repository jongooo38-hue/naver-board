"""KRX 상장법인 목록을 받아 template.html에 넣어 index.html을 만든다.

신규 상장 종목을 반영하려면 다시 실행: python build.py
"""
import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

KRX_URL = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
MARKET = {"유가": "코스피", "코스닥": "코스닥", "코넥스": "코넥스"}
KST = timezone(timedelta(hours=9))
HERE = Path(__file__).parent


def fetch_stocks():
    raw = urllib.request.urlopen(KRX_URL, timeout=30).read().decode("euc-kr", "replace")
    stocks = []
    for row in re.findall(r"<tr>(.*?)</tr>", raw, re.S)[1:]:
        cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) >= 3:
            name, market, code = cells[0], cells[1], cells[2]
            stocks.append([name, code, MARKET.get(market, market)])
    if len(stocks) < 2000:
        raise SystemExit(f"종목 수가 너무 적음({len(stocks)}) — KRX 응답 확인 필요")
    return stocks


def main():
    stocks = fetch_stocks()
    data = json.dumps(stocks, ensure_ascii=False, separators=(",", ":"))
    updated = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*STOCKS*/[]", data).replace('/*UPDATED*/""', json.dumps(updated))
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html 생성: {len(stocks)}종목")


if __name__ == "__main__":
    main()
