---
name: spigen-slides
description: "PPT 만들어줘 / 피피티 만들어줘 / 장표 만들어줘 / 슬라이드 만들어줘 / 발표자료 만들어줘 / 프레젠테이션 만들어줘 / 보고서 슬라이드 만들어줘 / 덱 만들어줘 등 슬라이드 생성 요청 시 발동. Spigen 내부용 Google Slides 자동 생성 스킬."
license: MIT
metadata:
  category: productivity
  locale: ko-KR
  phase: v2.0.0
---

# spigen-slides (V2 — 디자인 자유 / 출력만 고정)

## 이 스킬의 철학

이 스킬은 **디자인을 가르치지 않는다.** 어떤 레이아웃을 쓰라거나, 어떤 컴포넌트로 무엇을 표현하라는 규칙이 없다 — 그런 가이드가 매번 같은 화면(답습)을 만들어 냈기 때문이다.

대신 **내용에서 매번 새로 화면을 구성한다.** 자료마다 시각이 다른 것이 정상이다. 내용이 빽빽하면 한 페이지에 밀도 높게, 내용이 비면 이미지 자리로, 표가 맞으면 표로 — **통일성을 추구하지 않는다.** 슬라이드를 가로지르는 시각적 일관성 강제는 없다. 유일한 메타 규칙은 "이전 덱·이전 슬라이드의 레이아웃을 그대로 가져오지 말고, 이 내용에 맞는 화면을 새로 그린다"이다.

고정하는 것은 디자인이 아니라 **출력**이다: ① 표지 ② 브랜드(폰트·컬러) ③ 어조 ④ 내용 충실도(주장) ⑤ 깨짐 없는 출력. 그 안에서 화면 설계는 전적으로 자유다.

---

## 진행 흐름

```
Step 1. 내용 수집
Step 2. 슬라이드별 브리프 작성 → 사용자 승인   ← 내용 충실도의 원천
Step 3. 빌드 (저수준 그리기 API로 자유 배치)
Step 4. 썸네일 채점 (깨짐만 점검, 최대 1회 수정) → 링크 전달
```

---

## Step 2. 슬라이드별 브리프 (★ 주장 게이트)

빌드 전 슬라이드마다 **주장 한 문장**을 쓴다. 이것이 내용 충실도의 핵심이며, 이 게이트가 없으면 AI가 의도를 모른 채 화면만 채운다.

```
[N] (제목)
주장: 이 슬라이드가 증명하는 단 한 문장. "그래서 뭐?"에 답이 되어야 한다.
근거: 주장을 뒷받침하는 원본 사실·수치 (원본에 없는 것 창작 금지)
화면: 이 주장을 어떻게 보여줄지 — 자유롭게. 컴포넌트 이름이 아니라 "어떻게 보이는가"로.
시선: 눈이 어디서 시작해 어디로 흐르는가 (①→②→③). 한 방향(좌→우 / 위→아래)으로 정리.
어조: 명사형 헤더 / 서술형 줄글 금지 / 핵심만 — 이 슬라이드 텍스트가 이걸 지켰는지 자가 확인.
```

규칙:
- 주장은 **결론**이어야 한다. "X의 단계 / X의 구성"은 주장이 아니라 목차다 — 그런 슬라이드는 합치거나 버린다.
- **내용 충분성 게이트**: 원본에서 주장을 뽑을 근거가 부족하면 빌드를 멈추고 사용자에게 되묻는다("이 내용으로 무엇을 말하고 싶으세요? 결론이 무엇인가요?"). AI는 내용을 창작하지 않는다.
- "화면"은 직전 덱을 베끼지 말고 이 내용에서 새로 도출한다. 같은 종류의 내용이라도 주장이 다르면 다른 화면이 나와야 정상이다.

승인 형식: `[N] (제목) — 주장: ... / 화면: ...` 를 나열하고 승인받는다. 표지는 브리프 대상이 아니다(템플릿 복사).

---

## 고정 1. 표지 (직접 그리지 않음)

표지는 지정 템플릿 cover를 복사하고 텍스트만 교체한다. **어떤 상황에도 모드별 표지 디자인은 동일하게 유지** — 본문을 어떻게 그리든 표지 복사·매핑 로직은 건드리지 않는다.

