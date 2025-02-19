import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader
from deep_translator import GoogleTranslator
from fpdf import FPDF
import threading

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
        with open(file_path, 'rb') as pdf_file:
            print("Abriendo archivo PDF...")
            reader = PdfReader(pdf_file)
            
            if reader.is_encrypted:
                messagebox.showinfo("Protección de Derechos de Autor", "El archivo que intentas traducir está sujeto a derechos de autor y está protegido.")
                return

            content = []
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                print(f"Extrayendo texto de la página {page_num + 1}...")
                content.append(page.extract_text())
                content.append('\n\n')  # Añadir saltos de línea entre páginas

        fragments = split_text(''.join(content))
        translated_fragments = []

        update_progress(0, len(fragments), "Iniciando traducción del PDF...")

        for i, fragment in enumerate(fragments):
            print(f"Traduciendo fragmento {i + 1} de {len(fragments)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
            translated_fragments.append(translated_fragment)
            update_progress(i + 1, len(fragments), f"Traduciendo fragmento {i + 1} de {len(fragments)}...")

        translated_content = ''.join(translated_fragments)

        # Crear un nuevo PDF con el texto traducido
        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            for line in translated_content.split('\n'):
                pdf.multi_cell(0, 10, line)

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
            print(f"Traduciendo fragmento {i + 1} de {len(fragments)}...")
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
            translated_fragments.append(translated_fragment)
            update_progress(i + 1, len(fragments), f"Traduciendo fragmento {i + 1} de {len(fragments)}...")

        translated_content = ''.join(translated_fragments)

        # Crear un nuevo PDF con el texto traducido
        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            for line in translated_content.split('\n'):
                pdf.multi_cell(0, 10, line)

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
