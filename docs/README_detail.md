# Lifecycle Analysis Library

時系列イベントから「存在期間（Lifecycle）」を抽出し、
統計解析を行うためのライブラリです。

当初は Firewall の接続イベント解析を目的として開発しましたが、
設計を汎用化することで、時系列イベント全般に適用できる構成を目指しています。

---

# 設計コンセプト

本ライブラリでは、

> **「観測されたイベント」と「解析に利用できるイベント」は異なる**

という考え方を基本としています。

例えば、

- 観測開始時点ですでに存在していたデータ
- 観測終了時点でも存在しているデータ
- 状態遷移が破綻しているデータ

は、観測はされていても、本来のライフサイクルを正しく表しているとは限りません。

そこで本ライブラリでは、

- **Lifecycle** は「観測された事実」を保持する
- **AnalysisData** は「解析可能なデータ」を保持する

というように両者を明確に分離しています。

これにより、

- 解析の再現性
- 解析結果の信頼性
- フィルタ条件の切り替え（trusted=True / False）

を一貫した設計で実現しています。

---

# 全体構成

ライブラリは責務ごとに4層へ分離しています。

```
Raw Events
    │
    ▼
LifecycleBuilder
    │
    ▼
Lifecycle
    │
    ▼
AnalysisBuilder
    │
    ▼
AnalysisData
    │
    ▼
LifecycleAnalyzer
```

各層は役割を明確に分離し、それぞれ単一責務となるよう設計しています。

---

# Phase 1 : Raw Events

入力となるイベントデータです。

例）

| datetime | ip | event |
|----------|----|-------|
| 10:00 | A | ACCEPT |
| 10:01 | A | ACCEPT |

イベントの形式は任意ですが、

- 時刻
- 対象（IP、ユーザー、製品など）
- イベント種別

を持つことを想定しています。

---

# Phase 2 : LifecycleBuilder

イベント列から、観測情報のみを生成します。

```
Events
    │
    ▼
Presence
    │
    ▼
Transition
    │
    ▼
Observation
    │
    ▼
Lifecycle
```

Lifecycle が保持するのは観測事実のみです。

```
Lifecycle
├── presence
├── transition
├── observation
└── sample_interval
```

この段階では解析は行いません。

---

# Phase 3 : AnalysisBuilder

Lifecycle を解析用データへ変換します。

```
Lifecycle
      │
      ▼
Raw State
      │
      ▼
Quality
      │
      ▼
Analysis Mask
      │
      ▼
Analysis State
      │
      ▼
Lifetime
      │
      ▼
Boundary
      │
      ▼
Segment
      │
      ▼
AnalysisData
```

trusted=True の場合は、

```
analysis_mask =
    observation.trusted_mask
    &
    quality.good
```

を適用し、

- 観測開始前から存在していたデータ
- 観測終了後まで存在しているデータ
- 状態遷移が異常なデータ

を解析対象から除外します。

---

# Phase 4 : LifecycleAnalyzer

AnalysisData を入力として統計解析を行います。

主な解析項目

- Duration
- Segment Duration
- Summary
- Statistics
- Histogram

Analyzer は解析のみを担当し、
データ生成やフィルタリングは行いません。

---

# 設計方針

各クラスの責務は以下の通りです。

| クラス | 役割 |
|---------|------|
| LifecycleBuilder | イベントから Lifecycle を生成する |
| Lifecycle | 観測事実を保持する |
| AnalysisBuilder | 解析用データを生成する |
| AnalysisData | 解析用データを保持する |
| LifecycleAnalyzer | 統計解析を行う |

各クラスは単一責務となるよう設計し、
解析アルゴリズムとデータ生成処理を分離しています。


# データフロー

本ライブラリは、イベントデータから解析結果を得るまでを4段階に分けています。

```text
Raw Events
    │
    ▼
LifecycleBuilder
    │
    ▼
Lifecycle
    │
    ▼
AnalysisBuilder
    │
    ▼
AnalysisData
    │
    ▼
LifecycleAnalyzer
```

各層は前段のデータを入力として受け取り、新しい情報を生成します。

- LifecycleBuilder は観測データを生成します。
- AnalysisBuilder は解析可能なデータを生成します。
- LifecycleAnalyzer は統計解析のみを担当します。

# Lifecycle

Lifecycle は「観測された事実」を保持します。

```
Events
    │
    ▼
Presence
    │
    ▼
Transition
    │
    ▼
Observation
```

保持する情報

- Presence
- Transition
- Observation
- Sample Interval

この層では解析は行いません。

# AnalysisData

