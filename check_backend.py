#!/usr/bin/env python3
"""
Backend deployment durumunu kontrol etme scripti
"""
import requests
import sys

BACKEND_URL = "https://seng-451-hw4.onrender.com"

def check_backend():
    """Backend'in çalışıp çalışmadığını kontrol et"""
    print(f"🔍 Backend kontrol ediliyor: {BACKEND_URL}\n")
    
    # Health check
    try:
        print("1. Health check endpoint kontrol ediliyor...")
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Health check başarılı!")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ⚠️ Health check yanıt verdi ama status: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"   ⏳ Backend yanıt vermiyor (timeout) - Muhtemelen hala deploy ediliyor veya uyku modunda")
        print(f"   💡 Free tier'da backend 15 dakika kullanılmazsa uyku moduna geçer")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Backend'e bağlanılamıyor - Deploy edilmemiş veya hata var")
        return False
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False
    
    # Root endpoint
    try:
        print("\n2. Root endpoint kontrol ediliyor...")
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Root endpoint çalışıyor!")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Hata: {e}")
    
    # API docs
    try:
        print("\n3. API docs kontrol ediliyor...")
        response = requests.get(f"{BACKEND_URL}/docs", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ API docs erişilebilir: {BACKEND_URL}/docs")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Hata: {e}")
    
    print(f"\n✅ Backend çalışıyor gibi görünüyor!")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"📚 API Docs: {BACKEND_URL}/docs")
    return True

if __name__ == "__main__":
    success = check_backend()
    sys.exit(0 if success else 1)

