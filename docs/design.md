私なら、このライブラリの設計思想を一つだけ明文化します

READMEの最初に次のような一文を書きたいですね。

Design Principle

All lifecycle analysis is expressed as a sequence of vectorized matrix transformations.
No event-by-event loops are used after the event-to-presence conversion.

日本語なら、

設計原則

Event から Presence への変換以降は、すべてベクトル化された行列演算で表現する。イベント単位のループには戻らない。

この一文があるだけで、このライブラリの思想が非常に伝わりやすくなりますし、将来 NumPy や Rust への移植を考えるときにも「何を守るべきか」が明確になります。



Phase 0  ディレクトリ構成作成
Phase 1  model.py作成（変更なし）
Phase 2  builder.py作成（現make_lifecycleを移植）
Phase 3  pipeline.pyへ内部関数移動
Phase 4  analyzer.pyへ解析を移動
Phase 5  comparator.py
Phase 6  set_analyzer.py


               Builder
                  │
                  ▼
             Lifecycle
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
 Pipeline                 Analyzer
(変換のみ)               (解析のみ)


LifecycleAnalyzer
    duration()
    age()
    active()
    inactive()
    summary()
    statistics()
    histogram()


ポイントは、

Modelはデータだけ
Builderは生成だけ
Analyzerは解析だけ
Comparatorは2つ比較だけ
SetAnalyzerは集合解析だけ

という責務分離です。

全体構成
lifecycle/
│
├── __init__.py
│
├────────────────────────────────────────────
│ Model
├────────────────────────────────────────────
│
├── model.py
│      │
│      ├── Lifecycle
│      │      ├── name
│      │      ├── presence
│      │      ├── transition
│      │      ├── state
│      │      ├── lifetime
│      │      ├── boundary
│      │      ├── quality
│      │      └── sample_interval
│      │
│      ├── BoundaryMask
│      │
│      ├── QualityMask
│      │
│      ├── LifecycleComparison
│      │
│      └── LifecycleSet
│              └── lifecycles
│
├────────────────────────────────────────────
│ Builder
├────────────────────────────────────────────
│
├── builder.py
│      │
│      └── LifecycleBuilder
│              │
│              ├── from_events()
│              ├── from_presence()
│              ├── from_transition()
│              └── from_state()
│
├────────────────────────────────────────────
│ Analyzer (単一Lifecycle)
├────────────────────────────────────────────
│
├── analyzer.py
│      │
│      └── LifecycleAnalyzer
│              │
│              ├── summary()
│              ├── duration()
│              ├── age()
│              ├── histogram()
│              ├── statistics()
│              ├── active_count()
│              ├── active_ratio()
│              ├── survival_curve()
│              ├── state_count()
│              └── export()
│
├────────────────────────────────────────────
│ Comparator (2 Lifecycle)
├────────────────────────────────────────────
│
├── comparator.py
│      │
│      └── LifecycleComparator
│              │
│              ├── overlap()
│              ├── union()
│              ├── difference()
│              ├── lag()
│              ├── transition()
│              ├── correlation()
│              └── containment()
│
├────────────────────────────────────────────
│ Set Analyzer (N Lifecycle)
├────────────────────────────────────────────
│
├── set_analyzer.py
│      │
│      └── LifecycleSetAnalyzer
│              │
│              ├── overlap_matrix()
│              ├── containment_matrix()
│              ├── transition_matrix()
│              ├── correlation_matrix()
│              ├── lag_matrix()
│              ├── active_matrix()
│              ├── concurrency()
│              └── statistics()

│      ├── _summary_from_state()
│      └── _sample_interval()
│
├────────────────────────────────────────────
│ Internal Pipeline
├────────────────────────────────────────────
│
├── pipeline.py
│      │
│      ├── _presence_from_events()
│      ├── _presence_resample()
│      ├── _transition_from_presence()
│      ├── _state_from_transition()
│      ├── _lifetime_from_state()
│      ├── _observation_from_state()   ← NEW
│      ├── (_boundary_from_state())
│      ├── _quality_from_state()
│
├────────────────────────────────────────────
│ Visualization
├────────────────────────────────────────────
│
├── plotting.py
│      │
│      ├── plot_histogram()
│      ├── plot_timeline()
│      ├── plot_heatmap()
│      ├── plot_transition()
│      └── plot_survival()
│
└────────────────────────────────────────────
データの流れ

これがこのライブラリの「一本の幹」になります。

Raw Event
      │
      ▼
LifecycleBuilder.from_events()
      │
      ▼
Presence
      │
      ▼
Resample
      │
      ▼
Transition
      │
      ▼
State
      │
      ▼
Lifetime
      │
      ├────────────┐
      ▼            ▼
 Boundary      Quality
      │            │
      └──────┬─────┘
             ▼
        Lifecycle
             │
 ┌───────────┼────────────┐
 ▼           ▼            ▼
