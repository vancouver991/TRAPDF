import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF
from deep_translator import GoogleTranslator
import threading
import fitz  # PyMuPDF
import os
import time

# Variable de control para detener el proceso
stop_flag = False

# Función para cargar el diccionario de correcciones desde un archivo de texto
def load_corrections(file_path):
    corrections = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if ':' in line:
                    incorrect, correct = line.strip().split(':')
                    corrections[incorrect.strip()] = correct.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
    except Exception as e:
        print(f"Error al cargar el archivo de correcciones: {e}")
    return corrections

# Cargar el diccionario de correcciones
corrections = load_corrections(r'C:\Users\Usuario\Desktop\Proyectos\TRAPDF\biblioteca_de_correcciones.txt')

# Función para cargar el diccionario de correcciones contextuales desde un archivo de texto
def load_contextual_corrections(file_path):
    contextual_corrections = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if ':' in line:
                    incorrect, correct = line.strip().split(':')
                    contextual_corrections[incorrect.strip()] = correct.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
    except Exception as e:
        print(f"Error al cargar el archivo de correcciones contextuales: {e}")
    return contextual_corrections

# Cargar el diccionario de correcciones contextuales
contextual_corrections = load_contextual_corrections(r'C:\Users\Usuario\Desktop\Proyectos\TRAPDF\correcciones_contextuales.txt')

# Función para aplicar correcciones
def apply_corrections(text):
    if text is None:
        return ""  # Devolver una cadena vacía si el texto es None
    for incorrect, correct in corrections.items():
        text = text.replace(incorrect, correct)
    return text

# Función para aplicar correcciones contextuales
def apply_contextual_corrections(text):
    if text is None:
        return ""  # Devolver una cadena vacía si el texto es None
    for incorrect, correct in contextual_corrections.items():
        text = text.replace(incorrect, correct)
    return text

# Función para extraer texto con formato desde un archivo PDF
def extract_text_with_format(file_path):
    doc = fitz.open(file_path)
    text_with_format = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_with_format.append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": span["size"]
                        })
    return text_with_format

# Función para seleccionar un archivo
def select_file():
    global stop_flag
    stop_flag = False  # Resetear la bandera de detención
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
    if file_path:
        status_label.config(text="Archivo seleccionado: " + file_path)
        if file_path.endswith('.pdf'):
            threading.Thread(target=translate_pdf, args=(file_path,)).start()
        elif file_path.endswith('.txt'):
            threading.Thread(target=translate_text, args=(file_path,)).start()

# Función para detener el proceso
def stop_process():
    global stop_flag
    stop_flag = True

# Función para dividir el texto en fragmentos de máximo 4800 caracteres
def split_text(text, max_length=4800):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Función para actualizar la barra de progreso, mensaje de estado y tiempo estimado restante
def update_progress(current, total, message, start_time=None):
    if total == 0:
        progress = 0
    else:
        progress = (current / total) * 100
    progress_bar['value'] = progress
    status_label.config(text=message)
    if start_time:
        elapsed_time = time.time() - start_time
        if current == 0:
            estimated_total_time = 0
        else:
            estimated_total_time = elapsed_time * total / current
        remaining_time = estimated_total_time - elapsed_time
        time_label.config(text=f"Tiempo restante estimado: {int(remaining_time // 60)} min {int(remaining_time % 60)} seg")
    root.update_idletasks()

# Función para traducir un archivo PDF y convertirlo en un nuevo PDF
def translate_pdf(file_path):
    start_time = time.time()
    try:
        text_with_format = extract_text_with_format(file_path)
        translated_fragments = []

        update_progress(0, len(text_with_format), "Iniciando traducción del PDF...", start_time)

        for i, fragment in enumerate(text_with_format):
            if stop_flag:
                status_label.config(text="Proceso detenido por el usuario")
                time_label.config(text="Tiempo restante estimado: -- min -- seg")
                return

            print(f"Traduciendo fragmento {i + 1} de {len(text_with_format)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment["text"])
            translated_fragment = apply_corrections(translated_fragment)
            translated_fragment = apply_contextual_corrections(translated_fragment)
            fragment["text"] = translated_fragment
            translated_fragments.append(fragment)
            update_progress(i + 1, len(text_with_format), f"Traduciendo fragmento {i + 1} de {len(text_with_format)}...", start_time)

        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            font_path = r'C:\Users\Usuario\Desktop\Proyectos\TRAPDF\Fuentes\Brother-1816-ExtraBold.ttf'  # Ruta corregida
            pdf.add_font('Brother1816ExtraBold', '', font_path)
            pdf.set_font('Brother1816ExtraBold', size=12)

            for fragment in translated_fragments:
                pdf.set_font('Brother1816ExtraBold', size=fragment["size"])
                pdf.multi_cell(0, 10, fragment["text"].encode('latin-1', 'replace').decode('latin-1'))

            print("Guardando archivo traducido...")
            pdf.output(output_file_path)
            messagebox.showinfo("Éxito", "El archivo ha sido traducido y guardado correctamente como PDF.")
            status_label.config(text="Traducción completada con éxito.")
            time_label.config(text="Tiempo restante estimado: Completado")
    
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print("Error:", str(e))

# Función para traducir un archivo de texto y convertirlo en un nuevo PDF
def translate_text(file_path):
    start_time = time.time()
    try:
        with open(file_path, 'r', encoding='utf-8') as text_file:
            print("Abriendo archivo de texto...")
            content = text_file.read()

        fragments = split_text(content)
        translated_fragments = []

        update_progress(0, len(fragments), "Iniciando traducción del texto...", start_time)

        for i, fragment in enumerate(fragments):
            if stop_flag:
                status_label.config(text="Proceso detenido por el usuario")
                time_label.config(text="Tiempo restante estimado: -- min -- seg")
                return

            print(f"Traduciendo fragmento {i + 1} de {len(fragments)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
            translated_fragment = apply_corrections(translated_fragment)
            translated_fragment = apply_contextual_corrections(translated_fragment)
            translated_fragments.append(translated_fragment)
            update_progress(i + 1, len(fragments), f"Traduciendo fragmento {i + 1} de {len(fragments)}...", start_time)

        translated_content = ''.join(translated_fragments)

        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)  # Ajustar la fuente y el tamaño según sea necesario

            for line in translated_content.split('\n'):
                pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))

            print("Guardando archivo traducido...")
            pdf.output(output_file_path)
            messagebox.showinfo("Éxito", "El archivo ha sido traducido y guardado correctamente como PDF.")
            status_label.config(text="Traducción completada con éxito.")
            time_label.config(text="Tiempo restante estimado: Completado")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        print("Error:", str(e))

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Traductor de Archivos")
root.geometry("400x300")

select_button = tk.Button(root, text="Seleccionar Archivo", command=select_file)
select_button.pack(pady=10)

stop_button = tk.Button(root, text="Detener", command=stop_process)
stop_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="Seleccione un archivo para traducir")
status_label.pack(pady=10)

time_label = tk.Label(root, text="Tiempo restante estimado: -- min -- seg")
time_label.pack(pady=10)

root.mainloop()
