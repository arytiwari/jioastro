"""Test network connectivity to Supabase"""
import socket
import time

import pytest

pytestmark = pytest.mark.skip(
    reason="Network connectivity diagnostics require external Supabase endpoints"
)

def test_port(host, port, timeout=5):
    """Test if a port is reachable"""
    print(f"\nTesting connection to {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        elapsed = time.time() - start_time
        sock.close()

        if result == 0:
            print(f"✅ Port {port} is OPEN (connected in {elapsed:.2f}s)")
            return True
        else:
            print(f"❌ Port {port} is CLOSED or FILTERED (error code: {result})")
            return False
    except socket.timeout:
        print(f"❌ Connection TIMED OUT after {timeout}s")
        return False
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        return False

def main():
    print("=" * 70)
    print("NETWORK CONNECTIVITY TEST")
    print("=" * 70)

    # Test DNS resolution
    host = "db.jyawjajnxzuhzisjcnpn.supabase.co"
    print(f"\n1. Testing DNS resolution for {host}")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✅ DNS resolved to: {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return

    # Test ports
    print(f"\n2. Testing database ports:")
    direct_reachable = test_port(host, 5432, timeout=10)

    pooler_host = "aws-1-ap-southeast-2.pooler.supabase.com"
    print(f"\n3. Testing pooler connection:")
    print(f"   Testing DNS resolution for {pooler_host}")
    try:
        pooler_ip = socket.gethostbyname(pooler_host)
        print(f"   ✅ DNS resolved to: {pooler_ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        pooler_ip = None

    if pooler_ip:
        pooler_reachable = test_port(pooler_host, 6543, timeout=10)
    else:
        pooler_reachable = False

    # Test HTTPS (to verify general internet connectivity)
    print(f"\n4. Testing HTTPS connectivity to Supabase API:")
    https_reachable = test_port("jyawjajnxzuhzisjcnpn.supabase.co", 443, timeout=5)

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    if not https_reachable:
        print("\n❌ Cannot reach Supabase API (port 443)")
        print("   This suggests a general internet/firewall issue")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Try disabling VPN if you're using one")
        print("3. Check firewall settings (System Preferences → Security → Firewall)")
        print("4. Try from a different network (e.g., mobile hotspot)")
    elif not direct_reachable and not pooler_reachable:
        print("\n❌ PostgreSQL ports (5432, 6543) are blocked")
        print("   HTTPS works but database ports are blocked")
        print("\nPossible causes:")
        print("1. Corporate/network firewall blocking PostgreSQL ports")
        print("2. ISP blocking database ports")
        print("3. Local firewall on your Mac")
        print("\nSolutions:")
        print("1. Check Supabase → Settings → Database → 'Add a restriction'")
        print("   - Make sure your IP is allowed (or allow all IPs for testing)")
        print("2. Try connecting from a different network (mobile hotspot)")
        print("3. Check Mac firewall: System Preferences → Security → Firewall")
        print("4. Consider using Supabase's REST API instead of direct DB connection")
    elif direct_reachable or pooler_reachable:
        print("\n✅ Network connectivity looks good!")
        print("   The issue might be:")
        print("   1. Wrong password")
        print("   2. Wrong username format")
        print("   3. Database authentication settings")
        print("\nNext steps:")
        print("1. Double-check your database password in Supabase")
        print("2. Reset database password if needed")
        print("3. Verify the connection string format")

if __name__ == "__main__":
    main()