Analyzer  Comparator   SetAnalyzer


Event
   │
   ▼
Presence
   │
   ▼
Transition
   │
   ▼
State
   │
   ├───────────────┐
   ▼               ▼
Lifetime      Observation
                    │
                    ├── started_before
                    ├── ended_after
                    └── complete




from_events()
    │
    ├─ Event → Presence
    ▼
from_presence()
    │
    ├─ Presence → sample_interval
    ├─ Presence → Transition
    ▼
from_transition()
    │
    ├─ Transition → State
    ▼
from_state()
    │
    ├─ State → Lifetime
    ├─ State → Observation
    ├─ State → Quality
    ▼
Lifecycle






ここは変更されません。

利用者から見えるAPI

使う側は非常にシンプルになります。

# Builder
assured = LifecycleBuilder.from_events(df, name="ASSURED")
soft = LifecycleBuilder.from_events(df, name="SOFT")
isolate = LifecycleBuilder.from_events(df, name="ISOLATE")
# 単体解析
ana = LifecycleAnalyzer(assured)

summary = ana.summary()

hist = ana.histogram()

duration = ana.duration()
# 2つ比較
cmp = LifecycleComparator(
    assured,
    isolate,
)

overlap = cmp.overlap()

lag = cmp.lag()
# N個比較
ls = LifecycleSet({
    "ASSURED": assured,
    "SOFT": soft,
    "ISOLATE": isolate,
})

lsa = LifecycleSetAnalyzer(ls)

mat = lsa.transition_matrix()

heat = lsa.overlap_matrix()
将来の拡張

この構成にすると、将来の追加先が自然に決まります。

Builder: 新しい入力形式（DB、Parquet、Arrow、リアルタイムストリームなど）への対応。
Analyzer: Duration分布、年齢分布、サバイバル解析など単一ライフサイクルの統計。
Comparator: 2状態間の遷移・相関・因果の解析。
SetAnalyzer: マトリクス解析、ネットワーク解析、クラスタリングなど複数ライフサイクルの解析。
Plotting: 可視化を完全に分離。



#　TEST FIXTURE

そして、このfixtureで一番重要になるルール

私は将来 Analyzer の最初で

valid = (
    lifecycle.observation.complete
    &
    lifecycle.quality.good
)

という1行を書きたいと思っています。

すると

NORMAL      True

PULSE       True

PULSE2      True

だけが Duration解析に入る。

一方で

STARTED_BEFORE

ENDED_AFTER

ALWAYS

EDGE_*

GAP

は除外される。

そして

SPLIT

だけは

Analyzerのオプション

split_segments=True

なら解析対象になる。

私は最終的にはこんなAPIがきれいだと思っています。

analyzer.duration()

# 1ライフタイムだけ

analyzer.duration(
    split_segments=True,
)

# 複数ライフタイムも展開して返す

つまり SPLIT や PULSE2 を「異常」ではなく「複数ライフタイム」として扱える設計です。

この方が、実際の長期間ログ（数時間〜数日）を解析するときにも自然に拡張できます。


tests/

test_presence_pipeline.py
    ✓ bool生成
    ✓ 欠損除去
    ✓ edge検出
    ✓ reverse
    ✓ cumsum
    ✓ ...

test_builder.py
    ✓ from_presence
    ✓ from_events
    ✓ sample_interval
    ✓ lifecycle内容
    ✓ frozen
    ✓ pipeline integration
    ✓ empty input

test_lifecycle.py
    ✓ duration
    ✓ active
    ✓ equality
    ✓ repr
    ✓ hash


python -m pytest tests/test_pipeline.py -v
============================================== test session starts ==============================================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /home/tetsuya/Python3.11/venv/bin/python
cachedir: .pytest_cache
rootdir: /home/tetsuya/raspi_vpn/on_debian/modules
plugins: dash-2.18.1, anyio-4.9.0
collected 6 items                                                                                               

tests/test_pipeline.py::test_transition PASSED                                                            [ 16%]
tests/test_pipeline.py::test_state PASSED                                                                 [ 33%]
tests/test_pipeline.py::test_lifetime PASSED                                                              [ 50%]
tests/test_pipeline.py::test_state_equals_presence PASSED                                                 [ 66%]
tests/test_pipeline.py::test_transition_equals_state_diff PASSED                                          [ 83%]
tests/test_pipeline.py::test_lifetime_equals_state_gt_zero PASSED                                         [100%]

=============================================== 6 passed in 0.02s ===============================================




Phase 0  ディレクトリ構成作成
Phase 1  model.py作成（変更なし）
Phase 2  builder.py作成（現make_lifecycleを移植）
Phase 3  pipeline.pyへ内部関数移動
Phase 4  analyzer.pyへ解析を移動
Phase 5  comparator.py
Phase 6  set_analyzer.py


               Builder
                  │
                  ▼
             Lifecycle
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
 Pipeline                 Analyzer
