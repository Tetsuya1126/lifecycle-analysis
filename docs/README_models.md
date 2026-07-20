
# Lifecycle Model

## Overview

本ライブラリは、時系列のライフサイクル情報を解析するために、複数のデータモデルを定義しています。

各モデルは以下の役割を持ちます。

```
Lifecycle
    │
    ├── Presence
    ├── Transition
    ├── State
    ├── ObservationMask
    │
    └──────────────┐
                   │
                   ▼
             AnalysisData
                   │
                   ├── QualityMask
                   ├── ActivityAnalysis
                   └── Analysis State
```

---

# Lifecycle

ライフサイクル全体を保持する基本モデルです。

```python
Lifecycle
```

| Field             | Description    |
| ----------------- | -------------- |
| `name`            | ライフサイクル名       |
| `presence`        | Presence（存在情報） |
| `transition`      | 状態変化イベント       |
| `state`           | 各時刻の状態         |
| `observation`     | 観測品質情報         |
| `sample_interval` | サンプリング周期（秒）    |

---

# ObservationMask

観測区間の品質を管理します。

```python
ObservationMask
```

| Field            | Description |
| ---------------- | ----------- |
| `observed`       | 観測されたIP     |
| `started_before` | 観測開始以前から存在  |
| `ended_after`    | 観測終了後も存在    |
| `complete`       | 完全に観測できたIP  |
| `trusted_mask`   | 信頼できる時系列領域  |

`trusted_mask` は、観測開始・終了の影響を除去するためのマスクです。

---

# QualityMask

状態遷移品質の判定結果です。

```python
QualityMask
```

| Field       | Description |
| ----------- | ----------- |
| `duplicate` | 重複イベント      |
| `orphan`    | 孤立イベント      |
| `good`      | 正常イベント      |

---

# BoundaryMask

アクティブ区間の境界情報を保持します。

```python
BoundaryMask
```

| Field             | Description |
| ----------------- | ----------- |
| `boundary_start`  | 区間開始        |
| `boundary_end`    | 区間終了        |
| `active_duration` | 区間内継続時間     |

---

# ActivityAnalysis

ライフサイクルの活動状況を解析した結果です。

```python
ActivityAnalysis
```

| Field            | Description  |
| ---------------- | ------------ |
| `lifetime`       | Active状態     |
| `boundary`       | BoundaryMask |
| `segment_length` | 各セグメント長      |

---

# AnalysisData

解析処理全体で利用する統合データです。

```python
AnalysisData
```

## Raw Data

| Field             | Description |
| ----------------- | ----------- |
| `raw_state`       | 元State      |
| `sample_interval` | サンプリング周期    |
| `quality`         | QualityMask |

## Analysis Data

| Field            | Description |
| ---------------- | ----------- |
| `analysis_mask`  | 解析対象マスク     |
| `analysis_state` | マスク適用後State |

## Activity

| Field      | Description      |
| ---------- | ---------------- |
| `activity` | ActivityAnalysis |

---

# LifecycleComparison

2つのライフサイクルを比較した結果です。

```python
LifecycleComparison
```

| Field        | Description |
| ------------ | ----------- |
| `left_name`  | 左側ライフサイクル名  |
| `right_name` | 右側ライフサイクル名  |
| `overlap`    | 共通部分        |
| `only_left`  | 左のみ         |
| `only_right` | 右のみ         |
| `union`      | 和集合         |

---

# LifecycleSet

複数ライフサイクルを管理します。

```python
LifecycleSet
```

| Field        | Description |
| ------------ | ----------- |
| `lifecycles` | ライフサイクル辞書   |

---

# Design Principles

本ライブラリでは以下の方針を採用しています。

* **Immutable (`frozen=True`)** を基本とし、副作用を防ぐ。
* **`slots=True`** によりメモリ使用量を削減する。
* 各モデルは役割を明確に分離する。
* `Lifecycle` は入力データ、`AnalysisData` は解析結果を保持する。
* マスク系モデル（`ObservationMask`、`QualityMask`、`BoundaryMask`）は解析ロジックを単純化するための補助情報として扱う。
