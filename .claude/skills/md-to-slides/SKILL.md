---
name: md-to-slides
description: md 문서를 public 사이트 스타일 발표 슬라이드(단일 html)로 변환. "슬라이드로 만들어줘", "발표 덱", "프레젠테이션" 요청 시 사용. 템플릿은 저장소 루트의 bloom-2sigma-slides.html(최신 원본).
---

# md → 발표 슬라이드 변환

md 문서를 받아 저장소 루트 `bloom-2sigma-slides.html` 스타일의 단일 파일 발표 덱을 만든다.
결과물은 외부 의존성 CDN 2개(Pretendard 폰트, Fabric.js)만 쓰는 self-contained html.

## 작업 순서

1. 원본 md를 읽고 **내러티브 아크**를 먼저 설계한다 (아래 판단 규칙).
2. 저장소 루트 `bloom-2sigma-slides.html`을 읽어 CSS·JS 골격을 그대로 가져온다 — 새로 발명하지 말 것.
3. 슬라이드 구성안(장별 한 줄 메시지)을 먼저 사용자에게 보여주고 확인받는다.
4. html 작성 → 헤드리스 Chrome 스크린샷 검증 → 수정 반복.
5. 완료 보고 시 검증한 프레임(스크린샷) 근거를 언급한다.

## 판단 규칙 (콘텐츠)

- **주장형 헤드라인**: 슬라이드 제목은 명사구가 아니라 주장 문장으로. ("결과" ✕ → "상위 20%만 도달하던 수준에, 90%가 도달했다" ○)
- **슬라이드당 한 메시지**: 한 장에서 말하는 것은 하나. 근거·보조 정보는 그 메시지를 받치는 역할만.
- **내러티브 아크**: 문제 제기 → 긴장(왜 못 풀었나) → 해소(해법) → 우리 것으로(시사점·행동) 순서. md의 목차 순서를 그대로 따르지 말고 재배열한다.
- **섹션 구조**: 3부 내외로 나누고 섹션 표지(`slide sec`)에 `sectrack`(현재 위치 표시)·`gnum`(배경 대형 숫자)을 넣는다.
- **분량**: 15~20장 내외. 표지 1 + 섹션 표지 n + 본문 + 인용 1 + 맺음 1 + 참고문헌 1.

## 판단 규칙 (데이터 시각화 — 표→SVG 변환)

- **막대 높이는 값에 비례**해야 한다. viewBox 좌표를 계산해서 그릴 것 (20%·70%·90%면 픽셀 높이도 그 비율).
- **벨커브 σ 간격은 정확히**: 눈금·평균선 위치를 σ 단위 픽셀로 계산 (예: σ=45px면 2σ 이동 = 90px).
- 애니메이션은 템플릿의 기존 클래스 재사용: `.bar`/`.barval`(막대), `.bells .b1/.b2/.bn`(벨커브 시프트), `.slope .sline/.sd`(슬로프 라인드로잉). `prefers-reduced-motion`·print 무효화 규칙 유지.
- 모든 viz SVG에 `role="img"` + 한국어 `aria-label`(데이터 값 포함) 필수.
- 차트 아래 `vizcap`으로 읽는 법·단서를 한 줄 단다.
- 완성된 viz SVG는 `img/` 폴더에 `{덱이름}-{슬라이드번호}-{주제}.svg`로 독립 파일 추출을 고려한다 (index.html 카드용 — 기존 8종 참고).

## 판단 규칙 (신뢰성 가드)

- **연구 인용에는 맥락 단서를 붙인다**: 표본·맥락의 한계를 `.s`(부속 행)나 vizcap으로 명시. (예: "대학 단일 과목 결과 — 초·중등 일반화는 자체 시범으로 검증할 문제")
- **표현 수위**: 원 문헌이 말한 만큼만. "증명했다" ✕ → "실증했다/보고했다" 수준으로, 축적 중인 근거는 "축적 중"이라고 쓴다.
- **참고문헌은 실링크 + 접속 검증**: 각 항목에 DOI/원문 URL을 걸고, WebFetch 등으로 실제 접속되는지 확인한 것만 싣는다.
- **기관명 공식 표기**: "제주도교육감직인수위원회" ('직' 포함 축약형). 다른 변형 금지.
- 보도자료 인용 시 6.11자는 미배포이므로 인용 금지 — 6.23 초개별화 보도자료만 사용.

## 템플릿 골격 (bloom-2sigma-slides.html에서 가져올 것)

