# Use stable Debian 12 image (important)
FROM python:3.11-slim-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# -------------------------------
# 1️⃣ Basic system dependencies
# -------------------------------
RUN apt-get update -o Acquire::Retries=5 \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg2 \
    apt-transport-https \
    software-properties-common \
 && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 2️⃣ OCR + ODBC dependencies
# -------------------------------
RUN apt-get update -o Acquire::Retries=5 \
 && apt-get install -y --no-install-recommends \
    unixodbc \
    libodbc1 \
    libgssapi-krb5-2 \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 3️⃣ Microsoft SQL ODBC Driver
# -------------------------------
RUN curl https://packages.microsoft.com/keys/microsoft.asc \
 | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update -o Acquire::Retries=5 \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
 && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 4️⃣ Python dependencies
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# 5️⃣ Copy project files
# -------------------------------
COPY . .

# -------------------------------
# 6️⃣ Start FastAPI (your path is correct)
# -------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
