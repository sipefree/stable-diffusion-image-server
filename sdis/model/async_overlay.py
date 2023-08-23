from redis.commands.json._util import JsonType as JsonType
from redis.commands.json.path import Path as Path
from typing import Optional, Union, TypeVar, Generic, Callable, Any
from concurrent.futures import ProcessPoolExecutor
import asyncio
from asyncio.futures import Future
from tqdm.asyncio import tqdm as tqdm
from collections.abc import Generator, AsyncIterator, Awaitable

PathLike = Union[str, Path]

class AsyncJSONCommands:
    async def arrappend(self, name: str, path: Optional[PathLike] = ..., *args: list[JsonType]) -> list[Union[int, None]]: ...
    async def arrindex(self, name: str, path: PathLike, scalar: int, start: Optional[int] = ..., stop: Optional[int] = ...) -> list[Union[int, None]]: ...
    async def arrinsert(self, name: str, path: PathLike, index: int, *args: list[JsonType]) -> list[Union[int, None]]: ...
    async def arrlen(self, name: str, path: Optional[PathLike] = ...) -> list[Union[int, None]]: ...
    async def arrpop(self, name: str, path: Optional[PathLike] = ..., index: Optional[int] = ...) -> list[Union[str, None]]: ...
    async def arrtrim(self, name: str, path: PathLike, start: int, stop: int) -> list[Union[int, None]]: ...
    async def type(self, name: str, path: Optional[PathLike] = ...) -> list[str]: ...
    async def objkeys(self, name: str, path: Optional[PathLike] = ...) -> list[Union[list[str], None]]: ...
    async def objlen(self, name: str, path: Optional[PathLike] = ...) -> int: ...
    async def numincrby(self, name: str, path: PathLike, number: int) -> str: ...
    async def nummultby(self, name: str, path: PathLike, number: int) -> str: ...
    async def clear(self, name: str, path: Optional[PathLike] = ...) -> int: ...
    async def delete(self, key: str, path: Optional[PathLike] = ...) -> int: ...
    forget = delete
    async def get(self, name: str, *args: PathLike, no_escape: Optional[bool] = ...) -> list[JsonType]: ...
    async def mget(self, keys: list[str], path: PathLike) -> list[JsonType]: ...
    async def set(self, name: str, path: PathLike, obj: JsonType, nx: Optional[bool] = ..., xx: Optional[bool] = ..., decode_keys: Optional[bool] = ...) -> Optional[str]: ...
    async def mset(self, triplets: list[tuple[str, str, JsonType]]) -> Optional[str]: ...
    async def merge(self, name: str, path: PathLike, obj: JsonType, decode_keys: Optional[bool] = ...) -> Optional[str]: ...
    async def set_file(self, name: str, path: PathLike, file_name: str, nx: Optional[bool] = ..., xx: Optional[bool] = ..., decode_keys: Optional[bool] = ...) -> Optional[str]: ...
    async def set_path(self, json_path: PathLike, root_folder: str, nx: Optional[bool] = ..., xx: Optional[bool] = ..., decode_keys: Optional[bool] = ...) -> list[dict[str, bool]]: ...
    async def strlen(self, name: str, path: Optional[PathLike] = ...) -> list[Union[int, None]]: ...
    async def toggle(self, name: str, path: Optional[PathLike] = ...) -> Union[bool, list[Optional[int]]]: ...
    async def strappend(self, name: str, value: str, path: Optional[int] = ...) -> Union[int, list[Optional[int]]]: ...
    async def debug(self, subcommand: str, key: Optional[str] = ..., path: Optional[PathLike] = ...) -> Union[int, list[str]]: ...

Input = TypeVar('Input')
Output = TypeVar('Output')

class AsyncProcessMap(Generic[Input, Output], AsyncIterator[Output]):
    """
    Asynchronous process map implementation.
    
    Maps input items to output by applying a function in parallel using process pool.
    The class is designed to be used as an asynchronous iterator.
    
    Args:
        func: The function to apply to each input item.
        input: List of input items.
        max_workers: The maximum number of processes that can be used to execute the calls. 
                     If None, the number will be the number of processors on the machine.
        tqdm_kwargs: Additional keyword arguments for tqdm progress bar.
    """
    
    def __init__(self, 
                 func: Callable[[Input], Output],
                 input: list[Input],
                 max_workers: Optional[int] = None,
                 **tqdm_kwargs: Any):
        self.func: Callable[[Input], Output] = func
        self.input = input
        self.tqdm_kwargs: dict[str, Any] = tqdm_kwargs
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.task_iter: Optional[Generator[Awaitable[Output], None, None]]
        self.is_submitted = False
    
    def __aiter__(self):
        """Returns the async iterator instance."""
        if self.is_submitted:
            raise RuntimeError("Cannot iterate over AsyncProcessMap more than once.")
        return self
    
    async def __anext__(self) -> Output:
        """Yields next processed result or raises StopAsyncIteration when done."""
        if not self.is_submitted:
            self.is_submitted = True
            await self._submit_work()
        try:
            if self.task_iter is None:
                raise StopAsyncIteration
            try:
                task = next(self.task_iter)
                return await task
            except StopIteration:
                raise StopAsyncIteration
        except Exception as e:
            self.task_iter = None
            self.executor.shutdown()
            raise e
        
    async def _submit_work(self):
        """
        Submit work to the process pool executor.
        
        This function will generate a list of futures representing the work to be done.
        The futures are then wrapped in an async iterator with a tqdm progress bar.
        """
        loop = asyncio.get_running_loop()
        futures: list[Future[Output]] = []
        for item in self.input:
            future = loop.run_in_executor(self.executor, self.func, item)
            futures.append(future)
        if len(futures) == 0:
            return
        self.task_iter = tqdm.as_completed(futures, **self.tqdm_kwargs)
    