- **다크 톤 체계**: 명암 반전 없이 명도 단계로 리듬 — 콘텐츠 `#14283e`(`--surface-d`), 섹션 표지가 최저 명도 골짜기, 인용은 teal 틴트(`slide soft`). 배경 4종: `light`(콘텐츠)·`navy`(임팩트)·`soft`(인용·메시지)·`sec`(섹션).
- **세로 2:3 배치**: 콘텐츠를 기하 중앙보다 위에 — 비콘텐츠 슬라이드는 `::before flex:2 / ::after flex:3`, 콘텐츠 슬라이드는 `.bodyarea::before max-height:9vh` 상한.
- **헤더 존 고정**: `.slide.content`의 `.head{min-height:17vh}` — 제목 축이 장마다 출렁이지 않게.
- **내비**: 화면 좌우 10% 클릭, ←→·PgUp/PgDn·Space·Home/End, F 전체화면, 터치 스와이프, `#n` 해시 직접 진입.
- **좌·우 중앙 화살표 버튼**(`.navarrow.prev`/`.navarrow.next`, `#navPrev`/`#navNext`): 화면 좌우 가장자리 세로 중앙의 44px 원형 이전/다음 버튼. 클릭 핸들러에 `stopPropagation()` 필수 — 없으면 가장자리 클릭 내비와 겹쳐 한 번에 2장 넘어간다. 인트로 표시 중 클릭하면 `__endIntro()`로 인트로만 닫는다. `@media print` 숨김.
- **플로팅 버튼 반투명**: 화살표·홈·주석 토글 버튼은 기본 `opacity:.28`, 호버 시 `opacity:1`(`transition:opacity .25s`) — 발표 중 집중도를 해치지 않기 위함. 단 `.anntoggle.active`(주석 도구 켜짐)는 상태가 보여야 하므로 항상 `opacity:1`.
- **인트로 페이드**: 질문 문구 5s 페이드인 → 멈춤 없이 3s 아웃(표지 크로스페이드), 자동 진행 타이머 5000ms. 해시로 2장 이후 진입 시 인트로 생략. 문구는 문서 주제에 맞게 교체.
- **Fabric.js 주석 툴바**: 선택·펜·직선·사각형·원·텍스트·색·두께·undo/redo·삭제·전체지우기·PNG 저장. 우상단 연필 토글(P 키). 슬라이드별 잉크 저장/복원.
- **홈 버튼**(좌상단, public 사이트 홈 링크), 진행바·카운터·힌트, 인쇄 대응(`@media print` — 슬라이드 전부 표시·landscape·도구 숨김).
- 폰트 크기는 전부 `clamp()` — 새 요소를 추가할 때도 clamp로.
- **모바일 대응**(`@media (max-width:820px)`): ① `html{font-size:70%}` — rem 기반 clamp 가 전부 비례 축소된다. ② `.slide{overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch}` — 세로 화면에서 넘치는 내용을 스크롤로 접근(기본은 overflow:hidden 이라 폰에서 아랫부분을 볼 방법이 없다). ③ 데스크톱 배치용 `transform:translate(...)`가 걸린 viz(사다리·루프 등)는 `transform:none;max-width:100%`로 해제 — 안 하면 오른쪽이 잘린다. 새 viz 에 배치용 transform 을 줄 때는 반드시 모바일 해제 규칙을 같이 추가할 것.

## 검증 절차 (필수)

헤드리스 Chrome으로 각 슬라이드를 스크린샷 찍어 눈으로 확인한다. 애니메이션이 있으므로 `--virtual-time-budget`으로 중간·완료 두 프레임을 본다:

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
# n번 슬라이드, 애니메이션 완료 프레임 (인트로 5s + 아웃 3s + 여유)
"$CHROME" --headless --disable-gpu --screenshot=slide-n.png --window-size=1600,900 \
  --virtual-time-budget=12000 "file:///.../deck.html#n"
# 애니메이션 중간 프레임 (성장 중 막대·이동 중 벨커브 확인)
"$CHROME" --headless --disable-gpu --screenshot=slide-n-mid.png --window-size=1600,900 \
  --virtual-time-budget=600 "file:///.../deck.html#n"
```

- Chrome이 없으면 Edge(`msedge.exe`)로 대체 가능 — 같은 플래그를 지원한다.
- 해시 진입(`#n`)은 인트로를 생략하므로 2장 이후는 virtual-time-budget을 짧게 잡아도 된다. 1장(표지)만 인트로 시간 포함.
- 확인 항목: 텍스트 오버플로/잘림, 차트 비례 정확성, 헤더 축 정렬, 애니메이션 시작·끝 상태, 콘솔 에러(`--enable-logging` 시).
- **캡처 함정(이 PC)**: Windows 배율 125% 때문에 헤드리스가 페이지를 `window-size × 1.26` CSS px 로 렌더하고 비트맵은 window-size 그대로라 **스크린샷 오른쪽이 잘려 보인다**(`--force-device-scale-factor=1` 무시됨). 모바일 잘림 여부는 스크린샷만 믿지 말고 probe 로 판정: `</body>` 앞에 `getBoundingClientRect` 로 요소 right·`scrollWidth` vs `clientWidth` 를 `document.title` 에 쓰는 스크립트를 끼워 `--dump-dom` 으로 읽는다. 또한 헤드리스 창은 CSS 폭 ~477px 밑으로 안 줄어들어 실제 폰 폭(320~430) 재현 불가 — 좁은 폭 이슈는 레이아웃 수식으로 검증한다.
- CSS 애니메이션은 `--virtual-time-budget` 을 안 따르는 경우가 있다 — 슬라이드쇼류는 `animation-delay` 를 N초 당긴 사본을 만들어 원하는 시점 프레임을 즉시 캡처한다.

## 선택 옵션 (요청 시에만)

- **전문가 다인 리뷰**: 사용자가 원하면 서로 다른 관점(프레젠테이션 디자인·데이터 시각화·교육학 내용 검증·청중 관점) 에이전트 리뷰를 돌리고 종합해 반영.
- **애니메이션/주석 도구 제외**: 배포 대상에 따라 인트로·Fabric.js 툴바를 뺀 경량판 요청 가능 — 해당 CSS/JS 블록을 통째로 제거.

## 동기화 주의

이 저장소에서는 템플릿 원본이 루트의 `bloom-2sigma-slides.html` 자체이므로 별도 사본이 없다.
골격(내비·버튼·인트로·주석 도구 등)을 개선하면 ① 나머지 두 덱(`paradigm-slides.html`, `ax-transformation-slides.html`)에도 동일 적용하고, ② `미례학력분과/.claude/skills/md-to-slides/template.html`(ready2026 저장소)에도 역반영할 것 — 사본이 갈라지면 안 된다.

## 완료 후

이 저장소는 GitHub Pages 배포용이므로 작업 완료 시 항상 `git add → commit(한국어 conventional commit) → push`까지 수행한다. 새 덱은 `index.html`에 카드/링크로 연결한다.