(変換のみ)               (解析のみ)


LifecycleAnalyzer
    duration()
    age()
    active()
    inactive()
    summary()
    statistics()
    histogram()


ポイントは、

Modelはデータだけ
Builderは生成だけ
Analyzerは解析だけ
Comparatorは2つ比較だけ
SetAnalyzerは集合解析だけ

という責務分離です。

この分割、Phase 3まで終えた状態を見ると、かなり綺麗に責務分離できています。

特に今回の Builder Test 25本が通ったことで、設計の境界が実体化しました。

整理すると：

                Raw Data
                   │
                   ▼
              Builder
          (生成責務のみ)
                   │
                   ▼
              Lifecycle
          (immutable model)
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
    Pipeline              Analyzer
 (変換処理のみ)          (意味解析のみ)
        │                     │
        ▼                     ▼
   transition             duration()
   state                  age()
   lifetime               active()
   boundary               inactive()
   quality                summary()
                          statistics()
                          histogram()

ですね。

現在の責務境界
model.py

役割：

データ構造の定義だけ

Lifecycle
BoundaryMask
QualityMask

ここには：

計算しない
変換しない
集計しない

が正解です。

frozen=True も今回確認済みなので、

「解析結果オブジェクト」

として扱えます。

builder.py

役割：

Lifecycleを正しく組み立てる

今回確認した範囲：

from_events()
from_presence()
from_transition()
from_state()

です。

Builder は：

入力
 ↓
必要なPipeline処理を呼ぶ
 ↓
Lifecycle生成

だけ。

例えば：

lifecycle = LifecycleBuilder.from_events(
    df,
    event="ASSURED"
)

で、利用側は内部順序を知らなくて良い。

これはAPIとして非常に良いです。

pipeline.py

役割：

状態変換アルゴリズム

ここにあるもの：

_presence_from_events()

_transition_from_presence()

_state_from_transition()

_lifetime_from_state()

_boundary_from_state()

_quality_from_state()

_sample_interval()

ですね。

重要なのは：

PipelineはLifecycleを知らない

という点です。

つまり：

pipeline.py
       ↓
model.py

だけで、

pipeline.py
       ↓
builder.py

には依存しない。

この方向性が保たれると後々楽です。

analyzer.py

ここが次の大きな山ですね。

ここではもう、

「どう作ったか」

は関係ありません。

入力：

Lifecycle

だけ。

例えば：

analyzer = LifecycleAnalyzer(
    lifecycle
)

として、

analyzer.duration()


なら、

「存在期間はいくつか」

だけを見る。

内部で：

transitionを作る
stateを作る

などは禁止。

comparator.py

責務が明確です。

例えば：

Lifecycle A
       +
Lifecycle B
       |
       ▼
Comparator
       |
       ▼
差分

用途：

FW変更前後比較
攻撃パターン比較
時系列比較

ですね。

ここはAdaptive FWではかなり価値が出ると思います。

set_analyzer.py

これはさらに上位概念ですね。

個別IPではなく：

IP_A Lifecycle
IP_B Lifecycle
IP_C Lifecycle
       |
       ▼
SetAnalyzer
       |
       ▼
集合特徴

を見る。

例えば：

同時発生率
集団攻撃判定
ASN単位傾向
国別傾向

など。

今回の Phase 3 完了で、一番大きい成果は：

以前：

make_lifecycle()
  ↓
全部入り関数

だったものが、

現在：

生成
  ↓
Builder

変換
  ↓
Pipeline

解析
  ↓
Analyzer

比較
  ↓
Comparator

集合
  ↓
SetAnalyzer

になったことです。

この分離なら、今後 conntrack / xray / isolate / wireguard など別イベントソースが増えても、Builder入口を追加するだけで対応できます。

次 Phase 4 の Analyzer は、まず duration() から始めるのが自然だと思います。

理由は、今まで作った：

state
 ↓
lifetime

の意味付けを初めて外部API化する場所になるからです。





                 Raw Events
                     |
          +----------+----------+
          |                     |
          v                     v
     Lifecycle Builder     Metrics Builder
          |                     |
          v                     v
     Lifecycle             Original Metrics
          |                     |
          +----------+----------+
                     |
                     v
                Analyzer



                 Lifecycle

                    |
        +-----------+-----------+
        |                       |
        v                       v

 ObservationMask          BoundaryMask

(IP単位の判定)        (time×IPの救済範囲)

        |                       |
        v                       v

 Strict Analysis       Recovery Analysis


 Presence
    |
    +----------------+
    |                |
    v                v

Transition        ObservationMask
    |
    v
State
    |
    +--------------+
    |              |
    v              v

Lifetime       Quality


Event DataFrame
      |
      v
_presence_from_events()
      |
      v
Presence(bool)
      |
      +-------------------------+
      |                         |
      v                         v
