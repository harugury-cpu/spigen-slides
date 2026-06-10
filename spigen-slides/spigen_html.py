"""
spigen_html.py — Spigen Slides HTML 시안 렌더러 (V3)

SpigenBuilder와 동일한 메서드 시그니처로 HTML 미리보기를 생성한다.

목적:
  1. 빌드 전 시각 시안 — 사용자가 텍스트 구성안 대신 실제 레이아웃을 보고 승인
  2. gws/Google 인증 없이 로컬에서 즉시 확인 (이 파일은 네트워크 호출 없음)
  3. 시안 승인 후 같은 호출 코드를 SpigenBuilder로 바꾸면 그대로 빌드됨
  4. (선택) headless Chrome으로 PNG 캡처 → b.image()/full_image()로 삽입하는
     "리치 이미지 모드" 소스

사용:
    from spigen_html import HtmlDeck
    d = HtmlDeck("덱 제목", theme="dark")
    d.cover(title="제목")
    d.start_slide(heading="현황", eyebrow="STATUS")
    d.stat_row(120, [{"value": "96.4%", "label": "달성률", "delta": "+4.2%p"}])
    path = d.flush("/tmp/spigen_preview_demo.html")

좌표계: SpigenBuilder와 동일한 720×405pt. CSS pt 단위를 그대로 사용한다.
HTML에서만 가능한 craft 보정(자간 등)은 자동 적용된다:
  - ALL CAPS 라벨/eyebrow: letter-spacing 0.08em
  - 대형 헤딩(34pt+): letter-spacing -0.01em
"""
import html as _html
import re
from datetime import datetime

from spigen_build import COLORS


def _hex(c):
    return "#{:02X}{:02X}{:02X}".format(
        round(c["red"] * 255), round(c["green"] * 255), round(c["blue"] * 255))


def _md(text):
    """HTML escape 후 **굵게** 마크업 변환 + 줄바꿈 처리."""
    out = _html.escape(str(text))
    out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
    return out.replace("\n", "<br>")


