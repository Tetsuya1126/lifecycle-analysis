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