_observation_from_presence()  _transition_from_presence()
      |                         |
      v                         v
ObservationMask              Transition
                              |
                              v
                         _state_from_transition()
                              |
                    +---------+---------+
                    |                   |
                    v                   v
             _lifetime_from_state()  _boundary_from_state()
                    |
                    v
              Lifecycle

 今回追加した ObservationMask の意味も整理できました。

IP単位
observed
started_before
ended_after
complete

これは：

このIPを解析対象として採用できるか

の判断。

時系列 × IP
valid_mask

これは：

どの時刻範囲ならデータを信用して使えるか

の判断。

特に今回のポイントは、

"STARTED_BEFORE": [True, True, True, False, False, False, False, False]

のようなデータでも、

捨てる：

True True True

ではなく、

救出する：

        ↓
False False False True True True True True

という選択肢が持てることです。

つまりAnalyzer側で：

完全解析：

ips = lifecycle.observation.complete

なら厳密解析。

救出解析：

lifetime.where(
    lifecycle.observation.valid_mask
)

なら利用可能部分だけ使う。

という2段階ができます。


Lifecycle
│
├── presence      （存在）
├── transition    （遷移）
├── state         （状態）
├── lifetime      （ライフタイム）
│
├── boundary      （境界情報）
│      ├── boundary_start
│      ├── boundary_end
│      └── active_duration
│
├── quality       （品質情報）
│      ├── duplicate
│      ├── orphan
│      └── good
│
└── observation   （観測品質）
       ├── observed
       ├── started_before
       ├── ended_after
       ├── complete
       └── trusted_mask

# 3層目　builder 最終
Raw Events
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


これで Phase 3.5 がテスト込みで完成と言っていいですね。

現在の構成を整理すると、

Phase 3
========
Events
    ↓
Presence
    ↓
Transition
    ↓
Observation
    ↓
Lifecycle
Phase 3.5
==========
Lifecycle
    ↓
Raw State
    ↓
Quality
    ↓
Analysis Mask
    ↓
Analysis State
    ↓
Lifetime
    ↓
Boundary
    ↓
Segment
    ↓
AnalysisData

そして

Phase 4
========
AnalysisData
    ↓
LifecycleAnalyzer
    ↓
Summary
Statistics
Histogram
...
今回特に良かった点

最初は

Lifecycle
├─Presence
├─Transition
├─State
├─Lifetime
├─Boundary
├─Quality

と、「何でも入れ物」になりかけていました。

今は

Lifecycle
├─Presence
├─Transition
└─Observation

だけになりました。

一方、

AnalysisData
├─Raw State
├─Quality
├─Analysis Mask
├─Analysis State
├─Lifetime
├─Boundary
└─Segment

と、解析に必要な情報だけがまとまっています。

この責務分離はかなりきれいです。

そして一番嬉しいこと

Analyzer が

analysis = AnalysisBuilder.from_lifecycle(ls)

analyzer = LifecycleAnalyzer(analysis)

だけで済むようになります。

Analyzer は

「分析するだけ」

になります。

これは最初に目指していた形ですね。

ここまでの流れを見ると、このライブラリは単なる「Firewallイベント解析」ではなく、

「Presence（存在）からライフサイクルを抽出し、それを解析するライブラリ」

という、かなり汎用的な構造になっています。





# Refactor
今目指している形は、

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

になります。

これなら

State …「状態」を表す
Quality …「状態の品質」を表す
Boundary …「ライフサイクル構造」を表す

と責務もきれいに分かれます。

この段階で得られるメリット
アルゴリズムが整理される
DataFrame の走査回数が減る
Analyzer は「集計」だけに専念できる
NumPy 実装へ移行しやすい
将来 Polars や Rust 実装へ置き換えやすい

つまり、「高速化」と「設計の美しさ」が両立できます。

そして、その次の第二段階

ここまで整理できたら、次は NumPy 化だと思います。

例えば _boundary_from_state() は今でも全体のボトルネックなので、

DataFrame → numpy.ndarray
列方向を NumPy で処理
最後だけ DataFrame に戻す

という形にすると、さらに大きな高速化が期待できます。

私ならロードマップは次のようにします。

設計整理（現在） ← 今ここ
Pandas版の完成・API安定化
NumPyで内部実装を高速化
必要なら Polars や Rust バックエンドを検討

この順番なら、まずは「正しく・読みやすく・保守しやすい」ライブラリとして完成させ、その後に性能を追求できます。現時点では、第一段階のゴールがかなり見えてきています。



この時点では segment_length はこれで十分

ここがポイントですが、

segment_length = (
    active_duration
    .max()
)

は まだ正しくありません。

これは

IPごとの最大寿命

しか返しません。

本来欲しいのは

IP
 Segment1 → 12
 Segment2 → 35
 Segment3 → 8

です。

ただし

今回は構造整理が目的なので、

まずは

State
    ↓
