from invoke.collection import Collection
from utils.tasks import daily_sync, one_time_tasks

ns = Collection(daily_sync, one_time_tasks)
