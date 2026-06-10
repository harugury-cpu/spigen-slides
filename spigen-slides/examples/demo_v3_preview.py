"""V3 리치 블록 데모 — HTML 시안 렌더러 동작 확인용.

실행: python3 examples/demo_v3_preview.py
출력: /tmp/spigen_preview_V3_데모.html (gws/Google 인증 불필요)

시안 승인 후 같은 호출 코드를 SpigenBuilder로 바꾸면 그대로 빌드된다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from spigen_html import HtmlDeck


def build(theme="dark"):
    d = HtmlDeck("패키지 리뉴얼 V3 데모", theme=theme)

    # [1] 표지
    d.cover(title="패키지 리뉴얼 진행 보고\nV3 리치 블록 데모")

    # [2] 핵심 수치 — stat_row
    d.start_slide(heading="진행 현황 요약", eyebrow="STATUS")
    d.stat_row(120, [
        {"value": "96.4%", "label": "H1 달성률", "delta": "+4.2%p", "delta_tone": "good"},
        {"value": "12건", "label": "완료 항목", "delta": "잔여 3건", "delta_tone": "warn"},
        {"value": "06.27", "label": "차기 마감", "delta": "D-17", "delta_tone": "bad"},
    ])
    d.divider(48, 230, 624, orange=False)
    d.text(48, 250, 624, 60,
           "표지·내지 디자인 확정 후 인쇄 발주 단계 진입. "
           "잔여 3건은 **바커 문안 검수** 대기 상태.", size=10.5)

    # [3] 수치 비교 — bars
    d.start_slide(heading="채널별 출하 비중", eyebrow="DATA")
    d.bars(48, 120, 624, [
        {"label": "쿠팡", "value": 42, "display": "42%", "primary": True},
        {"label": "아마존 US", "value": 31, "display": "31%"},
        {"label": "자사몰", "value": 17, "display": "17%"},
        {"label": "기타", "value": 10, "display": "10%"},
    ])
    d.text(48, 250, 624, 40, "쿠팡 비중이 가장 크므로 **쿠팡 규격 라벨**을 기준 규격으로 확정.",
           size=10.5)

    # [4] 일정 — timeline
    d.start_slide(heading="리뉴얼 일정", eyebrow="SCHEDULE")
    d.timeline(140, [
        {"label": "디자인 확정", "date": "05.30", "state": "done"},
        {"label": "샘플 인쇄", "date": "06.10", "state": "done"},
        {"label": "문안 검수", "date": "06.18", "state": "current"},
        {"label": "본 발주", "date": "06.27", "state": "next"},
        {"label": "입고", "date": "07.15", "state": "next"},
    ])
    d.text(48, 240, 624, 40, "현재 **문안 검수** 단계 — 패키지팀 검수 완료 시 즉시 발주.",
           size=10.5)

    # [5] 진행률 + 배지 조합
    d.start_slide(heading="품목별 진척", eyebrow="PROGRESS")
    d.progress(48, 120, 500, 100, label="슬림 아머 — 인쇄 완료", tone="good")
    d.badge(572, 118, "완료", tone="good")
    d.progress(48, 165, 500, 72, label="울트라 하이브리드 — 검수 중", tone="accent")
    d.badge(572, 163, "진행중", tone="accent")
    d.progress(48, 210, 500, 35, label="터프 아머 — 문안 보정 대기", tone="warn")
    d.badge(572, 208, "대기", tone="warn")

    # [6] 기존 블록 호환 확인 — 카드 + 강조
    d.start_slide(heading="다음 액션", eyebrow="ACTION PLAN")
    d.card(48, 110, 198, 180, label="01", title="문안 검수 완료",
           body="패키지팀 검수 의견 반영 후 최종 PDF 확정. 마감 **06.18**.")
    d.card(261, 110, 198, 180, label="02", title="본 발주", emphasis="full",
           body="검수 완료 즉시 인쇄소 발주. 수량 확정 필요.")
    d.card(474, 110, 198, 180, label="03", title="입고 검수",
           body="입고 시 인쇄 품질 확인 — 색상 편차 기준 적용.")

    path = d.flush(f"/tmp/spigen_preview_v3_demo_{theme}.html")
    return path


if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
    build(theme)