- light cover 템플릿: `1BBG9PR6ZBsEABbJLhbUUfRMkgGYQtNMOWAmLQgPhr70`
- dark cover 템플릿: `1HJbTWXPCr38gXDQuarglSLrkheDQXAojlrYUKcfVgAc`
- `cover(title=...)` — 제목 2줄 이내(`\n` 1개 이하). `date` 생략 시 오늘 날짜 자동 입력.
- 첫 슬라이드는 항상 `cover()`. 마지막은 콘텐츠 슬라이드로 끝낸다(클로징 없음).

---

## 고정 2. 브랜드 토큰

색은 hex 문자열이 아니라 `{"red","green","blue"}` 0~1 dict로 전달한다. 빌더의 `b.c[...]`로 테마별 값을 바로 쓸 수 있다.

- 담당자 `한원진 담당` / 부서 `디자인부문ㅣ패키지디자인팀`
- 폰트: Noto Sans KR (한글) — 빌더 기본값
- 오렌지(브랜드 accent, 포인트 컬러): `#FF6B1A` = `b.c["accent"]`
- dark: 배경 `#000000`, 텍스트 `#F5F5F5`(`b.c["fg"]`), dim `#ACACAC`(`b.c["dim"]`), line `#323232`(`b.c["border"]`), surface `#0E0E0E`(`b.c["surface"]`)
- light: 배경 `#FFFFFF`, 텍스트 `#1C1C1E`
- 의미색: green `#34A853`(완료/정상) / yellow `#F5B041`(대기/보정) / red `#FF7A7A`(위험) — 의미가 있을 때만, 장식용 금지
- 오렌지는 브랜드 포인트이자 1순위 강조색이다. 모든 것을 오렌지로 칠하지 않는다 — 강조는 절제할수록 강하다.

---

## 고정 3. 어조 (회사 보이스 — 글 쓰는 법, 디자인 아님)

- **헤더는 명사형.** 동사 어미(`~한다` `~된다` `~만든다`) 금지 → 명사형(`~제작` `~검토` `~방안` `~흐름`). 10자 이내 권장.
- **간결·정확.** 서술형 줄글을 피하고 핵심만. 한 항목 1줄 이내 권장.
- **AI 클리셰 금지**: 혁신적인·원활한·극대화·시너지·솔루션·최적화·스마트한·강력한·게임체인저 → 구체 사실·수치로.
- **수치 위조 금지**: 원본에 없는 "10배 향상", "99% 정확도" 등 절대 금지. 수치가 없으면 수치 없이 쓴다.
- **플레이스홀더 금지**: "추가 예정", "내용 입력", 빈 자리로 채우지 않는다. 채울 내용이 없으면 슬라이드를 줄인다.

---

## 고정 4. 시각 원칙 (레이아웃 지정 아님 — 어떻게 그리든 지킬 성질)

레이아웃을 정하지 않는다. 화면을 어떻게 구성하든 아래는 만족해야 한다. 이게 없으면 자유도가 산만함으로 샌다.

- **시선 흐름**: 눈이 한 방향으로 흐르게 한다(좌→우 / 위→아래). 요소가 사방에 흩어지면 어디부터 볼지 길을 잃는다.
- **정렬**: 모든 요소를 보이지 않는 격자에 맞춘다. 들쭉날쭉한 가장자리·제멋대로인 시작점이 아마추어 인상의 가장 흔한 원인. x·y 좌표를 눈대중하지 말고 같은 열·행은 같은 값으로.
- **강조 절제**: 강조(오렌지·굵게·큰 크기)는 한 화면에 1~2개만. 다 강조하면 강조가 없는 것과 같다. 표·나열처럼 동등한 항목들은 강조하지 않는다 — 균일하게 둔다.
- **장수 최소**: 요약·목차·클로징 같은 보조 페이지를 넣지 않는다. 한 장에 담을 수 있으면 합친다. 페이지로 내용을 늘리지 말고 줄인다.

---

## Step 3. 빌드 — 저수준 그리기 API

화면은 아래 **그리기 프리미티브**로 직접 배치한다. 이게 전부다 — "이럴 땐 이 컴포넌트" 같은 목록은 없다. 캔버스는 720×405pt, 콘텐츠 영역은 y=100~373(위아래 여백 대칭).

