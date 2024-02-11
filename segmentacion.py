import subprocess
from concurrent.futures import ThreadPoolExecutor
from sys import argv
import os
from colorama import Fore, Style


ip_rango = argv[1]  # Rango de IPs
ip_objetivo = argv[2]  # IP objetivo

# Crear un directorio con el nombre de la IP objetivo
directorio_resultados = f"{ip_objetivo}_resultados"
os.makedirs(directorio_resultados, exist_ok=True)

def modificar_ultima_parte_ip(ip_original, decrementar=True, cantidad=1):
    ip_lista = ip_original.split(".")
    if decrementar:
        ip_lista[-1] = str(int(ip_lista[-1]) - cantidad)
    else:
        ip_lista[-1] = str(int(ip_lista[-1]) + cantidad)
    ip_modificada = ".".join(ip_lista)
    return ip_modificada

ip_a = modificar_ultima_parte_ip(ip_objetivo, True, 1)
ip_b = modificar_ultima_parte_ip(ip_objetivo, True, 2)
ip_c = modificar_ultima_parte_ip(ip_objetivo, False, 1)

# Cambiar el directorio actual al directorio de resultados
os.chdir(directorio_resultados)

# Comandos con IP específica y el IP general ingresado
comandos = [
    f"nmap -sS -n {ip_rango} -oN general",
    f"nmap -sS -T4 -f -Pn {ip_objetivo} -oN fragmentacion",
    f'echo "Comando ejecutado: sudo hping3 -c 1 -S {ip_c} -a {ip_objetivo}" >> hping; nohup hping3 -c 1 -S 192.168.0.10 -a 192.168.1.11 >> hping 2>&1 &',
    f'echo "Comando ejecutado: sudo hping3 -c 1 --icmp -S {ip_c} -a {ip_objetivo}" >> hping_icmp; nohup hping3 -c 1 --icmp -S 192.168.0.10 -a 192.168.1.11 >> hping_icmp 2>&1 &',
    f'echo "Comando ejecutado: sudo hping3 -c 1 --udp -S {ip_c} -a {ip_objetivo}" >> hping_udp; nohup hping3 -c 1 --udp -S 192.168.0.10 -a 192.168.1.11 >> hping_udp 2>&1 &',
    f"nmap -sS -T4 -n -Pn -D {ip_a},{ip_b},ME,{ip_c} {ip_objetivo} -oN decoy"
]

def ejecutar_comando(comando):
    try:
        subprocess.run(comando, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        return False

# Ejecuta los comandos en paralelo
with ThreadPoolExecutor() as executor:
    resultados = list(executor.map(ejecutar_comando, comandos))

# Verifica si al menos uno de los comandos dio error
if any(not resultado for resultado in resultados):
    print(Fore.RED + "\nAl menos uno de los comandos dio error." + Style.RESET_ALL)
else:
    print(Fore.GREEN + "\nTodos los comandos se ejecutaron correctamente." + Style.RESET_ALL)


