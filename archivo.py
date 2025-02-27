import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF
from deep_translator import GoogleTranslator
import threading
import fitz  # PyMuPDF
import os
import time
import traceback

# Variable de control para detener el proceso
stop_flag = False

# Función para ejecutar con seguimiento de errores
def run_with_debug(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

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
            if block['type'] == 0:  # Ignorar bloques que no son de texto (gráficos, imágenes, etc.)
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
        
        # Obtener el nombre del archivo sin la ruta y la extensión
        titulo = os.path.splitext(os.path.basename(file_path))[0]
        selected_file_title_label.config(text=titulo)

        if file_path.endswith('.pdf'):
            threading.Thread(target=lambda: run_with_debug(translate_pdf, file_path)).start()
        elif file_path.endswith('.txt'):
            threading.Thread(target=lambda: run_with_debug(translate_text, file_path)).start()

# Función para detener el proceso
def stop_process():
    global stop_flag
    stop_flag = True

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

# Función para Validar la traducción y ver si tiene errores
def extract_plain_text(file_path):
    doc = fitz.open(file_path)
    plain_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        plain_text += text + "\n"

    return plain_text

# Función para dividir el texto en líneas de un máximo de caracteres
def split_text_into_lines(text, max_chars_per_line=60):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(word) > max_chars_per_line:
            # Si una sola palabra excede el límite, la dividimos
            while len(word) > max_chars_per_line:
                lines.append(word[:max_chars_per_line])
                word = word[max_chars_per_line:]
            current_line = word + " "
        elif len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines

# Función para dividir el texto en fragmentos de un máximo de caracteres
def split_text(text, max_length=4800):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Función para traducir el texto
def translate_text(text):
    fragments = split_text(text)
    translated_text = ""
    for fragment in fragments:
        translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
        translated_text += translated_fragment + " "
    translated_text = ' '.join(translated_text.split())  # Reemplazar múltiples espacios en blanco
    return translated_text

# Función para traducir un archivo PDF
def translate_pdf(file_path):
    start_time = time.time()
    try:
        plain_text = extract_plain_text(file_path)
        translated_text = translate_text(plain_text)

        fragments = split_text(translated_text)
        total_fragments = len(fragments)
        
        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font('Helvetica', size=12)

            # Agregar el título del archivo seleccionado al inicio del PDF
            titulo = os.path.splitext(os.path.basename(file_path))[0]  # Obtener el título del archivo
            pdf.set_font('Helvetica', size=16)
            pdf.multi_cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(10)  # Agregar un espacio después del título

            # Agregar el texto traducido por fragmentos y líneas
            pdf.set_font('Helvetica', size=12)
            for i, fragment in enumerate(fragments):
                lines = split_text_into_lines(fragment)
                for line in lines:
                    success = False
                    font_size = 12
                    while not success and font_size > 0:
                        try:
                            pdf.set_font('Helvetica', size=font_size)
                            # Ajustar la celda para asegurar espacio horizontal suficiente
                            pdf.cell(200, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                            success = True
                        except Exception as e:
                            font_size -= 1
                            if font_size <= 0:
                                print(f"Error: {e}")
                                raise

                # Actualizar el progreso después de cada fragmento
                update_progress(i + 1, total_fragments, f"Traduciendo fragmento {i+1}/{total_fragments}", start_time)

            pdf.output(output_file_path)
            messagebox.showinfo("Éxito", "El archivo ha sido traducido y guardado correctamente como PDF.")
            status_label.config(text="Traducción completada con éxito.")
            time_label.config(text="Tiempo restante estimado: Completado")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Error durante la traducción")
        print("Error:", str(e))
        traceback.print_exc()  # Añadir traceback para obtener más detalles del error


# Crear la interfaz gráfica
root = tk.Tk()
root.title("Traductor de Archivos")
root.geometry("400x350")

# Continuación del código de la interfaz...
file_title_label = tk.Label(root, text="Título del archivo seleccionado:")
file_title_label.pack(pady=10)

selected_file_title_label = tk.Label(root, text="", font=("Arial", 12))
selected_file_title_label.pack(pady=10)

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
