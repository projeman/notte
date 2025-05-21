# Notte AI Agent Dockerfile
FROM python:3.11-slim

# Sistem bağımlılıklarını yükle (ör: Chromium için)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        chromium-driver \
        chromium \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Proje dosyalarını kopyala
COPY . .

# pip ve pipx güncelle
RUN pip install --upgrade pip pipx

# pyproject.toml ile bağımlılıkları kur
RUN pip install --no-cache-dir .

# Gradio bağımlılığını ayrıca kur (eğer pyproject.toml'da yoksa)
RUN pip install --no-cache-dir gradio

# Ortam değişkenleri (gerekirse dışarıdan override edilebilir)
ENV GEMINI_API_KEY=""
ENV OPENAI_API_KEY=""
ENV OPENROUTER_API_KEY=""
ENV GROQ_API_KEY=""
ENV CEREBRAS_API_KEY=""

# 7860 portunu aç (Gradio default)
EXPOSE 7860

# Uygulamayı başlat
CMD ["python", "notte_gradio_app.py"] 