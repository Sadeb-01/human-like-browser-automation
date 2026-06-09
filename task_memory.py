import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from logger import system_logger
from config import DEFAULT_CONFIG

class TaskMemoryManager:
    """
    Manages the persistence of task progress and state.
    """

    def __init__(self, memory_dir: Path = DEFAULT_CONFIG.memory.memory_dir):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        system_logger.info(f"TaskMemoryManager initialized. Memory directory: {self.memory_dir}")

    def _get_memory_path(self, task_name: str) -> Path:
        """
        Returns the file path for a given task's memory.
        """
        return self.memory_dir / f"{task_name}.json"

    def load_task_memory(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Loads the memory for a specific task.
        Returns None if no memory exists for the task.
        """
        memory_path = self._get_memory_path(task_name)
        if memory_path.exists():
            try:
                with open(memory_path, 'r') as f:
                    memory = json.load(f)
                system_logger.info(f"Loaded memory for task \'{task_name}\'.")
                return memory
            except json.JSONDecodeError as e:
                system_logger.error(f"Error decoding JSON for task \'{task_name}\': {e}")
                return None
        system_logger.info(f"No existing memory found for task \'{task_name}\'.")
        return None

    def save_task_memory(self, task_name: str, memory_data: Dict[str, Any]):
        """
        Saves the current state of the task memory.
        """
        memory_path = self._get_memory_path(task_name)
        memory_data["last_run_timestamp"] = datetime.now().isoformat()
        with open(memory_path, 'w') as f:
            json.dump(memory_data, f, indent=4)
        system_logger.info(f"Saved memory for task \'{task_name}\'.")

    def update_task_progress(
        self,
        task_name: str,
        current_step: Optional[str] = None,
        status: Optional[str] = None,
        last_error: Optional[str] = None,
        browser_state_path: Optional[str] = None,
        history: Optional[List[str]] = None,
        last_url: Optional[str] = None
    ):
        """
        Updates specific fields in the task memory.
        """
        memory = self.load_task_memory(task_name) or {
            "task_name": task_name,
            "current_step": "start",
            "status": "new",
            "last_error": None,
            "browser_state_path": None,
            "history": [],
            "last_url": None
        }
        
        # Ensure history exists if loading from an older memory file
        if "history" not in memory:
            memory["history"] = []

        if current_step is not None:
            memory["current_step"] = current_step
        if status is not None:
            memory["status"] = status
        if last_error is not None:
            memory["last_error"] = last_error
        if browser_state_path is not None:
            memory["browser_state_path"] = browser_state_path
        if history is not None:
            memory["history"] = history
        if last_url is not None:
            memory["last_url"] = last_url

        self.save_task_memory(task_name, memory)

    def clear_task_memory(self, task_name: str):
        """
        Clears the memory file for a specific task.
        """
        memory_path = self._get_memory_path(task_name)
        if memory_path.exists():
            memory_path.unlink()
            system_logger.info(f"Cleared memory for task \'{task_name}\'.")

