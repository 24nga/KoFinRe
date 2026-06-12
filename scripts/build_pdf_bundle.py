"""docs/ markdown 모음을 PDF로 묶기 — 논문 제출용.

사용:
    python scripts/build_pdf_bundle.py --output dist/KoFinRe_v2.3.pdf
"""
import argparse
from pathlib import Path


DOCS_ORDER = [
    'JOURNEY.md',
    'PAPER_DRAFT.md',
    'FRAMEWORK_GAP_ANALYSIS.md',
    'EXTRACTION_RULES.md',
    'PASKA_KOREAN_ADAPTATION.md',
    'IMPROVEMENT_RECOMMENDATIONS.md',
    'UPDATE.MD',
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=Path('dist/KoFinRe_documents.pdf'))
    ap.add_argument('--docs-dir', type=Path,
                   default=Path(__file__).resolve().parent.parent / 'docs')
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        from markdown_pdf import MarkdownPdf, Section
    except ImportError:
        print('markdown_pdf 미설치 — pip install markdown-pdf')
        return 1

    pdf = MarkdownPdf(toc_level=2, optimize=True)

    # 표지
    cover = """# KoFinRe — Korean Public Financial RFP Quality Analyzer

## Document Bundle

KoFinRe-QA Framework
A Framework for Quality Analysis and Dataset Construction
of Korean Public Financial RFP Requirements

---

Version: 2.3.0
Repository: https://github.com/24nga/KoFinRe
Generated: 2026-06-12

---

## 목차

1. PAPER_DRAFT — 학술 정리본
2. FRAMEWORK_GAP_ANALYSIS — 논문 vs 구현 갭
3. EXTRACTION_RULES — 추출·평가 규칙
4. PASKA_KOREAN_ADAPTATION — 원본 Paska 대비 변경
5. IMPROVEMENT_RECOMMENDATIONS — 개선 권고문
6. UPDATE — 변경 이력
"""
    pdf.add_section(Section(cover, root='.'))

    for fn in DOCS_ORDER:
        p = args.docs_dir / fn
        if not p.exists():
            print(f'스킵 — 파일 없음: {p}')
            continue
        content = p.read_text(encoding='utf-8')
        # 섹션 시작 마커
        header = f'\n\n---\n\n# 📄 {fn}\n\n'
        pdf.add_section(Section(header + content, root=str(args.docs_dir)))
        print(f'  ✓ {fn} ({len(content)} chars)')

    pdf.meta['title'] = 'KoFinRe Documents Bundle'
    pdf.meta['author'] = 'KoFinRe Project (24nga/KoFinRe)'
    pdf.save(args.output)
    size = args.output.stat().st_size / 1024
    print(f'\nPDF: {args.output} ({size:.1f} KB)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main() or 0)