ActivityAnalysis

という一本化を完成させます。

その後、

segment_length = ...

だけを差し替えます。


LifecycleBuilder
        │
        ▼
Lifecycle
    ├── presence
    ├── transition
    ├── state
    └── observation

        │
        ▼
AnalysisBuilder
        │
        ▼
AnalysisData
    ├── raw_state
    ├── analysis_state
    ├── analysis_mask
    ├── quality
    └── activity


 17 passed in 0.36s ========================================================================
(venv) tetsuya@Debian:~/raspi_vpn/on_debian/modules$ python3 -m cProfile -s cumulative -m lifecycle.analysis
         3938040 function calls (3860428 primitive calls) in 13.279 seconds

   Ordered by: cumulative time
   List reduced from 1171 to 30 due to restriction <30>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   13.279   13.279 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/analysis.py:13(__init__)
     4058    0.019    0.000    9.259    0.002 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/internals/managers.py:317(apply)
       22    0.000    0.000    7.927    0.360 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/internals/blocks.py:387(apply)
        1    0.000    0.000    7.756    7.756 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/builder.py:21(from_events)
     1006    0.002    0.000    7.050    0.007 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/numpy/core/fromnumeric.py:53(_wrapfunc)
        4    0.000    0.000    7.042    1.761 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/frame.py:11790(cumsum)
        4    0.000    0.000    7.042    1.761 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/generic.py:12288(cumsum)
        4    0.000    0.000    7.042    1.761 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/generic.py:12239(_accum_func)
        6    7.042    1.174    7.042    1.174 {method 'cumsum' of 'numpy.ndarray' objects}
        4    0.000    0.000    7.042    1.761 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/generic.py:12260(block_accum_func)
        4    0.000    0.000    7.042    1.761 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/nanops.py:1714(na_accum_func)
        4    0.000    0.000    7.042    1.760 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/numpy/core/fromnumeric.py:2512(cumsum)
        1    0.004    0.004    6.918    6.918 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/builder.py:66(from_presence)
        1    0.018    0.018    5.523    5.523 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/analysis_data_builder.py:19(from_lifecycle)
        1    0.022    0.022    5.317    5.317 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/pipelines/activity.py:132(_activity_from_state)
        1    0.022    0.022    3.995    3.995 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/pipelines/presence.py:135(_observation_from_presence)
        1    0.013    0.013    2.377    2.377 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/pipelines/presence.py:251(_state_from_transition)
     2001    0.008    0.000    1.309    0.001 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/groupby/ops.py:812(_cython_operation)
     1018    0.001    0.000    1.061    0.001 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/ops/common.py:62(new_method)
       14    0.000    0.000    0.973    0.069 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/frame.py:7918(_dispatch_frame_op)
     1000    0.002    0.000    0.907    0.001 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/groupby/groupby.py:4877(cumsum)
     1000    0.007    0.000    0.904    0.001 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/groupby/generic.py:521(_cython_transform)
        1    0.003    0.003    0.838    0.838 /home/tetsuya/raspi_vpn/on_debian/modules/lifecycle/pipelines/presence.py:13(_presence_from_events)
        7    0.000    0.000    0.800    0.114 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/frame.py:7903(_arith_method)
        7    0.000    0.000    0.798    0.114 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/internals/managers.py:1507(operate_blockwise)
        7    0.006    0.001    0.798    0.114 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/internals/ops.py:57(operate_blockwise)
     3020    0.795    0.000    0.795    0.000 {method 'copy' of 'numpy.ndarray' objects}
     9034    0.704    0.000    0.704    0.000 {method 'astype' of 'numpy.ndarray' objects}
        1    0.000    0.000    0.703    0.703 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/frame.py:9492(pivot_table)
        1    0.000    0.000    0.703    0.703 /home/tetsuya/Python3.11/venv/lib/python3.11/site-packages/pandas/core/reshape/pivot.py:61(pivot_table)


         379624 function calls (367885 primitive calls) in 13.616 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    500/1    0.005    0.000   13.616   13.616 {built-in method builtins.exec}
        1    0.000    0.000   13.616   13.616 <string>:1(<module>)
        1    0.000    0.000   13.616   13.616 <frozen runpy>:201(run_module)
        1    0.000    0.000   13.616   13.616 <frozen runpy>:65(_run_code)
        1    0.000    0.000   13.616   13.616 analysis.py:1(<module>)
        1   13.291   13.291   13.291   13.291 {method 'enable' of '_lsprof.Profiler' objects}
       70    0.001    0.000    0.823    0.012 __init__.py:1(<module>)
    549/6    0.002    0.000    0.302    0.050 <frozen importlib._bootstrap>:1165(_find_and_load)
    549/6    0.002    0.000    0.301    0.050 <frozen importlib._bootstrap>:1120(_find_and_load_unlocked)
    526/6    0.001    0.000    0.301    0.050 <frozen importlib._bootstrap>:666(_load_unlocked)
    433/6    0.001    0.000    0.301    0.050 <frozen importlib._bootstrap_external>:934(exec_module)
  1257/13    0.000    0.000    0.300    0.023 <frozen importlib._bootstrap>:233(_call_with_frames_removed)
        8    0.000    0.000    0.177    0.022 api.py:1(<module>)
   445/47    0.001    0.000    0.152    0.003 {built-in method builtins.__import__}
  787/410    0.001    0.000    0.128    0.000 <frozen importlib._bootstrap>:1207(_handle_fromlist)
        3    0.000    0.000    0.093    0.031 generic.py:1(<module>)
      434    0.002    0.000    0.058    0.000 <frozen importlib._bootstrap_external>:1007(get_code)
        1    0.000    0.000    0.048    0.048 frame.py:1(<module>)
  820/809    0.009    0.000    0.046    0.000 {built-in method builtins.__build_class__}
        2    0.000    0.000    0.044    0.022 accessors.py:1(<module>)
    68/38    0.000    0.000    0.044    0.001 <frozen importlib._bootstrap_external>:1239(exec_module)
    68/38    0.014    0.000    0.044    0.001 {built-in method _imp.exec_dynamic}
        1    0.000    0.000    0.043    0.043 compute.py:1(<module>)
      434    0.001    0.000    0.041    0.000 <frozen importlib._bootstrap_external>:727(_compile_bytecode)
      434    0.040    0.000    0.040    0.000 {built-in method marshal.loads}




