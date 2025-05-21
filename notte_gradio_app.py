import os
import notte
import gradio as gr
import datetime
import json

# API Anahtarları (varsayılan olarak)
DEFAULT_GEMINI_API_KEY = ""
DEFAULT_OPENAI_API_KEY = ""  # Varsayılan olarak boş, kullanıcı girecek
DEFAULT_OPENROUTER_API_KEY = ""  # Varsayılan olarak boş, kullanıcı girecek
DEFAULT_GROQ_API_KEY = ""  # Varsayılan olarak boş, kullanıcı girecek

# Çevre değişkenleri ayarla
os.environ["GEMINI_API_KEY"] = DEFAULT_GEMINI_API_KEY

# Desteklenen sağlayıcılar (providers)
PROVIDERS = {
    "Google Gemini": {
        "models": [
            "gemini/gemini-2.0-flash",
            "vertex_ai/gemini-2.0-flash"
        ],
        "api_key_env": "GEMINI_API_KEY",
        "default_key": DEFAULT_GEMINI_API_KEY
    },
    "OpenAI": {
        "models": [
            "openai/gpt-4o"
        ],
        "api_key_env": "OPENAI_API_KEY",
        "default_key": DEFAULT_OPENAI_API_KEY
    },
    "OpenRouter": {
        "models": [
            "openrouter/google/gemma-3-27b-it"
        ],
        "api_key_env": "OPENROUTER_API_KEY",
        "default_key": DEFAULT_OPENROUTER_API_KEY
    },
    "Cerebras": {
        "models": [
            "cerebras/llama-3.3-70b"
        ],
        "api_key_env": "CEREBRAS_API_KEY",
        "default_key": ""
    },
    "Groq": {
        "models": [
            "groq/llama-3.3-70b-versatile"
        ],
        "api_key_env": "GROQ_API_KEY",
        "default_key": DEFAULT_GROQ_API_KEY
    }
}

# Tüm modellerin düz listesi
ALL_MODELS = [model for provider in PROVIDERS.values() for model in provider["models"]]

