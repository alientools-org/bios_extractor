import subprocess
import sys
import os
import shutil
import argparse

def run_cmd(cmd, capture_output=False):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture_output)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von {' '.join(cmd)}:\n{e}")
        sys.exit(1)

def is_mounted(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            if mount_point in line.split():
                return True
    return False

def unmount(mount_point):
    if is_mounted(mount_point):
        print(f"Hänge {mount_point} aus (vorher vorhanden)...")
        run_cmd(['sudo', 'umount', mount_point])
        print("Aushängen erfolgreich.")
    else:
        print(f"{mount_point} ist nicht gemountet, kein Aushängen nötig.")

def cleanup_mount(mount_point):
    # Erst aushängen, dann Verzeichnis entfernen, falls leer
    unmount(mount_point)
    if os.path.exists(mount_point):
        try:
            os.rmdir(mount_point)
            print(f"Mountpoint-Verzeichnis {mount_point} wurde gelöscht.")
        except OSError:
            print(f"Mountpoint-Verzeichnis {mount_point} konnte nicht gelöscht werden (evtl. nicht leer).")

def mount_image(img_path, mount_point, offset):
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)

    unmount(mount_point)

    print(f"Mounten des Images mit Offset {offset} bei {mount_point} ...")
    run_cmd(['sudo', 'mount', '-o', f'loop,offset={offset},ro', img_path, mount_point])
    print("Mount erfolgreich.")

def extract_with_geteltorito(iso_path, output_img):
    print(f"Extrahiere BIOS-Image mit geteltorito aus {iso_path} nach {output_img} ...")
    run_cmd(['perl', '/bin/geteltorito.pl', '-o', output_img, iso_path])
    print("Extraktion abgeschlossen.")

def extract_with_innoextract(exe_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Extrahiere EXE mit innoextract aus {exe_path} nach {output_dir} ...")
    run_cmd(['innoextract', '-d', output_dir, exe_path])
    print("Extraktion abgeschlossen.")

def copy_files(src_dir, dest_dir):
    print(f"Kopiere Dateien von {src_dir} nach {dest_dir} ...")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        dest_subdir = os.path.join(dest_dir, rel_path)
        os.makedirs(dest_subdir, exist_ok=True)
        for file in files:
            shutil.copy2(os.path.join(root, file), os.path.join(dest_subdir, file))
    print("Kopieren abgeschlossen.")

def main():
    parser = argparse.ArgumentParser(description="BIOS Update Extraktor für ISO oder EXE")
    parser.add_argument("input_file", help="Pfad zur BIOS-Update-Datei (.iso oder .exe)")
    parser.add_argument("-t", "--type", choices=["iso", "exe"], required=True, help="Dateityp: iso oder exe")
    parser.add_argument("-o", "--output", default="./output", help="Ausgabeordner für extrahierte Dateien")
    args = parser.parse_args()

    input_file = args.input_file
    file_type = args.type
    output_dir = args.output

    if file_type == "iso":
        output_img = os.path.join(output_dir, "bios-update.img")
        mount_point = os.path.join(output_dir, "mnt_bios_img")
        final_files_dir = os.path.join(output_dir, "bios_files")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        extract_with_geteltorito(input_file, output_img)

        offset = 16384  # ggf. dynamisch bestimmen

        try:
            mount_image(output_img, mount_point, offset)
        except SystemExit:
            print("Mounten fehlgeschlagen. Programm wird beendet.")
            sys.exit(1)

        copy_files(mount_point, final_files_dir)

        cleanup_mount(mount_point)  # jetzt wird sauber ausgehängt und Verzeichnis gelöscht

        print(f"Fertig. BIOS-Dateien sind in {final_files_dir}.")

    elif file_type == "exe":
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        extract_with_innoextract(input_file, output_dir)
        print(f"Fertig. Dateien sind in {output_dir}.")

if __name__ == "__main__":
    main()