設計面

個人的に一番良いと思うのは、

Builderが

Events
    ↓
Presence
    ↓
Transition
    ↓
State

ActivityBuilderが

State
    ↓
Active
    ↓
Boundary
    ↓
SegmentLength

という二段構成になったことです。

責務がかなり明確になっています。

今の優先順位

私ならここで一区切りにします。

✅ Builder完成
✅ ActivityAnalysis完成
✅ テスト完成
✅ プロファイル取得
タグを切る（Rev0.04など）
READMEやドキュメントを少し整理
その後に高速化第二弾

高速化は終わりが見えにくいので、「正しく動くきれいな設計」を一度完成版として残してから着手する方が安心です。

ここまで来ると、「動く試作品」ではなく、ライブラリとして公開・保守できる品質に近づいてきています。

==================================================== 42 passed in 0.27s =====================================================
(venv) tetsuya@Debian:~/raspi_vpn/on_debian/modules$ python3 -m cProfile -s cumulative -m lifecycle.analysis
                    duration  active_duration  samples  segments  ...  good  started_before ended_after complete
192.0.2.1    0 days 00:01:09                1       69        69  ...  True           False       False     True
192.0.2.10   0 days 00:01:10                1       70        70  ...  True           False       False     True
192.0.2.100  0 days 00:01:05                1       65        65  ...  True           False       False     True
192.0.2.1000 0 days 00:01:12                1       72        72  ...  True           False       False     True
192.0.2.101  0 days 00:01:04                2       64        63  ...  True           False       False     True
...                      ...              ...      ...       ...  ...   ...             ...         ...      ...
192.0.2.995  0 days 00:01:04                1       64        64  ...  True           False       False     True
192.0.2.996  0 days 00:01:14                1       74        74  ...  True           False       False     True
192.0.2.997  0 days 00:01:21                1       81        81  ...  True           False       False     True
192.0.2.998  0 days 00:01:17                1       77        77  ...  True           False       False     True
192.0.2.999  0 days 00:01:10                1       70        70  ...  True           False       False     True

