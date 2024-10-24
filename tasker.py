import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Conectar a la base de datos SQLite (se creará automáticamente si no existe)
conn = sqlite3.connect('tareas.db')
cursor = conn.cursor()

# Crear la tabla para guardar las tareas si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        start_date TEXT,
        complete_date TEXT
    )
''')
conn.commit()

# Crear la ventana principal
root = tk.Tk()
root.title("Lista Diaria de Tareas")

# Configurar la ventana (hacerla redimensionable)
root.geometry("400x400")  # Tamaño inicial
root.resizable(True, True)  # Permitir que la ventana sea regulable en ambas direcciones

# Lista donde se guardarán las tareas
tasks = []

# Función para añadir tarea
def add_task():
    task_title = title_entry.get()
    task_desc = desc_entry.get("1.0", tk.END).strip()

    if task_title == "" or task_desc == "":
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('INSERT INTO tasks (title, description, start_date) VALUES (?, ?, ?)', 
                   (task_title, task_desc, start_date))
    conn.commit()

    task_id = cursor.lastrowid

    task_frame = tk.Frame(task_list_frame, pady=5)
    task_frame.pack(fill="x", padx=5)

    task_label = tk.Label(task_frame, text=f"{task_title}: {task_desc}", anchor="w")
    task_label.pack(side="left", fill="x", expand=True)

    # Crear los botones con la función separada
    create_task_buttons(task_frame, task_label, task_id)

    title_entry.delete(0, tk.END)
    desc_entry.delete("1.0", tk.END)


# Función para marcar como "En progreso"
def mark_in_progress(task_frame, task_label, task_id):
    task_label.config(bg="yellow", fg="black")
    # Registrar en la base de datos que la tarea está en progreso (no se actualiza la fecha de finalización)
    cursor.execute('UPDATE tasks SET complete_date = NULL WHERE id = ?', (task_id,))
    conn.commit()

# Función para marcar como "Completada"
def mark_complete(task_frame, task_label, task_id):
    task_label.config(bg="lightgreen", fg="black")
    complete_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Registrar la fecha de finalización en la base de datos
    cursor.execute('UPDATE tasks SET complete_date = ? WHERE id = ?', (complete_date, task_id))
    conn.commit()

def create_task_buttons(task_frame, task_label, task_id):
    # Botón "En progreso"
    btn_in_progress = tk.Button(task_frame, text="En progreso", command=lambda: mark_in_progress(task_frame, task_label, task_id))
    btn_in_progress.pack(side="left", padx=5)

    # Botón "Completada"
    btn_complete = tk.Button(task_frame, text="Completada", command=lambda: mark_complete(task_frame, task_label, task_id))
    btn_complete.pack(side="left", padx=5)


# Crear la interfaz de la aplicación
title_label = tk.Label(root, text="Título de la tarea:")
title_label.pack(pady=5)

title_entry = tk.Entry(root, width=50)
title_entry.pack(pady=5)

desc_label = tk.Label(root, text="Descripción de la tarea:")
desc_label.pack(pady=5)

desc_entry = tk.Text(root, height=4, width=50)
desc_entry.pack(pady=5)

add_button = tk.Button(root, text="Añadir tarea", command=add_task)
add_button.pack(pady=10)

task_list_frame = tk.Frame(root)
task_list_frame.pack(pady=10, fill="both", expand=True)

# Cargar solo las tareas que están en progreso al iniciar la aplicación
def load_tasks():
    cursor.execute('SELECT id, title, description, start_date, complete_date FROM tasks WHERE complete_date IS NULL')
    for task in cursor.fetchall():
        task_id, task_title, task_desc, start_date, complete_date = task

        task_frame = tk.Frame(task_list_frame, pady=5)
        task_frame.pack(fill="x", padx=5)

        task_label = tk.Label(task_frame, text=f"{task_title}: {task_desc}", anchor="w")
        task_label.pack(side="left", fill="x", expand=True)

        task_label.config(bg="yellow", fg="black")

        # Crear los botones con la función separada
        create_task_buttons(task_frame, task_label, task_id)



# Llamar la función para cargar las tareas al iniciar la app
load_tasks()

# Iniciar la aplicación
root.mainloop()

# Cerrar la conexión a la base de datos al cerrar la aplicación
conn.close()
