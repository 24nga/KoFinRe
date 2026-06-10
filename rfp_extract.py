"""
RFP_자료_56건 폴더에서 사업별로 텍스트 추출
- HTML(BeautifulSoup), HWP(한컴 COM), PDF(pdfplumber)
- 사업 폴더당 하나의 .txt로 통합
- HWP 보안 모듈 등록: FilePathCheckerModuleExample 회피용
"""
import os, sys, re, traceback
from pathlib import Path

BASE = Path(r'C:\Users\heen1\Desktop\RFP_자료_56건')
OUT  = Path(r'C:\Users\heen1\Desktop\assist\rfp_extract')
OUT.mkdir(parents=True, exist_ok=True)

# ───────── HWP ─────────
import win32com.client, pythoncom
def hwp_extract(path: Path, hwp) -> str:
    """1회 생성한 HwpObject 재사용. SetMessageBoxMode 로 모달 차단."""
    try:
        # 모든 메시지박스 자동 응답 (오류·확인·저장 등)
        try: hwp.SetMessageBoxMode(0x10)
        except: pass
        ok = hwp.Open(str(path.absolute()), "", "forceopen:true;suspendpassword:true")
        if not ok:
            return '<HWP_OPEN_FAILED>'
        text = hwp.GetTextFile("TEXT", "")
        # 닫기
        try: hwp.XHwpDocuments.Item(0).Close(isDirty=False)
        except:
            try: hwp.Clear(1)
            except: pass
        return text or ''
    except Exception as e:
        return f'<HWP_ERROR: {type(e).__name__}: {e}>'

# ───────── HTML / 시그니처 분기 ─────────
from bs4 import BeautifulSoup

def detect_kind(path: Path) -> str:
    """page.html 라고 저장돼 있어도 실제 내용이 다를 수 있음. 시그니처로 판별."""
    head = path.read_bytes()[:8]
    if head.startswith(b'%PDF'):
        return 'pdf'
    if head.startswith(b'PK\x03\x04'):
        return 'zip'
    if head.startswith(b'\xd0\xcf\x11\xe0'):
        return 'ole2'  # HWP/DOC
    if head.startswith(b'\xe9\xa5\x89\x11'):
        return 'hwp_alt'  # 한컴 변형
    if head[:1] in (b'<', b'\n', b'\r') or head[:3] == b'\xef\xbb\xbf' or b'<html' in head.lower():
        return 'html'
    # HTTP raw 응답 흔적 ("\r\n\r\n" 어디쯤)
    sample = path.read_bytes()[:512]
    if b'<html' in sample.lower() or b'<HTML' in sample:
        return 'html'
    return 'unknown'

