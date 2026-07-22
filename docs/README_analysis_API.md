# Lifecycle Analyzer API

`LifecycleAnalysis` はイベントログからライフサイクルを構築し、
各ライフサイクルの時間的特徴・構造・品質を解析します。

## Basic Usage

```python
from lifecycle import LifecycleAnalysis

analysis = LifecycleAnalysis(
    df,
    event="ASSURED",
)

summary = analysis.summary()
```

---

# API Overview

| Category | Methods |
|-----------|---------|
| Time | `duration()`, `active_duration()`, `segment_duration()`, `mean_segment_duration()`, `max_segment_duration()`, `min_segment_duration()`, `mean_segment_duration_seconds()`, `max_segment_duration_seconds()`, `min_segment_duration_seconds()` |
| Structure | `samples()`, `segments()`, `segment_count()` |
| Quality | `duplicate()`, `orphan()`, `good()`, `started_before()`, `ended_after()`, `complete()`, `coverage_ratio()` |
| Distribution | `lifetime_distribution()`, `segment_distribution()`, `histogram()` |
| Summary | `summary()`, `statistics()` |

---

# Time Features

時間に関する特徴量です。

## duration()

ライフサイクル全体の活動時間を返します。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

### Example

```
USER_A   0 days 00:15:00
USER_B   0 days 01:32:00
```

---

## active_duration()

最も長い連続活動区間の長さを返します。

```
11110001111111

↓

7 samples
```

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

---

## segment_duration()

各セグメントの長さを返します。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")

Index:
(lifecycle, segment_id)
```

### Example

```
USER_A  1   0 days 00:01:00
USER_B  2   0 days 00:04:00
USER_C  3   0 days 00:08:00
```

---

## mean_segment_duration()

平均セグメント長を返します。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

---

## max_segment_duration()

最長セグメントを返します。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

---

## min_segment_duration()

最短セグメントを返します。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

---

## mean_segment_duration_seconds()

平均セグメント長を**秒単位**で返します。

`Timedelta` ではなく整数値が返るため、
統計解析や機械学習の特徴量として利用しやすい形式です。

### Returns

```python
pd.Series(dtype=int)
```

### Example

```
USER_A     182
USER_B     45
```

---

## max_segment_duration_seconds()

最長セグメント長を秒単位で返します。

### Returns

```python
pd.Series(dtype=int)
```

---

## min_segment_duration_seconds()

最短セグメント長を秒単位で返します。

### Returns

```python
pd.Series(dtype=int)
```

---

# Structure Features

ライフサイクルの構造を表す特徴量です。

## samples()

活動サンプル数です。

```
111011

↓

5
```

### Returns

```python
pd.Series(dtype=int)
```

---

## segments()

開始セグメント数です。

```
001110011

↓

2
```

### Returns

```python
pd.Series(dtype=int)
```

---

## segment_count()

検出されたセグメント数です。

通常は

```
segment_count == segments
```

となります。

### Returns

```python
pd.Series(dtype=int)
```

---

# Quality Features

解析品質を表す特徴量です。

## duplicate()

重複イベントが検出されたか。

### Returns

```python
pd.Series(dtype=bool)
```

---

## orphan()

開始または終了イベントが欠落しているか。

### Returns

```python
pd.Series(dtype=bool)
```

---

## good()

品質上の問題が存在しないライフサイクルです。

```
good =
not duplicate
and
not orphan
```

### Returns

```python
pd.Series(dtype=bool)
```

---

## started_before()

観測開始以前から存在していたライフサイクルです。

```
Observation

|-------------->

Presence

1111111000
^^^^^^
```

### Returns

```python
pd.Series(dtype=bool)
```

---

## ended_after()

観測終了後も継続していたライフサイクルです。

```
Observation

<--------------|

Presence

0001111111
      ^^^^^^
```

### Returns

```python
pd.Series(dtype=bool)
```

---

## complete()

観測期間内で開始・終了がともに観測されたライフサイクルです。

```
not started_before
and
not ended_after
```

### Returns

```python
pd.Series(dtype=bool)
```

---

## coverage_ratio()

解析対象として利用できた活動サンプル割合です。

```
analysis samples
----------------
raw samples
```

### Range

```
0.0 ～ 1.0
```

### Returns

```python
pd.Series(dtype=float)
```

---

# Distribution

## lifetime_distribution()

ライフサイクル全体の活動時間分布です。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")
```

---

## segment_distribution()

各セグメント長の分布です。

### Returns

```python
pd.Series(dtype="timedelta64[ns]")

Index:
(lifecycle, segment_id)
```

---

# Summary API

## summary()

ライフサイクルごとの特徴量を 1 行にまとめた DataFrame を返します。

### Columns

| Category | Columns |
|----------|---------|
| Time | `duration`, `active_duration`, `mean_segment_duration`, `max_segment_duration`, `min_segment_duration` |
| Structure | `samples`, `segments`, `segment_count` |
| Quality | `duplicate`, `orphan`, `good`, `started_before`, `ended_after`, `complete`, `coverage_ratio` |

### Returns

```python
pd.DataFrame
```

---

## statistics()

`summary()` の数値列について `describe()` を返します。

`Timedelta` 型は秒へ変換して集計されます。

### Returns

```python
pd.DataFrame
```

---

## histogram()

指定した特徴量のヒストグラムを作成します。

```python
analysis.histogram(
    "duration",
    bins=20,
)
```

### Parameters

| Name | Description |
|------|-------------|
| `column` | `summary()` の列名 |
| `bins` | ヒストグラムのビン数 |

### Returns

| Column | Description |
|--------|-------------|
| `count` | サンプル数 |
| `left` | ビン左端 |
| `right` | ビン右端 |

`Timedelta` 型は秒へ変換してヒストグラムを作成します。


# Creating a LifecycleAnalysis

`LifecycleAnalysis` はイベントログ (`DataFrame`) からライフサイクル解析を行うためのエントリーポイントです。

## Constructor

```python
LifecycleAnalysis(
    df,
    *,
    event,
    trusted=True,
    name=None,
    event_col="event",
    time_col="datetime",
    ip_col="ip",
    interval=None,
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `pd.DataFrame` | - | Event log to analyze. |
| `event` | `str` | - | Target event name. Only rows matching this event are analyzed. |
| `trusted` | `bool` | `True` | If `True`, exclude uncertain observation boundaries from the analysis. |
| `name` | `str \| None` | `None` | Name assigned to the generated lifecycle. If omitted, `event` is used. |
| `event_col` | `str` | `"event"` | Column containing event names. |
| `time_col` | `str` | `"datetime"` | Column containing timestamps. |
| `ip_col` | `str` | `"ip"` | Column identifying each lifecycle (typically IP address or device ID). |
| `interval` | `str \| None` | `None` | Sampling interval. If omitted, it is inferred automatically from the event timestamps. |

## Example

```python
from lifecycle import LifecycleAnalysis

analysis = LifecycleAnalysis(
    df,
    event="LOGIN",
)
```

Specify custom column names:

```python
analysis = LifecycleAnalysis(
    df,
    event="LOGIN",
    event_col="event_name",
    time_col="timestamp",
    ip_col="client_id",
)
```

Analyze without excluding observation boundaries:

```python
analysis = LifecycleAnalysis(
    df,
    event="LOGIN",
    trusted=False,
)
```