AnalysisData は解析に必要な情報のみを保持します。

```
Raw State
    │
    ▼
Quality
    │
    ▼
Analysis Mask
    │
    ▼
Analysis State
    │
    ▼
Lifetime
    │
    ▼
Boundary
    │
    ▼
Segment
```

trusted=True の場合、

```
analysis_mask =
    observation.trusted_mask
    &
    quality.good
```

を適用して解析用データを生成します。

# LifecycleAnalyzer

LifecycleAnalyzer は AnalysisData を入力として統計解析を行います。

現在実装している解析

- Summary
- Statistics
- Histogram
- Duration
- Segment Duration

今後追加予定

- Survival Analysis
- Transition Matrix
- State Distribution


# 実装方針

本ライブラリでは、可能な限り

- for文
- Pythonループ

を使用せず、

Pandas / NumPy のベクトル演算によって実装しています。

これにより、

- 高速な処理
- シンプルなアルゴリズム
- テストしやすい関数

を実現しています。


# BIT行列演算

本ライブラリでは、Presence（存在情報）を基準とした BIT 行列を、
段階的に変換することでライフサイクル解析を行います。

可能な限り for 文を使用せず、Pandas / NumPy のベクトル演算のみで実装しています。

---

## Presence

観測された存在情報です。

```
Time      A
00:00     0
00:01     1
00:02     1
00:03     0
00:04     0
```

---

## Transition

Presence の変化点を表します。

```
Presence

0
1
1
0
0

↓

Transition

 0
+1
 0
-1
 0
```

生成方法

```python
transition = presence.astype(int).diff()
```

---

## State

Transition の累積和です。

```
Transition

 0
+1
 0
-1
 0

↓

State

0
1
1
0
0
```

生成方法

```python
state = transition.cumsum()
```

State が 0 より大きい間を「存在中」とみなします。

---

## Lifetime

State を bool に変換したものです。

```
State

0
1
2
1
0

↓

Lifetime

0
1
1
1
0
```

生成方法

```python
lifetime = state > 0
```

---

## Observation

観測開始・終了の影響を除去するためのマスクです。

```
Presence

1111001111101111

↓

Trusted Mask

0000111111100000
```

解析対象

    ↑↑↑↑↑↑↑

- 観測開始時にすでに存在していた期間は除外します。
- 観測終了時まで継続している期間は除外します。
- 開始位置・終了位置の両方が観測できた期間のみを解析対象とします。
観測開始前から存在していた期間、および観測終了後も継続している期間を除外します。

### 導出方法

開始側

```
Presence

1111001111101111

↓

NOT

0000110000010000

↓

cumsum()

0000123333344444

↓

> 0

0000111111111111
```

終了側

```
Presence

1111001111101111

↓

Reverse

1111011111001111

↓

NOT

0000100000110000

↓

cumsum()

0000111111223334

↓

Reverse

1111111111100000
```

Trusted Mask

```
Left Mask

0000111111111111

AND

Right Mask

1111111111100000

↓

Trusted Mask

0000111111100000
```

生成コード

```python
left = (~presence).cumsum() > 0

right = (
    (~presence.iloc[::-1])
    .cumsum()
    .iloc[::-1]
    > 0
)

trusted_mask = left & right

```

このマスクにより、

- 観測開始前から存在していたデータ
- 観測終了後も継続しているデータ

を除外し、開始・終了の両方が観測できた期間のみを解析対象とします。

---

## Analysis Mask

解析対象となるデータを決定します。

```
analysis_mask =
    observation.trusted_mask
    &
    quality.good
```

---

## Segment ID

Lifetime の立ち上がりを検出し、
各ライフサイクルへ番号を付与します。

```
Lifetime

011001110

↓

Segment ID

011002220
```

生成イメージ

```python
segment_id = (
    lifetime
    &
    ~lifetime.shift(fill_value=False)
).cumsum()
```

---

## Segment Length

Segment ID ごとの長さを集計します。

```
Segment ID

011002220

↓

Segment Length

Segment 1 : 2
Segment 2 : 3
```

groupby によりベクトル演算で求めています。

---

以上の変換を組み合わせることで、

```
Presence
    │
    ▼
Transition
    │
    ▼
State
    │
    ▼
Segment
    │
    ▼
Lifetime
```

という流れでライフサイクル解析を実現しています。


Events
 ↓
Presence
 ↓
Transition
 ↓
State
        │
        ├─ Quality
        │
        └─ Boundary Analysis
              ├ boundary_start
              ├ boundary_end
              ├ active_duration
              ├ segment_length
              ├ segment_count
              └ duration statistics


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
