
## Структура проекта

```
prompt_enrichment_pipeline/
│
├── config/
│   ├── models.yaml          # Конфиг моделей (какая модель для какой задачи)
│   ├── domains.yaml         # Конфиг доменов (kernel, web, data и т.д.)
│   └── prompts/             # Шаблоны промптов для каждого этапа
│       ├── classifier.txt
│       ├── rewriter.txt
│       └── executor.txt
│
├── core/
│   ├── __init__.py
│   ├── classifier.py        # Модуль классификации запросов
│   ├── context_retriever.py # Модуль сбора контекста
│   ├── rewriter.py          # Модуль переписывания промптов
│   └── executor.py          # Модуль выполнения обогащённых промптов
│
├── utils/
│   ├── __init__.py
│   ├── model_loader.py      # Загрузка и кэширование моделей
│   ├── file_parser.py       # Парсинг кода (tree-sitter)
│   ├── vector_store.py      # Векторный поиск (chromadb)
│   └── prompt_builder.py    # Сборка финального промпта
│
├── adapters/
│   ├── __init__.py
│   ├── ollama_adapter.py    # Адаптер для Ollama
│   ├── vllm_adapter.py      # Адаптер для vLLM
│   └── llamacpp_adapter.py  # Адаптер для llama.cpp
│
├── main.py                  # Точка входа (CLI)
└── requirements.txt
```

## Детальная структура каждого модуля

### 1. `core/classifier.py`

**Задача:** Определить тип запроса и домен.

**Интерфейс:**
```python
class RequestClassifier:
    def __init__(self, model_adapter, config_path: str)
    
    def classify(self, user_input: str) -> ClassificationResult
    
    # ClassificationResult - это dataclass:
    # - domain: str (kernel|web|data|devops|general)
    # - task_type: str (implement|debug|refactor|explain|review)
    # - keywords: list[str]
    # - required_expertise: list[str]
    # - complexity: str (simple|medium|complex)
```

**Зависимости:**
- `adapters/ollama_adapter.py` (для маленькой модели типа Qwen2.5-1.5B)
- `config/domains.yaml` (описание доменов)
- `config/prompts/classifier.txt` (шаблон промпта для классификации)

**Логика:**
1. Загружает шаблон промпта из `config/prompts/classifier.txt`
2. Подставляет `user_input` в шаблон
3. Отправляет в маленькую модель через `model_adapter`
4. Парсит JSON-ответ в `ClassificationResult`

---

### 2. `core/context_retriever.py`

**Задача:** Собрать релевантный контекст из кодовой базы.

**Интерфейс:**
```python
class ContextRetriever:
    def __init__(self, project_root: str, vector_store: VectorStore)
    
    def retrieve(self, keywords: list[str], domain: str, max_tokens: int = 8000) -> str
    
    # Возвращает строку с контекстом, готовую для вставки в промпт
```

**Зависимости:**
- `utils/file_parser.py` (парсинг кода через tree-sitter)
- `utils/vector_store.py` (векторный поиск через chromadb)
- `config/domains.yaml` (специфичный контекст для каждого домена)

**Логика:**
1. Ищет файлы по `keywords` через `file_parser`
2. Делает векторный поиск по `keywords` через `vector_store`
3. Добавляет домен-специфичный контекст (например, для kernel — спецификации x86)
4. Обрезает до `max_tokens`
5. Возвращает отформатированную строку

---

### 3. `core/rewriter.py`

**Задача:** Превратить простой запрос в role-based промпт.

**Интерфейс:**
```python
class PromptRewriter:
    def __init__(self, model_adapter, config_path: str)
    
    def rewrite(self, user_input: str, classification: ClassificationResult, context: str) -> str
    
    # Возвращает готовый промпт для executor
```

**Зависимости:**
- `adapters/ollama_adapter.py` (для маленькой модели)
- `config/prompts/rewriter.txt` (шаблон промпта)
- `utils/prompt_builder.py` (сборка финального промпта)

**Логика:**
1. Загружает шаблон из `config/prompts/rewriter.txt`
2. Подставляет `user_input`, `classification`, `context`
3. Отправляет в маленькую модель
4. Возвращает переписанный промпт

---

### 4. `core/executor.py`

**Задача:** Выполнить обогащённый промпт на большой модели.

**Интерфейс:**
```python
class PromptExecutor:
    def __init__(self, model_adapter, config_path: str)
    
    def execute(self, rewritten_prompt: str) -> str
    
    # Возвращает ответ модели
```

