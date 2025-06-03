#!/usr/bin/env python3
import json
import os
import sys
import platform
import subprocess
import importlib
import shutil
from datetime import datetime

def check_and_install_modules():
    """Überprüft und installiert/aktualisiert benötigte Module - Cross-Platform"""
    print("=== Überprüfung der benötigten Module ===")
    
    required_modules = {
        'requests': 'requests',
        'ftplib': None,  # Built-in module
        're': None,      # Built-in module
        'json': None,    # Built-in module
        'os': None,      # Built-in module
        'sys': None,     # Built-in module
        'platform': None, # Built-in module
        'subprocess': None, # Built-in module
        'importlib': None,  # Built-in module
        'datetime': None,   # Built-in module
        'shutil': None      # Built-in module
    }
    
    missing_modules = []
    
    # Überprüfe jedes Modul
    for module_name, pip_name in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} ist verfügbar")
        except ImportError:
            if pip_name:
                print(f"❌ {module_name} fehlt")
                missing_modules.append(pip_name)
            else:
                print(f"⚠️  {module_name} (Built-in) nicht verfügbar - Python-Installation prüfen")
    
    # Installiere fehlende Module
    if missing_modules:
        print(f"\n📦 Installiere fehlende Module: {', '.join(missing_modules)}")
        for module in missing_modules:
            try:
                # Verschiedene Python-Executables versuchen
                python_executables = [sys.executable, 'python3', 'python', 'py']
                success = False
                
                for python_exe in python_executables:
                    try:
                        subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", module], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"✅ {module} erfolgreich installiert/aktualisiert mit {python_exe}")
                        success = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                if not success:
                    print(f"❌ Fehler beim Installieren von {module} - versuche alternative Methode")
                    # Fallback: pip direkt aufrufen
                    try:
                        subprocess.check_call(["pip", "install", "--upgrade", module])
                        print(f"✅ {module} erfolgreich installiert mit pip")
                    except:
                        print(f"❌ Konnte {module} nicht installieren")
                        return False
                        
            except Exception as e:
                print(f"❌ Fehler beim Installieren von {module}: {e}")
                return False
    else:
        print("✅ Alle benötigten Module sind verfügbar")
    
    return True

def is_termux():
    """Prüft ob das Script in Termux läuft"""
    return (os.path.exists("/data/data/com.termux") or 
            os.environ.get('PREFIX', '').startswith('/data/data/com.termux'))

def is_android():
    """Prüft ob das Script auf Android läuft (auch außerhalb Termux)"""
    return (os.path.exists("/system/build.prop") or 
            os.path.exists("/android_root") or
            'ANDROID_ROOT' in os.environ)

def execute_termux_commands():
    """Führt benötigte Termux-Befehle aus - nur wenn in Termux"""
    print("\n=== System-Konfiguration ===")
    
    if not is_termux():
        print("ℹ️  Nicht in Termux-Umgebung - überspringe Termux-spezifische Befehle")
        return True
    
    print("📱 Termux-Umgebung erkannt")
    
    # Prüfe ob pkg verfügbar ist
    if not shutil.which('pkg'):
        print("❌ pkg-Befehl nicht gefunden - möglicherweise nicht in Termux")
        return True
    
    termux_commands = [
        ("pkg update -y", "Paketliste aktualisieren"),
        ("pkg upgrade -y", "Pakete aktualisieren"),
        ("pkg install python -y", "Python installieren/aktualisieren"),
        ("pkg install curl -y", "Curl installieren"),
        ("pkg install wget -y", "Wget installieren")
    ]
    
    for cmd, description in termux_commands:
        print(f"🔧 {description}...")
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {description} erfolgreich")
            else:
                print(f"⚠️  {description} - möglicherweise bereits vorhanden oder Fehler")
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  {description} - Timeout")
        except FileNotFoundError:
            print(f"❌ Befehl nicht gefunden: {cmd}")
        except Exception as e:
            print(f"❌ Fehler bei {description}: {e}")
    
    # Termux-setup-storage separat behandeln
    try:
        print("🔧 Speicher-Zugriff einrichten...")
        if shutil.which('termux-setup-storage'):
            print("📁 Führe termux-setup-storage aus (falls noch nicht geschehen)...")
            subprocess.run(['termux-setup-storage'], timeout=30)
            print("✅ Speicher-Zugriff konfiguriert")
        else:
            print("⚠️  termux-setup-storage nicht verfügbar")
    except:
        print("⚠️  Speicher-Zugriff konnte nicht automatisch konfiguriert werden")
    
    print("✅ System-Konfiguration abgeschlossen")
    return True

