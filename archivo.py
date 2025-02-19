import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
from deep_translator import GoogleTranslator

# Función para seleccionar un archivo
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        translate_pdf(file_path)

# Función para dividir el texto en fragmentos de máximo 4800 caracteres
def split_text(text, max_length=4800):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Función para traducir un archivo PDF
def translate_pdf(file_path):
    try:
        # Leer el contenido del PDF
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfFileReader(pdf_file)
            content = ""
            for page in range(reader.numPages):
                content += reader.getPage(page).extractText()
        
        # Dividir el contenido en fragmentos manejables
        fragments = split_text(content)
        translated_fragments = []

        # Traducir cada fragmento
        for fragment in fragments:
            translated_fragment = GoogleTranslator(source='auto', target='es').translate(fragment)
            translated_fragments.append(translated_fragment)

        # Combinar los fragmentos traducidos
        translated_content = ''.join(translated_fragments)
        
        # Guardar el contenido traducido en un nuevo archivo
        output_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_file_path:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(translated_content)
            messagebox.showinfo("Éxito", "El archivo ha sido traducido y guardado correctamente.")
    
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Traductor de PDF")
root.geometry("300x150")

select_button = tk.Button(root, text="Seleccionar Archivo PDF", command=select_file)
select_button.pack(expand=True)

root.mainloop()