```python
import os, sys, shutil
SKILL_DIR = os.path.expanduser("~/.agents/skills/spigen-slides")
for f in ["spigen_build.py", "spigen_lib.py", "spigen_tokens.py",
          "spigen_models.py", "spigen_layout.py"]:
    shutil.copy2(os.path.join(SKILL_DIR, f), f"/tmp/{f}")
sys.path.insert(0, "/tmp")
from spigen_build import SpigenBuilder, load_pid, save_pid
import spigen_lib as lib

BUILD_NAME, THEME = "my_deck", "dark"   # 같은 BUILD_NAME = 같은 URL에 누적 수정

def build():
    lib.set_theme(THEME)
    pid = load_pid(BUILD_NAME, THEME)
    b = SpigenBuilder("(제목)", theme=THEME, presentation_id=pid)
    if pid is None:
        save_pid(BUILD_NAME, THEME, b.pid)

    # [1] 표지 — 템플릿 복사 (변경 금지)
    b.cover(title="(제목 1줄)\n(제목 2줄)")

    # [2~] 콘텐츠 슬라이드 — 헤더 후 자유 배치
    b.start_slide(heading="(명사형 제목)", eyebrow="CATEGORY")
    sid = b._current_slide   # _hline/_vline/_rect 의 첫 인자로 사용

    # ── 그리기 프리미티브 (이걸로 무엇이든 자유롭게 구성) ──
    # 텍스트 — 크기/굵기/색/정렬 자유. **굵게** 마크업 인식.
    b.text(x=48, y=120, w=624, h=40, content="자유 위치 텍스트 **강조**",
           size=14, bold=True, color=b.c["fg"], align="START")
    # 큰 수치 한 덩어리
    b.stat(x=48, y=120, w=200, value="96.4%", label="달성률", tone="accent")
    # 선 (구분·정렬용)
    b.divider(x=48, y=240, w=624, orange=False)        # 가로 구분선
    b._hline(sid, 48, 200, 624, weight=0.5, color=b.c["border"])  # 가는 가로선
    b._vline(sid, 360, 120, 130, weight=0.5, color=b.c["border"]) # 세로 분할선
    # 사각형 (정말 묶음·강조가 필요할 때만 — 기본은 선·여백으로)
    b._rect(sid, 48, 120, 300, 120, b.c["surface"], b.c["border"], 0.4)
    # 이미지 (공개 URL 필수)
    b.image(url="https://...", x=48, y=110, w=300, h=200)
    b.full_image(url="https://...", heading="제목", eyebrow="DESIGN", caption="캡션")

    ok = b.flush()
    if ok:
        print(f"https://docs.google.com/presentation/d/{b.pid}/edit")

if __name__ == "__main__":
    build()
```

빌드 규칙:
- `theme="dark"` 기본 — light는 사용자가 명시할 때만. 테마는 Q4로 묻는다.
- in-place: 같은 `BUILD_NAME`은 같은 URL에 누적 수정한다. `clear_pid()` 금지. 수정 빌드는 항상 **전체 슬라이드 코드**로 실행한다(in-place는 표지 외 전량 재생성이므로 일부만 빌드하면 나머지가 사라진다).
- 색은 반드시 dict. 좌표는 캔버스·콘텐츠 영역 안에서.

---

## Step 4. 썸네일 채점 (깨짐만, 최대 1회)

빌드 후 각 슬라이드 PNG를 받아 **직접 보고** 점검한다. "더 예쁘게"는 묻지 않는다 — 깨짐(요소 겹침, 캔버스/영역 넘침, 텍스트 잘림)만 본다. 발견 시 그 항목만 1회 수정하고 종료. 무한 수정 루프 금지.

```bash
# 슬라이드 objectId 조회
gws slides presentations get --params '{"presentationId":"<PID>","fields":"slides.objectId"}'
# 페이지별 썸네일 URL
gws slides presentations pages getThumbnail --params '{"presentationId":"<PID>","pageObjectId":"<SID>","thumbnailProperties.thumbnailSize":"LARGE"}'
```

완료 보고: Google Slides URL 전달. (검증·검수는 별도 `spigen-slides-review` 스킬 — 사용자가 명시할 때만.)

---

## 레퍼런스

| 파일 | 용도 |
|------|------|
| `spigen_build.py` | 빌더 — cover / start_slide / 그리기 프리미티브(text·stat·divider·_hline·_vline·_rect·image·full_image) / flush |
| `spigen_tokens.py` | 색·폰트·캔버스 토큰 |
| `spigen_pid_guard.py` | in-place PID 안정성 확인 (expect-stable / assert-stable) |

> 빌더 코드에는 과거의 카드형 헬퍼가 남아 있을 수 있으나, **이 문서는 그것들을 쓰지 않는다.** 화면은 위 그리기 프리미티브로 내용마다 새로 구성한다.
