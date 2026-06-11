"""V3 리치 블록 — 실제 Google Slides 빌드 데모.

stat_row / bars / timeline / progress / badge / 강조 카드를 한 덱에서 시연한다.

실행 (gws + Google 인증이 있는 본인 머신에서):
    python3 examples/demo_v3_build.py            # dark
    python3 examples/demo_v3_build.py light      # light

출력: 생성된 Google Slides URL. 같은 BUILD_NAME 으로 다시 돌리면 같은 덱에 누적 수정.
"""
import os
import sys

# 에이전트 스킬 경로에서 의존 파일까지 /tmp 로 복사 (설치 위치 무관 동작)
SKILL_DIR = os.path.expanduser("~/.agents/skills/spigen-slides")
if not os.path.isdir(SKILL_DIR):
    # 저장소에서 직접 실행하는 경우 — 이 파일 상위 폴더를 스킬 디렉토리로 사용
    SKILL_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, SKILL_DIR)

from spigen_build import SpigenBuilder, load_pid, save_pid

BUILD_NAME = "v3_demo"


def build(theme="dark"):
    pid = load_pid(BUILD_NAME, theme)
    b = SpigenBuilder("패키지 리뉴얼 V3 데모", theme=theme, presentation_id=pid)
    if pid is None:
        save_pid(BUILD_NAME, theme, b.pid)

    # [1] 표지
    b.cover(title="패키지 리뉴얼 진행 보고\nV3 리치 블록 데모")

    # [2] 핵심 수치 — stat_row
    b.start_slide(heading="진행 현황 요약", eyebrow="STATUS")
    b.stat_row(120, [
        {"value": "96.4%", "label": "H1 달성률", "delta": "+4.2%p", "delta_tone": "good"},
        {"value": "12건", "label": "완료 항목", "delta": "잔여 3건", "delta_tone": "warn"},
        {"value": "06.27", "label": "차기 마감", "delta": "D-17", "delta_tone": "bad"},
    ])
    b.divider(48, 230, 624, orange=False)
    b.text(48, 250, 624, 60,
           "표지·내지 디자인 확정 후 인쇄 발주 단계 진입. "
           "잔여 3건은 **바커 문안 검수** 대기 상태.", size=10.5)

    # [3] 수치 비교 — bars
    b.start_slide(heading="채널별 출하 비중", eyebrow="DATA")
    b.bars(48, 120, 624, [
        {"label": "쿠팡", "value": 42, "display": "42%", "primary": True},
        {"label": "아마존 US", "value": 31, "display": "31%"},
        {"label": "자사몰", "value": 17, "display": "17%"},
        {"label": "기타", "value": 10, "display": "10%"},
    ])
    b.text(48, 250, 624, 40,
           "쿠팡 비중이 가장 크므로 **쿠팡 규격 라벨**을 기준 규격으로 확정.", size=10.5)

    # [4] 일정 — timeline
    b.start_slide(heading="리뉴얼 일정", eyebrow="SCHEDULE")
    b.timeline(140, [
        {"label": "디자인 확정", "date": "05.30", "state": "done"},
        {"label": "샘플 인쇄", "date": "06.10", "state": "done"},
        {"label": "문안 검수", "date": "06.18", "state": "current"},
        {"label": "본 발주", "date": "06.27", "state": "next"},
        {"label": "입고", "date": "07.15", "state": "next"},
    ])
    b.text(48, 240, 624, 40,
           "현재 **문안 검수** 단계 — 패키지팀 검수 완료 시 즉시 발주.", size=10.5)

    # [5] 진행률 + 배지 조합
    b.start_slide(heading="품목별 진척", eyebrow="PROGRESS")
    b.progress(48, 120, 500, 100, label="슬림 아머 — 인쇄 완료", tone="good")
    b.badge(572, 118, "완료", tone="good")
    b.progress(48, 165, 500, 72, label="울트라 하이브리드 — 검수 중", tone="accent")
    b.badge(572, 163, "진행중", tone="accent")
    b.progress(48, 210, 500, 35, label="터프 아머 — 문안 보정 대기", tone="warn")
    b.badge(572, 208, "대기", tone="warn")

    # [6] 기존 블록 호환 — 카드 + 강조
    b.start_slide(heading="다음 액션", eyebrow="ACTION PLAN")
    b.card(48, 110, 198, 180, label="01", title="문안 검수 완료",
           body="패키지팀 검수 의견 반영 후 최종 PDF 확정. 마감 **06.18**.")
    b.card(261, 110, 198, 180, label="02", title="본 발주", emphasis="full",
           body="검수 완료 즉시 인쇄소 발주. 수량 확정 필요.")
    b.card(474, 110, 198, 180, label="03", title="입고 검수",
           body="입고 시 인쇄 품질 확인 — 색상 편차 기준 적용.")

    ok = b.flush()
    if ok:
        print(f"[{theme}] {'NEW' if pid is None else 'UPDATE'} "
              f"https://docs.google.com/presentation/d/{b.pid}/edit")
    else:
        print(f"[{theme}] 생성 실패 — 위 오류 메시지 확인")


if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
    build(theme)
