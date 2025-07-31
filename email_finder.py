from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import csv
from pathlib import Path
import sys
import subprocess

# Windows Unicode fix - Set UTF-8 encoding for stdout and environment
if sys.platform.startswith('win'):
    import codecs
    import io
    import locale
    
    # Set environment variables for UTF-8 encoding FIRST
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
    os.environ['PYTHONLEGACYWINDOWSIOENCODING'] = '0'
    
    # Force Python to use UTF-8 for all I/O operations
    import _locale
    try:
        _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
    except:
        pass
    
    # Additional encoding protection
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass
    
    # Try to set console code page to UTF-8
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    
    # Fix for Windows encoding issues with stdout
    try:
        # Check if stdout needs to be wrapped
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        elif not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), errors='replace')
    except Exception:
        # Fallback if stdout is already wrapped or other issues
        pass
    
    # Also handle stderr
    try:
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
        elif not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding.lower() != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), errors='replace')
    except Exception:
        pass

def safe_print(text, flush=False):
    """Safe print function that handles Unicode on Windows"""
    try:
        # First try normal print
        print(text, flush=flush)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        try:
            # Try encoding as UTF-8 with error handling
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            safe_text = str(text).encode('utf-8', errors='replace').decode('utf-8')
            print(safe_text, flush=flush)
        except Exception:
            # Final fallback: replace problematic characters with safe alternatives
            try:
                # Replace common emojis and special characters
                safe_text = str(text)
                replacements = {
                    '🔍': '[SEARCH]',
                    '✅': '[OK]',
                    '📧': '[EMAIL]',
                    '❌': '[ERROR]',
                    '📊': '[STATS]',
                    '💾': '[SAVE]',
                    '📁': '[FILE]',
                    '⏳': '[WAIT]',
                    '🚀': '[START]',
                    '💡': '[INFO]',
                    '🌐': '[WEB]',
                    '📍': '[LOCATION]',
                    '🔧': '[TOOL]',
                    '👋': '[WAVE]'
                }
                for emoji, replacement in replacements.items():
                    safe_text = safe_text.replace(emoji, replacement)
                
                # Remove any remaining non-ASCII characters
                safe_text = safe_text.encode('ascii', 'replace').decode('ascii')
                print(safe_text, flush=flush)
            except Exception:
                # Ultimate fallback
                print("[MESSAGE ENCODING ERROR]", flush=flush)
    except Exception as e:
        # Handle any other printing errors
        try:
            print(f"[PRINT ERROR: {e}]", flush=flush)
        except:
            pass

def validar_email(email):
    """
    Valida se um email é válido:
    - Remove texto extra anexado
    - Verifica se termina com domínios válidos
    - Verifica estrutura básica
    """
    # Domínios válidos mais comuns
    dominios_validos = [
        '.com', '.pt', '.org', '.net', '.edu', '.gov', '.mil', '.int',
        '.co.uk', '.de', '.fr', '.es', '.it', '.nl', '.be', '.ch',
        '.at', '.se', '.no', '.dk', '.fi', '.pl', '.cz', '.hu',
        '.gr', '.ie', '.lu', '.cy', '.mt', '.si', '.sk', '.lv',
        '.lt', '.ee', '.bg', '.ro', '.hr', '.eu', '.info', '.biz'
    ]
    
    # Primeiro, extrair a parte base do email
    email_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)', email)
    if not email_match:
        return None
    
    base_email = email_match.group(1)
    
    # Remover números no início do email (antes do @)
    # Exemplo: "2173contact@domain.com" → "contact@domain.com"
    if '@' in base_email:
        local_part, domain_part = base_email.split('@', 1)
        # Remove números e hífens do início da parte local
        local_part = re.sub(r'^[0-9-]+', '', local_part)
        # Se depois da remoção não sobrou nada na parte local, retornar None
        if not local_part:
            return None
        base_email = local_part + '@' + domain_part
    
    # Agora procurar qual domínio válido está presente
    email_limpo = None
    for ext in dominios_validos:
        # Verificar se o domínio está presente no email
        if ext in base_email.lower():
            # Encontrar a posição do domínio e cortar até lá
            pos = base_email.lower().find(ext)
            if pos > 0:  # Deve ter algo antes do domínio
                email_limpo = base_email[:pos + len(ext)]
                break
    
    if not email_limpo:
        return None
    
    # Verificar estrutura básica: deve ter @ e pelo menos um ponto depois do @
    if '@' not in email_limpo or email_limpo.count('@') != 1:
        return None
    
    # Dividir em parte local e domínio
    try:
        local, dominio = email_limpo.split('@')
        
        # Verificar se a parte local não está vazia
        if not local or len(local) < 1:
            return None
            
        # Verificar se o domínio não está vazio e tem pelo menos um ponto
        if not dominio or '.' not in dominio:
            return None
            
        # Verificar se termina com um domínio válido
        dominio_lower = dominio.lower()
        if not any(dominio_lower.endswith(ext) for ext in dominios_validos):
            return None
            
        # Verificar se não há caracteres inválidos na estrutura final
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$', email_limpo):
            return None
            
        return email_limpo.lower()
        
    except ValueError:
        return None