class HtmlDeck:
    """SpigenBuilder 미러 — Google API 대신 HTML 시안 출력."""

    _TONES = {
        "accent":  ("accent", "accent_bg"),
        "good":    ("good", "good_bg"),
        "warn":    ("warn", "warn_bg"),
        "bad":     ("bad", "bad_bg"),
        "neutral": ("dim", "surface_hi"),
    }

    def __init__(self, title, theme="dark", template="standard",
                 presentation_id=None, custom_template_id=None):
        if theme not in COLORS:
            theme = "light"
        self.theme = theme
        self.title = title
        self.c = {k: _hex(v) for k, v in COLORS[theme].items()}
        self._slides = []   # [{"note": str, "els": [html, ...]}]
        self._cur = None

    # ── 내부 헬퍼 ────────────────────────────────────────────────

    def _new(self, note=""):
        slide = {"note": note, "els": []}
        self._slides.append(slide)
        self._cur = slide
        return slide

    def _el(self, html_str):
        if self._cur is None:
            raise RuntimeError("start_slide()를 먼저 호출하세요.")
        self._cur["els"].append(html_str)

    def _div(self, x, y, w, h, style="", content="", valign="center"):
        """절대 위치 박스. valign: center(기본, 빌더 MIDDLE) / top / bottom."""
        align = {"center": "center", "top": "flex-start",
                 "bottom": "flex-end"}.get(valign, "center")
        self._el(
            f'<div style="position:absolute;left:{x}pt;top:{y}pt;'
            f'width:{w}pt;height:{h}pt;display:flex;flex-direction:column;'
            f'justify-content:{align};{style}">{content}</div>')

    def _tone(self, tone):
        fg_key, bg_key = self._TONES.get(tone or "accent", self._TONES["accent"])
        return self.c[fg_key], self.c[bg_key]

    def _num_font(self, value):
        if re.search(r"[가-힣]", str(value)):
            return "'Noto Sans KR',sans-serif"
        return "'Proxima Nova','Montserrat',sans-serif"

    @staticmethod
    def _caps_style():
        return "text-transform:uppercase;letter-spacing:0.08em;"

    # ── 표지 / 헤더 ──────────────────────────────────────────────

    def cover(self, title, subtitle="", dept="디자인부문ㅣ패키지디자인팀",
              name="한원진 담당", date=None):
        """표지 시안 — 실제 빌드는 테마별 템플릿 cover를 복사한다 (이건 근사 미리보기)."""
        self._new(note="표지 (실제 빌드 시 지정 템플릿 cover 복사)")
        date_text = date if date is not None else datetime.now().strftime("%Y.%m.%d")
        self._el(f'<div style="position:absolute;left:48pt;top:140pt;'
                 f'width:4pt;height:104pt;background:{self.c["accent"]}"></div>')
        self._div(66, 140, 600, 104,
                  f"font-size:34pt;font-weight:700;letter-spacing:-0.01em;"
                  f"line-height:1.25;color:{self.c['fg']}",
                  _md(title))
        if subtitle:
            self._div(66, 250, 600, 24,
                      f"font-size:17pt;color:{self.c['dim']}", _md(subtitle))
        self._div(48, 358, 400, 16,
                  f"font-size:11pt;color:{self.c['dim']}",
                  _md(f"{dept}  |  {name}"))
        self._div(560, 358, 112, 16,
                  f"font-size:11pt;color:{self.c['dim']};align-items:flex-end;"
                  f"font-family:{self._num_font(date_text)}",
                  _md(date_text))

    def start_slide(self, heading="", eyebrow=""):
        self._new()
        if eyebrow:
            self._div(48, 32, 320, 10,
                      f"font-size:8pt;font-weight:700;color:{self.c['accent']};"
                      + self._caps_style(), _md(eyebrow))
            if heading:
                self._div(48, 46, 624, 26,
                          f"font-size:22pt;font-weight:700;color:{self.c['fg']}",
                          _md(heading))
        elif heading:
            self._div(48, 20, 624, 38,
                      f"font-size:22pt;font-weight:700;color:{self.c['fg']}",
                      _md(heading))
        return self._cur

    # ── 기존 빌딩 블록 미러 ──────────────────────────────────────

    def card(self, x, y, w, h, title="", body="", label="", primary=False,
             emphasis=None, footer_label="", footer_body=""):
        if primary and emphasis is None:
            emphasis = "dim"
        if emphasis == "full":
            fill, border = self.c["accent"], self.c["accent"]
            label_c = title_c = body_c = self.c["bg"]
        elif emphasis == "dim":
            fill, border = self.c["accent_bg"], self.c["accent"]
            label_c, title_c, body_c = self.c["accent"], self.c["fg"], self.c["dim"]
        else:
            fill, border = self.c["surface"], self.c["border"]
            label_c, title_c, body_c = self.c["accent"], self.c["fg"], self.c["dim"]
        self._el(f'<div style="position:absolute;left:{x}pt;top:{y}pt;'
                 f'width:{w}pt;height:{h}pt;background:{fill};'
                 f'border:0.5pt solid {border};box-sizing:border-box"></div>')
        pad = 18
        iw = w - pad * 2
        sections = [s for s in (label, title, body) if s]
        if h < 80 or len(sections) < 3:
            # 스택 배치 (간이) — 빌더의 소형/2섹션 경로 근사
            cy = y + (0 if h < 80 else 16)
            ch = h if h < 80 else None
            inner = []
            if label:
                inner.append(f'<div style="font-size:8pt;font-weight:700;'
                             f'color:{label_c};{self._caps_style()}'
                             f'margin-bottom:4pt">{_md(label)}</div>')
            if title:
                inner.append(f'<div style="font-size:10.5pt;font-weight:700;'
                             f'color:{title_c};margin-bottom:4pt">{_md(title)}</div>')
            if body:
                inner.append(f'<div style="font-size:9pt;line-height:1.5;'
                             f'color:{body_c}">{_md(body)}</div>')
            self._div(x + pad, y, iw, h, "", "".join(inner))
            return
        self._div(x + pad, y + 16, iw, 12,
                  f"font-size:8pt;font-weight:700;color:{label_c};"
                  + self._caps_style(), _md(label))
        self._div(x + pad, y + 39, iw, 28,
                  f"font-size:10.5pt;font-weight:700;color:{title_c}", _md(title))
        has_footer = bool(footer_label or footer_body)
        footer_h = 56 if has_footer else 0
        body_h = max(16, h - 79 - 14 - footer_h)
        self._div(x + pad, y + 79, iw, body_h,
                  f"font-size:9pt;line-height:1.5;color:{body_c}",
                  _md(body), valign="top")
        if has_footer:
            fy = y + h - footer_h - 8
            self._el(f'<div style="position:absolute;left:{x+pad}pt;top:{fy}pt;'
                     f'width:{iw}pt;height:0.5pt;background:{self.c["dim"]}"></div>')
            if footer_label:
                self._div(x + pad, fy + 6, iw, 12,
                          f"font-size:8pt;font-weight:700;color:{label_c};"
                          + self._caps_style(), _md(footer_label))
            if footer_body:
                self._div(x + pad, fy + 22, iw, 24,
                          f"font-size:10pt;font-weight:700;color:{title_c}",
                          _md(footer_body))

    def flow_step(self, x, y, w, h, num, name, desc="", primary=False):
        if primary:
            fill, border = self.c["accent_bg"], self.c["accent"]
        else:
            fill, border = self.c["surface"], self.c["border"]
        self._el(f'<div style="position:absolute;left:{x}pt;top:{y}pt;'
                 f'width:{w}pt;height:{h}pt;background:{fill};'
                 f'border:0.5pt solid {border};box-sizing:border-box"></div>')
        pad = 16
        iw = w - pad * 2
        self._div(x + pad, y + 14, iw, 16,
                  f"font-size:10pt;font-weight:700;color:{self.c['accent']};"
                  f"font-family:{self._num_font(num)}", _md(num))
        self._div(x + pad, y + 36, iw, 22,
                  f"font-size:10.5pt;font-weight:700;color:{self.c['fg']}",
                  _md(name))
        if desc:
            self._div(x + pad, y + 62, iw, max(16, h - 76),
                      f"font-size:9pt;line-height:1.5;color:{self.c['dim']}",
                      _md(desc), valign="top")

    def compare_pair(self, y, item, before, after, h=44):
        h = max(28, h)
        x0 = 40
        item_w, before_w, after_w = 140, 240, 240
        gap = (640 - item_w - before_w - after_w) // 2
        self._div(x0, y, item_w, h,
                  f"font-size:10.5pt;font-weight:700;color:{self.c['fg']}",
                  _md(item))
        bx = x0 + item_w + gap
        self._el(f'<div style="position:absolute;left:{bx}pt;top:{y}pt;'
                 f'width:{before_w}pt;height:{h}pt;background:{self.c["surface"]};'
                 f'border:0.4pt solid {self.c["border"]};box-sizing:border-box"></div>')
        self._div(bx + 12, y, before_w - 24, h,
                  f"font-size:9pt;color:{self.c['dim']}", _md(before))
        ax = bx + before_w + gap
        self._el(f'<div style="position:absolute;left:{ax}pt;top:{y}pt;'
                 f'width:{after_w}pt;height:{h}pt;background:{self.c["accent_bg"]};'
                 f'border:0.5pt solid {self.c["accent"]};box-sizing:border-box"></div>')
        self._div(ax + 12, y, after_w - 24, h,
                  f"font-size:9pt;color:{self.c['fg']}", _md(after))

    def callout(self, text, sub=""):
        self._new()
        self._el(f'<div style="position:absolute;left:60pt;top:130pt;'
                 f'width:4pt;height:145pt;background:{self.c["accent"]}"></div>')
        self._div(90, 140, 590, 60,
                  f"font-size:22pt;font-weight:700;color:{self.c['fg']}", _md(text))
        if sub:
            self._div(90, 210, 590, 50,
                      f"font-size:9pt;line-height:1.5;color:{self.c['dim']}",
                      _md(sub), valign="top")

    def section_divider(self, number, title, label="Section"):
        self._new()
        num_str = f"{number:02d}" if isinstance(number, int) else str(number)
        self._div(50.9, 102.7, 150, 110,
                  f"font-size:100pt;font-weight:700;color:{self.c['accent']};"
                  f"letter-spacing:-0.02em;line-height:1;"
                  f"font-family:{self._num_font(num_str)}",
                  _md(num_str), valign="top")
        self._div(183.2, 163.2, 200, 16,
                  f"font-size:11.5pt;color:{self.c['dim']};"
                  f"font-family:'Proxima Nova','Montserrat',sans-serif", _md(label))
        self._div(183.2, 180.6, 300, 32,
                  f"font-size:21pt;color:{self.c['fg']}", _md(title))

    def checklist(self, heading, items, eyebrow=""):
        self.start_slide(heading=heading, eyebrow=eyebrow)
        n = max(len(items), 1)
        item_h = max(16, min(52, (373 - 100 - (n - 1) * 4) // n))
        for i, (label, done) in enumerate(items):
            y = 100 + i * (item_h + 4)
            mark_c = self.c["accent"] if done else self.c["dim"]
            self._div(40, y, 32, item_h,
                      f"font-size:12pt;color:{mark_c};align-items:center",
                      "●" if done else "○")
            self._div(82, y, 598, item_h,
                      f"font-size:10.5pt;color:"
                      f"{self.c['dim'] if done else self.c['fg']}", _md(label))

    def numbered_steps(self, heading, items, eyebrow=""):
        self.start_slide(heading=heading, eyebrow=eyebrow)
        n = max(len(items), 1)
        item_h = max(16, min(52, (373 - 100 - (n - 1) * 4) // n))
        for i, item in enumerate(items):
            label = item[0] if isinstance(item, tuple) else item
            y = 100 + i * (item_h + 4)
            self._div(48, y, 32, item_h,
                      f"font-size:10.5pt;font-weight:700;color:{self.c['accent']};"
                      f"align-items:center;font-family:{self._num_font('01')}",
                      f"{i+1:02d}")
            self._div(88, y, 584, item_h,
                      f"font-size:10.5pt;color:{self.c['fg']}", _md(label))

    def conclusion(self, metric, caption="", details=None, heading="", eyebrow=""):
        self.start_slide(heading=heading, eyebrow=eyebrow)
        self._div(36, 130, 290, 80,
                  f"font-size:56pt;font-weight:700;color:{self.c['accent']};"
                  f"letter-spacing:-0.02em;line-height:1;"
                  f"font-family:{self._num_font(metric)}", _md(metric))
        if caption:
            self._div(42, 215, 290, 50,
                      f"font-size:11pt;line-height:1.5;color:{self.c['dim']}",
                      _md(caption), valign="top")
        for i, d in enumerate((details or [])[:4]):
            cy = 110 + i * 52
            self._el(f'<div style="position:absolute;left:370pt;top:{cy}pt;'
                     f'width:314pt;height:44pt;background:{self.c["surface"]};'
                     f'border:0.4pt solid {self.c["border"]};box-sizing:border-box">'
                     f'</div>')
            if d.get("label"):
                self._div(382, cy + 6, 80, 32,
                          f"font-size:8pt;font-weight:700;color:{self.c['accent']};"
                          + self._caps_style(), _md(d["label"]))
            if d.get("body"):
                self._div(470, cy + 6, 210, 32,
                          f"font-size:9pt;line-height:1.4;color:{self.c['fg']}",
                          _md(d["body"]))

    def text(self, x, y, w, h, content, size=10.5, bold=False, color=None,
             align="START"):
        css_align = {"START": "flex-start", "CENTER": "center",
                     "END": "flex-end"}.get(align, "flex-start")
        c = color if isinstance(color, str) else (self.c["fg"] if color is None
                                                  else _hex(color))
        weight = 700 if bold else 400
        self._div(x, y, w, h,
                  f"font-size:{size}pt;font-weight:{weight};color:{c};"
                  f"align-items:{css_align};line-height:1.4", _md(content))

    def divider(self, x, y, w, orange=True):
        color = self.c["accent"] if orange else self.c["dim"]
        weight = 2 if orange else 0.75
        self._el(f'<div style="position:absolute;left:{x}pt;top:{y}pt;'
                 f'width:{w}pt;height:{weight}pt;background:{color}"></div>')

    def slide(self, heading, body, body_size=14):
        self.start_slide(heading=heading)
        self._div(40, 72, 640, 310,
                  f"font-size:{body_size}pt;line-height:1.5;color:{self.c['fg']}",
                  _md(body), valign="top")

    def two_col(self, heading, left_title, left_body, right_title, right_body):
        self.start_slide(heading=heading)
        self._div(40, 76, 310, 28,
                  f"font-size:15pt;font-weight:700;color:{self.c['accent']}",
                  _md(left_title))
        self._div(40, 108, 310, 274,
                  f"font-size:13pt;line-height:1.5;color:{self.c['fg']}",
                  _md(left_body), valign="top")
        self._el(f'<div style="position:absolute;left:365pt;top:76pt;'
                 f'width:1pt;height:300pt;background:{self.c["dim"]}"></div>')
        self._div(375, 76, 310, 28,
                  f"font-size:15pt;font-weight:700;color:{self.c['accent']}",
                  _md(right_title))
        self._div(375, 108, 310, 274,
                  f"font-size:13pt;line-height:1.5;color:{self.c['fg']}",
                  _md(right_body), valign="top")

    # ── V3 리치 블록 미러 ────────────────────────────────────────

    def stat(self, x, y, w, value, label="", delta="", tone=None,
             delta_tone="good", h=80):
        value_c = self.c["fg"] if tone is None else self._tone(tone)[0]
        vy = y
        if label:
            self._div(x, y, w, 12,
                      f"font-size:8pt;font-weight:700;color:{self.c['dim']};"
                      + self._caps_style(), _md(label))
            vy = y + 16
        self._div(x, vy, w, 44,
                  f"font-size:36pt;font-weight:700;color:{value_c};"
                  f"letter-spacing:-0.01em;line-height:1;"
                  f"font-family:{self._num_font(value)}", _md(value))
        if delta:
            self._div(x, vy + 46, w, 14,
                      f"font-size:9pt;font-weight:700;"
                      f"color:{self._tone(delta_tone)[0]}", _md(delta))

    def stat_row(self, y, stats, x=48, w=624, h=80, dividers=True):
        n = max(len(stats), 1)
        gap = 24
        col_w = (w - gap * (n - 1)) / n
        for i, s in enumerate(stats):
            cx = x + i * (col_w + gap)
            self.stat(cx, y, col_w, s.get("value", ""), s.get("label", ""),
                      s.get("delta", ""), s.get("tone"),
                      s.get("delta_tone", "good"), h=h)
            if dividers and i > 0:
                self._el(f'<div style="position:absolute;left:{cx - gap/2}pt;'
                         f'top:{y+6}pt;width:0.5pt;height:{h-12}pt;'
                         f'background:{self.c["border"]}"></div>')

    def bars(self, x, y, w, data, max_value=None, bar_h=16, gap=10,
             label_w=120, value_w=56):
        vals = [float(d.get("value", 0)) for d in data]
        mv = float(max_value) if max_value else (max(vals) if vals else 1.0)
        mv = mv or 1.0
        track_x = x + label_w + 10
        track_w = w - label_w - 10 - value_w - 8
        for i, d in enumerate(data):
            ry = y + i * (bar_h + gap)
            self._div(x, ry, label_w, bar_h,
                      f"font-size:9pt;color:{self.c['fg']}", _md(d.get("label", "")))
            self._el(f'<div style="position:absolute;left:{track_x}pt;top:{ry}pt;'
                     f'width:{track_w}pt;height:{bar_h}pt;'
                     f'background:{self.c["surface_hi"]};'
                     f'border:0.4pt solid {self.c["border"]};box-sizing:border-box">'
                     f'</div>')
            ratio = max(0.0, min(1.0, float(d.get("value", 0)) / mv))
            if d.get("primary"):
                fill = self._tone(d.get("tone", "accent"))[0]
            elif d.get("tone"):
                fill = self._tone(d["tone"])[0]
            else:
                fill = self.c["border_hi"]
            fw = track_w * ratio
            if fw >= 1:
                self._el(f'<div style="position:absolute;left:{track_x}pt;'
                         f'top:{ry}pt;width:{fw}pt;height:{bar_h}pt;'
                         f'background:{fill}"></div>')
            disp = d.get("display", d.get("value", ""))
            self._div(track_x + track_w + 8, ry, value_w, bar_h,
                      f"font-size:9pt;font-weight:700;color:{self.c['fg']};"
                      f"align-items:flex-end;font-family:{self._num_font(disp)}",
                      _md(disp))

    def progress(self, x, y, w, pct, label="", tone="accent", bar_h=8):
        tone_fg, _ = self._tone(tone)
        pct_num = float(pct)
        if label:
            self._div(x, y, w - 64, 12,
                      f"font-size:9pt;color:{self.c['dim']}", _md(label))
        self._div(x + w - 60, y, 60, 12,
                  f"font-size:9pt;font-weight:700;color:{tone_fg};"
                  f"align-items:flex-end;font-family:{self._num_font('0')}",
                  f"{pct_num:g}%")
        by = y + 16
        self._el(f'<div style="position:absolute;left:{x}pt;top:{by}pt;'
                 f'width:{w}pt;height:{bar_h}pt;background:{self.c["surface_hi"]};'
                 f'border:0.4pt solid {self.c["border"]};box-sizing:border-box">'
                 f'</div>')
        fw = w * max(0.0, min(1.0, pct_num / 100.0))
        if fw >= 1:
            self._el(f'<div style="position:absolute;left:{x}pt;top:{by}pt;'
                     f'width:{fw}pt;height:{bar_h}pt;background:{tone_fg}"></div>')

    def timeline(self, y, milestones, x=48, w=624):
        n = max(len(milestones), 1)
        line_y = y + 30
        self._el(f'<div style="position:absolute;left:{x+12}pt;top:{line_y}pt;'
                 f'width:{w-24}pt;height:1pt;background:{self.c["border_hi"]}">'
                 f'</div>')
        seg = w / n
        state_color = {"done": self.c["good"], "current": self.c["accent"],
                       "next": self.c["border_hi"]}
        for i, m in enumerate(milestones):
            cx = x + seg * i + seg / 2
            state = m.get("state", "next")
            color = state_color.get(state, self.c["border_hi"])
            d = 10 if state == "current" else 8
            self._el(f'<div style="position:absolute;left:{cx - d/2}pt;'
                     f'top:{line_y - d/2}pt;width:{d}pt;height:{d}pt;'
                     f'border-radius:50%;background:{color};'
                     f'border:1pt solid {self.c["bg"]};box-sizing:border-box">'
                     f'</div>')
            if m.get("date"):
                self._div(cx - seg / 2, y, seg, 12,
                          f"font-size:8pt;color:{self.c['dim']};"
                          f"align-items:center;"
                          f"font-family:{self._num_font(m['date'])}",
                          _md(m["date"]))
            is_current = state == "current"
            label_c = self.c["fg"] if state in ("done", "current") else self.c["dim"]
            self._div(cx - seg / 2, line_y + 12, seg, 16,
                      f"font-size:9.5pt;font-weight:{700 if is_current else 400};"
                      f"color:{label_c};align-items:center",
                      _md(m.get("label", "")))
            if m.get("desc"):
                self._div(cx - seg / 2, line_y + 30, seg, 24,
                          f"font-size:8pt;line-height:1.4;color:{self.c['dim']};"
                          f"align-items:center;text-align:center",
                          _md(m["desc"]), valign="top")

    def badge(self, x, y, text, tone="neutral", w=None, h=16):
        tone_fg, tone_bg = self._tone(tone)
        text = str(text)
        if w is None:
            est = sum(9.0 if ord(ch) > 0x2E80 else 5.0 for ch in text)
            w = max(36, est + 18)
        self._div(x, y, w, h,
                  f"font-size:7.5pt;font-weight:700;color:{tone_fg};"
                  f"background:{tone_bg};border:0.5pt solid {tone_fg};"
                  f"border-radius:3pt;align-items:center;box-sizing:border-box",
                  _md(text))
        return w

    def image(self, url, x, y, w, h):
        self._el(f'<img src="{_html.escape(url, quote=True)}" '
                 f'style="position:absolute;left:{x}pt;top:{y}pt;'
                 f'width:{w}pt;height:{h}pt;object-fit:cover">')

    def full_image(self, url, heading="", eyebrow="", caption=""):
        if heading or eyebrow:
            self.start_slide(heading=heading, eyebrow=eyebrow)
            img_h = 273 - (14 if caption else 0)
            self.image(url, 48, 100, 624, img_h)
            if caption:
                self._div(48, 100 + img_h + 2, 624, 12,
                          f"font-size:7.5pt;color:{self.c['dim']}", _md(caption))
        else:
            self._new()
            self.image(url, 0, 0, 720, 405)

    # ── 출력 ─────────────────────────────────────────────────────

    def flush(self, path=None):
        """HTML 파일 작성. 반환: 파일 경로."""
        if path is None:
            safe = re.sub(r"[^\w가-힣-]+", "_", self.title)[:40] or "deck"
            path = f"/tmp/spigen_preview_{safe}.html"
        bg = self.c["bg"]
        page_bg = "#1A1A1A" if self.theme == "dark" else "#ECEAE3"
        chrome_fg = "#888888" if self.theme == "dark" else "#696867"
        slides_html = []
        total = len(self._slides)
        for i, s in enumerate(self._slides, 1):
            note = f' — {_html.escape(s["note"])}' if s["note"] else ""
            slides_html.append(
                f'<div class="wrap">'
                f'<div class="meta">{i} / {total}{note}</div>'
                f'<div class="slide">{"".join(s["els"])}</div>'
                f'</div>')
        doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html.escape(self.title)} — Spigen 시안</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; }}
  body {{ background:{page_bg}; font-family:'Noto Sans KR',sans-serif;
         padding:24pt 0 48pt; }}
  .wrap {{ width:720pt; margin:0 auto 28pt; }}
  .meta {{ font-size:9pt; color:{chrome_fg}; margin:0 0 4pt 2pt;
          font-family:'Montserrat','Noto Sans KR',sans-serif; }}
  .slide {{ position:relative; width:720pt; height:405pt; background:{bg};
           overflow:hidden; box-shadow:0 2pt 14pt rgba(0,0,0,0.35); }}
  .slide b {{ font-weight:700; }}
</style>
</head>
<body>
<div class="meta" style="width:720pt;margin:0 auto 16pt;font-size:11pt">
{_html.escape(self.title)} — 시안 미리보기 ({self.theme} / {total}장)
</div>
{"".join(slides_html)}
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[HTML 시안] {path} ({total}장, theme={self.theme})")
        return path
