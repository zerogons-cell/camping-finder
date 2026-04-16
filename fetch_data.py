import urllib.request
import urllib.parse
import json
import os
import time

API_KEY = os.environ.get('API_KEY', '')
BASE_URL = 'https://apis.data.go.kr/B551011/GoCamping'

def fetch_all_camping():
    all_items = []
    page = 1
    num_of_rows = 500

    while True:
        params = urllib.parse.urlencode({
            'serviceKey': API_KEY,
            'numOfRows': num_of_rows,
            'pageNo': page,
            'MobileOS': 'ETC',
            'MobileApp': 'CampingFinder',
            '_type': 'json',
        })
        url = f'{BASE_URL}/basedList?{params}'

        try:
            with urllib.request.urlopen(url, timeout=30) as res:
                data = json.loads(res.read().decode('utf-8'))
        except Exception as e:
            print(f'페이지 {page} 오류: {e}')
            break

        body = data.get('response', {}).get('body', {})
        items = body.get('items', {}).get('item', [])

        if not items:
            break
        if not isinstance(items, list):
            items = [items]

        all_items.extend(items)
        total = body.get('totalCount', 0)
        print(f'페이지 {page} 수집: {len(items)}개 (총 {len(all_items)}/{total})')

        if len(all_items) >= total:
            break

        page += 1
        time.sleep(0.5)  # API 과부하 방지

    return all_items

def main():
    print('캠핑장 데이터 수집 시작...')
    items = fetch_all_camping()
    print(f'총 {len(items)}개 캠핑장 수집 완료')

    # 필요한 필드만 추출해서 용량 줄이기
    cleaned = []
    for c in items:
        cleaned.append({
            'facltNm':    c.get('facltNm', ''),
            'doNm':       c.get('doNm', ''),
            'sigunguNm':  c.get('sigunguNm', ''),
            'addr1':      c.get('addr1', ''),
            'tel':        c.get('tel', ''),
            'induty':     c.get('induty', ''),
            'intro':      c.get('intro', ''),
            'lineIntro':  c.get('lineIntro', ''),
            'sbrsCl':     c.get('sbrsCl', ''),
            'extshrCl':   c.get('extshrCl', ''),
            'animalCmgCl':c.get('animalCmgCl', ''),
            'gnrlSiteCo': c.get('gnrlSiteCo', ''),
            'autoSiteCo': c.get('autoSiteCo', ''),
            'glampSiteCo':c.get('glampSiteCo', ''),
            'caravSiteCo':c.get('caravSiteCo', ''),
            'mapX':       c.get('mapX', ''),
            'mapY':       c.get('mapY', ''),
            'homepage':   c.get('homepage', ''),
        })

    output = {
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'total': len(cleaned),
        'items': cleaned
    }

    with open('camping_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = os.path.getsize('camping_data.json') / 1024
    print(f'camping_data.json 저장 완료 ({size_kb:.1f} KB)')

if __name__ == '__main__':
    main()