def get_password_input(prompt="Passwort: "):
    """Sichere Passwort-Eingabe mit Cross-Platform Fallback"""
    try:
        # Versuche zuerst getpass
        import getpass
        return getpass.getpass(prompt)
    except Exception:
        # Fallback: normale Eingabe mit Warnung
        print("⚠️  Sichere Passwort-Eingabe nicht verfügbar - Passwort wird sichtbar eingegeben!")
        print("💡 Tipp: Stelle sicher, dass niemand auf deinen Bildschirm schaut.")
        return input(prompt)

def get_ftp_config():
    """Fragt FTP-Konfiguration ab - Cross-Platform"""
    print("\n=== FTP-Upload Konfiguration ===")
    
    try:
        upload_choice = input("Möchten Sie die Playlist auf einen FTP-Server hochladen? (j/n): ").lower().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Eingabe abgebrochen")
        return False, None
    
    if upload_choice in ['j', 'ja', 'y', 'yes', '1']:
        print("\n📡 FTP-Zugangsdaten eingeben:")
        
        try:
            ftp_host = input("FTP-Server (z.B. ftp.example.com): ").strip()
            if not ftp_host:
                print("❌ FTP-Server ist erforderlich!")
                return False, None
                
            ftp_user = input("FTP-Benutzername: ").strip()
            if not ftp_user:
                print("❌ Benutzername ist erforderlich!")
                return False, None
            
            ftp_pass = get_password_input("FTP-Passwort: ")
            if not ftp_pass:
                print("❌ Passwort ist erforderlich!")
                return False, None
                
            remote_path = input("Remote-Pfad (Enter für Root-Verzeichnis): ").strip()
            if not remote_path:
                remote_path = "/"
            
            # Bestätigung der Eingaben
            print(f"\n📋 FTP-Konfiguration:")
            print(f"   Server: {ftp_host}")
            print(f"   Benutzer: {ftp_user}")
            print(f"   Passwort: {'*' * len(ftp_pass)}")
            print(f"   Pfad: {remote_path}")
            
            confirm = input("\nSind diese Angaben korrekt? (j/n): ").lower().strip()
            if confirm not in ['j', 'ja', 'y', 'yes', '1']:
                print("❌ FTP-Konfiguration abgebrochen.")
                return False, None
            
            return True, (ftp_host, ftp_user, ftp_pass, remote_path)
            
        except (EOFError, KeyboardInterrupt):
            print("\n❌ FTP-Konfiguration abgebrochen")
            return False, None
    else:
        return False, None

