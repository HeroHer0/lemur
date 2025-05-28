import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import shutil
import os
import socket
import threading
import concurrent.futures
from wakeonlan import send_magic_packet  # Importar la función send_magic_packet

# Mapeo de nombres de PCs a direcciones MAC
pc_mac_mapping = {
    "LC01": "B0-22-7A-2D-88-DA",
    "LC02": "B0-22-7A-2D-89-40",
    "LC03": "B0-22-7A-2D-89-17",
    "LC04": "B0-22-7A-2D-88-4F",
    "LC09": "B0-22-7A-2D-87-D7",
    "LC10": "B0-22-7A-2C-EC-2B",
    "LC11": "B0-22-7A-2D-89-2B",
    "LC17": "B0-22-7A-2D-88-CA",
    "LC18": "B0-22-7A-2D-88-27",
    "LC19": "B0-22-7A-2D-87-F3",
    "LC20": "B0-22-7A-2D-88-08",
    "LC24": "B0-22-7A-2D-89-19",
    "LC25": "B0-22-7A-2D-87-C4",
    "LC26": "B0-22-7A-2D-88-39",
    "LC27": "B0-22-7A-2D-87-C0",
    "LC28": "B0-22-7A-2D-87-DA",
    "LC32": "B0-22-7A-2D-89-46",
    "LC35": "B0-22-7A-2D-87-D4",
    "LC36": "B0-22-7A-2D-87-EE",
    "LC37": "0A-00-27-00-00-16",
    "LC38": "0A-00-27-00-00-17"
    
}
# Función para realizar ping a una PC
def ping_pc(pc_name):
    try:
        comando = f'ping -n 1 {pc_name}'  # Envía un solo paquete de ping
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Analizar la salida del comando ping
        salida = resultado.stdout.lower()  # Convertir la salida a minúsculas para facilitar la comparación
        
        if "tiempo de espera agotado" in salida or "host de destino inaccesible" in salida:
            return False
        elif "bytes=" in salida:  # Si hay una respuesta exitosa
            return True
        else:
            return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Ocurrió un error al ejecutar el comando: {e}")
        return None

