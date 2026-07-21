import pandas as pd

def to_array(df, dtype=None):
    return df.to_numpy(dtype=dtype, copy=False)

def to_df(arr, like):
    return pd.DataFrame(
        arr,
        index=like.index,
        columns=like.columns,
    )

def to_series(arr, like):
    return pd.Series(
        arr,
        index=like.columns,
    )

def to_pandas(arr, like):
    if arr.ndim == 1:
        return pd.Series(arr, index=like.columns)
    else:
        return pd.DataFrame(
            arr,
            index=like.index,
            columns=like.columns,
        )