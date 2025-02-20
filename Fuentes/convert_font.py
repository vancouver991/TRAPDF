import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF
from deep_translator import GoogleTranslator
import threading
import fitz  # PyMuPDF

# Función para cargar el diccionario de correcciones desde un archivo de texto
def load_corrections(file_path):
    corrections = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if ':' in line:
                incorrect, correct = line.strip().split(':')
                corrections[incorrect.strip()] = correct.strip()
    return corrections

# Cargar el diccionario de correcciones
corrections = load_corrections('biblioteca_de_correcciones.txt')

# Función para cargar el diccionario de correcciones contextuales desde un archivo de texto
def load_contextual_corrections(file_path):
    contextual_corrections = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if ':' in line:
                incorrect, correct = line.strip().split(':')
                contextual_corrections[incorrect.strip()] = correct.strip()
    return contextual_corrections

# Cargar el diccionario de correcciones contextuales
contextual_corrections = load_contextual_corrections('correcciones_contextuales.txt')

# Función para aplicar correcciones
def apply_corrections(text):
    for incorrect, correct in corrections.items():
        text = text.replace(incorrect, correct)
    return text

# Función para aplicar correcciones contextuales
def apply_contextual_corrections(text):
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
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
    if file_path:
        status_label.config(text="Archivo seleccionado: " + file_path)
        if file_path.endswith('.pdf'):
            threading.Thread(target=translate_pdf, args=(file_path,)).start()
        elif file_path.endswith('.txt'):
            threading.Thread(target=translate_text, args=(file_path,)).start()

# Función para dividir el texto en fragmentos de máximo 4800 caracteres
def split_text(text, max_length=4800):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Función para actualizar la barra de progreso y el mensaje de estado
def update_progress(current, total, message):
    progress_bar['value'] = (current / total) * 100
    status_label.config(text=message)
    root.update_idletasks()

# Función para traducir un archivo PDF y convertirlo en un nuevo PDF
def translate_pdf(file_path):
    try:
        text_with_format = extract_text_with_format(file_path)
        translated_fragments = []

        update_progress(0, len(text_with_format), "Iniciando traducción del PDF...")

        for i, fragment in enumerate(text_with_format):
            print(f"Traduciendo fragmento {i + 1} de {len(text_with_format)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment["text"])
            translated_fragment = apply_corrections(translated_fragment)
            translated_fragment = apply_contextual_corrections(translated_fragment)
            fragment["text"] = translated_fragment
            translated_fragments.append(fragment)
            update_progress(i + 1, len(text_with_format), f"Traduciendo fragmento {i + 1} de {len(text_with_format)}...")

        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_font('Brother1816ExtraBold', '', 'brother1816-extrabold.ttf', uni=True)
            pdf.set_font('Brother1816ExtraBold', size=12)

            for fragment in translated_fragments:
                pdf.set_font('Brother1816ExtraBold', size=fragment["size"])
                pdf.multi_cell(0, 10, fragment["text"].encode('latin-1', 'replace').decode('latin-1'))

            print("Guardando archivo traducido...")
            pdf.output(output_file_path)
            messagebox.showinfo("Éxito", "El archivo ha sido traducido y guardado correctamente como PDF.")
            status_label.config(text="Traducción completada con éxito.")
    
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print("Error:", str(e))

# Función para traducir un archivo de texto y convertirlo en un nuevo PDF
def translate_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as text_file:
            print("Abriendo archivo de texto...")
            content = text_file.read()

        fragments = split_text(content)
        translated_fragments = []

        update_progress(0, len(fragments), "Iniciando traducción del texto...")

        for i, fragment in enumerate(fragments):
            print(f"Traduciendo fragmento {i + 1 de {len(fragments)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
            translated_fragment = apply_corrections(translated_fragment)
            translated_fragment = apply_contextual_corrections(translated_fragment)
            translated_fragments.append(translated_fragment)
            update_progress(i + 1, len(fragments), f"Traduciendo fragmento {i + 1} de {len(fragments)}...")

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
    
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print("Error:", str(e))

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Traductor de Archivos")
root.geometry("400x200")

select_button = tk.Button(root, text="Seleccionar Archivo", command=select_file)
select_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="Seleccione un archivo para traducir")
status_label.pack(pady=10)

root.mainloop()