# Función para leer la contraseña desde un archivo
def read_password():
    try:
        with open("password.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "admin"  # Contraseña por defecto si no existe el archivo

# Función para escribir la nueva contraseña en el archivo
def write_password(new_password):
    with open("password.txt", "w") as file:
        file.write(new_password)

# Funciones de las tareas
def Prender(pc_name):
    msg = tk.Toplevel()
    msg.title("Ejecución de Tarea")
    tk.Label(msg, text=f"Ejecutando Prender en {pc_name}").pack()
    msg.after(3000, msg.destroy)
    msg.bind('<Escape>', lambda e: msg.destroy())
    try:
        # Obtener la dirección MAC de la PC desde el mapeo
        mac_address = pc_mac_mapping.get(pc_name)
        if mac_address:
            print(f"Enviando paquete mágico WOL a {pc_name} con MAC {mac_address}")  # Depuración
            send_magic_packet(mac_address)
            print(f"Paquete mágico WOL enviado a {pc_name} ({mac_address})")
            messagebox.showinfo("Éxito", f"Paquete mágico WOL enviado a {pc_name} ({mac_address})")
        else:
            raise ValueError(f"No se encontró la dirección MAC para {pc_name}")
    except Exception as e:
        print(f"Ocurrió un error al enviar el paquete WOL: {e}")
        messagebox.showerror("Error", f"No se pudo encender {pc_name}: {e}")

def Apagar(pc_name):
    msg = tk.Toplevel()
    msg.title("Ejecución de Tarea")
    tk.Label(msg, text=f"Ejecutando Apagar en {pc_name}").pack()
    msg.after(3000, msg.destroy)
    msg.bind('<Escape>', lambda e: msg.destroy())
    try:
        comando = f'shutdown -m \\\\{pc_name} -s -t 0'
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Salida estándar:", resultado.stdout)
        print("Salida de error (si la hay):", resultado.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar el comando: {e}")
        messagebox.showerror("Error", f"No se pudo apagar {pc_name}: {e}")

def Reiniciar(pc_name):
    msg = tk.Toplevel()
    msg.title("Ejecución de Tarea")
    tk.Label(msg, text=f"Ejecutando Reiniciar en {pc_name}").pack()
    msg.after(3000, msg.destroy)
    msg.bind('<Escape>', lambda e: msg.destroy())
    try:
        if not ping_pc(pc_name):
            raise Exception(f"{pc_name} está apagada. Primero debe encender la computadora.")
        
        comando = f'shutdown -m \\\\{pc_name} -r -t 0'
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Salida estándar:", resultado.stdout)
        print("Salida de error (si la hay):", resultado.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar el comando para reiniciar: {e}")
        messagebox.showerror("Error", f"No se pudo reiniciar {pc_name}: {e}")
    except Exception as e:
        print(e)
        messagebox.showerror("Error", str(e))

def Bloquear(pc_name):
    msg = tk.Toplevel()
    msg.title("Ejecución de Tarea")
    tk.Label(msg, text=f"Ejecutando Bloquear en {pc_name}").pack()
    msg.after(3000, msg.destroy)
    msg.bind('<Escape>', lambda e: msg.destroy())
    try:
        # Asegúrate de que la ruta a PsExec.exe sea correcta
        psexec_path = r"C:\Users\install\Documents\servicio\PsExec.exe"
        if not os.path.exists(psexec_path):
            raise FileNotFoundError(f"PsExec.exe no se encontró en la ruta especificada: {psexec_path}")
        
        comando = f'"{psexec_path}" \\\\{pc_name} -accepteula -s -d -i 1 rundll32 user32.dll,LockWorkStation'
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Salida estándar:", resultado.stdout)
        print("Salida de error (si la hay):", resultado.stderr)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        messagebox.showerror("Error", str(fnf_error))
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar el comando: {e}")
        print("Salida estándar:", e.stdout)
        print("Salida de error (si la hay):", e.stderr)
        messagebox.showerror("Error", f"No se pudo bloquear {pc_name}: {e}")

def ping_pc(pc_name):
    try:
        comando = f'ping -n 1 {pc_name}'  # Envía un solo paquete de ping
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Analizar la salida del comando ping
        salida = resultado.stdout.lower()  # Convertir la salida a minúsculas para facilitar la comparación
        
        if "tiempo de espera agotado" in salida or "host de destino inaccesible" in salida:
            return False
        elif "bytes=" in salida:  # Si hay una respuesta exitosa
            return True
        else:
            return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Ocurrió un error al ejecutar el comando: {e}")
        return None

def enviar_archivo(pc_name):
    # Seleccionar el archivo a enviar
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo para enviar",
        filetypes=[("Todos los archivos", "*.*")]
    )
    if ruta_archivo:
        try:
            # Definir la ruta de destino en la PC remota
            ruta_destino = f"\\\\{pc_name}\\C$\\Temp\\{os.path.basename(ruta_archivo)}"
            
            # Copiar el archivo a la PC remota
            shutil.copy(ruta_archivo, ruta_destino)
            messagebox.showinfo("Éxito", f"Archivo enviado correctamente a {pc_name}.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el archivo a {pc_name}: {e}")

def control_remoto(pc_name):
    try:
        resultado = messagebox.askyesno("Confirmación", f"¿Está seguro de que desea conectarse a {pc_name}?")
        if not resultado:  # Intercambiar el comportamiento de los botones Sí y No
            return
        comando = f'mstsc /v:{pc_name} /admin'
        print(f"Ejecutando comando: {comando}")  # Depuración
        resultado = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Salida estándar:", resultado.stdout)
        print("Salida de error (si la hay):", resultado.stderr)
        if resultado.returncode != 0:
            messagebox.showerror("Error", f"No se pudo iniciar la sesión RDP en {pc_name}: {resultado.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Ocurrió un error al ejecutar el comando: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la sesión RDP en {pc_name}: {e}")

class PCManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Manager")
        self.pcerda = None  # Variable para almacenar el nombre de la PC seleccionada
        self.create_widgets()
        self.root.bind('<Escape>', lambda e: self.root.destroy())

    def create_widgets(self):
        self.pc_buttons = []
        for i in range(40):
            if (i < 9):
                pc_button = tk.Button(self.root, text=f"LC0{i+1}", command=lambda i=i: self.select_pc(i))
            else:
                pc_button = tk.Button(self.root, text=f"LC{i+1}", command=lambda i=i: self.select_pc(i))
            pc_button.grid(row=i//8, column=i%8, padx=5, pady=5)
            self.pc_buttons.append(pc_button)

        self.update_button = tk.Button(self.root, text="Actualizar", command=self.update_status)
        self.update_button.grid(row=6, column=0, columnspan=4, pady=10)

        self.shut_all_button = tk.Button(self.root, text="Apagar Todas", command=self.shut_down_all)
        self.shut_all_button.grid(row=6, column=4, columnspan=4, pady=10)

        self.change_password_button = tk.Button(self.root, text="Cambiar Contraseña", command=self.change_password)
        self.change_password_button.grid(row=7, column=0, columnspan=8, pady=10)

    def select_pc(self, pc_index):
        self.pcerda = f"LC{pc_index + 1:02}"  # Guardar el nombre de la PC seleccionada
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title(f"PC {self.pcerda} Tasks")
        self.task_window.bind('<Escape>', lambda e: self.task_window.destroy())
        
        tk.Label(self.task_window, text=f"Selecciona lo que deseas hacer").grid(row=0, column=0, columnspan=2)
        
        tk.Button(self.task_window, text="Prender", command=lambda: self.execute_task(Prender)).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self.task_window, text="Apagar", command=lambda: self.execute_task(Apagar)).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.task_window, text="Reiniciar", command=lambda: self.execute_task(Reiniciar)).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self.task_window, text="Bloquear", command=lambda: self.execute_task(Bloquear)).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.task_window, text="Ping", command=lambda: self.execute_task(ping_pc)).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self.task_window, text="Enviar Archivo", command=lambda: self.execute_task(enviar_archivo)).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.task_window, text="Control Remoto", command=lambda: self.execute_task(control_remoto)).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
    def execute_task(self, task_function):
        if self.pcerda:
            task_function(self.pcerda)  # Ejecutar la función de tarea con el nombre de la PC
        self.task_window.destroy()

    def update_status(self):
        """Inicia la actualización del estado de las PCs usando hilos."""
        thread = threading.Thread(target=self._update_status_thread)
        thread.start()

    def _update_status_thread(self):
        """Actualiza el estado de cada PC en paralelo utilizando hilos."""
        local_pc_name = socket.gethostname().upper()  # Obtener el nombre de la PC local y convertir a mayúsculas
        
        # Crear un diccionario de colores para actualizar los botones
        button_colors = {}

        def check_pc_status(pc_name):
            """Verifica el estado de una PC (ping) y retorna el color correspondiente."""
            if pc_name == local_pc_name:
                return 'green'  # La PC local siempre está activa
            elif ping_pc(pc_name):
                return 'green'
            else:
                return 'red'

        # Usar ThreadPoolExecutor para realizar las verificaciones en paralelo
        with concurrent.futures.ThreadPoolExecutor() as executor:
            pc_names = [f"LC{str(i + 1).zfill(2)}" for i in range(len(self.pc_buttons))]
            results = executor.map(check_pc_status, pc_names)

        # Actualizar los colores de los botones basado en los resultados
        for button, color in zip(self.pc_buttons, results):
            button_colors[button] = color

        # Actualizar los botones en el hilo principal
        def update_all_buttons():
            for button, color in button_colors.items():
                button.config(bg=color)
        
        self.root.after(0, update_all_buttons)

    def shut_down_all(self):
        """Apaga todas las PCs que están marcadas en verde."""
        for i, button in enumerate(self.pc_buttons):
            if button.cget("bg") == "green":  # Verificar si el botón está verde
                pc_name = f"LC{str(i + 1).zfill(2)}"
                Apagar(pc_name)  # Apagar la PC correspondiente
        messagebox.showinfo("Información", "Se enviaron las solicitudes para apagar las PCs activas.")

    def change_password(self):
        self.change_password_window = tk.Toplevel(self.root)
        self.change_password_window.title("Cambiar Contraseña")
        self.change_password_window.bind('<Escape>', lambda e: self.change_password_window.destroy())

        tk.Label(self.change_password_window, text="Ingrese nueva Contraseña:").grid(row=0, column=0, padx=5, pady=5)
        self.new_password_entry = tk.Entry(self.change_password_window, show="*")
        self.new_password_entry.grid(row=0, column=1, padx=5, pady=5)
        self.new_password_entry.bind('<Return>', self.save_new_password)  # Llamar a save_new_password al presionar Enter

        tk.Button(self.change_password_window, text="Guardar", command=self.save_new_password).grid(row=1, column=0, columnspan=2, pady=5)

    def save_new_password(self, event=None):
        new_password = self.new_password_entry.get()
        if new_password:
            write_password(new_password)
            messagebox.showinfo("Exito", "La Contraseña fue cambiada exitosamente")
            self.change_password_window.destroy()
        else:
            messagebox.showerror("Error", "La Contraseña no puede quedar en blanco")

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.create_widgets()
        self.root.bind('<Escape>', lambda e: self.root.destroy())

    def create_widgets(self):
        tk.Label(self.root, text="Contraseña:").grid(row=0, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.bind('<Return>', self.check_password)  # Llamar a check_password al presionar Enter

        tk.Button(self.root, text="Entrar", command=self.check_password).grid(row=1, column=0, columnspan=2, pady=5)

    def check_password(self, event=None):
        entered_password = self.password_entry.get()
        if entered_password == read_password():
            self.root.destroy()
            root = tk.Tk()
            app = PCManager(root)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Contraseña Incorrecta")

if __name__ == "__main__":
    root = tk.Tk()
    app = Login(root)
    root.mainloop()
