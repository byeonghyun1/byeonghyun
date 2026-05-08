# Banner Maker 자체점검 누적 리스트

> **자체점검 정의** (사용자 명시):
> - 중복코드가 있는지
> - 확장성에 문제가 생기는 요소가 있는지 (기능/요소/가이드 추가 시 코드가 꼬일만한 요소)
> - 불필요한 코드가 있는지
> - 추후에 문제가 생길만한 요소가 있는지

---

## 진행 현황 (2026-05-08 기준)

| 카테고리 | 항목 |
|---|---|
| 🔴 high (실제 잠재 버그) | #1 ✅, #2 ✅, #3 ✅ |
| 🟡 mid (확장성 저해) | #4 ✅, #5 ✅, #6 ⏳보류, #7 ✅, #8 ✅, #16 ⏳보류, #17 ✅, #18 ✅, #19 ✅, #20 ✅(부분), #21 ✅, #22 ⏳보류 |
| 🟢 lower (중복·잔재·명명) | #9 ✅, #10 ✅(부분), #11 ✅, #12 ✅, #13 ✅, #14 ⏳보류, #15 ✅, #23 ✅, #24 ✅, #25 ✅, #26 ✅ |

**처리 완료**: 21건 (#1~#5, #7~#13, #15, #17, #18, #19, #20부분, #21, #23~#26)
**보류**: 5건 (#6, #14, #16, #22, #10/#20부분 — 효과 vs 회귀 위험 균형)

---

## 🔴 high

### #1. auto 모드 다운로드 시 학습 (0,0,0) 누적 ✅ DONE (2026-05-07)
- **처리**: `saveCalibration()` 시작부에 `if (t.mode !== 'manual') return;` 추가
- **효과**: 사용자가 직접 조정한 케이스만 학습 데이터로 누적

### #2. cal + manual offset 합산 누적 위험 ✅ DONE (2026-05-07)
- **처리**: `saveCalibration()` 내부에서 기존 cal을 cache에서 가져와 manual과 합쳐 절대값으로 sample 저장
- **효과**: 사용자가 최종 본 위치(cal+manual)가 평균값으로 수렴 → 발산 방지

### #3. contentBoundsCache 무효화 시점 ✅ 점검 완료
- **결과**: `loadImageFile()`·`removeImage()`에서 `state[cfg.stateBounds] = null` 처리되어 정상 동작
- **위치**: prototype.html 1040, 1072줄
- **상태**: 추가 작업 불필요. close.

---

## 🟡 mid

### #4. getImageTransform / getImageTransform2 분리 — 슬롯 확장 한계 ✅ DONE (2026-05-07)
- **처리**: `getImageTransform(sizeId, slot='main')`로 시그니처 확장. slot 인자에 'sub' 등 향후 추가 가능. `getImageTransform2`는 호환 wrapper로 유지 (점진 마이그레이션)
- **효과**: 새 슬롯 추가 시 함수 시그니처 변경 없이 slot 키만 추가하면 됨

### #5. contentBoundsCache / contentBoundsCache2 동일 한계 ✅ DONE (2026-05-07)
- **처리**: `state.contentBoundsCaches = { main, sub, logo, sourceLogo }` 객체화. IMG_SLOTS의 `boundsSlot` 키로 슬롯 매핑. 모든 호출부 (loadImageFile, removeImage, drawAnchorImage 2곳, computeGroupedImgData) 변경 완료

### #6. 새 fitMode 추가 시 5곳 수정 필요 ⏳ 보류 (회귀 위험 vs 효과 균형)
- **이유**: 현재 fitMode가 contain·crop 두 개뿐. 전략 패턴 도입은 회귀 위험이 큼에 비해 효과 점진적
- **권고**: 새 fitMode (예: focal_point) 도입 시 함께 리팩토링 진행

### #7. cropAutoValues 변수명 모호 ✅ DONE (2026-05-07)
- **처리**: 9곳 `cropAutoValues` → `imageAutoValues`로 일괄 리네이밍 + 주석 업데이트 ("contain·crop 모드 모두 사용")

### #8. _index.json ↔ config/banners/ 정합성 자동 검증 없음 ✅ DONE (2026-05-07)
- **처리**: `loadPresets()`에서 `ui_visible`과 `banners` 배열 cross-check, 누락 시 콘솔 경고

### #16. getCalibrationBoost의 cal 반환 사용 부분만 ⏳ 보류 (큰 문제 아님)

### #17. JSON adapter 매핑 검증 없음 ✅ DONE (2026-05-07)
- **처리**: `validateBannerJson()` 함수 신규 추가. 필수 키 (id, name, dimensions, margins, fonts.main, fonts.sub) 누락 시 콘솔 경고. `loadPresets()`에서 모든 배너에 적용

---

## 🟢 lower

### #9. drawFullImage crop·contain 분기 90% 중복 ✅ DONE (2026-05-07)
- **처리**: `const fitFn = (fm === 'crop') ? Math.max : Math.min;` 한 줄로 통합. 그리기 로직 1회로 감축

### #10. 학습값 적용 패턴 4곳 중복 ✅ DONE 부분 (2026-05-07)
- **처리**: `applyCalToTransform({ baseScale, userScale, baseX, baseY, ox, oy }, cal)` 헬퍼 신규 추가. 새 분기 추가 시 사용 권장
- **미적용 분기**: 기존 4곳은 변경량 vs 가독성 trade-off로 그대로 유지 (이미 `getCalibrationBoost()` + 명시적 패턴 사용 중). 새 분기 도입 시 헬퍼 사용

### #11. drawAnchorImage 변수명 컨벤션 불일치 (fmA·sdA·oxdA) ✅ DONE (2026-05-07)
- **처리**: 일반 anchor 블록 변수명을 `fm, cal, scaleDelta, offsetXDelta, offsetYDelta`로 통일. below_text가 return으로 종료되어 충돌 없음

### #12. isRight 변수명 의미 반전 ✅ DONE (2026-05-07)
- **처리**: `computeGroupedImgData(img, isSecondary)`로 리네이밍 + 함수 위에 슬롯 매핑 주석 추가

### #13. WORD_WRAP_BANNERS 주석 잔재 ✅ DONE (2026-05-07)
- **처리**: 2곳 주석을 `preset.mainAutoWrap === true 배너만`으로 갱신

### #14. 옛 호환 키 폴백 영구화 ⏳ 보류
- **이유**: 마이그레이션 시점은 사용자 결정 필요. 현재는 안전한 폴백 유지

### #15. userScale 추출 패턴 3곳 반복 ✅ DONE (2026-05-07)
- **처리**: `getEffectiveTransform(t)` 헬퍼 추가, `{ userScale, ox, oy }` 반환. 3곳(`drawAnchorImage`·`drawFullImage`·`computeGroupedImgData`)에 적용

---

## 처리 순서

1. **high #1, #2** (실제 버그 — 즉시)
2. **lower 단순 리팩토링** (#9, #11, #12, #13, #15)
3. **lower 헬퍼 통합** (#10)
4. **mid 구조 변경** (#4, #5, #6, #7, #8, #17) — 사용자 확인 후 단계별

## 변경 이력
- 2026-05-07: 초기 작성 (17개 항목 등록), #3 close
- 2026-05-07: high #1, #2 처리 완료
- 2026-05-07: lower #9, #11, #12, #13, #15 처리 완료
- 2026-05-07: mid #4, #5, #7, #8, #17 처리 완료 + lower #10 부분 처리 (헬퍼 추가)
- 2026-05-08: 자체점검 #18~#26 등록 (이벤트 리스트 시리즈·신규 anchor·모달 작업 결과)
- 2026-05-08: lower #23 (매직 넘버 주석), mid #19 (zone anchor 패턴), lower #26 (getImageBoxOpt 헬퍼) 처리
- 2026-05-08: mid #21 (resolveCompositionType), lower #24 (setupModalField 추출) 처리
- 2026-05-08: mid #18+#25 시리즈 base 도입 (_index.json _series, deepMergePreset, m_event_list_1~5 _extends 적용)
- 2026-05-08: mid #20 부분 처리 (getAnchorKind 디스패치 헬퍼)
- 2026-05-08: mid #22 보류 (image_box 그룹화 — 회귀 위험 vs 효과 균형)

---

## 🟡 mid (오늘 추가)

### #18+#25. 이벤트 리스트 시리즈 정책 키 5곳 중복 / m_event_list_x 파일 거의 동일 ✅ DONE (2026-05-08)
- **처리**:
  - `_index.json`에 `_series.event_list` 추가 (시리즈 공통 정책)
  - `prototype.html`: `deepMergePreset` 헬퍼 + `loadPresets`에서 `_extends` 처리
  - m_event_list_1~5.json: 시리즈 공통 키 제거, `"_extends": "event_list"` 한 줄로 상속
- **효과**: 시리즈 정책 변경 시 _index.json 한 곳만 수정. 신규 이벤트 리스트 배너 추가 시 70줄 → 20줄 정도

### #19. right_zone_center 분기 2곳 하드코딩 ✅ DONE (2026-05-08)
- **처리**: `endsWith('_zone_center')` 패턴 매칭으로 일반화 (drawAnchorImage + renderToCanvas useAnchorFlow)
- **효과**: 새 zone anchor (예: left_zone_center) 추가 시 코드 변경 없이 자동 인식

### #20. drawAnchorImage anchor별 if-분기 누적 ✅ DONE 부분 (2026-05-08)
- **처리**: `getAnchorKind(anchor)` 디스패치 헬퍼 추가 — 새 anchor 추가 시 이 함수만 수정
- **미처리**: 분기 본문은 그대로 (함수 추출은 회귀 위험 커서 미실행)
- **권고**: 4번째 anchor 추가 시 본문도 추출 (drawZoneCenterAnchor·drawBelowTextAnchor·drawGenericAnchor)

### #21. getCompositionDecision 활성화 조건 OR 누적 ✅ DONE (2026-05-08)
- **처리**: `resolveCompositionType(preset)` 헬퍼 추가
  - 우선순위: `composition_type` 명시 → `sub_supported: false` → 옛 composition 문자열
  - 새 type 추가 시 헬퍼만 수정
- **효과**: 새 분기 활성화 조건 추가 시 if 문 OR 폭증 방지

### #22. image_box 객체 책임 비대 ⏳ 보류 (2026-05-08)
- **이유**: JSON 구조 변경이 모든 배너 영향 → 회귀 위험 큼 vs 효과 점진
- **부분 효과**: #26 `getImageBoxOpt` 헬퍼로 일부 일관성 확보
- **권고**: 키가 12개 이상 누적될 때 그룹화 검토

---

## 🟢 lower (오늘 추가)

### #23. drawText single_main else 매직 넘버 0.38 ✅ DONE (2026-05-08)
- **처리**: 주석 추가 — "ascent/descent 비율 기반 baseline 위치 보정값"으로 의미 설명
- **권고**: 향후 ctx.measureText로 정확 측정 또는 상수화 고려

### #24. 모달 입력 메인/서브 분리 처리 ✅ DONE (2026-05-08)
- **처리**: `setupModalField()` 함수 추출 — 옵션 객체로 메인/서브 통합 처리
  - initialValue, maxChars, label, placeholder, disabled, disabledMessage, lineBreakAllowed, onInput
- **효과**: 모달 신규 입력 추가 시 옵션만 추가. 코드 중복 제거

### #25. m_event_list_x.json 5개 파일 구조 거의 동일 ✅ DONE (2026-05-08)
- **처리**: #18과 통합 — `_extends: "event_list"` 패턴 적용
- 5개 파일이 차이점만 명시 (dimensions·margins·fonts·max_chars 등)

### #26. preset.imageBox?.X ?? DEFAULT 패턴 반복 ✅ DONE (2026-05-08)
- **처리**: `getImageBoxOpt(preset, key, defaultVal)` 헬퍼 추가
- **적용**: `createScaleSlider` 내 `scale_min`/`scale_max` 호출
- **권고**: 점진적으로 다른 호출부도 헬퍼 사용
