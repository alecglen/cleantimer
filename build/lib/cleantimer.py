from typing import Any, Callable
from contexttimer import Timer
from pandas import DataFrame, Series, concat
from tqdm import tqdm


class CTimer(Timer):
    
    def __init__(self, message: str, precision: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.precision = precision
        
    def __enter__(self, *args, **kwargs):
        super().__enter__(*args, **kwargs)
        self.last_check = 0
        print(self.message + '...', end='', flush=True)
        return self

    def __exit__(self, exception, *args, **kwargs):
        super().__exit__(exception, *args, **kwargs)
        if not exception:
            print(f'done. ({round(self.elapsed, self.precision)}s)')
            
    def child(self, message: str):
        indents = "\t" * (self.message.count("\t") + 1)
        return CTimer(f"\n{indents}{message}", self.precision)

    def progress_apply(self, df: DataFrame, action: Callable[[Series], Any], message: str = "", split_col: str = None):
        if not split_col:
            return self.__progress_apply_single(df, action, message)
        
        output = DataFrame()
        for key in df[split_col].drop_duplicates().to_list():
            subset = df.loc[df[split_col] == key]
            subset_results = self.__progress_apply_single(subset, action, message.format(key))
            output = concat([output, subset_results], ignore_index=True)
                
        output.reset_index(drop=True, inplace=True)
            
        return output
    
    def __progress_apply_single(self, df: DataFrame, action: Callable[[Series], Any], message: str):
        print()
        tqdm.pandas(desc="    " + message)
        return df.progress_apply(action, axis=1)
