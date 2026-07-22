import pandas as pd

from .collection import LifecycleCollection


class CollectionAnalyzer:
    """
    LifecycleCollection の解析
    """

    def __init__(
        self,
        collection: LifecycleCollection,
    ):
        self.collection = collection


    def overlap_count_matrix(self) -> pd.DataFrame:
        """
        共起数 Matrix

        AとBが同時に存在した時間
        """

        names = self.collection.names()

        mat = pd.DataFrame(
            index=names,
            columns=names,
            dtype=float,
        )

        for a in names:

            A = self.collection.get(a).activity.lifetime

            for b in names:

                B = self.collection.get(b).activity.lifetime

                mat.loc[a, b] = (
                    (A & B)
                    .sum()
                    .sum()
                )

        return mat


    def containment_matrix(self) -> pd.DataFrame:
        """
        行正規化

        Aが存在している時間のうち、
        Bも存在していた割合
        """

        names = self.collection.names()

        mat = pd.DataFrame(
            index=names,
            columns=names,
            dtype=float,
        )

        for a in names:

            A = self.collection.get(a).activity.lifetime

            total = A.sum().sum()

            for b in names:

                B = self.collection.get(b).activity.lifetime

                overlap = (
                    (A & B)
                    .sum()
                    .sum()
                )

                mat.loc[a, b] = (
                    overlap / total
                    if total > 0
                    else 0.0
                )

        return mat


    def transition_matrix(
        self,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        状態開始点から状態開始点への遷移

        A開始後、Bが開始する割合
        """

        names = self.collection.names()

        mat = pd.DataFrame(
            index=names,
            columns=names,
            dtype=float,
        )

        for a in names:

            A = (
                self.collection
                .get(a)
                .activity
                .boundary
                .boundary_start
            )

            total = A.sum().sum()

            for b in names:

                B = (
                    self.collection
                    .get(b)
                    .activity
                    .boundary
                    .boundary_start
                    .shift(-offset)
                )

                transition = (
                    (A & B)
                    .sum()
                    .sum()
                )

                mat.loc[a, b] = (
                    transition / total
                    if total > 0
                    else 0.0
                )

        return mat
