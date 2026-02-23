import os
import psutil
import platform
from datetime import datetime
from pathlib import Path
import json

# Safe import
try:
    import ollama
except ImportError:
    raise RuntimeError("Ollama is not installed. Install with: pip install ollama")

# -------------------------
# Security Configuration
# -------------------------

BASE_DIR = Path.cwd().resolve()
REMINDER_FILE = BASE_DIR / "reminders.txt"
MAX_REMINDER_LENGTH = 300
MAX_HISTORY = 20

# -------------------------
# Secure Utilities
# -------------------------

def safe_path(path_str: str) -> Path:
    """Prevent path traversal and restrict to BASE_DIR."""
    requested = (BASE_DIR / path_str).resolve()
    if not str(requested).startswith(str(BASE_DIR)):
        raise PermissionError("Access outside allowed directory is not permitted.")
    return requested

# -------------------------
# Tools
# -------------------------

def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"CPU Usage: {cpu}% | RAM Usage: {ram}%"

def list_files(directory="."):
    try:
        directory_path = safe_path(directory)
        files = os.listdir(directory_path)
        return f"Files in {directory_path}: " + ", ".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

def manage_tasks(action: str, task_text: str = ""):
    if action not in ["add", "list"]:
        return "Invalid action. Use 'add' or 'list'."

    if action == "add":
        if not task_text or len(task_text) > MAX_REMINDER_LENGTH:
            return "Invalid reminder text."

        with open(REMINDER_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_text}\n")

        return "Reminder saved securely."

    elif action == "list":
        if not REMINDER_FILE.exists():
            return "No reminders found."

        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            return f.read()

# Placeholder secured stubs
def set_performance_mode(mode: str):
    if mode not in ["normal", "high", "eco"]:
        return "Invalid mode."
    return f"Performance mode set to {mode} (simulated)."

def organize_folder(directory: str):
    try:
        directory_path = safe_path(directory)
        return f"Folder '{directory_path}' organization simulated."
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------
# Supervisor Agent
# -------------------------

ALLOWED_TOOLS = {
    "get_system_stats": get_system_stats,
    "list_files": list_files,
    "manage_tasks": manage_tasks,
    "set_performance_mode": set_performance_mode,
    "organize_folder": organize_folder,
}

def validate_arguments(tool_name, arguments):
    """Strict argument validation."""
    if not isinstance(arguments, dict):
        return {}

    if tool_name == "list_files":
        return {"directory": str(arguments.get("directory", "."))}

    if tool_name == "manage_tasks":
        return {
            "action": str(arguments.get("action", "")),
            "task_text": str(arguments.get("task_text", "")),
        }

    if tool_name == "set_performance_mode":
        return {"mode": str(arguments.get("mode", "normal"))}

    if tool_name == "organize_folder":
        return {"directory": str(arguments.get("directory", "."))}

    return {}

def trim_history(messages):
    if len(messages) > MAX_HISTORY:
        return messages[-MAX_HISTORY:]
    return messages

def run_supervisor_agent():
    model = "llama3.2"
    print("--- Secure OS Supervisor ---")

    messages = [{
        "role": "system",
        "content": (
            "You are an OS Supervisor. You have access ONLY to: "
            "get_system_stats, list_files, manage_tasks, "
            "set_performance_mode, organize_folder. "
            "Never invent tools. Always use provided ones."
        )
    }]

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})
        messages = trim_history(messages)

        response = ollama.chat(
            model=model,
            messages=messages,
            tools=list(ALLOWED_TOOLS.values())
        )

        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            messages.append(message)

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                raw_args = tool_call["function"].get("arguments", {})

                if name not in ALLOWED_TOOLS:
                    result = f"Security Error: Tool '{name}' not allowed."
                else:
                    try:
                        args = validate_arguments(name, raw_args)
                        result = ALLOWED_TOOLS[name](**args)
                    except Exception as e:
                        result = f"Execution error: {str(e)}"

                messages.append({"role": "tool", "content": result})

            messages = trim_history(messages)

            final_response = ollama.chat(model=model, messages=messages)
            print("Agent:", final_response["message"]["content"], "\n")

        else:
            messages.append(message)
            print("Agent:", message.get("content", ""), "\n")

if __name__ == "__main__":
    run_supervisor_agent()