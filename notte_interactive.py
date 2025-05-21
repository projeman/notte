import os
import notte
import sys

# Gemini API anahtarı
os.environ["GEMINI_API_KEY"] = ""

def run_notte_agent(task_description, max_steps=10):
    """Notte agent ile bir görevi yerine getir"""
    print(f"\n⏳ Görev başlatılıyor: {task_description}")
    print("İşlem devam ediyor, lütfen bekleyin...")
    
    # Agent oluştur
    agent = notte.Agent(
        reasoning_model="gemini/gemini-2.0-flash", 
        max_steps=max_steps
    )
    
    # Görevi çalıştır
    result = agent.run(task=task_description)
    
    print("\n🔍 Agent Sonucu:")
    print(f"✅ Başarılı: {result.success}")
    print(f"⏱️ Süre: {result.duration_in_s:.2f} saniye")
    print(f"📝 Cevap: {result.answer}")
    
    return result

def interactive_console():
    """Konsol üzerinden interaktif mod"""
    print("=" * 60)
    print("📱 Notte AI Agent Interactive Console")
    print("=" * 60)
    
    while True:
        print("\nNe yapmak istiyorsunuz?")
        print("1. Tek görev çalıştır")
        print("2. Çoklu görev çalıştır")
        print("3. Çıkış")
        
        choice = input("\nSeçiminiz (1-3): ")
        
        if choice == "1":
            task = input("\nYapılmasını istediğiniz görevi yazın: ")
            steps = input("Maksimum adım sayısı (varsayılan: 10): ")
            max_steps = int(steps) if steps.isdigit() else 10
            
            run_notte_agent(task, max_steps)
            
        elif choice == "2":
            try:
                task_count = int(input("\nKaç görev çalıştırmak istiyorsunuz?: "))
                tasks = []
                
                for i in range(task_count):
                    task = input(f"Görev {i+1}: ")
                    tasks.append(task)
                
                steps = input("Tüm görevler için maksimum adım sayısı (varsayılan: 10): ")
                max_steps = int(steps) if steps.isdigit() else 10
                
                for i, task in enumerate(tasks):
                    print(f"\n🔄 Görev {i+1}/{task_count} çalıştırılıyor...")
                    run_notte_agent(task, max_steps)
                    
            except ValueError:
                print("❌ Hata: Lütfen geçerli bir sayı girin!")
            
        elif choice == "3":
            print("\n👋 Program sonlandırılıyor...")
            break
            
        else:
            print("❌ Geçersiz seçim! Lütfen 1-3 arasında bir değer girin.")

if __name__ == "__main__":
    # İnteraktif konsol modunu başlat
    interactive_console() 