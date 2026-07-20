
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