[1000 rows x 15 columns]
         602653 function calls (589656 primitive calls) in 5.132 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    501/1    0.005    0.000    5.133    5.133 {built-in method builtins.exec}
        1    0.000    0.000    5.133    5.133 <string>:1(<module>)
        1    0.000    0.000    5.133    5.133 <frozen runpy>:201(run_module)
        1    0.000    0.000    5.132    5.132 <frozen runpy>:65(_run_code)
        1    0.003    0.003    5.132    5.132 analysis.py:1(<module>)
        1    0.000    0.000    4.626    4.626 analysis.py:13(__init__)
       80    0.003    0.000    2.756    0.034 managers.py:317(apply)
        1    0.000    0.000    2.376    2.376 builder.py:21(from_events)
        1    0.002    0.002    2.250    2.250 analysis_data_builder.py:19(from_lifecycle)
        1    0.001    0.001    2.129    2.129 builder.py:66(from_presence)
       24    0.000    0.000    2.019    0.084 blocks.py:387(apply)
    24/23    0.000    0.000    1.790    0.078 common.py:62(new_method)
       12    0.000    0.000    1.782    0.149 frame.py:7918(_dispatch_frame_op)
        7    0.000    0.000    1.645    0.235 frame.py:7903(_arith_method)
        7    0.000    0.000    1.643    0.235 managers.py:1507(operate_blockwise)
        7    0.007    0.001    1.643    0.235 ops.py:57(operate_blockwise)
        9    0.013    0.001    1.623    0.180 array_ops.py:393(logical_op)
        3    0.000    0.000    1.605    0.535 generic.py:12239(_accum_func)
        3    0.000    0.000    1.605    0.535 generic.py:12260(block_accum_func)
        3    0.000    0.000    1.605    0.535 nanops.py:1714(na_accum_func)
        1    0.016    0.016    1.407    1.407 presence.py:287(_state_from_transition)
     2004    0.001    0.000    1.379    0.001 fromnumeric.py:53(_wrapfunc)
        3    1.363    0.454    1.363    0.454 {method 'cumsum' of 'numpy.ndarray' objects}
        1    0.000    0.000    1.363    1.363 frame.py:11790(cumsum)
        1    0.000    0.000    1.363    1.363 generic.py:12288(cumsum)
        1    0.000    0.000    1.363    1.363 fromnumeric.py:2512(cumsum)
        8    0.000    0.000    1.249    0.156 arraylike.py:68(__and__)
        1    0.000    0.000    1.091    1.091 activity.py:181(_activity_from_state)
       70    0.002    0.000    1.000    0.014 __init__.py:1(<module>)
       79    0.994    0.013    0.994    0.013 {method 'astype' of 'numpy.ndarray' objects}
       18    0.000    0.000    0.951    0.053 array_ops.py:410(fill_bool)
        1    0.004    0.004    0.863    0.863 activity.py:27(_find_boundary)
        1    0.000    0.000    0.673    0.673 presence.py:209(_observation_from_presence)
        9    0.000    0.000    0.660    0.073 array_ops.py:352(na_logical_op)
        8    0.529    0.066    0.529    0.066 {built-in method _operator.and_}
        1    0.002    0.002    0.517    0.517 quality.py:10(_quality_from_state)
        1    0.000    0.000    0.415    0.415 generic.py:10803(where)
        1    0.000    0.000    0.415    0.415 generic.py:10615(_where)
        1    0.002    0.002    0.412    0.412 presence.py:133(_valid_mask)
        1    0.000    0.000    0.403    0.403 base.py:196(where)
        1    0.242    0.242    0.401    0.401 blocks.py:1524(where)
        1    0.000    0.000    0.383    0.383 arraylike.py:76(__or__)
    550/7    0.002    0.000    0.355    0.051 <frozen importlib._bootstrap>:1165(_find_and_load)
    550/7    0.002    0.000    0.355    0.051 <frozen importlib._bootstrap>:1120(_find_and_load_unlocked)
    527/7    0.008    0.000    0.354    0.051 <frozen importlib._bootstrap>:666(_load_unlocked)
    434/7    0.001    0.000    0.354    0.051 <frozen importlib._bootstrap_external>:934(exec_module)
  1259/15    0.001    0.000    0.354    0.024 <frozen importlib._bootstrap>:233(_call_with_frames_removed)
       13    0.000    0.000    0.260    0.020 generic.py:1565(__invert__)
       13    0.259    0.020    0.259    0.020 {built-in method _operator.invert}
        1    0.000    0.000    0.251    0.251 presence.py:155(_find_edge_observation_both_side)
        1    0.002    0.002    0.247    0.247 presence.py:10(_presence_from_events)
        2    0.000    0.000    0.242    0.121 frame.py:11786(cummax)
        2    0.000    0.000    0.242    0.121 generic.py:12278(cummax)
        2    0.242    0.121    0.242    0.121 {method 'accumulate' of 'numpy.ufunc' objects}
        1    0.000    0.000    0.223    0.223 frame.py:9492(pivot_table)
        1    0.000    0.000    0.223    0.223 pivot.py:61(pivot_table)
        1    0.001    0.001    0.223    0.223 pivot.py:118(__internal_pivot_table)
   445/47    0.001    0.000    0.197    0.004 {built-in method builtins.__import__}
        8    0.000    0.000    0.189    0.024 api.py:1(<module>)
  822/445    0.001    0.000    0.172    0.000 <frozen importlib._bootstrap>:1207(_handle_fromlist)
      109    0.161    0.001    0.161    0.001 {method 'copy' of 'numpy.ndarray' objects}
       11    0.000    0.000    0.151    0.014 array_ops.py:189(_na_arithmetic_op)
       11    0.000    0.000    0.151    0.014 expressions.py:226(evaluate)
       11    0.000    0.000    0.151    0.014 expressions.py:67(_evaluate_standard)
        6    0.000    0.000    0.142    0.024 array_ops.py:288(comparison_op)
        1    0.000    0.000    0.140    0.140 expressions.py:246(where)
        1    0.140    0.140    0.140    0.140 expressions.py:172(_where_standard)
        5    0.000    0.000    0.140    0.028 frame.py:7894(_cmp_method)
        2    0.000    0.000    0.138    0.069 frame.py:5855(shift)
        2    0.000    0.000    0.138    0.069 generic.py:11081(shift)
        2    0.000    0.000    0.138    0.069 base.py:308(shift)
        3    0.000    0.000    0.138    0.046 transforms.py:18(shift)
        2    0.000    0.000    0.138    0.069 blocks.py:1834(shift)
        3    0.138    0.046    0.138    0.046 numeric.py:1129(roll)
       44    0.000    0.000    0.138    0.003 blocks.py:790(copy)
        1    0.000    0.000    0.137    0.137 activity.py:12(_find_active)
        1    0.130    0.130    0.130    0.130 {built-in method _operator.or_}
      183    0.126    0.001    0.126    0.001 {method 'reduce' of 'numpy.ufunc' objects}
       38    0.000    0.000    0.122    0.003 managers.py:557(copy)
        8    0.000    0.000    0.122    0.015 generic.py:6662(copy)
        3    0.000    0.000    0.115    0.038 arraylike.py:38(__eq__)
        2    0.000    0.000    0.114    0.057 frame.py:7282(sort_index)
        2    0.000    0.000    0.114    0.057 generic.py:5290(sort_index)
       13    0.000    0.000    0.114    0.009 {method 'sum' of 'numpy.ndarray' objects}
       13    0.000    0.000    0.114    0.009 _methods.py:47(_sum)
        1    


