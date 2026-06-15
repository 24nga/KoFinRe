"""docs/ markdown 모음을 PDF로 묶기 — 논문 제출용 (v2.8).

사용:
    python scripts/build_pdf_bundle.py --output dist/KoFinRe_v2.8.pdf

old/ 폴더의 historical 문서는 기본 제외. --include-old 플래그로 포함 가능.
"""
import argparse
from pathlib import Path


# 활성 문서 (v2.8 기준) — docs/
DOCS_ORDER = [
    'PAPER_FINAL.md',                # v2.8 MECE 학술 최종본 (19종)
    'CMMI_NCS_COMPARISON.md',        # v2.8 CMMI 9 원칙 + NCS 5 카테고리
    'JOURNEY.md',                    # 전체 여정 v1.0 → v2.8
    'EXTRACTION_RULES.md',           # 추출·필터 규칙
    'PASKA_KOREAN_ADAPTATION.md',    # Paska 원본 대비 변경
    'IMPROVEMENT_RECOMMENDATIONS.md',# 작성자·도구·프로세스 권고
    'UPDATE.MD',                     # changelog v1.0 → v2.8
]

# Historical 문서 (시점별 보관) — old/
OLD_DOCS_ORDER = [
    'PAPER_DRAFT.md',                # v2.1 시점 초안 (10종)
    'FRAMEWORK_GAP_ANALYSIS.md',     # v2.0 시점 갭 분석
    'STANDARDS_COMPARISON.md',       # v2.7 시점 IEEE/ISO/INCOSE/EARS 갭
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=Path('dist/KoFinRe_v2.8.pdf'))
    ap.add_argument('--docs-dir', type=Path,
                   default=Path(__file__).resolve().parent.parent / 'docs')
    ap.add_argument('--old-dir', type=Path,
                   default=Path(__file__).resolve().parent.parent / 'old')
    ap.add_argument('--include-old', action='store_true',
                   help='old/ 폴더의 historical 문서까지 부록으로 포함')
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

## Document Bundle (v2.8)

KoFinRe-QA Framework
A Framework for Quality Analysis and Dataset Construction
of Korean Public Financial RFP Requirements

19종 한국어 smell taxonomy + 6대 요구공학 표준 정렬
(Paska + IEEE 830 + ISO 29148 + INCOSE + EARS + CMMI REQM/RD + NCS)

---

Version: 2.8.0
Repository: https://github.com/24nga/KoFinRe
Generated: 2026-06-15

---

## 목차 — 활성 문서 (v2.8)

1. PAPER_FINAL — v2.8 MECE 학술 최종본 (19종)
2. CMMI_NCS_COMPARISON — CMMI 9 원칙 + NCS 5 카테고리 분석
3. JOURNEY — 전체 여정 v1.0 → v2.8 (13단계)
4. EXTRACTION_RULES — 추출·필터·평가 규칙
5. PASKA_KOREAN_ADAPTATION — Paska 원본 대비 변경
6. IMPROVEMENT_RECOMMENDATIONS — 작성자·도구·프로세스 권고
7. UPDATE — 변경 이력 (v1.0~v2.8)
"""
    if args.include_old:
        cover += """
## 목차 — 부록 (시점별 historical)

8. PAPER_DRAFT (v2.1 시점) — 초기 학술 정리본 (10종)
9. FRAMEWORK_GAP_ANALYSIS (v2.0 시점) — 논문 vs 구현 갭
10. STANDARDS_COMPARISON (v2.7 시점) — IEEE/ISO/INCOSE/EARS 갭
"""
    pdf.add_section(Section(cover, root='.'))

    # 활성 문서
    for fn in DOCS_ORDER:
        p = args.docs_dir / fn
        if not p.exists():
            print(f'스킵 — 파일 없음: {p}')
            continue
        content = p.read_text(encoding='utf-8')
        header = f'\n\n---\n\n# 📄 {fn}\n\n'
        pdf.add_section(Section(header + content, root=str(args.docs_dir)))
        print(f'  ✓ {fn} ({len(content)} chars)')

    # Historical 부록 (옵션)
    if args.include_old:
        appendix_intro = """
\n\n---\n\n# 📚 부록 — 시점별 Historical 문서

본 부록은 이전 버전 시점에서 정확했던 문서를 보관용으로 포함합니다.
현재 활성 상태는 본문 PAPER_FINAL.md (v2.8 19종)를 우선 참조하세요.
"""
        pdf.add_section(Section(appendix_intro, root='.'))
        for fn in OLD_DOCS_ORDER:
            p = args.old_dir / fn
            if not p.exists():
                print(f'스킵 — 파일 없음: {p}')
                continue
            content = p.read_text(encoding='utf-8')
            header = f'\n\n---\n\n# 📜 old/{fn}\n\n'
            pdf.add_section(Section(header + content, root=str(args.old_dir)))
            print(f'  ✓ old/{fn} ({len(content)} chars)')

    pdf.meta['title'] = 'KoFinRe v2.8 Documents Bundle'
    pdf.meta['author'] = 'KoFinRe Project (24nga/KoFinRe)'
    pdf.save(args.output)
    size = args.output.stat().st_size / 1024
    print(f'\nPDF: {args.output} ({size:.1f} KB)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main() or 0)
