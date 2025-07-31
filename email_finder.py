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

# Windows Unicode fix - Set UTF-8 encoding for stdout
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def safe_print(text, flush=False):
    """Safe print function that handles Unicode on Windows"""
    try:
        print(text, flush=flush)
    except UnicodeEncodeError:
        # Fallback: replace emojis with simple text
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        # Replace common emojis with text equivalents
        replacements = {
            '🔍': '[SEARCH]',
            '✅': '[OK]',
            '📧': '[EMAIL]',
            '❌': '[ERROR]',
            '📊': '[STATS]',
            '💾': '[SAVE]',
            '📁': '[FILE]'
        }
        for emoji, replacement in replacements.items():
            safe_text = safe_text.replace('?', replacement, 1) if '?' in safe_text else safe_text
        print(safe_text, flush=flush)

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
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code != 200:
            return {'url': url, 'emails': [], 'company': 'Unknown'}

        html = resposta.text
        soup = BeautifulSoup(html, 'html.parser')
        texto = soup.get_text()

        emails = extrair_emails(texto)
        
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
    except Exception as e:
        safe_print(f"[ERRO] {url}: {e}")
        return {'url': url, 'emails': [], 'company': 'Unknown'}

def search_and_extract_emails(query, max_urls=50, max_threads=10):
    """
    Função principal para buscar URLs e extrair emails
    """
    safe_print(f"🔍 Procurando URLs para: {query}")
    
    # Buscar URLs no Google
    urls = list(search(query, num_results=max_urls))
    safe_print(f"✅ Encontrados {len(urls)} URLs")
    
    safe_print(f"📧 Extraindo emails usando {max_threads} threads...")
    resultados = []
    resultados_lock = threading.Lock()
    contador = {"processados": 0}
    contador_lock = threading.Lock()
    
    # Função worker para threads
    def worker(url):
        resultado = processar_url(url)
        
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

def salvar_resultados(resultados, query):
    """Salva os resultados em arquivo CSV"""
    # Criar nome de arquivo sanitizado
    nome_sanitizado = re.sub(r'[\\/*?:"<>|]', "_", query)
    nome_arquivo = f"results/{nome_sanitizado}.csv"
    
    # Criar diretório se não existir
    os.makedirs("results", exist_ok=True)
    
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['Company', 'Email', 'URL']
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        writer.writeheader()
        
        # Escrever dados
        for resultado in resultados:
            if resultado['emails']:
                for email in resultado['emails']:
                    writer.writerow({
                        'Company': resultado['company'],
                        'Email': email,
                        'URL': resultado['url']
                    })
    
    safe_print(f"💾 Resultados salvos em: {nome_arquivo}")
    return nome_arquivo

if __name__ == '__main__':
    # Exemplo de uso
    query = input("Digite sua busca: ")
    max_urls = int(input("Número máximo de URLs (padrão 50): ") or 50)
    
    resultados = search_and_extract_emails(query, max_urls)
    arquivo_resultado = salvar_resultados(resultados, query)
    
    # Estatísticas
    total_emails = sum(len(r['emails']) for r in resultados)
    safe_print(f"\n📊 Estatísticas:")
    safe_print(f"URLs processados: {len(resultados)}")
    safe_print(f"Emails encontrados: {total_emails}")
