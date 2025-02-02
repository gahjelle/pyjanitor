from __future__ import annotations

import pandas_flavor as pf
import pandas as pd

from janitor.utils import deprecated_alias
from janitor.utils import deprecated_kwargs


@pf.register_dataframe_method
@deprecated_kwargs(
    "old_min",
    "old_max",
    "new_min",
    "new_max",
    message=(
        "The keyword argument {argument!r} of {func_name!r} is deprecated. "
        "Please use 'feature_range' instead."
    ),
)
@deprecated_alias(col_name="column_name")
def min_max_scale(
    df: pd.DataFrame,
    feature_range: tuple[int | float, int | float] = (0, 1),
    column_name: str | int | list[str | int] | pd.Index = None,
) -> pd.DataFrame:
    """
    Scales data to between a minimum and maximum value.

    This method mutates the original DataFrame.

    If `minimum` and `maximum` are provided, the true min/max of the
    `DataFrame` or column is ignored in the scaling process and replaced with
    these values, instead.

    One can optionally set a new target minimum and maximum value using the
    `feature_range[0]` and `feature_range[1]` keyword arguments.
    This will result in the transformed data being bounded between
    `feature_range[0]` and `feature_range[1]`.

    If a particular column name is specified, then only that column of data
    are scaled. Otherwise, the entire dataframe is scaled.

    Example: Basic usage.

        >>> import pandas as pd
        >>> import janitor
        >>> df = pd.DataFrame({'a':[1, 2], 'b':[0, 1]})
        >>> df.min_max_scale()
             a    b
        0  0.5  0.0
        1  1.0  0.5

    Example: Setting custom minimum and maximum.

        >>> import pandas as pd
        >>> import janitor
        >>> df = pd.DataFrame({'a':[1, 2], 'b':[0, 1]})
        >>> df.min_max_scale(feature_range=(0, 100))
               a     b
        0   50.0   0.0
        1  100.0  50.0

    Example: Apply min-max to the selected columns.

        >>> import pandas as pd
        >>> import janitor
        >>> df = pd.DataFrame({'a':[1, 2], 'b':[0, 1]})
        >>> df.min_max_scale(feature_range=(0, 100), column_name=['a', 'b'])
               a      b
        0    0.0    0.0
        1  100.0  100.0
        >>> df.min_max_scale(feature_range=(0, 100), column_name='a')
               a  b
        0    0.0  0
        1  100.0  1

    The aforementioned example might be applied to something like scaling the
    isoelectric points of amino acids. While technically they range from
    approx 3-10, we can also think of them on the pH scale which ranges from
    1 to 14. Hence, 3 gets scaled not to 0 but approx. 0.15 instead, while 10
    gets scaled to approx. 0.69 instead.

    :param df: A pandas DataFrame.
    :param feature_range: (optional) Desired range of transformed data.
    :param column_name: (optional) The column on which to perform scaling.
    :returns: A pandas DataFrame with scaled data.
    :raises ValueError: if `feature_range` isn't tuple type.
    :raises ValueError: if the length of `feature_range` isn't equal to two.
    :raises ValueError: if the element of `feature_range` isn't number type.
    :raises ValueError: if `feature_range[1]` <= `feature_range[0]`.
    """

    if not (
        isinstance(feature_range, (tuple, list))
        and len(feature_range) == 2
        and all((isinstance(i, (int, float))) for i in feature_range)
        and feature_range[1] > feature_range[0]
    ):
        raise ValueError(
            "`feature_range` should be a range type contains number element, "
            "the first element must be greater than the second one"
        )

    new_min, new_max = feature_range
    new_range = new_max - new_min

    if column_name is not None:
        old_min = df[column_name].min()
        old_max = df[column_name].max()
        old_range = old_max - old_min

        df = df.copy()
        df[column_name] = (
            df[column_name] - old_min
        ) * new_range / old_range + new_min
    else:
        old_min = df.min().min()
        old_max = df.max().max()
        old_range = old_max - old_min

        df = (df - old_min) * new_range / old_range + new_min

    return df
