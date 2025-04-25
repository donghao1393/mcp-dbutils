# دليل التثبيت الخاص بالمنصات

*[English](../en/installation-platform-specific.md) | [中文](../zh/installation-platform-specific.md) | [Français](../fr/installation-platform-specific.md) | [Español](../es/installation-platform-specific.md) | العربية | [Русский](../ru/installation-platform-specific.md)*

يوفر هذا المستند تعليمات تثبيت مفصلة لـ MCP Database Utilities على أنظمة تشغيل وبيئات مختلفة.

## التثبيت على نظام Windows

### المتطلبات الأساسية

- Python 3.10 أو أحدث
- صلاحيات المسؤول (لبعض الخطوات)
- اتصال بالإنترنت (لتنزيل الحزم)

### تثبيت Python

1. قم بتنزيل Python من [python.org](https://www.python.org/downloads/windows/)
2. قم بتشغيل المثبت وتأكد من تحديد خيار "Add Python to PATH"
3. تحقق من التثبيت بفتح موجه الأوامر وكتابة:
   ```
   python --version
   ```

### تثبيت uv

1. افتح PowerShell كمسؤول
2. قم بتنفيذ الأمر التالي:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. تحقق من التثبيت:
   ```
   uv --version
   ```

### تثبيت MCP Database Utilities

#### الخيار 1: التثبيت باستخدام uvx (موصى به)

```powershell
# لا يلزم تثبيت مسبق
# يتعامل uvx مع كل شيء تلقائيًا
```

قم بإعداد عميل الذكاء الاصطناعي الخاص بك لاستخدام:
```
uvx mcp-dbutils --config C:\path\to\config.yaml
```

#### الخيار 2: التثبيت التقليدي

```powershell
# إنشاء بيئة افتراضية (اختياري ولكن موصى به)
python -m venv venv
.\venv\Scripts\activate

# التثبيت باستخدام uv
uv pip install mcp-dbutils
```

#### الخيار 3: التثبيت باستخدام Smithery

```powershell
# تأكد من تثبيت Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## التثبيت على نظام macOS

### المتطلبات الأساسية

- Python 3.10 أو أحدث
- Homebrew (موصى به)
- اتصال بالإنترنت (لتنزيل الحزم)

### تثبيت Python

1. قم بتثبيت Homebrew إذا لم يكن مثبتًا بالفعل:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. قم بتثبيت Python:
   ```bash
   brew install python@3.10
   ```

3. تحقق من التثبيت:
   ```bash
   python3 --version
   ```

### تثبيت uv

1. افتح Terminal
2. قم بتنفيذ الأمر التالي:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. تحقق من التثبيت:
   ```bash
   uv --version
   ```

### تثبيت MCP Database Utilities

#### الخيار 1: التثبيت باستخدام uvx (موصى به)

```bash
# لا يلزم تثبيت مسبق
# يتعامل uvx مع كل شيء تلقائيًا
```

قم بإعداد عميل الذكاء الاصطناعي الخاص بك لاستخدام:
```
uvx mcp-dbutils --config /path/to/config.yaml
```

#### الخيار 2: التثبيت التقليدي

```bash
# إنشاء بيئة افتراضية (اختياري ولكن موصى به)
python3 -m venv venv
source venv/bin/activate

# التثبيت باستخدام uv
uv pip install mcp-dbutils
```

#### الخيار 3: التثبيت باستخدام Smithery

```bash
# تأكد من تثبيت Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## التثبيت على نظام Linux

### المتطلبات الأساسية

- Python 3.10 أو أحدث
- صلاحيات sudo (لبعض الخطوات)
- اتصال بالإنترنت (لتنزيل الحزم)

### تثبيت Python

#### على Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

#### على Fedora:

```bash
sudo dnf install python3.10 python3.10-devel
```

#### على Arch Linux:

```bash
sudo pacman -S python
```

### تثبيت uv

1. افتح Terminal
2. قم بتنفيذ الأمر التالي:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. تحقق من التثبيت:
   ```bash
   uv --version
   ```

### تثبيت MCP Database Utilities

#### الخيار 1: التثبيت باستخدام uvx (موصى به)

```bash
# لا يلزم تثبيت مسبق
# يتعامل uvx مع كل شيء تلقائيًا
```

قم بإعداد عميل الذكاء الاصطناعي الخاص بك لاستخدام:
```
uvx mcp-dbutils --config /path/to/config.yaml
```

#### الخيار 2: التثبيت التقليدي

```bash
# إنشاء بيئة افتراضية (اختياري ولكن موصى به)
python3 -m venv venv
source venv/bin/activate

# التثبيت باستخدام uv
uv pip install mcp-dbutils
```

#### الخيار 3: التثبيت باستخدام Smithery

```bash
# تأكد من تثبيت Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## التثبيت في حاوية Docker

### المتطلبات الأساسية

- Docker مثبت ويعمل
- اتصال بالإنترنت (لتنزيل صورة Docker)

### استخدام صورة Docker الرسمية

1. قم بسحب صورة Docker:
   ```bash
   docker pull mcp/dbutils
   ```

2. قم بتشغيل الحاوية مع ملف التكوين الخاص بك:
   ```bash
   docker run -i --rm -v /path/to/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml
   ```

### إنشاء صورة Docker مخصصة

إذا كنت بحاجة إلى تخصيص صورة Docker، يمكنك إنشاء Dockerfile الخاص بك:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp-dbutils

ENTRYPOINT ["mcp-dbutils"]
CMD ["--help"]
```

قم ببناء وتشغيل صورتك المخصصة:

```bash
docker build -t custom-mcp-dbutils .
docker run -i --rm -v /path/to/config.yaml:/app/config.yaml custom-mcp-dbutils --config /app/config.yaml
```

## التثبيت بدون اتصال بالإنترنت

للبيئات التي لا تتوفر فيها إمكانية الوصول إلى الإنترنت، يمكنك تحضير تثبيت بدون اتصال:

### الخطوة 1: تنزيل الحزم (على جهاز متصل بالإنترنت)

```bash
# إنشاء دليل للحزم
mkdir mcp-dbutils-offline
cd mcp-dbutils-offline

# تنزيل الحزم مع التبعيات
uv pip download mcp-dbutils -d ./packages
```

### الخطوة 2: نقل إلى الجهاز غير المتصل بالإنترنت

قم بنقل دليل `mcp-dbutils-offline` إلى الجهاز غير المتصل بالإنترنت باستخدام محرك أقراص USB أو وسيلة أخرى.

### الخطوة 3: التثبيت على الجهاز غير المتصل بالإنترنت

```bash
# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate  # على Linux/macOS
# أو
.\venv\Scripts\activate  # على Windows

# التثبيت من الحزم المنزلة
uv pip install --no-index --find-links=./packages mcp-dbutils
```

## استكشاف الأخطاء وإصلاحها

### المشكلة: "Command not found" بعد التثبيت

**الحل**:
- تأكد من أن دليل التثبيت موجود في PATH الخاص بك
- على Windows، حاول إعادة تشغيل موجه الأوامر أو PowerShell
- على Linux/macOS، قم بتنفيذ `source ~/.bashrc` أو `source ~/.zshrc`

### المشكلة: أخطاء في التبعيات

**الحل**:
- تأكد من أن لديك Python 3.10 أو أحدث
- حاول التثبيت مع `--verbose` لرؤية الأخطاء المفصلة:
  ```
  uv pip install --verbose mcp-dbutils
  ```

### المشكلة: أخطاء في الصلاحيات

**الحل**:
- على Windows، قم بتشغيل PowerShell كمسؤول
- على Linux/macOS، استخدم `sudo` إذا لزم الأمر أو قم بالتثبيت في بيئة افتراضية

### المشكلة: أخطاء مع Docker

**الحل**:
- تحقق من أن Docker قيد التشغيل: `docker info`
- تأكد من أن مسارات التثبيت صحيحة ويمكن الوصول إليها
- على Linux، قد تحتاج إلى إضافة المستخدم الخاص بك إلى مجموعة docker:
  ```
  sudo usermod -aG docker $USER
  ```
  (قم بتسجيل الخروج وإعادة تسجيل الدخول لتطبيق التغييرات)

## موارد إضافية

- [توثيق Python](https://docs.python.org/)
- [توثيق Docker](https://docs.docker.com/)
- [توثيق uv](https://github.com/astral-sh/uv)
- [توثيق Smithery](https://smithery.ai/docs)