def run_notte_agent(task_description, model_name="gemini/gemini-2.0-flash", max_steps=10, provider_name="Google Gemini", api_key=None):
    """Notte agent ile bir görevi yerine getir"""
    
    # Doğru provider'ı belirle
    selected_provider = None
    for provider, info in PROVIDERS.items():
        if model_name in info["models"]:
            selected_provider = provider
            break
    
    if not selected_provider:
        selected_provider = provider_name
    
    # API anahtarı ayarla
    provider_info = PROVIDERS[selected_provider]
    env_var = provider_info["api_key_env"]
    
    # Kullanıcının kendi API anahtarı varsa onu kullan
    if api_key and api_key.strip():
        os.environ[env_var] = api_key.strip()
    else:
        # Yoksa varsayılan anahtarı kullan
        default_key = provider_info.get("default_key", "")
        if default_key:
            os.environ[env_var] = default_key
    
    # Agent oluştur
    try:
        agent = notte.Agent(
            reasoning_model=model_name, 
            max_steps=max_steps
        )
        
        # Görevi çalıştır
        result = agent.run(task=task_description)
        
        # Sonuç formatı
        output = f"""
### 🔍 Agent Sonucu:

**Başarı Durumu:** {'✅ Başarılı' if result.success else '❌ Başarısız'}  
**Tamamlanma Süresi:** {result.duration_in_s:.2f} saniye  
**Kullanılan Model:** {model_name}
**Provider:** {selected_provider}

**Cevap:**  
{result.answer}
        """
        
        # Farklı formatlarda sonuçlar
        result_data = {
            "task": task_description,
            "success": result.success,
            "duration_seconds": result.duration_in_s,
            "model": model_name,
            "provider": selected_provider,
            "answer": result.answer,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Farklı formatlar için dosya isimleri
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"notte_result_{timestamp}"
        
        # Markdown formatı
        md_content = f"""
# Notte AI Agent Sonucu

- **Görev:** {task_description}
- **Tarih:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Model:** {model_name}
- **Provider:** {selected_provider}
- **Başarı:** {'Evet' if result.success else 'Hayır'}
- **Süre:** {result.duration_in_s:.2f} saniye

## Sonuç:

{result.answer}
"""
        
        # Düz metin formatı
        txt_content = f"""
Notte AI Agent Sonucu
=====================

Görev: {task_description}
Tarih: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Model: {model_name}
Provider: {selected_provider}
Başarı: {'Evet' if result.success else 'Hayır'}
Süre: {result.duration_in_s:.2f} saniye

Sonuç:
------
{result.answer}
"""
        
        # JSON formatı
        json_content = json.dumps(result_data, indent=2, ensure_ascii=False)
        
        # Dosyalara yaz
        with open(f"{filename_base}.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        
        with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
            f.write(txt_content)
        
        with open(f"{filename_base}.json", "w", encoding="utf-8") as f:
            f.write(json_content)
        
        # Oluşturulan dosyaların yolları
        file_paths = [
            f"{filename_base}.md",
            f"{filename_base}.txt",
            f"{filename_base}.json"
        ]
        
        return output, file_paths
    
    except Exception as e:
        error_msg = f"❌ Hata oluştu: {str(e)}"
        return error_msg, []

def create_gradio_interface():
    with gr.Blocks(title="Notte AI Agent", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🤖 Notte AI Agent Web Arayüzü
        
        Bu uygulama ile Notte AI Agent'ı kullanarak web görevleri gerçekleştirebilirsiniz.
        Bir görev yazın ve Notte'un bu görevi nasıl yerine getirdiğini izleyin.
        """)
        
        with gr.Tab("Tek Görev"):
            with gr.Row():
                with gr.Column(scale=3):
                    task_input = gr.Textbox(
                        label="Görev", 
                        placeholder="Örn: Find the latest news about artificial intelligence and summarize the top story",
                        lines=3
                    )
                    
                    with gr.Row():
                        max_steps = gr.Slider(
                            minimum=3, 
                            maximum=25, 
                            value=10, 
                            step=1, 
                            label="Maksimum Adım Sayısı"
                        )
                    
                    with gr.Row():
                        provider_dropdown = gr.Dropdown(
                            choices=list(PROVIDERS.keys()),
                            value="Google Gemini",
                            label="Provider (Sağlayıcı)"
                        )
                        
                        model_dropdown = gr.Dropdown(
                            choices=PROVIDERS["Google Gemini"]["models"],
                            value="gemini/gemini-2.0-flash",
                            label="Model"
                        )
                    
                    api_choice = gr.Radio(
                        choices=["Varsayılan API Kullan", "Kendi API Anahtarımı Gireceğim"],
                        value="Varsayılan API Kullan",
                        label="API Seçeneği"
                    )
                    
                    # API anahtarı giriş kutusu - başlangıçta gizli
                    api_key_input = gr.Textbox(
                        label="API Anahtarı", 
                        placeholder="Seçilen provider için API anahtarınızı buraya girin",
                        visible=False,
                        type="password"
                    )
                    
                    run_btn = gr.Button("Görevi Başlat", variant="primary")
                
                with gr.Column(scale=4):
                    output = gr.Markdown(label="Sonuç")
                    download_files = gr.File(label="Sonuçları İndir", file_count="multiple")
            
            # Provider değiştiğinde model listesini güncelle
            def update_model_list(provider):
                models = PROVIDERS[provider]["models"]
                return gr.update(choices=models, value=models[0])
            
            provider_dropdown.change(
                fn=update_model_list,
                inputs=provider_dropdown,
                outputs=model_dropdown
            )
            
            # API seçimi değiştiğinde API giriş kutusunu göster/gizle
            def on_api_choice_change(choice):
                if choice == "Kendi API Anahtarımı Gireceğim":
                    return gr.update(visible=True)
                else:
                    return gr.update(visible=False)
            
            # Provider değiştiğinde API anahtarı etiketi ve placeholder metni güncelle
            def update_api_key_input(provider, api_choice):
                provider_info = PROVIDERS[provider]
                env_var = provider_info["api_key_env"].replace("_API_KEY", "")
                
                visible = api_choice == "Kendi API Anahtarımı Gireceğim"
                
                return gr.update(
                    label=f"{env_var} API Anahtarı",
                    placeholder=f"{provider} için API anahtarınızı buraya girin",
                    visible=visible
                )
            
            api_choice.change(
                fn=on_api_choice_change, 
                inputs=api_choice, 
                outputs=api_key_input
            )
            
            provider_dropdown.change(
                fn=update_api_key_input,
                inputs=[provider_dropdown, api_choice],
                outputs=api_key_input
            )
            
            # Buton tıklaması
            def on_run_click(task, steps, provider, model, api_choice, api_key_input):
                if not task.strip():
                    return "❌ Lütfen bir görev girin!", []
                
                api_key = None
                if api_choice == "Kendi API Anahtarımı Gireceğim" and api_key_input and api_key_input.strip():
                    api_key = api_key_input.strip()
                
                result_text, file_paths = run_notte_agent(task, model, int(steps), provider, api_key)
                return result_text, file_paths
            
            run_btn.click(
                fn=on_run_click, 
                inputs=[task_input, max_steps, provider_dropdown, model_dropdown, api_choice, api_key_input], 
                outputs=[output, download_files]
            )
        
        with gr.Tab("Çoklu Görev"):
            with gr.Row():
                with gr.Column():
                    tasks_input = gr.Textbox(
                        label="Görevler (Her satıra bir görev yazın)", 
                        placeholder="Find the latest news about SpaceX\nFind the weather for Istanbul\nSearch for the best Italian restaurants in New York",
                        lines=5
                    )
                    
                    with gr.Row():
                        multi_max_steps = gr.Slider(
                            minimum=3, 
                            maximum=25, 
                            value=10, 
                            step=1, 
                            label="Maksimum Adım Sayısı (Tüm görevler için)"
                        )
                    
                    with gr.Row():
                        multi_provider_dropdown = gr.Dropdown(
                            choices=list(PROVIDERS.keys()),
                            value="Google Gemini",
                            label="Provider (Sağlayıcı)"
                        )
                        
                        multi_model_dropdown = gr.Dropdown(
                            choices=PROVIDERS["Google Gemini"]["models"],
                            value="gemini/gemini-2.0-flash",
                            label="Model"
                        )
                    
                    multi_api_choice = gr.Radio(
                        choices=["Varsayılan API Kullan", "Kendi API Anahtarımı Gireceğim"],
                        value="Varsayılan API Kullan",
                        label="API Seçeneği"
                    )
                    
                    multi_api_key_input = gr.Textbox(
                        label="API Anahtarı", 
                        placeholder="Seçilen provider için API anahtarınızı buraya girin",
                        visible=False,
                        type="password"
                    )
                    
                    multi_run_btn = gr.Button("Görevleri Başlat", variant="primary")
                    
                with gr.Column():
                    multi_output = gr.Markdown(label="Sonuçlar")
                    multi_download_files = gr.File(label="Sonuçları İndir", file_count="multiple")
            
            # Provider değiştiğinde model listesini güncelle (çoklu görev için)
            multi_provider_dropdown.change(
                fn=update_model_list,
                inputs=multi_provider_dropdown,
                outputs=multi_model_dropdown
            )
            
            # API seçimi değiştiğinde API giriş kutusunu göster/gizle (çoklu görev için)
            multi_api_choice.change(
                fn=on_api_choice_change, 
                inputs=multi_api_choice, 
                outputs=multi_api_key_input
            )
            
            # Provider değiştiğinde API anahtarı etiketi ve placeholder metni güncelle (çoklu görev için)
            multi_provider_dropdown.change(
                fn=update_api_key_input,
                inputs=[multi_provider_dropdown, multi_api_choice],
                outputs=multi_api_key_input
            )
            
            # Çoklu görev çalıştırma
            def run_multiple_tasks(tasks_text, steps, provider, model, api_choice, api_key_input):
                tasks = [t.strip() for t in tasks_text.strip().split('\n') if t.strip()]
                
                if not tasks:
                    return "❌ Lütfen en az bir görev girin!", []
                
                api_key = None
                if api_choice == "Kendi API Anahtarımı Gireceğim" and api_key_input and api_key_input.strip():
                    api_key = api_key_input.strip()
                
                results = []
                all_files = []
                
                for i, task in enumerate(tasks):
                    try:
                        result_header = f"## 🔄 Görev {i+1}/{len(tasks)}: {task}\n\n"
                        result_text, file_paths = run_notte_agent(task, model, int(steps), provider, api_key)
                        results.append(result_header + result_text)
                        all_files.extend(file_paths)
                    except Exception as e:
                        results.append(f"## 🔄 Görev {i+1}/{len(tasks)}: {task}\n\n❌ Hata: {str(e)}")
                
                return "\n\n---\n\n".join(results), all_files
            
            multi_run_btn.click(
                fn=run_multiple_tasks, 
                inputs=[
                    tasks_input, 
                    multi_max_steps, 
                    multi_provider_dropdown,
                    multi_model_dropdown, 
                    multi_api_choice, 
                    multi_api_key_input
                ], 
                outputs=[multi_output, multi_download_files]
            )
        
        with gr.Tab("API Ayarları"):
            gr.Markdown("""
            # API Anahtarları Ayarları

            Her sağlayıcı (provider) için API anahtarlarınızı buraya girebilirsiniz. 
            Girilen anahtarlar sadece bu oturum boyunca saklanır ve tarayıcınızı kapattığınızda silinir.
            
            ## Nasıl API Anahtarı Alabilirim?
            
            - **Google Gemini API:** [Google AI Studio](https://ai.google.dev/)
            - **OpenAI API:** [OpenAI Platform](https://platform.openai.com/)
            - **OpenRouter API:** [OpenRouter](https://openrouter.ai/)
            - **Groq API:** [Groq](https://console.groq.com/)
            """)
            
            with gr.Row():
                with gr.Column():
                    gemini_api_key = gr.Textbox(
                        label="Google Gemini API Anahtarı",
                        type="password",
                        value=DEFAULT_GEMINI_API_KEY
                    )
                    
                    openai_api_key = gr.Textbox(
                        label="OpenAI API Anahtarı",
                        type="password",
                        value=DEFAULT_OPENAI_API_KEY
                    )
                    
                with gr.Column():
                    openrouter_api_key = gr.Textbox(
                        label="OpenRouter API Anahtarı",
                        type="password",
                        value=DEFAULT_OPENROUTER_API_KEY
                    )
                    
                    groq_api_key = gr.Textbox(
                        label="Groq API Anahtarı",
                        type="password",
                        value=DEFAULT_GROQ_API_KEY
                    )
                    
                    cerebras_api_key = gr.Textbox(
                        label="Cerebras API Anahtarı",
                        type="password",
                        value=""
                    )
            
            save_api_btn = gr.Button("API Anahtarlarını Kaydet", variant="primary")
            api_status = gr.Markdown("")
            
            def save_api_keys(gemini, openai, openrouter, groq, cerebras):
                global DEFAULT_GEMINI_API_KEY, DEFAULT_OPENAI_API_KEY, DEFAULT_OPENROUTER_API_KEY, DEFAULT_GROQ_API_KEY
                
                # API anahtarlarını güncelle
                if gemini.strip():
                    DEFAULT_GEMINI_API_KEY = gemini.strip()
                    os.environ["GEMINI_API_KEY"] = DEFAULT_GEMINI_API_KEY
                    PROVIDERS["Google Gemini"]["default_key"] = DEFAULT_GEMINI_API_KEY
                
                if openai.strip():
                    DEFAULT_OPENAI_API_KEY = openai.strip()
                    os.environ["OPENAI_API_KEY"] = DEFAULT_OPENAI_API_KEY
                    PROVIDERS["OpenAI"]["default_key"] = DEFAULT_OPENAI_API_KEY
                
                if openrouter.strip():
                    DEFAULT_OPENROUTER_API_KEY = openrouter.strip()
                    os.environ["OPENROUTER_API_KEY"] = DEFAULT_OPENROUTER_API_KEY
                    PROVIDERS["OpenRouter"]["default_key"] = DEFAULT_OPENROUTER_API_KEY
                
                if groq.strip():
                    DEFAULT_GROQ_API_KEY = groq.strip()
                    os.environ["GROQ_API_KEY"] = DEFAULT_GROQ_API_KEY
                    PROVIDERS["Groq"]["default_key"] = DEFAULT_GROQ_API_KEY
                
                if cerebras.strip():
                    os.environ["CEREBRAS_API_KEY"] = cerebras.strip()
                    PROVIDERS["Cerebras"]["default_key"] = cerebras.strip()
                
                return "✅ API anahtarları başarıyla kaydedildi!"
            
            save_api_btn.click(
                fn=save_api_keys,
                inputs=[gemini_api_key, openai_api_key, openrouter_api_key, groq_api_key, cerebras_api_key],
                outputs=api_status
            )
        
        gr.Markdown("""
        ### 📝 Örnek Görevler:
        
        - Search for the latest news about AI and summarize the top story
        - Find information about the Mediterranean diet and list its main benefits
        - What is the current weather in Tokyo?
        - Find the highest rated Italian restaurants in Paris
        - Search for upcoming technology conferences in 2023
        
        ### 📋 Notlar:
        
        - Her görevin tamamlanması 20-60 saniye sürebilir
        - Maksimum adım sayısı, ajanın görev için kullanabileceği maksimum adım sayısını belirler
        - Daha karmaşık görevler için adım sayısını artırabilirsiniz
        - Sonuçlar TXT, MD ve JSON formatlarında indirilebilir
        - Farklı model sağlayıcılar için uygun API anahtarlarını girmeniz gerekebilir
        """)
    
    return app

# Uygulamayı oluştur ve başlat
if __name__ == "__main__":
    # Gradio'yu kurmak için önce pip install gradio yapmalısınız
    try:
        app = create_gradio_interface()
        app.launch(share=True)
    except ImportError:
        print("❌ Gradio kütüphanesi bulunamadı!")
        print("Lütfen şu komutu çalıştırarak Gradio'yu yükleyin:")
        print("pip install gradio")
        print("\nYükledikten sonra bu scripti tekrar çalıştırın.") 