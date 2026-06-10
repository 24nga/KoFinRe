"""Download RFP pages and attachments per organization folder."""
import os, sys, io, json, re, csv, time
from urllib.parse import urljoin, urlparse, unquote, parse_qs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup

BASE = r'C:\Users\heen1\Desktop\RFP_자료_56건'
ITEMS = json.load(open(r'C:\Users\heen1\Desktop\assist\rfp_list.json', encoding='utf-8'))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36',
    'Accept-Language': 'ko,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def safe(s, maxlen=80):
    s = str(s) if s is not None else ''
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', s).strip()
    return s[:maxlen] if len(s) > maxlen else s

def org_folder(org):
    from collections import defaultdict
    by_org = defaultdict(list)
    for it in ITEMS: by_org[it['org']].append(it)
    order = sorted(by_org.keys(), key=lambda o: -len(by_org[o]))
    idx = order.index(org) + 1
    return os.path.join(BASE, f"{idx:02d}_{safe(org)}")

ATTACH_EXTS = ('.pdf', '.hwp', '.hwpx', '.zip', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt')

def find_attachments(html, base_url):
    """Return list of (label, abs_url) for attachment links found in the page."""
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    seen = set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('#') or href.lower().startswith('javascript'):
            # Try to capture javascript downloadFile() patterns later
            txt = a.get_text(strip=True)
            m = re.search(r"(?:fnFileDown|downloadFile|fileDown|fnDownload)\(\s*['\"]?([\w\-/.]+)['\"]?\s*[,)]", href)
            if m:
                pass  # Site-specific; skip generic
            continue
        full = urljoin(base_url, href)
        low = full.lower()
        label = a.get_text(strip=True) or os.path.basename(urlparse(full).path)
        # Heuristics: link looks like file download
        is_file = (
            any(low.split('?')[0].endswith(ext) for ext in ATTACH_EXTS)
            or 'download' in low
            or 'fileDown' in full
            or 'atchFileId' in full
            or 'fileSn' in full
            or '/file/' in low
            or '/cmm/fms/' in low
        )
        if is_file and full not in seen:
            seen.add(full)
            out.append((label, full))
    return out

def filename_from_response(resp, fallback):
    cd = resp.headers.get('Content-Disposition', '')
    fname = None
    m = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", cd, re.I)
    if m:
        fname = unquote(m.group(1).strip().strip('"'))
    if not fname:
        m = re.search(r'filename="?([^";]+)"?', cd, re.I)
        if m:
            fname = m.group(1).strip()
            try:
                fname = fname.encode('latin-1').decode('utf-8')
            except Exception:
                try:
                    fname = fname.encode('latin-1').decode('euc-kr')
                except Exception:
                    pass
    if not fname:
        path = unquote(urlparse(resp.url).path)
        fname = os.path.basename(path) or fallback
    return safe(fname, 150)

def download_url(url, sess, timeout=25):
    try:
        r = sess.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
        return r
    except Exception as e:
        return e

def process_item(it, sess):
    no = it['no']
    org = it['org']
    pname = it['pname']
    year = it['year']
    url = it['url']
    folder = org_folder(org)
    prefix = f"{no:02d}_{year}_{safe(pname, 60)}"
    item_dir = os.path.join(folder, prefix)
    os.makedirs(item_dir, exist_ok=True)

    result = {
        'no': no, 'org': org, 'year': year, 'pname': pname, 'url': url,
        'html_saved': '', 'http_status': '', 'attachments': 0, 'attachment_files': '', 'error': ''
    }

    # Save metadata
    with open(os.path.join(item_dir, '_info.txt'), 'w', encoding='utf-8') as f:
        f.write(f"순번: {no}\n등급: {it.get('grade')}\n기관: {org}\n사업명: {pname}\n연도: {year}\n유형: {it.get('ptype')}\n링크유형: {it.get('ltype')}\nURL: {url}\n출처: {it.get('src')}\n저작권: {it.get('copyright')}\n비고: {it.get('note')}\n")

    r = download_url(url, sess)
    if isinstance(r, Exception):
        result['error'] = f"page: {type(r).__name__}: {r}"
        return result
    result['http_status'] = r.status_code
    if r.status_code != 200:
        result['error'] = f"page status {r.status_code}"
        return result

    # Detect encoding
    if not r.encoding or r.encoding.lower() == 'iso-8859-1':
        r.encoding = r.apparent_encoding or 'utf-8'
    html = r.text
    html_path = os.path.join(item_dir, 'page.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    result['html_saved'] = 'page.html'

    # Attachments
    attachments = find_attachments(html, r.url)
    saved = []
    for i, (label, aurl) in enumerate(attachments[:10], 1):
        try:
            ar = sess.get(aurl, headers=HEADERS, timeout=40, verify=False, allow_redirects=True, stream=True)
            if ar.status_code != 200:
                continue
            ctype = ar.headers.get('Content-Type', '').lower()
            # Skip HTML responses that aren't files
            if 'text/html' in ctype and 'attachment' not in ar.headers.get('Content-Disposition', '').lower():
                continue
            fname = filename_from_response(ar, f'attachment_{i}.bin')
            # Avoid collision
            out_path = os.path.join(item_dir, fname)
            cnt = 1
            base, ext = os.path.splitext(out_path)
            while os.path.exists(out_path):
                out_path = f"{base}_{cnt}{ext}"; cnt += 1
            with open(out_path, 'wb') as f:
                for chunk in ar.iter_content(8192):
                    if chunk: f.write(chunk)
            saved.append(os.path.basename(out_path))
        except Exception as e:
            continue
    result['attachments'] = len(saved)
    result['attachment_files'] = ' | '.join(saved)
    return result

def main():
    sess = requests.Session()
    results = []
    for i, it in enumerate(ITEMS, 1):
        print(f"[{i:02d}/{len(ITEMS)}] {it['org']} - {it['pname'][:40]}", flush=True)
        try:
            res = process_item(it, sess)
        except Exception as e:
            res = {'no': it['no'], 'org': it['org'], 'year': it['year'], 'pname': it['pname'], 'url': it['url'],
                   'html_saved': '', 'http_status': '', 'attachments': 0, 'attachment_files': '', 'error': f'{type(e).__name__}: {e}'}
        results.append(res)
        time.sleep(0.6)

    # Write manifest CSV
    out_csv = os.path.join(BASE, '_manifest.csv')
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['no','org','year','pname','url','http_status','html_saved','attachments','attachment_files','error'])
        w.writeheader()
        for r in results: w.writerow(r)

    # Summary
    ok_html = sum(1 for r in results if r['html_saved'])
    total_att = sum(r['attachments'] for r in results)
    fail = sum(1 for r in results if r['error'])
    print()
    print(f"=== 완료 ===")
    print(f"페이지 저장 성공: {ok_html}/{len(results)}")
    print(f"첨부파일 총 다운로드: {total_att}건")
    print(f"실패/에러: {fail}건")
    print(f"manifest: {out_csv}")

if __name__ == '__main__':
    main()
