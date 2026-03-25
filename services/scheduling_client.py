# services/scheduling_client.py
from datetime import datetime, timezone
from typing import Any, Dict
import uuid

from services.queue_client import QueueClient  # абстракция, можно сделать под Redis/Rabbit


class SchedulingClient:
    def __init__(self, queue_client: QueueClient, topic: str = "scheduling_jobs"):
        self._queue = queue_client
        self._topic = topic

    def enqueue_cpm_and_dashboard_recalc(
        self,
        project_id: int,
        priority: int = 5,
        source: str = "system",
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        job = {
            "job_id": str(uuid.uuid4()),
            "job_type": "cpm_and_dashboard_recalc",
            "project_id": project_id,
            "priority": priority,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "metadata": metadata or {},
        }
        self._queue.publish(self._topic, job)