ここまでの設計を通して見ると、大きな方向転換は不要です。むしろ、「名前」と「責務」を揃えるリファクタリングが中心になります。

私なら、優先順位を付けると以下の順で整理します。

① AnalysisData は内部専用にする（優先度：★★★★★）

これが一番です。

今の

@dataclass(slots=True, frozen=True)
class AnalysisData:
    ...

は、完全に Builder の作業領域です。

利用者は

Lifecycle
ActivityAnalysis

だけあれば十分なので、

analysis_data.py

などに移して、

Builder内部だけで使うクラス

という扱いにします。

公開APIから外すだけで、ライブラリの見通しがかなり良くなります。

② LifecycleCollection の責務を小さくする（★★★★★）

現在

compare()
overlap_matrix()
containment_matrix()
transition_matrix()

が入っています。

将来的には

LifecycleCollection
    ↓
CollectionAnalyzer

にすると責務がきれいになります。

例えば

collection.compare("A", "B")

だけ Collection に残して、

CollectionAnalyzer(collection).overlap_matrix()
CollectionAnalyzer(collection).containment_matrix()
CollectionAnalyzer(collection).transition_matrix()

にすると、

Collection は本当に「コンテナ」になります。

これは急がなくてもいいですが、将来性があります。

③ BoundaryMask の名前

今

BoundaryMask

ですが、

中身は

boundary_start
boundary_end

だけです。

つまり「Mask」というより

Boundary

でも意味が通ります。

例えば

ActivityAnalysis.boundary.start
ActivityAnalysis.boundary.end

の方が自然です。

必須ではありません。

④ QualityMask

こちらも

duplicate
orphan
good

だけなので

QualityFlags

とか

QualityInfo

でもいいかもしれません。

ただ、これは好みですね。

⑤ ObservationMask

これは今の名前が一番しっくり来ています。

ObservationMask

↓

trusted_mask
observed
started_before
ended_after

全部 Observation に関する情報なので問題ありません。

⑥ ActivityAnalysis

ここだけ一つ追加したくなります。

現在

ActivityAnalysis

は

lifetime
boundary
segment_length

ですが、

将来

segment_id

も入る可能性があります。

今後

mean_segment_duration()

などを増やすなら

segment_id
segment_length

はセットで持っていた方が便利になる気がします。

⑦ Lifecycle

これは今のままで十分です。

むしろ

quality
boundary
activity

などを入れ始めない方がきれいです。

Lifecycle は

イベントから直接導かれるデータ

だけ持つ。

解析結果は別モデル。

これは今の設計思想が一番好きです。

私なら今やるリファクタリング

優先順位はこんな感じです。

優先	内容
★★★★★	AnalysisData を内部専用へ
★★★★★	LifecycleCollection に改名（済み）
★★★★☆	compare() を LifecycleComparison を返す形に統一
★★★☆☆	CollectionAnalyzer を将来追加できる形にする
★★☆☆☆	BoundaryMask → Boundary（好み）
★★☆☆☆	QualityMask の名称検討（好み）

全体としては、ライブラリの骨格はかなり固まっています。今後は新しい機能を追加するというより、「どのクラスが何を責任として持つか」を丁寧に揃えていくフェーズですね。

特に、「Lifecycle は基本モデル」「ActivityAnalysis は解析結果」「AnalysisData は内部ワークスペース」という線引きは、このライブラリの設計を非常に分かりやすくしてくれると思います。