def extrair_emails(texto):
    # Padrão mais abrangente para emails internacionais
    emails_brutos = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[^\s]*", texto)
    
    # Validar e limpar emails
    emails_validos = []
    for email in emails_brutos:
        email_validado = validar_email(email)
        if email_validado and email_validado not in emails_validos:
            emails_validos.append(email_validado)
    
    return emails_validos

def processar_url(url):
    """Processa um URL e extrai emails"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Make request with additional error handling
        try:
            resposta = requests.get(url, headers=headers, timeout=10)
        except UnicodeDecodeError as e:
            safe_print(f"❌ [REQUEST ENCODING ERROR] {url}: {e}")
            return {'url': url, 'emails': [], 'company': 'Unknown'}
        except Exception as e:
            safe_print(f"❌ [REQUEST ERROR] {url}: {e}")
            return {'url': url, 'emails': [], 'company': 'Unknown'}
            
        if resposta.status_code != 200:
            return {'url': url, 'emails': [], 'company': 'Unknown'}

        # Enhanced encoding handling for Windows
        html = None
        
        # Method 1: Try to get encoding from response headers
        content_type = resposta.headers.get('content-type', '').lower()
        encoding_from_header = None
        if 'charset=' in content_type:
            try:
                encoding_from_header = content_type.split('charset=')[1].split(';')[0].strip()
            except:
                pass
        
        # Method 2: Try multiple encoding strategies
        encodings_to_try = []
        
        # Add header encoding first if available
        if encoding_from_header:
            encodings_to_try.append(encoding_from_header)
        
        # Add common encodings
        encodings_to_try.extend(['utf-8', 'cp1252', 'iso-8859-1', 'latin1'])
        
        # Remove duplicates while preserving order
        seen = set()
        encodings_to_try = [x for x in encodings_to_try if not (x in seen or seen.add(x))]
        
        # Try each encoding
        for encoding in encodings_to_try:
            try:
                html = resposta.content.decode(encoding)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        # Final fallback - force UTF-8 with error replacement
        if html is None:
            try:
                html = resposta.content.decode('utf-8', errors='replace')
            except Exception:
                # Last resort - use requests default but catch any encoding errors
                try:
                    html = resposta.text
                except UnicodeDecodeError:
                    html = str(resposta.content, errors='replace')
        
        # Parse HTML with error handling
        try:
            soup = BeautifulSoup(html, 'html.parser')
            texto = soup.get_text()
        except Exception as e:
            safe_print(f"[HTML PARSE ERROR] {url}: {e}")
            return {'url': url, 'emails': [], 'company': 'Unknown'}

        # Extract emails with additional error handling
        try:
            emails = extrair_emails(texto)
        except Exception as e:
            safe_print(f"[EMAIL EXTRACTION ERROR] {url}: {e}")
            emails = []
        
        # Extrair nome da empresa da URL
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            company_name = domain.split('.')[0].title() if domain else 'Unknown'
        except:
            company_name = 'Unknown'

        return {
            'url': url,
            'emails': emails,
            'company': company_name
        }
    except UnicodeDecodeError as e:
        safe_print(f"❌ [ENCODING ERROR] {url}: {e}")
        return {'url': url, 'emails': [], 'company': 'Unknown'}
    except Exception as e:
        safe_print(f"❌ [ERROR] {url}: {e}")
        return {'url': url, 'emails': [], 'company': 'Unknown'}

def safe_google_search(query, num_results=50):
    """
    Safe Google search wrapper that handles encoding issues on Windows
    """
    try:
        # Force environment encoding before search
        if sys.platform.startswith('win'):
            # Set additional Windows-specific encoding variables
            os.environ['PYTHONLEGACYWINDOWSIOENCODING'] = '0'
            os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
        
        safe_print(f"🔍 Starting safe Google search for: {query}")
        
        # Method 1: Use isolated subprocess (most reliable on Windows)
        try:
            safe_print("� Using isolated search process...")
            script_path = Path(__file__).parent / "isolated_search.py"
            
            process = subprocess.run(
                [sys.executable, str(script_path), query, str(num_results)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60  # 60 second timeout
            )
            
            if process.returncode == 0:
                urls = []
                for line in process.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('SEARCH_ERROR:') and line.startswith('http'):
                        urls.append(line)
                
                if urls:
                    safe_print(f"✅ Isolated search successful: {len(urls)} URLs found")
                    return urls
            else:
                safe_print(f"⚠️ Isolated search failed: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            safe_print("⚠️ Isolated search timed out")
        except Exception as e:
            safe_print(f"⚠️ Isolated search error: {e}")
        
        # Method 2: Direct search with sanitized query
        try:
            safe_query = query.encode('ascii', 'ignore').decode('ascii')
            if not safe_query.strip():
                safe_query = ''.join(c for c in query if ord(c) < 128)
            
            safe_print(f"🔧 Direct search with sanitized query: {safe_query}")
            urls = list(search(safe_query, num_results=num_results))
            safe_print(f"✅ Direct search successful: {len(urls)} URLs found")
            return urls
            
        except UnicodeDecodeError as e:
            safe_print(f"⚠️ Direct search encoding error: {e}")
        except Exception as e:
            safe_print(f"⚠️ Direct search failed: {e}")
        
        # Method 3: Ultra-safe ASCII-only search
        try:
            ascii_query = ''.join(c for c in query if c.isalnum() or c.isspace())
            if ascii_query.strip():
                safe_print(f"🔧 ASCII-only search: {ascii_query}")
                urls = list(search(ascii_query, num_results=num_results))
                safe_print(f"✅ ASCII search successful: {len(urls)} URLs found")
                return urls
        except Exception as e:
            safe_print(f"⚠️ ASCII search failed: {e}")
        
        # If all methods fail
        safe_print("❌ All search methods failed")
        safe_print("💡 Please try using a simpler search query with basic English words only")
        safe_print("💡 Example: 'dental clinic' instead of 'clínica dental'")
        return []
        
    except Exception as e:
        safe_print(f"❌ [CRITICAL SEARCH ERROR]: {e}")
        return []

def search_and_extract_emails(query, max_urls=50, max_threads=10):
    """
    Função principal para buscar URLs e extrair emails
    """
    try:
        safe_print(f"🔍 Procurando URLs para: {query}")
        
        # Use our safe Google search wrapper
        urls = safe_google_search(query, max_urls)
        
        if not urls:
            safe_print("❌ Nenhuma URL encontrada")
            return []
            
        safe_print(f"✅ Encontrados {len(urls)} URLs")
        
        if not urls:
            safe_print("❌ Nenhuma URL encontrada")
            return []
        
        safe_print(f"📧 Extraindo emails usando {max_threads} threads...")
        resultados = []
        resultados_lock = threading.Lock()
        contador = {"processados": 0}
        contador_lock = threading.Lock()
        
        # Função worker para threads
        def worker(url):
            try:
                resultado = processar_url(url)
            except Exception as e:
                # Catch any unexpected errors including encoding issues
                safe_print(f"❌ [WORKER ERROR] {url}: {e}")
                resultado = {'url': url, 'emails': [], 'company': 'Unknown'}
            
            # Adicionar resultado à lista com lock
            with resultados_lock:
                resultados.append(resultado)
            
            # Atualizar contador
            with contador_lock:
                contador["processados"] += 1
                safe_print(f"[{contador['processados']}/{len(urls)}] Processado: {url}")
        
        # Usar ThreadPoolExecutor para gerenciar threads
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(worker, urls)
        
        return resultados
        
    except Exception as e:
        safe_print(f"❌ [SEARCH_AND_EXTRACT ERROR]: {e}")
        return []
        executor.map(worker, urls)
    
    return resultados

def salvar_resultados(resultados, query):
    """Salva os resultados em arquivo CSV"""
    # Criar nome de arquivo sanitizado
    nome_sanitizado = re.sub(r'[\\/*?:"<>|]', "_", query)
    nome_arquivo = f"results/{nome_sanitizado}.csv"
    
    # Criar diretório se não existir
    os.makedirs("results", exist_ok=True)
    
    # Force UTF-8 encoding for Windows compatibility with BOM for Excel
    try:
        with open(nome_arquivo, 'w', newline='', encoding='utf-8-sig') as arquivo_csv:
            campos = ['Company', 'Email', 'URL']
            writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
            writer.writeheader()
            
            # Escrever dados com tratamento de encoding
            for resultado in resultados:
                if resultado['emails']:
                    for email in resultado['emails']:
                        try:
                            # Ensure all strings are properly encoded
                            company = str(resultado['company']).encode('utf-8', errors='replace').decode('utf-8')
                            email_clean = str(email).encode('utf-8', errors='replace').decode('utf-8')
                            url_clean = str(resultado['url']).encode('utf-8', errors='replace').decode('utf-8')
                            
                            writer.writerow({
                                'Company': company,
                                'Email': email_clean,
                                'URL': url_clean
                            })
                        except Exception as e:
                            safe_print(f"❌ [CSV WRITE ERROR] {e}")
                            continue
        
        safe_print(f"💾 Resultados salvos em: {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        safe_print(f"❌ [FILE SAVE ERROR] {e}")
        # Fallback to basic encoding
        try:
            with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                campos = ['Company', 'Email', 'URL']
                writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
                writer.writeheader()
                
                for resultado in resultados:
                    if resultado['emails']:
                        for email in resultado['emails']:
                            writer.writerow({
                                'Company': resultado['company'],
                                'Email': email,
                                'URL': resultado['url']
                            })
            safe_print(f"💾 Resultados salvos em: {nome_arquivo} (fallback mode)")
            return nome_arquivo
        except Exception as e2:
            safe_print(f"❌ [CRITICAL FILE ERROR] {e2}")
            return None

if __name__ == '__main__':
    # Wrap everything in comprehensive error handling
    try:
        # Exemplo de uso
        safe_print("🔍 ClientHunter - Email Finder")
        safe_print("=" * 40)
        
        try:
            query = input("Digite sua busca: ")
        except UnicodeDecodeError as e:
            safe_print(f"❌ Input encoding error: {e}")
            query = input("Search term (ASCII only): ")
        
        try:
            max_urls_input = input("Número máximo de URLs (padrão 50): ")
            max_urls = int(max_urls_input or 50)
        except (ValueError, UnicodeDecodeError):
            safe_print("⚠️ Using default: 50 URLs")
            max_urls = 50
        
        if not query:
            safe_print("❌ Erro: Query não pode estar vazia")
            sys.exit(1)
        
        safe_print(f"🚀 Iniciando busca para: '{query}' (max {max_urls} URLs)")
        
        resultados = search_and_extract_emails(query, max_urls)
        
        if not resultados:
            safe_print("❌ Nenhum resultado encontrado")
            sys.exit(1)
        
        arquivo_resultado = salvar_resultados(resultados, query)
        
        # Estatísticas
        total_emails = sum(len(r['emails']) for r in resultados if r['emails'])
        safe_print(f"\n📊 Estatísticas:")
        safe_print(f"URLs processados: {len(resultados)}")
        safe_print(f"Emails encontrados: {total_emails}")
        
        if arquivo_resultado:
            safe_print(f"📁 Arquivo salvo: {arquivo_resultado}")
        
    except KeyboardInterrupt:
        safe_print("\n⏹️ Operação cancelada pelo usuário")
        sys.exit(0)
    except UnicodeDecodeError as e:
        safe_print(f"\n❌ Erro de codificação: {e}")
        safe_print("💡 Tente usar caracteres ASCII simples na busca")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Erro inesperado: {e}")
        safe_print("🔧 Contate o suporte se o problema persistir")
        sys.exit(1)
