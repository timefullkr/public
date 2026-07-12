# 제주교육 AI · 공개 참고 문서

미래학력분과 관련 자료 중 외부 공개용 참고 문서입니다.

## 웹으로 보기 (GitHub Pages)

- 목록: `https://timefullkr.github.io/public/`
- 초개별화 맞춤형 교육의 이론적 배경(블룸 2 시그마): `https://timefullkr.github.io/public/bloom-2sigma.html` (PDF: `https://timefullkr.github.io/public/bloom-2sigma.pdf`)
- AI 교육 패러다임: `https://timefullkr.github.io/public/paradigm.html`
- AX 전환과 교육: `https://timefullkr.github.io/public/ax-transformation.html`

## 원문 마크다운

- [초개별화 맞춤형 교육의 이론적 배경 — 벤저민 블룸 '2 시그마 문제'](고의숙%20교육감의%20초개별화%20맞춤형%20교육%20이론적%20배경.md)
- [AI 교육 패러다임](AI교육-패러다임.md)
- [AX 전환과 교육](AX전환과%20교육.md)

## 사이트 재빌드 방법

원문 마크다운을 고친 뒤 아래를 실행하면 HTML·index·PDF가 재생성되고 PDF 무결성까지 검증된다.

```
python -m pip install markdown pypdf
python build.py
```

- `build.py`는 스크립트가 있는 폴더 기준으로만 동작하므로 경로 하드코딩이 없다.
- PDF는 Chrome/Edge 헤드리스로 생성하며, 빈 페이지·에러 페이지(ERR_FILE 등)를 자동 검출해 실패 처리한다.
- HTML 페이지는 `.nojekyll`로 정적 서빙된다.
