import asyncio
import redis
import dill
import pickle
import json
from typing import Callable, List, Any, Tuple, Dict
import threading

from pytask_io.client import deserialize_task, deserialize_store_data
from pytask_io.logger import logger

# --------------------------------------
#    Public functions
# --------------------------------------


def create_task_queue(host: str = "localhost", port: int = 6379, db: int = 0) -> redis.Redis:
    return redis.Redis(
        host=host,
        port=port,
        db=db,
    )


def serialize_unit_of_work(unit_of_work: Any, *args) -> bytes:
    """
    Serializes a unit of work & returns the results
    :param unit_of_work:s
    :param args:
    :return:
    """
    serialized_uow = dill.dumps((unit_of_work, [*args]))
    return serialized_uow


def serialize_store_data(store_data: Any) -> bytes:
    """
    Serializes a unit of work & returns the results
    :param unit_of_work:s
    :param args:
    :return:
    """
    serialized_uow = dill.dumps((store_data))
    return serialized_uow


async def pole_for_store_results(queue_client: redis.Redis, task_meta: Dict, tries: int, interval: int):
    """
    Streams back results to
    :param queue_client:
    :param task_meta:
    :param tries:
    :param interval:
    :return:
    """
    list_name = task_meta.get("list_name")
    task_index = task_meta.get("task_index")
    dumped = None
    if interval:
        while tries > 0:
            current_loop = asyncio.get_running_loop()

            result = await current_loop.run_in_executor(None, queue_client.lindex, *[list_name, task_index])
            if result:
                dumped = await deserialize_store_data(result)
                tries -= 1
                break
            elif not result:
                break
            else:
                await asyncio.sleep(interval)
    return dumped