def get_download_folder():
    """Ermittelt den Download-Ordner - Cross-Platform optimiert"""
    system = platform.system().lower()
    
    # Android/Termux spezifische Pfade
    if is_android() or is_termux():
        android_paths = [
            "/storage/emulated/0/Download/Vavoo-IPTV",  # Standard Android Download
            "/sdcard/Download/Vavoo-IPTV",              # Alternative Android Download
            os.path.expanduser("~/storage/downloads/Vavoo-IPTV"),  # Termux storage
            os.path.expanduser("~/downloads/Vavoo-IPTV"),          # Termux fallback
            os.path.join(os.getcwd(), "Vavoo-IPTV")                # Aktuelles Verzeichnis
        ]
        
        for path in android_paths:
            try:
                os.makedirs(path, exist_ok=True)
                # Test ob schreibbar
                test_file = os.path.join(path, ".write_test")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print(f"📁 Verwende Android/Termux Pfad: {path}")
                return path
            except (OSError, PermissionError):
                continue
    
    # Windows
    elif system == "windows":
        paths = [
            os.path.join(os.path.expanduser("~"), "Downloads", "Vavoo-IPTV"),
            os.path.join(os.environ.get('USERPROFILE', ''), "Downloads", "Vavoo-IPTV"),
            os.path.join("C:", "Users", os.environ.get('USERNAME', 'User'), "Downloads", "Vavoo-IPTV"),
            os.path.join(os.getcwd(), "Vavoo-IPTV")
        ]
    
    # macOS
    elif system == "darwin":
        paths = [
            os.path.join(os.path.expanduser("~"), "Downloads", "Vavoo-IPTV"),
            os.path.join("/Users", os.environ.get('USER', 'user'), "Downloads", "Vavoo-IPTV"),
            os.path.join(os.getcwd(), "Vavoo-IPTV")
        ]
    
    # Linux und andere Unix-ähnliche Systeme
    else:
        paths = [
            os.path.join(os.path.expanduser("~"), "Downloads", "Vavoo-IPTV"),
            os.path.join(os.path.expanduser("~"), "downloads", "Vavoo-IPTV"),  # lowercase
            os.path.join("/home", os.environ.get('USER', 'user'), "Downloads", "Vavoo-IPTV"),
            os.path.join(os.getcwd(), "Vavoo-IPTV")
        ]
    
    # Teste jeden Pfad
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
            # Test ob schreibbar
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"📁 Verwende Pfad: {path}")
            return path
        except (OSError, PermissionError):
            continue
    
    # Fallback: aktuelles Verzeichnis
    fallback_path = os.path.join(os.getcwd(), "Vavoo-IPTV")
    try:
        os.makedirs(fallback_path, exist_ok=True)
        print(f"📁 Fallback-Pfad: {fallback_path}")
        return fallback_path
    except:
        print("❌ Konnte keinen schreibbaren Ordner finden!")
        return os.getcwd()

def upload_to_ftp(file_path, ftp_host, ftp_user, ftp_pass, remote_path="/"):
    """Lädt eine Datei auf einen FTP-Server hoch - Cross-Platform"""
    try:
        import ftplib
        import socket
        
        print(f"📡 Verbinde mit FTP-Server {ftp_host}...")
        
        # FTP-Verbindung herstellen mit erweiterten Optionen
        ftp = ftplib.FTP()
        
        # Verschiedene Verbindungsmethoden versuchen
        try:
            ftp.connect(ftp_host, 21, timeout=30)
        except socket.gaierror:
            # Versuche mit ftp:// Präfix zu entfernen falls vorhanden
            clean_host = ftp_host.replace('ftp://', '').replace('ftps://', '')
            ftp.connect(clean_host, 21, timeout=30)
        
        ftp.login(ftp_user, ftp_pass)
        print(f"✅ Erfolgreich mit {ftp_host} verbunden")
        
        # In das Zielverzeichnis wechseln
        if remote_path and remote_path != "/":
            try:
                ftp.cwd(remote_path)
                print(f"📁 Verzeichnis gewechselt zu: {remote_path}")
            except ftplib.error_perm as e:
                print(f"⚠️  Konnte nicht zu {remote_path} wechseln: {e}")
                print("📁 Verwende Root-Verzeichnis")
        
        # Datei hochladen
        filename = os.path.basename(file_path)
        print(f"📤 Lade {filename} hoch...")
        
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
        
        print(f"✅ Datei erfolgreich hochgeladen: {filename}")
        
        # Verbindung schließen
        ftp.quit()
        return True
        
    except ftplib.all_errors as e:
        print(f"❌ FTP-Fehler: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Allgemeiner Fehler beim Upload: {str(e)}")
        return False

def download_json_from_url(url):
    """Lädt Channel-Daten von der angegebenen URL herunter - Cross-Platform"""
    try:
        import requests
        
        # User-Agent für bessere Kompatibilität
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"🌐 Lade Daten von: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Prüfe Content-Type
        content_type = response.headers.get('content-type', '').lower()
        if 'json' not in content_type:
            print(f"⚠️  Unerwarteter Content-Type: {content_type}")
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Netzwerk-Fehler beim Herunterladen der Channel-Daten: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON-Dekodierung fehlgeschlagen: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Allgemeiner Fehler beim Herunterladen der Channel-Daten: {str(e)}")
        return None

