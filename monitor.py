import ollama
import os
import psutil
import platform
from datetime import datetime


def get_system_stats():
    """Returns real-time CPU and RAM usage percentage."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"CPU Usage: {cpu}% | RAM Usage: {ram}%"

def list_files(directory="."):
    """Lists files in a given directory (defaults to current)."""
    try:
        files = os.listdir(directory)
        return f"Files in {directory}: " + ", ".join(files)
    except Exception as e:
        return f"Error reading directory: {str(e)}"

def manage_tasks(action: str, task_text: str = ""):
    """Actions: 'add' to save a reminder, 'list' to see all reminders."""
    filename = "reminders.txt"
    if action == "add":
        with open(filename, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_text}\n")
        return f"Reminder saved: {task_text}"
    elif action == "list":
        if not os.path.exists(filename): return "No reminders found."
        with open(filename, "r") as f:
            return f.read()


def run_supervisor_agent():
    model = "llama3.2"
    print(f"--- 2026 Advanced OS Agent (Py 3.14) ---")
    
    messages = [{
        "role": "system",
        "content": (
            "You are an OS Supervisor. You have access ONLY to: "
            "get_system_stats, list_files, manage_tasks, set_performance_mode, organize_folder. "
            "If a user says 'yes' to a suggestion, proceed with the relevant tool. "
            "Do not invent new tools like 'disk_usage'."
        )
    }]

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]: break
        
        messages.append({"role": "user", "content": user_input})

        available_tools = [get_system_stats, list_files, manage_tasks, set_performance_mode, organize_folder]

        response = ollama.chat(model=model, messages=messages, tools=available_tools)

        if response.get('message', {}).get('tool_calls'):
            messages.append(response['message'])
            
            for tool in response['message']['tool_calls']:
                name = tool['function']['name']
                args = tool['function']['arguments']
                
                if name == "get_system_stats":
                    result = get_system_stats()
                elif name == "list_files":
                    result = list_files(**args)
                elif name == "manage_tasks":
                    result = manage_tasks(**args)
                elif name == "set_performance_mode":
                    result = set_performance_mode(**args)
                elif name == "organize_folder":
                    result = organize_folder(**args)
                else:
                    result = f"Error: The tool '{name}' is not available. Please use an existing tool."
                
                messages.append({'role': 'tool', 'content': result})

            final_response = ollama.chat(model=model, messages=messages)
            print(f"Agent: {final_response['message']['content']}\n")
        else:
            messages.append(response['message'])
            print(f"Agent: {response['message']['content']}\n")

if __name__ == "__main__":
    run_supervisor_agent()