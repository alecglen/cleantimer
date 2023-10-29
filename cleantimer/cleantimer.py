from typing import Any, Callable
from datetime import datetime

from contexttimer import Timer
from pandas import DataFrame, Series, concat
from tqdm import tqdm


class CTimer(Timer):
    """
    A class that extends the Timer class from the contexttimer module.

    Args:
        message (str): A message to be displayed when the timer starts.
        precision (int, optional): The number of decimals to round the elapsed time. Defaults to 1.
    """

    def __init__(self, message: str, *args, precision: int = 1, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.precision = precision
        self.is_first_child = True

    def __enter__(self, *args, **kwargs):
        """
        Called when the timer starts. Prints the message and starts the timer.

        Returns:
            CTimer: The CTimer object.
        """
        super().__enter__(*args, **kwargs)
        intro = f"{self.message} ({datetime.now().time().strftime('%-I:%M%p')})..."
        print(intro, end="", flush=True)
        return self

    def __exit__(self, exception, *args, **kwargs):
        """
        Called when the timer ends. Prints the elapsed time if no exception occurred.

        Args:
            exception: The exception that occurred, if any.
        """
        super().__exit__(exception, *args, **kwargs)
        if not exception:
            indents = ""
            if not self.is_first_child:
                msg = self.message.strip("\n")
                indents = "\t" * (len(msg) - len(msg.lstrip("\t")))

            runtime = round(self.elapsed, self.precision)
            if self.precision == 0:
                runtime = int(runtime)

            print(f"{indents}done. ({runtime}s)")

    def child(self, message: str, precision: int | None = None):
        """
        Creates a new CTimer object with an indented message.

        Args:
            message (str): The indented message.
            precision (int, optional): The number of decimals to round the elapsed time.
                Defaults to the value of the parent timer.

        Returns:
            CTimer: The new CTimer object.
        """
        whitespace = "\t" * (self.message.count("\t") + 1)

        if self.is_first_child:
            whitespace = "\n" + whitespace
            self.is_first_child = False

        return CTimer(whitespace + message, precision=(precision or self.precision))

    def progress_apply(
        self,
        df: DataFrame,
        action: Callable[[Series], Any],
        message: str = "",
        split_col: str | None = None,
    ):
        """
        Applies a function to a DataFrame with progress tracking.

        If split_col is not provided, the function is applied to the entire DataFrame.
        If split_col is provided, the function is applied in subsets of
        the DataFrame based on unique values in the split_col column.

        Args:
            df (DataFrame): The DataFrame to apply the function to.
            action (Callable[[Series], Any]): The function to apply to each row of the DataFrame.
            message (str, optional): A formattable message for each progress update. Defaults to "".
            split_col (str, optional): The column name to split the DataFrame by. Defaults to None.

        Returns:
            DataFrame: The output of the function applied to the DataFrame.
        """
        if not split_col:
            return self.__progress_apply_single(df, action, message)

        output = DataFrame()
        for key in df[split_col].drop_duplicates().to_list():
            subset = df.loc[df[split_col] == key]
            msg = message.format(key) if message else str(key)
            subset_results = self.__progress_apply_single(subset, action, msg)
            output = concat([output, subset_results], ignore_index=True)

        if len(output.columns) == 1:
            return output.squeeze()

        return output.reset_index(drop=True)

    def __progress_apply_single(
        self, df: DataFrame, action: Callable[[Series], Any], message: str
    ):
        """
        Applies the function to a single DataFrame and returns the results.

        Args:
            df (DataFrame): The DataFrame to apply the function to.
            action (Callable[[Series], Any]): The function to apply to each row of the DataFrame.
            message (str): The progress message.

        Returns:
            DataFrame: The output of the function applied to the DataFrame.
        """
        print()
        tqdm.pandas(desc=f"    {message}")
        return df.progress_apply(action, axis=1)  # type: ignore