**Зависимости:**
- `adapters/vllm_adapter.py` или `adapters/llamacpp_adapter.py` (для большой модели)
- `config/prompts/executor.txt` (шаблон промпта, если нужен)

**Логика:**
1. Отправляет `rewritten_prompt` в большую модель
2. Возвращает ответ

---

### 5. `utils/model_loader.py`

**Задача:** Загружать и кэшировать модели.

**Интерфейс:**
```python
class ModelLoader:
    def __init__(self, config_path: str)
    
    def get_model(self, model_name: str) -> Any
    def get_tokenizer(self, model_name: str) -> Any
    
    # Кэширует загруженные модели
```

**Зависимости:**
- `transformers` (для загрузки моделей)
- `config/models.yaml` (конфиг моделей)

---

### 6. `utils/file_parser.py`

**Задача:** Парсить код и извлекать структуры (функции, классы, импорты).

**Интерфейс:**
```python
class FileParser:
    def __init__(self, language: str = "python")
    
    def parse_file(self, file_path: str) -> FileStructure
    def search_by_keyword(self, keyword: str, files: list[str]) -> list[CodeSnippet]
    
    # FileStructure - dataclass с информацией о файле
    # CodeSnippet - dataclass с фрагментом кода
```

**Зависимости:**
- `tree-sitter` (парсинг кода)
- `tree-sitter-languages` (поддержка разных языков)

---

### 7. `utils/vector_store.py`

**Задача:** Векторный поиск по кодовой базе.

**Интерфейс:**
```python
class VectorStore:
    def __init__(self, collection_name: str)
    
    def index_files(self, files: list[str])
    def search(self, query: str, top_k: int = 5) -> list[CodeSnippet]
```

**Зависимости:**
- `chromadb` (векторная БД)
- `sentence-transformers` (эмбеддинги)

---

### 8. `adapters/ollama_adapter.py`

**Задача:** Обёртка над Ollama API.

**Интерфейс:**
```python
class OllamaAdapter:
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str
```

**Зависимости:**
- `requests` (HTTP-запросы к Ollama)

---

### 9. `adapters/vllm_adapter.py`

**Задача:** Обёртка над vLLM API.

**Интерфейс:**
```python
class VLLMAdapter:
    def __init__(self, model_name: str, base_url: str = "http://localhost:8000")
    
    def generate(self, prompt: str, max_tokens: int = 2048) -> str
```

**Зависимости:**
- `requests` (HTTP-запросы к vLLM)

---

### 10. `main.py`

**Задача:** Точка входа, CLI.

**Интерфейс:**
```python
def main():
    # 1. Парсит аргументы командной строки
    # 2. Инициализирует все модули
    # 3. Запускает pipeline:
    #    - classifier.classify()
    #    - context_retriever.retrieve()
    #    - rewriter.rewrite()
    #    - executor.execute()
    # 4. Выводит результат
```

**Зависимости:**
- `argparse` или `click` (CLI)
- Все модули из `core/`

---

## Поток данных через систему

```
1. main.py получает user_input
   ↓
2. classifier.classify(user_input) → ClassificationResult
   ↓
3. context_retriever.retrieve(keywords, domain) → context
   ↓
4. rewriter.rewrite(user_input, classification, context) → rewritten_prompt
   ↓
5. executor.execute(rewritten_prompt) → final_answer
   ↓
6. main.py выводит final_answer
```

## Конфигурационные файлы

### `config/models.yaml`
```yaml
classifier:
  model: "qwen2.5-1.5b-instruct"
  adapter: "ollama"
  temperature: 0.3

rewriter:
  model: "qwen2.5-7b-instruct"
  adapter: "ollama"
  temperature: 0.5

executor:
  model: "qwen2.5-72b-instruct"
  adapter: "vllm"
  temperature: 0.7
  max_tokens: 4096
```

### `config/domains.yaml`
```yaml
kernel:
  description: "Kernel development, bare-metal programming"
  expertise: ["x86 assembly", "C99", "hardware interfaces"]
  context_files:
    - "docs/x86_spec.md"
    - "docs/multiboot.md"

web:
  description: "Web development, frontend, backend"
  expertise: ["JavaScript", "Python", "HTML/CSS"]
  context_files:
    - "docs/react_patterns.md"
    - "docs/django_best_practices.md"
```

---

## Зависимости (`requirements.txt`)

```
transformers>=4.40.0
torch>=2.2.0
tree-sitter>=0.21.0
tree-sitter-languages>=1.10.0
chromadb>=0.5.0
sentence-transformers>=2.6.0
requests>=2.31.0
pyyaml>=6.0.1
click>=8.1.7
```

