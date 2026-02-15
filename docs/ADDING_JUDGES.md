# Guia: Adicionando Novas Plataformas (Judges)

Este guia explica como adicionar suporte a novas plataformas de programação competitiva no cptools.

## Índice

- [Introdução](#introdução)
- [Anatomia de um Judge](#anatomia-de-um-judge)
- [Implementações de Referência](#implementações-de-referência)
- [Passo a Passo](#passo-a-passo)
- [Utilitários Disponíveis](#utilitários-disponíveis)
- [Suporte a Autenticação](#suporte-a-autenticação)
- [Tratamento de Erros](#tratamento-de-erros)
- [Checklist de Verificação](#checklist-de-verificação)
- [Exemplos Completos](#exemplos-completos)
- [Troubleshooting](#troubleshooting)

## Introdução

CPTools usa uma arquitetura extensível baseada em classes para suportar diferentes plataformas de programação competitiva. Cada plataforma é implementada como uma classe "Judge" que herda de uma classe base abstrata.

### Quando adicionar um novo judge?

Você deve considerar adicionar um novo judge quando:
- A plataforma possui URLs públicas de problemas
- Os problemas possuem casos de teste de exemplo (inputs/outputs)
- Existe uma API pública ou a página HTML pode ser parseada
- A plataforma é usada por uma comunidade significativa

## Anatomia de um Judge

Todos os judges são implementados em **`lib/judges.py`** e devem herdar da classe base `Judge`.

### Classe Base `Judge`

```python
class Judge(ABC):
    """Base class for online judge platforms."""

    platform_name: str = "Unknown"
    requires_auth: bool = False

    @abstractmethod
    def detect(self, url: str) -> bool:
        """Check if URL belongs to this judge."""
        pass

    def needs_authentication(self, url: str) -> bool:
        """Determine if a specific URL requires authentication."""
        return self.requires_auth or self._is_private_url(url)

    def _is_private_url(self, url: str) -> bool:
        """Override in subclasses to detect private/group URLs."""
        return False

    @abstractmethod
    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """Fetch a single problem's name."""
        pass

    @abstractmethod
    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """Fetch all problems in a contest."""
        pass

    @abstractmethod
    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """Fetch sample test cases from a problem URL."""
        pass
```

### Classes Auxiliares

**`SampleTest`** (dataclass) - Representa um caso de teste:
```python
@dataclass
class SampleTest:
    input: str
    output: str
```

**`ProblemInfo`** (dataclass) - Metadados de um problema:
```python
@dataclass
class ProblemInfo:
    index: str      # Ex: "A", "B", "C1"
    name: str       # Ex: "Theatre Square"
    link: str       # URL do problema
```

### Função Utilitária

**`clean_sample_text(text: str)`** - Limpa HTML de textos de exemplo:
- Remove tags HTML (`<br/>`, `<div>`, etc.)
- Decodifica entidades HTML (`&lt;`, `&gt;`, `&amp;`)
- Remove whitespace excessivo

## Implementações de Referência

CPTools atualmente suporta 6 plataformas. Use-as como referência:

| Plataforma | Padrão | Autenticação | Características |
|------------|--------|--------------|-----------------|
| **Codeforces** | API + HTML parsing | Sim (grupos) | API pública, retry de auth, refresh de sessão |
| **AtCoder** | HTML parsing | Não | Suporte bilíngue (EN/JP), regex para samples |
| **CSES** | HTML parsing | Não | Sem contests tradicionais, estrutura HTML simples |
| **Yosupo** | Minimal | Não | Nomes derivados de slugs, sem samples |
| **SPOJ** | HTML parsing | Não | Multiplos blocos `<pre>`, parsing de código |
| **VJudge** | Não implementado | - | Placeholder para implementação futura |

### Quando usar cada padrão?

- **API-based** (Codeforces): Use quando a plataforma tiver API pública bem documentada
- **HTML parsing** (AtCoder, CSES, SPOJ): Use quando não houver API ou for mais confiável
- **Minimal** (Yosupo): Use para plataformas sem contests ou com estrutura muito simples
- **Com autenticação**: Use quando problemas privados/grupos forem comuns

## Passo a Passo

### Passo 1: Criar a Classe do Judge

Adicione uma nova classe em **`lib/judges.py`**:

```python
class MinhaPlataformaJudge(Judge):
    """Judge para Minha Plataforma."""

    platform_name = "MinhaPlataforma"
    requires_auth = False  # True se sempre precisar de login

    def detect(self, url: str) -> bool:
        """Detecta URLs da plataforma."""
        return 'minhaplataforma.com' in url

    def _is_private_url(self, url: str) -> bool:
        """Detecta URLs privadas (opcional)."""
        # Ex: URLs de grupos/organizações privadas
        return '/private/' in url or '/group/' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """
        Busca o nome de um problema específico.

        Args:
            contest_id: ID do contest (ex: "123")
            problem_id: ID/letra do problema (ex: "A")

        Returns:
            Nome do problema ou None se falhar
        """
        try:
            # Opção 1: Usar API JSON
            url = f"https://minhaplataforma.com/api/contest/{contest_id}/problem/{problem_id}"
            data = fetch_json(url, timeout=10)
            return data.get('name')

            # Opção 2: Parsear HTML
            # url = f"https://minhaplataforma.com/contest/{contest_id}/problem/{problem_id}"
            # html = fetch_url(url, timeout=15)
            # match = re.search(r'<h1 class="problem-title">(.*?)</h1>', html)
            # return match.group(1) if match else None
        except Exception as e:
            # Log ou ignore erros silenciosamente
            return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """
        Busca todos os problemas de um contest.

        Args:
            contest_id: ID do contest

        Returns:
            Dicionário {index: name} ou {} se falhar
        """
        try:
            # Exemplo com API
            url = f"https://minhaplataforma.com/api/contest/{contest_id}/problems"
            data = fetch_json(url, timeout=10)

            # Assumindo formato: {"problems": [{"index": "A", "name": "..."}, ...]}
            return {p['index']: p['name'] for p in data.get('problems', [])}
        except Exception:
            return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """
        Busca casos de teste de exemplo de uma URL.

        Args:
            url: URL completa do problema

        Returns:
            Lista de SampleTest ou None se falhar
        """
        try:
            # Buscar HTML (com auth se necessário)
            if self.needs_authentication(url):
                html = fetch_url_with_auth(url, domain='minhaplataforma.com')
            else:
                html = fetch_url(url, timeout=15)

            return self._parse_samples(html)
        except Exception:
            return None

    def _parse_samples(self, html: str) -> List[SampleTest]:
        """
        Parseia samples do HTML.

        Args:
            html: HTML completo da página

        Returns:
            Lista de SampleTest
        """
        samples = []

        # Exemplo: encontrar pares de <pre> tags
        # Ajuste os padrões regex para a estrutura HTML da sua plataforma

        # Padrão 1: inputs e outputs em tags separadas
        input_pattern = r'<div class="sample-input">.*?<pre>(.*?)</pre>'
        output_pattern = r'<div class="sample-output">.*?<pre>(.*?)</pre>'

        inputs = re.findall(input_pattern, html, re.DOTALL)
        outputs = re.findall(output_pattern, html, re.DOTALL)

        for inp, out in zip(inputs, outputs):
            samples.append(SampleTest(
                input=clean_sample_text(inp),
                output=clean_sample_text(out)
            ))

        return samples
```

### Passo 2: Registrar o Judge

No mesmo arquivo **`lib/judges.py`**, adicione o novo judge à lista **`ALL_JUDGES`** (linha ~520):

```python
ALL_JUDGES: List[Judge] = [
    CodeforcesJudge(),
    AtCoderJudge(),
    CSESJudge(),
    YosupoJudge(),
    SPOJJudge(),
    VJudgeJudge(),
    MinhaPlataformaJudge(),  # ADICIONAR AQUI
]
```

**Nota:** A ordem importa para auto-detecção. Judges mais específicos devem vir antes dos genéricos.

### Passo 3: Adicionar Parsing de URLs

Edite **`lib/parsing.py`** para reconhecer as URLs da plataforma.

#### Em `parse_problem_url()`:

```python
def parse_problem_url(url):
    """Parse problem URL and extract metadata."""

    # ... código existente ...

    # MinhaPlataforma: minhaplataforma.com/contest/123/problem/A
    match = re.search(r'minhaplataforma\.com/contest/(\d+)/problem/([A-Za-z]\d*)', url)
    if match:
        contest_id = match.group(1)
        letter = match.group(2)
        return {
            'platform_dir': 'MinhaPlataforma',
            'contest_id': contest_id,
            'letter': letter,
            'filename': f"{contest_id}{letter}",
            'link': url,
            'fetch_platform': 'minhaplataforma',
        }

    # ... resto do código ...
```

#### Em `parse_contest_url()`:

```python
def parse_contest_url(url):
    """Parse contest URL and extract metadata."""

    # ... código existente ...

    # MinhaPlataforma: minhaplataforma.com/contest/123
    match = re.search(r'minhaplataforma\.com/contest/(\d+)', url)
    if match:
        return {
            'platform': 'MinhaPlataforma',
            'base_url': 'https://minhaplataforma.com/contest/{id}/problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    # ... resto do código ...
```

### Passo 4: Atualizar Exports

Edite **`lib/__init__.py`** para exportar o novo judge:

```python
from .judges import (
    ProblemInfo,
    SampleTest,
    Judge,
    CodeforcesJudge,
    AtCoderJudge,
    CSESJudge,
    YosupoJudge,
    SPOJJudge,
    VJudgeJudge,
    MinhaPlataformaJudge,  # ADICIONAR
    ALL_JUDGES,
    detect_judge,
)

# E no __all__:
__all__ = [
    # ... outros exports ...
    'MinhaPlataformaJudge',  # ADICIONAR
    # ... resto ...
]
```

### Passo 5: Escrever Testes

Adicione testes em **`tests/test_judges.py`**:

```python
class TestMinhaPlataformaJudge:
    """Testes para MinhaPlataformaJudge."""

    def setup_method(self):
        self.judge = MinhaPlataformaJudge()

    def test_detect(self):
        """Testa detecção de URLs."""
        assert self.judge.detect("https://minhaplataforma.com/contest/123/problem/A")
        assert self.judge.detect("https://minhaplataforma.com/contest/456")
        assert not self.judge.detect("https://codeforces.com/contest/123")

    def test_platform_name(self):
        """Testa nome da plataforma."""
        assert self.judge.platform_name == "MinhaPlataforma"

    def test_fetch_problem_name(self):
        """Testa busca de nome de problema."""
        mock_response = {"name": "Problema Teste"}

        with patch('lib.judges.fetch_json', return_value=mock_response):
            name = self.judge.fetch_problem_name("123", "A")
            assert name == "Problema Teste"

    def test_fetch_contest_problems(self):
        """Testa busca de problemas de um contest."""
        mock_response = {
            "problems": [
                {"index": "A", "name": "Problema A"},
                {"index": "B", "name": "Problema B"},
            ]
        }

        with patch('lib.judges.fetch_json', return_value=mock_response):
            problems = self.judge.fetch_contest_problems("123")
            assert problems == {"A": "Problema A", "B": "Problema B"}

    def test_fetch_samples(self):
        """Testa busca de samples."""
        html = '''
        <div class="sample-input"><pre>1 2</pre></div>
        <div class="sample-output"><pre>3</pre></div>
        <div class="sample-input"><pre>3 4</pre></div>
        <div class="sample-output"><pre>7</pre></div>
        '''

        with patch('lib.judges.fetch_url', return_value=html):
            samples = self.judge.fetch_samples("https://minhaplataforma.com/contest/123/problem/A")
            assert len(samples) == 2
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"
            assert samples[1].input == "3 4"
            assert samples[1].output == "7"

    def test_fetch_samples_returns_none_on_error(self):
        """Testa que retorna None em caso de erro."""
        with patch('lib.judges.fetch_url', side_effect=Exception("Network error")):
            samples = self.judge.fetch_samples("https://minhaplataforma.com/contest/123/problem/A")
            assert samples is None
```

#### Adicionar teste de detecção global

Na classe `TestDetectJudge`:

```python
def test_detect_minhaplataforma(self):
    judge = detect_judge("https://minhaplataforma.com/contest/123")
    assert isinstance(judge, MinhaPlataformaJudge)
```

### Passo 6: Rodar Testes

Execute a suite de testes para garantir que tudo funciona:

```bash
# Testar apenas judges
pytest tests/test_judges.py -v

# Testar parsing de URLs
pytest tests/test_parsing.py -v

# Testar integração com comandos
pytest tests/test_cmd_fetch.py -v
pytest tests/test_cmd_add.py -v
pytest tests/test_cmd_new.py -v

# Rodar todos os testes
pytest tests/ -v
```

### Passo 7: Atualizar Documentação

#### **README.md**

Adicione a plataforma na lista de suportadas (linha ~5):

```markdown
Supports Codeforces, AtCoder, CSES, Yosupo, SPOJ, vJudge, MinhaPlataforma, and custom judges.
```

#### **docs/COMMANDS.md**

Adicione exemplos de URLs da nova plataforma nos comandos relevantes:

```markdown
## fetch

Fetch sample test cases from a problem URL.

### Examples

# ... exemplos existentes ...

cptools fetch https://minhaplataforma.com/contest/123/problem/A
```

## Utilitários Disponíveis

CPTools fornece várias funções utilitárias em **`lib/http_utils.py`**:

### `fetch_url(url, timeout=15, headers=None, cookies=None)`

Busca HTML de uma URL.

```python
html = fetch_url("https://example.com/problem/123", timeout=15)
```

### `fetch_json(url, timeout=10)`

Busca e parseia JSON de uma API.

```python
data = fetch_json("https://api.example.com/problems", timeout=10)
```

### `fetch_url_with_auth(url, domain, force_refresh=False)`

Busca URL usando cookies do navegador (para autenticação).

```python
html = fetch_url_with_auth("https://example.com/private/123", domain='example.com')
```

### `clean_sample_text(text)`

Limpa HTML de textos de exemplo (**`lib/judges.py`**):

```python
raw = "<div>1 2<br/>3 4</div>"
clean = clean_sample_text(raw)  # "1 2\n3 4"
```

## Suporte a Autenticação

### Quando é necessário?

Autenticação é necessária quando:
- Problemas privados ou de grupos exigem login
- A plataforma bloqueia scraping sem cookies
- Contests não-públicos precisam de credenciais

### Como implementar?

#### 1. Definir `requires_auth`

```python
class MinhaPlataformaJudge(Judge):
    platform_name = "MinhaPlataforma"
    requires_auth = True  # SEMPRE precisa de auth
```

#### 2. Implementar `_is_private_url()`

Para detectar URLs específicas que precisam de auth:

```python
def _is_private_url(self, url: str) -> bool:
    """Detecta URLs privadas."""
    return '/group/' in url or '/private/' in url
```

#### 3. Usar `fetch_url_with_auth()` em `fetch_samples()`

```python
def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
    try:
        if self.needs_authentication(url):
            html = fetch_url_with_auth(url, domain='minhaplataforma.com')
        else:
            html = fetch_url(url, timeout=15)

        return self._parse_samples(html)
    except Exception:
        return None
```

### Padrão de Retry com Autenticação

Para plataformas onde sessões podem expirar (como Codeforces):

```python
def _fetch_with_auth_retry(self, url: str, force_refresh: bool = False) -> str:
    """Busca com retry automático se sessão expirar."""
    html = fetch_url_with_auth(url, domain='minhaplataforma.com', force_refresh=force_refresh)

    # Detectar indicador de login
    if 'login-required' in html or 'sign-in' in html.lower():
        if not force_refresh:
            # Tentar novamente com cookies atualizados
            return self._fetch_with_auth_retry(url, force_refresh=True)
        else:
            raise PlatformError("Authentication failed. Please login in your browser.")

    return html
```

## Tratamento de Erros

### Quando lançar exceções?

Use `PlatformError` para erros específicos da plataforma:

```python
from .exceptions import PlatformError

if not logged_in:
    raise PlatformError("Login required. Please authenticate in your browser.")
```

### Quando retornar `None`?

Retorne `None` para falhas não-críticas:

```python
def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
    try:
        # ... tentar buscar ...
    except Exception:
        # Falha silenciosa - outros métodos podem tentar
        return None
```

### Mensagens Amigáveis

Sempre forneça contexto ao usuário:

```python
raise PlatformError(
    f"Failed to fetch problem {problem_id} from contest {contest_id}. "
    "Check if the contest exists and is public."
)
```

## Checklist de Verificação

Antes de submeter seu código, verifique:

- [ ] **Classe implementada** com todos os métodos abstratos
- [ ] **`platform_name`** definido corretamente
- [ ] **Registrado em `ALL_JUDGES`** (lib/judges.py)
- [ ] **URL parsing adicionado** para problemas e contests (lib/parsing.py)
- [ ] **Exports atualizados** (lib/__init__.py)
- [ ] **Testes escritos** (mínimo: detect, fetch_problem_name, fetch_samples)
- [ ] **Todos os testes passando**: `pytest tests/test_judges.py -v`
- [ ] **Parsing de URLs testado**: `pytest tests/test_parsing.py -v`
- [ ] **README.md atualizado** com nome da plataforma
- [ ] **COMMANDS.md atualizado** com exemplos de URLs
- [ ] **Código segue PEP 8** e estilo do projeto
- [ ] **Autenticação implementada** (se necessário)
- [ ] **Erros tratados adequadamente**

## Exemplos Completos

### Exemplo 1: Judge Simples (HTML Parsing, Sem Contests)

```python
class SimpleJudge(Judge):
    """Judge simples para plataforma sem contests."""

    platform_name = "Simple"
    requires_auth = False

    def detect(self, url: str) -> bool:
        return 'simple.com' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        # Extrair do slug da URL
        return problem_id.replace('-', ' ').title()

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        # Sem contests - retornar vazio
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        try:
            html = fetch_url(url, timeout=15)
            return self._parse_samples(html)
        except Exception:
            return None

    def _parse_samples(self, html: str) -> List[SampleTest]:
        samples = []
        # Padrão: <h3>Input</h3><pre>...</pre><h3>Output</h3><pre>...</pre>
        pattern = r'<h3>Input</h3>\s*<pre>(.*?)</pre>\s*<h3>Output</h3>\s*<pre>(.*?)</pre>'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

        for inp, out in matches:
            samples.append(SampleTest(
                input=clean_sample_text(inp),
                output=clean_sample_text(out)
            ))
        return samples
```

### Exemplo 2: Judge com API

```python
class APIJudge(Judge):
    """Judge que usa API pública."""

    platform_name = "APIJudge"
    requires_auth = False

    BASE_API = "https://api.apijudge.com/v1"

    def detect(self, url: str) -> bool:
        return 'apijudge.com' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        try:
            url = f"{self.BASE_API}/contests/{contest_id}/problems/{problem_id}"
            data = fetch_json(url, timeout=10)
            return data.get('title')
        except Exception:
            return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        try:
            url = f"{self.BASE_API}/contests/{contest_id}"
            data = fetch_json(url, timeout=10)
            return {p['code']: p['title'] for p in data.get('problems', [])}
        except Exception:
            return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        try:
            # Extrair contest_id e problem_id da URL
            match = re.search(r'/contests/(\d+)/problems/([A-Z])', url)
            if not match:
                return None

            contest_id, problem_id = match.groups()
            api_url = f"{self.BASE_API}/contests/{contest_id}/problems/{problem_id}/samples"
            data = fetch_json(api_url, timeout=10)

            return [
                SampleTest(input=s['input'], output=s['output'])
                for s in data.get('samples', [])
            ]
        except Exception:
            return None
```

### Exemplo 3: Judge com Autenticação

```python
class PrivateJudge(Judge):
    """Judge com suporte a problemas privados."""

    platform_name = "PrivateJudge"
    requires_auth = False  # Nem todos os problemas precisam

    def detect(self, url: str) -> bool:
        return 'privatejudge.com' in url

    def _is_private_url(self, url: str) -> bool:
        """Detecta URLs que precisam de auth."""
        return '/private/' in url or '/organization/' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        try:
            url = f"https://privatejudge.com/contest/{contest_id}/problem/{problem_id}"
            html = fetch_url(url, timeout=15)
            match = re.search(r'<h1>(.*?)</h1>', html)
            return match.group(1) if match else None
        except Exception:
            return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        try:
            url = f"https://privatejudge.com/api/contest/{contest_id}"
            data = fetch_json(url, timeout=10)
            return {p['index']: p['name'] for p in data.get('problems', [])}
        except Exception:
            return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        try:
            if self.needs_authentication(url):
                html = self._fetch_with_auth_retry(url)
            else:
                html = fetch_url(url, timeout=15)

            return self._parse_samples(html)
        except Exception:
            return None

    def _fetch_with_auth_retry(self, url: str, force_refresh: bool = False) -> str:
        """Busca com retry se sessão expirar."""
        html = fetch_url_with_auth(url, domain='privatejudge.com', force_refresh=force_refresh)

        # Detectar se precisa de login
        if '<div class="login-required">' in html:
            if not force_refresh:
                return self._fetch_with_auth_retry(url, force_refresh=True)
            else:
                from .exceptions import PlatformError
                raise PlatformError(
                    "Login required for private problems. "
                    "Please login at privatejudge.com in your browser."
                )

        return html

    def _parse_samples(self, html: str) -> List[SampleTest]:
        samples = []
        pattern = r'<div class="test-case">.*?<pre class="input">(.*?)</pre>.*?<pre class="output">(.*?)</pre>'
        matches = re.findall(pattern, html, re.DOTALL)

        for inp, out in matches:
            samples.append(SampleTest(
                input=clean_sample_text(inp),
                output=clean_sample_text(out)
            ))
        return samples
```

## Troubleshooting

### Problema: Regex não captura samples

**Solução:**
1. Use uma ferramenta como https://regex101.com para testar seu regex
2. Salve o HTML em um arquivo e inspecione a estrutura real:
   ```python
   html = fetch_url("...")
   with open('/tmp/debug.html', 'w') as f:
       f.write(html)
   ```
3. Use `re.DOTALL` para capturar newlines: `re.findall(pattern, html, re.DOTALL)`

### Problema: Testes falhando com "Connection refused"

**Solução:** Use mocks para evitar requests reais:

```python
with patch('lib.judges.fetch_url', return_value=mock_html):
    samples = judge.fetch_samples(url)
```

### Problema: Caracteres especiais aparecem como HTML entities

**Solução:** Use `clean_sample_text()`:

```python
text = clean_sample_text(raw_text)  # Converte &lt; para <, etc.
```

### Problema: Samples com whitespace incorreto

**Solução:** `clean_sample_text()` já remove whitespace excessivo. Se precisar de controle mais fino:

```python
text = text.strip()  # Remove espaços das pontas
text = re.sub(r'\n{2,}', '\n', text)  # Remove linhas vazias extras
```

### Problema: Auth não funciona

**Solução:**
1. Verifique se o browser suportado está instalado (Firefox/Chrome)
2. Certifique-se de estar logado no browser
3. Teste manualmente:
   ```python
   from lib.http_utils import fetch_url_with_auth
   html = fetch_url_with_auth(url, domain='example.com', force_refresh=True)
   print('login' in html.lower())  # Deve ser False se logado
   ```

### Problema: Como testar sem fazer requests reais?

**Solução:** Use `pytest` com mocks:

```python
def test_fetch_samples():
    # HTML salvo localmente ou string
    mock_html = '''<div class="sample">...</div>'''

    with patch('lib.judges.fetch_url', return_value=mock_html):
        samples = judge.fetch_samples("https://fake-url.com")
        assert len(samples) > 0
```

### Problema: Detecção de judge não funciona

**Solução:**
1. Verifique a ordem em `ALL_JUDGES` (mais específico primeiro)
2. Teste o método `detect()` isoladamente:
   ```python
   judge = MinhaPlataformaJudge()
   assert judge.detect("https://minhaplataforma.com/...")
   ```

---

## Referências

- **Código principal:** `lib/judges.py`
- **Testes:** `tests/test_judges.py`
- **URL parsing:** `lib/parsing.py`
- **HTTP utils:** `lib/http_utils.py`
- **Cookies:** `lib/cookies.py`

## Contribuindo

Ao adicionar um novo judge, abra um Pull Request com:
- Código da implementação
- Testes cobrindo casos principais
- Documentação atualizada
- Exemplo de URL funcional

Para dúvidas, abra uma issue no repositório.
