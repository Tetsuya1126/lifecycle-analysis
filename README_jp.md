# Lifecycle Analysis

[![Tests](https://github.com/Tetsuya1126/lifecycle-analysis/actions/workflows/test.yaml/badge.svg)](https://github.com/Tetsuya1126/lifecycle-analysis/actions/workflows/test.yaml)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/github/license/Tetsuya1126/lifecycle-analysis)



> **Lifecycle Analysis は、「観測されたデータ」と「解析可能なデータ」を分離することで、再現性と信頼性の高いライフサイクル解析を実現します。**

Lifecycle Analysis は、時系列の観測データからライフサイクル（存在期間）を抽出し、統計解析を行う Python ライブラリです。

当初は Firewall の接続イベント解析を目的として開発しましたが、設計を汎用化することで、さまざまな時系列データへ適用できるライブラリを目指しています。


---

# なぜ Lifecycle Analysis なのか

ライフサイクル解析では、**観測されたすべてのデータが解析に適しているとは限りません。**

例えば、

* 観測開始以前から存在していたデータ
* 観測終了後も継続しているデータ
* 状態遷移が破綻しているデータ

は、観測はできていても、ライフサイクル全体を正しく表しているとは限りません。

---

# 特徴
Lifecycle Analysis は、

> **「観測されたデータ」と「解析可能なデータ」は異なる**

という考え方を基本設計としています。

そのため、

```
  Observed Events
        │
        ▼
    Lifecycle
（観測された事実）
        │
        ▼
   AnalysisData
（解析可能なデータ）
        │
        ▼
 LifecycleAnalyzer
```

という構成を採用し、信頼できるライフサイクルのみを統計解析の対象とします。

---

# 利用例

Lifecycle Analysis は、以下のようなデータに利用できます。

* Firewall / VPN 接続ログ
* ユーザーログイン・ログアウト履歴
* IoT センサーデータ
* システム稼働状況
* 生産設備の稼働ログ
* サービス利用履歴
* その他、時系列イベントデータ全般

---

# インストール

GitHub からインストール

```bash
git clone https://github.com/Tetsuya1126/lifecycle-analysis.git

cd lifecycle-analysis

pip install -e .
```


---

# クイックスタート

以下はログインイベントからライフサイクルを生成し、
統計情報を取得する最小構成の例です。

LifecycleAnalysis は内部で LifecycleBuilder・AnalysisBuilder・LifecycleAnalyzer を統合した高レベルAPIです。

```python
import pandas as pd
import numpy as np

from lifecycle import (
    LifecycleAnalysis,
)


def create_event(N=100):
    rng = np.random.default_rng(42)

    return pd.DataFrame(
        {
            "datetime": pd.Timestamp("2026-01-01")
            + pd.to_timedelta(
                np.sort(rng.integers(0, 86400, size=N)),
                unit="s",
            ),
            "object": rng.choice(
                [
                    f"192.168.2.{i}" for i in range(1, 256)
                ],
                size=N,            
            ),
            "event": rng.choice(
                [
                "INVALID_SNI",
                "ASSURED",
                ],
                size=N,
                p=[0.7,0.3],
            ),
        }
    )

events = create_event()

analysis = LifecycleAnalysis(
    df      = events,
    event   = "INVALID_SNI",
    trusted = True,
    ip_col = "object"
)


print(events.head())
print()
print(analysis.summary().head())
```

```
 python3 ./quick_start.py 
             datetime         object        event
0 2026-01-01 01:03:04  192.168.2.213      ASSURED
1 2026-01-01 01:31:53   192.168.2.51  INVALID_SNI
2 2026-01-01 01:37:48  192.168.2.206  INVALID_SNI
3 2026-01-01 01:49:56    192.168.2.2      ASSURED
4 2026-01-01 02:03:45  192.168.2.204      ASSURED

                     duration  active_duration  samples  segments  segment_count  coverage_ratio  ... duplicate orphan  good  started_before  ended_after  complete
192.168.2.104 0 days 00:04:24              1.0        1         1              1             1.0  ...     False  False  True           False        False      True
192.168.2.105 0 days 00:08:48              1.0        2         2              2             1.0  ...     False  False  True           False        False      True
192.168.2.107 0 days 00:04:24              1.0        1         1              1             1.0  ...     False  False  True           False        False      True
192.168.2.111 0 days 00:04:24              1.0        1         1              1             1.0  ...     False  False  True           False        False      True
192.168.2.112 0 days 00:04:24              1.0        1         1              1             1.0  ...     False  False  True           False        False      True

[5 rows x 15 columns]
```

---

# 入力データ

入力は **時系列イベント** を表す `pandas.DataFrame` を想定しています。

最低限、以下のような情報を持つデータを扱います。

| 列        | 内容               |
| -------- | ---------------- |
| datetime | イベント発生時刻 (datetime形式)        |
| ip       | 対象（IP・ユーザー・設備など） |
| event    | イベント種別           |

例

```text
             datetime      ip        event
0  2026-01-01 10:00      host01      login
1  2026-01-01 10:10      host01      logout
2  2026-01-01 10:30      host02      login
```

データ形式は固定ではありません。

`LifecycleBuilder` が必要とする情報を指定することで、さまざまなイベントデータへ適用できます。

---

# アーキテクチャ

ライブラリは責務ごとに分離されています。

| コンポーネント           | 役割                   |
| ----------------- | -------------------- |
| LifecycleBuilder  | イベントから Lifecycle を生成 |
| Lifecycle         | 観測された事実を保持           |
| AnalysisBuilder   | 解析可能なデータを生成          |
| AnalysisData      | 解析用データを保持            |
| LifecycleAnalyzer | 統計解析を行う              |

各コンポーネントは単一責務となるよう設計されています。

---


ライフサイクルは、Presence（存在情報）を基準として段階的に構築されます。

```text

                Raw Events
                   │
                   ▼
          +----------------------+
          | LifecycleBuilder     |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | Lifecycle            |
          | ・Presence           |
          | ・Transition         |
          | ・State              |
          | ・Observation        |
          | ・Sample Interval    |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | AnalysisBuilder      |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | AnalysisData         |
          | ・Name               |
          | ・Raw State          |
          | ・Sample Interval    |
          | ・Quality            |
          | ・Analysis Filter    |
          | ・Activity           |
          |   -Lifetime          |
          |   -Boundary          |
          |   -Segment_length    |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | LifecycleAnalyzer    |
          +----------------------+
                   │
                   ▼
            Summary / Statistics

```

これらの処理は、可能な限り NumPy / pandas のベクトル演算によって実装されています。

---

# Trusted Analysis

解析時には、

* Observation（観測品質）
* Quality（状態遷移品質）

の両方を考慮して解析対象を決定します。
```
Observation
(観測データ)
↓

Trusted Mask
(観測境界を除外)

↓

Quality Mask
(異常状態を除外)

↓

Analysis Mask
```

```python
analysis_mask = (
    observation.trusted_mask
    &
    quality.good
)
```

これにより、

* 観測開始以前から存在していたライフサイクル
* 観測終了後まで継続しているライフサイクル
* 状態遷移が異常なライフサイクル

を解析対象から除外し、信頼できるライフサイクルのみを統計解析します。

---

# パフォーマンス

Lifecycle Analysis は、大規模な時系列データを対象として設計されています。

主な設計方針

* NumPy / pandas によるベクトル演算
* Python のループを最小限に抑制
* Immutable データモデル
* `slots=True` によるメモリ使用量の削減
* 再現性の高い解析

---

# ドキュメント

詳細な設計資料は `docs/` にまとめています。

```
docs/
├── README_calc_bit_vector.md
├── README_detail.md
├── README_files.md
└── README_models.md

```

設計資料では、

* 設計思想
* データフロー
* Lifecycle モデル
* AnalysisData モデル
* BIT 行列演算
* Observation Mask
* Quality Mask
* Boundary Analysis

について詳しく説明しています。

---

# ロードマップ

* [x] Lifecycle Builder
* [x] Analysis Builder
* [x] Lifecycle Analyzer (core features)
* [x] Lifecycle Comparison (core features)
* [ ] Additional statistical methods
* [ ] Collection Analysis
* [ ] Survival Analysis
* [ ] Visualization
* [ ] Polars Backend

---

# ライセンス

MIT License

