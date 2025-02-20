from fpdf import FPDF, make_font
import os

def make_font_files(ttf_path, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    base_name = os.path.basename(ttf_path).split('.')[0]
    php_filename = os.path.join(dest_folder, base_name + '.php')
    z_filename = os.path.join(dest_folder, base_name + '.z')
    make_font(ttf_path, php_filename, z_filename)
    print(f"Font files generated: {php_filename}, {z_filename}")

if __name__ == '__main__':
    ttf_path = 'brother1816-extrabold.ttf'
    dest_folder = 'font'
    make_font_files(ttf_path, dest_folder)