def clean_channel_name(name):
    """Entfernt HD, FHD, |E, |H, |D und Zahlen aus dem Sendernamen - Cross-Platform"""
    import re
    
    if not name or not isinstance(name, str):
        return "Unbekannter Kanal"
    
    # Ausnahmen für bestimmte Sender
    exceptions = [
        "BLUETV", "SKY BOX", "SKY SELECT", "123 TV", "1.2.3. TV",
        "STERN FILME", "GERMANY KONIG FILME", "GERMANY BESONDERE"
    ]
    
    name_upper = name.upper()
    is_exception = any(exc in name_upper for exc in exceptions)
    
    if is_exception:
        # Nur |E, |H, |D entfernen bei Ausnahmen
        name = re.sub(r'\s*\|[EHD]\s*', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    # Standard-Bereinigung
    name = re.sub(r'\s*HD\s*', ' ', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*FHD\s*', ' ', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*4K\s*', ' ', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\|[EHD]\s*', ' ', name)
    
    # Hauptname extrahieren (nur Buchstaben und Leerzeichen)
    main_name_match = re.match(r'^([A-Za-z]+(?:\s+[A-Za-z]+)*)', name)
    if main_name_match:
        name = main_name_match.group(1)
    
    # Mehrfache Leerzeichen entfernen
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name if name else "Unbekannter Kanal"

def get_channel_url(channel_id, channel_name):
    """Gibt die URL für den Kanal zurück - Cross-Platform"""
    if not channel_name:
        channel_name = ""
    
    # Spezielle Behandlung für bestimmte Kanäle
    if "BILD TV" in channel_name.upper():
        return "https://bild.personalstream.tv/v1/master.m3u8"
    elif channel_id:
        return f"https://huhu.to/play/{channel_id}/index.m3u8"
    else:
        return "https://example.com/placeholder.m3u8"

def convert_json_to_m3u8(channels, m3u8_file_path):
    """Konvertiert die Kanäle aus dem JSON-Format in das M3U8-Format - Cross-Platform"""
    try:
        # Stelle sicher, dass das Verzeichnis existiert
        directory = os.path.dirname(m3u8_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        print(f"📝 Erstelle M3U8-Datei: {m3u8_file_path}")
        
        with open(m3u8_file_path, 'w', encoding='utf-8', newline='\n') as m3u8_file:
            # Header mit EPG-URLs
            m3u8_file.write('#EXTM3U8 x-url-tvg=https://vav00.de/sources/epg/epg_de.xml,https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz\n')
            
            processed_channels = 0
            
            for channel in channels:
                try:
                    country = channel.get('country', 'Unbekannt')
                    channel_id = channel.get('id', '')
                    original_name = channel.get('name', 'Unbekannter Kanal')
                    
                    clean_name = clean_channel_name(original_name)
                    channel_url = get_channel_url(channel_id, original_name)
                    
                    # VLCOPT-Header
                    m3u8_file.write('#EXTVLCOPT:http-user-agent=VAVOO/2.6\n')
                    m3u8_file.write('#EXTVLCOPT:http-referrer=https://vavoo.tv/\n')
                    
                    # EXTINF-Zeile mit Metadaten
                    m3u8_file.write(f'#EXTINF:-1 group-title="{country}" tvg-logo="https://raw.githubusercontent.com/SuperNova-Repo/Vavuu-IPTV/refs/heads/main/VAVOO_%26_OTT-Navigator-icon.jpg" tvg-name="{clean_name}", {clean_name}\n')
                    
                    # Stream-URL
                    m3u8_file.write(f'{channel_url}\n')
                    
                    processed_channels += 1
                    
                except Exception as e:
                    print(f"⚠️  Fehler beim Verarbeiten von Kanal {original_name}: {e}")
                    continue
        
        print(f"✅ Konvertierung erfolgreich! {processed_channels} Kanäle verarbeitet")
        print(f"📄 M3U8-Datei erstellt: {m3u8_file_path}")
        
        # Dateigröße anzeigen
        try:
            file_size = os.path.getsize(m3u8_file_path)
            print(f"📊 Dateigröße: {file_size} Bytes ({file_size/1024:.1f} KB)")
        except:
            pass
        
        return True
    
    except PermissionError:
        print(f"❌ Keine Berechtigung zum Schreiben in: {m3u8_file_path}")
        return False
    except OSError as e:
        print(f"❌ Dateisystem-Fehler: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Fehler bei der Konvertierung: {str(e)}")
        return False

def main():
    """Hauptfunktion - Cross-Platform optimiert"""
    try:
        print("\n\n\n\n🚀 Vavoo Channel Downloader gestartet.\n\n[by ꀘꂦꌗ꓄ꌩꍏ🃏꒒ꂦ꒒ꀤꈤꁅꍟꋪ]")
        print("=" * 50)
        
        # System-Informationen anzeigen
        print(f"🖥️  Betriebssystem: {platform.system()} {platform.release()}")
        print(f"🐍 Python-Version: {platform.python_version()}")
        if is_termux():
            print("📱 Termux-Umgebung erkannt")
        elif is_android():
            print("🤖 Android-Umgebung erkannt")
        
        # 1. Module überprüfen und installieren/aktualisieren
        print("\n" + "=" * 50)
        if not check_and_install_modules():
            print("❌ Module-Installation fehlgeschlagen. Script wird beendet.")
            input("Drücke Enter zum Beenden...")
            sys.exit(1)
        
        # 2. System-Befehle ausführen
        print("\n" + "=" * 50)
        if not execute_termux_commands():
            print("❌ System-Konfiguration fehlgeschlagen. Script wird beendet.")
            input("Drücke Enter zum Beenden...")
            sys.exit(1)
        
        # 3. FTP-Konfiguration abfragen
        print("\n" + "=" * 50)
        upload_enabled, ftp_config = get_ftp_config()
        
        # 4. Playlist erstellen
        print("\n" + "=" * 50)
        print("=== Playlist-Erstellung ===")
        
        json_url = "https://huhu.to/channels"
        download_folder = get_download_folder()
        m3u8_file_path = os.path.join(download_folder, "Vavoo-IPTV.m3u8")
        
        print(f"📁 Download-Ordner: {download_folder}")
        print(f"📄 Playlist-Datei: {os.path.basename(m3u8_file_path)}")
        
        # Channel-Daten laden
        channels = download_json_from_url(json_url)
        
        if channels and isinstance(channels, list):
            print(f"✅ Channel-Daten erfolgreich geladen. {len(channels)} Kanäle gefunden.")
            
            # M3U8-Datei erstellen
            if convert_json_to_m3u8(channels, m3u8_file_path):
                print(f"📋 Die Playlist wurde erfolgreich gespeichert!")
                
                # 5. FTP-Upload durchführen (falls gewünscht)
                if upload_enabled and ftp_config:
                    print("\n" + "=" * 50)
                    ftp_host, ftp_user, ftp_pass, remote_path = ftp_config
                    print(f"📤 Starte FTP-Upload zu {ftp_host}...")
                    
                    if upload_to_ftp(m3u8_file_path, ftp_host, ftp_user, ftp_pass, remote_path):
                        print("✅ Playlist erfolgreich auf FTP-Server hochgeladen!")
                    else:
                        print("❌ FTP-Upload fehlgeschlagen.")
                else:
                    print("ℹ️  Kein FTP-Upload gewünscht.")
            else:
                print("❌ Fehler beim Erstellen der Playlist.")
        else:
            print("❌ Konnte keine gültigen Kanäle laden. Überprüfe deine Internetverbindung.")
            print("🔍 Mögliche Ursachen:")
            print("   - Keine Internetverbindung")
            print("   - Server nicht erreichbar")
            print("   - Firewall blockiert Zugriff")
    
    except KeyboardInterrupt:
        print("\n\n❌ Script durch Benutzer abgebrochen (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")
        print("🐛 Bitte melde diesen Fehler dem Entwickler")
    
    finally:
        print("\n" + "=" * 50)
        print("🏁 Script beendet")
        
        # Pause vor dem Schließen (besonders nützlich auf Windows)
        try:
            input("\nDrücke Enter zum Beenden...")
        except:
            pass

if __name__ == "__main__":
    main()