def html_extract(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ('utf-8', 'cp949', 'euc-kr'):
        try: txt = raw.decode(enc); break
        except UnicodeDecodeError: continue
    else: txt = raw.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(txt, 'html.parser')
    for s in soup(['script', 'style', 'noscript']): s.decompose()
    return soup.get_text(separator='\n')

def hwp_extract_via_temp(path: Path, hwp, suffix='.hwp') -> str:
    """page.html이 실제로 HWP/OLE2면 임시 .hwp 로 복사 후 한컴 COM 사용."""
    import tempfile, shutil
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(path.read_bytes()); tmp_path = Path(tmp.name)
    try:
        return hwp_extract(tmp_path, hwp)
    finally:
        try: tmp_path.unlink()
        except: pass

# ───────── PDF ─────────
import pdfplumber
def pdf_extract(path: Path) -> str:
    out = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ''
            out.append(t)
    return '\n'.join(out)

# ───────── 정리 ─────────
def normalize(text: str) -> str:
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [ln.strip() for ln in text.split('\n')]
    return '\n'.join(ln for ln in lines if ln)

def main():
    pythoncom.CoInitialize()
    hwp = win32com.client.Dispatch('HWPFrame.HwpObject')
    # 보안 다이얼로그 자동 응답
    try: hwp.SetMessageBoxMode(0x10)
    except Exception as e: print(f'(SetMessageBoxMode 실패: {e})', flush=True)

    orgs = sorted([d for d in BASE.iterdir() if d.is_dir() and d.name[:2].isdigit()])
    total_proj = 0
    log = []
    for org_dir in orgs:
        proj_dirs = sorted([d for d in org_dir.iterdir() if d.is_dir()])
        for proj_dir in proj_dirs:
            total_proj += 1
            info_txt = proj_dir / '_info.txt'
            html_files = list(proj_dir.glob('*.html')) + list(proj_dir.glob('*.htm'))
            hwp_files = list(proj_dir.glob('*.hwp')) + list(proj_dir.glob('*.hwpx'))
            pdf_files = list(proj_dir.glob('*.pdf'))

            parts = []
            parts.append(f'### PROJECT: {org_dir.name} / {proj_dir.name}')
            if info_txt.exists():
                parts.append('## META')
                parts.append(info_txt.read_text(encoding='utf-8', errors='ignore'))

            for h in html_files:
                kind = detect_kind(h)
                try:
                    if kind == 'pdf':
                        txt = pdf_extract(h); parts.append(f'## HTML→PDF: {h.name}'); parts.append(normalize(txt))
                    elif kind in ('ole2', 'hwp_alt'):
                        txt = hwp_extract_via_temp(h, hwp); parts.append(f'## HTML→HWP: {h.name}'); parts.append(normalize(txt))
                    elif kind == 'zip':
                        parts.append(f'## HTML→ZIP {h.name}: (스킵 — ZIP 처리 미구현)')
                    else:
                        txt = html_extract(h); parts.append(f'## HTML: {h.name}'); parts.append(normalize(txt))
                except Exception as e:
                    parts.append(f'## HTML_ERROR ({kind}) {h.name}: {e}')

            for h in hwp_files:
                try:
                    txt = hwp_extract(h, hwp); parts.append(f'## HWP: {h.name}'); parts.append(normalize(txt))
                except Exception as e:
                    parts.append(f'## HWP_ERROR {h.name}: {e}')

            for p in pdf_files:
                try:
                    txt = pdf_extract(p); parts.append(f'## PDF: {p.name}'); parts.append(normalize(txt))
                except Exception as e:
                    parts.append(f'## PDF_ERROR {p.name}: {e}')

            content = '\n\n'.join(parts)
            # 파일명: 사업번호_사업명_org슬러그 — 짧게
            m = re.match(r'(\d{2})_', proj_dir.name)
            n = m.group(1) if m else '00'
            slug = re.sub(r'[^A-Za-z0-9가-힣]+', '_', proj_dir.name)[:80]
            org_slug = org_dir.name[:30]
            out_file = OUT / f'{n}_{org_slug}_{slug}.txt'
            out_file.write_text(content, encoding='utf-8')
            log.append({'project': proj_dir.name, 'org': org_dir.name,
                        'html': len(html_files), 'hwp': len(hwp_files), 'pdf': len(pdf_files),
                        'chars': len(content), 'out': out_file.name})
            print(f'[{total_proj:02d}] {org_dir.name[:25]:<25} | HTML:{len(html_files)} HWP:{len(hwp_files)} PDF:{len(pdf_files)} → {len(content):>7} chars', flush=True)

    hwp.Quit()
    pythoncom.CoUninitialize()

    # 로그 CSV
    import csv
    with open(OUT / '_extract_log.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['project','org','html','hwp','pdf','chars','out'])
        w.writeheader()
        for r in log: w.writerow(r)
    print(f'\n총 {total_proj}건 사업 처리 → {OUT}')
    print(f'평균 문서 크기: {sum(x["chars"] for x in log)//max(total_proj,1):,} chars')

if __name__ == '__main__':
    main()
