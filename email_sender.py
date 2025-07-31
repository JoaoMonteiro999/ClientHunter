import smtplib
import time
import random
import csv
import os
import json
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_template import get_email_template

# Windows Unicode fix - Set UTF-8 encoding for stdout and environment
if sys.platform.startswith('win'):
    import codecs
    import io
    import locale
    
    # Set environment variables for UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
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
                    '📧': '[EMAIL]',
                    '📁': '[FILE]',
                    '🔍': '[SEARCH]',
                    '✅': '[OK]',
                    '⏭️': '[SKIP]',
                    '❌': '[ERROR]',
                    '📊': '[STATS]',
                    '📈': '[STATS]',
                    '🎉': '[DONE]',
                    '⏳': '[WAIT]',
                    '💾': '[SAVE]',
                    '🧹': '[CLEAN]',
                    '🔄': '[RESTORE]',
                    '⚠️': '[WARNING]',
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

# Configurações do email - Use environment variables or config file
try:
    # Try to import from config.py (not committed to git)
    from config import EMAIL_REMETENTE, SENHA_APP, SMTP_SERVER, SMTP_PORT
except ImportError:
    # Fallback to environment variables
    EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE', '')
    SENHA_APP = os.getenv('SENHA_APP', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    
    if not EMAIL_REMETENTE or not SENHA_APP:
        safe_print("❌ ERRO: Configurações de email não encontradas!")
        safe_print("📝 Por favor:")
        safe_print("   1. Copie config_template.py para config.py e preencha os dados")
        safe_print("   2. Ou defina as variáveis de ambiente EMAIL_REMETENTE e SENHA_APP")
        sys.exit(1)

# Arquivo para rastrear emails enviados
SENT_EMAILS_LOG = "sent_emails_log.json"

def remove_sent_emails_from_csv(csv_file, sent_emails_list):
    """
    Remove emails that were successfully sent from the CSV file
    This allows resuming campaigns with only remaining emails
    """
    if not sent_emails_list:
        safe_print("💾 Nenhum email foi enviado, arquivo mantido inalterado")
        return
    
    try:
        # Read the original CSV with encoding fallback
        all_rows = None
        fieldnames = None
        
        # Try multiple encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
        
        for encoding in encodings_to_try:
            try:
                with open(csv_file, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    all_rows = list(reader)
                    fieldnames = reader.fieldnames
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if all_rows is None:
            safe_print(f"❌ Erro: Não foi possível ler o arquivo CSV com nenhuma codificação")
            return None
        
        # Filter out sent emails
        remaining_rows = []
        removed_count = 0
        
        for row in all_rows:
            email = row.get('Email', '')
            if email in sent_emails_list:
                removed_count += 1
                safe_print(f"💾 Removendo: {row.get('Company', 'Unknown')} ({email})")
            else:
                remaining_rows.append(row)
        
        # Write back the filtered CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as file:
            if remaining_rows:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(remaining_rows)
            else:
                # Create empty CSV with headers
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
        
        safe_print(f"💾 Arquivo atualizado: {removed_count} emails removidos, {len(remaining_rows)} restantes")
        
        return {
            'removed_count': removed_count,
            'remaining_count': len(remaining_rows),
            'sent_emails': sent_emails_list
        }
        
    except Exception as e:
        safe_print(f"❌ Erro ao atualizar arquivo CSV: {e}")
        return None

def load_sent_emails_log():
    """Carrega o log de emails enviados"""
    if os.path.exists(SENT_EMAILS_LOG):
        try:
            with open(SENT_EMAILS_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_sent_emails_log(log_data):
    """Salva o log de emails enviados"""
    try:
        with open(SENT_EMAILS_LOG, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        safe_print(f"⚠️ Aviso: Não foi possível salvar o log: {e}")

def add_sent_email(email, company, language):
    """Adiciona um email ao log de enviados"""
    log_data = load_sent_emails_log()
    email_key = email.lower().strip()
    
    if email_key not in log_data:
        log_data[email_key] = []
    
    log_data[email_key].append({
        'company': company,
        'language': language,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_sent_emails_log(log_data)

def is_email_already_sent(email, language=None):
    """Verifica se um email já foi enviado"""
    log_data = load_sent_emails_log()
    email_key = email.lower().strip()
    
    if email_key not in log_data:
        return False, None
    
    # Se não especificar idioma, verifica se foi enviado em qualquer idioma
    if language is None:
        return True, log_data[email_key][-1]  # Retorna o último envio
    
    # Verifica se foi enviado no idioma específico
    for entry in log_data[email_key]:
        if entry.get('language') == language:
            return True, entry
    
    return False, None

def get_sent_emails_stats():
    """Retorna estatísticas dos emails enviados"""
    log_data = load_sent_emails_log()
    total_unique_emails = len(log_data)
    total_sends = sum(len(entries) for entries in log_data.values())
    
    # Contagem por idioma
    language_stats = {}
    for entries in log_data.values():
        for entry in entries:
            lang = entry.get('language', 'unknown')
            language_stats[lang] = language_stats.get(lang, 0) + 1
    
    return {
        'total_unique_emails': total_unique_emails,
        'total_sends': total_sends,
        'by_language': language_stats
    }

def send_emails_from_csv(csv_file, language='pt', update_csv_on_completion=False):
    """
    Envia emails para todos os destinatários de um arquivo CSV
    CSV deve ter colunas: Company, Email
    
    Args:
        csv_file: Path to the CSV file
        language: Language for email templates ('pt', 'en', 'de')
        update_csv_on_completion: If True, removes sent emails from CSV when done
    """
    
    safe_print(f"📧 Enviando emails em {language.upper()}")
    safe_print(f"📁 Arquivo: {csv_file}")
    
    # Carregar log de emails enviados
    safe_print("🔍 Verificando emails já enviados...")
    sent_stats = get_sent_emails_stats()
    safe_print(f"📊 Estatísticas do log: {sent_stats['total_unique_emails']} emails únicos, {sent_stats['total_sends']} envios totais")
    
    # Ler arquivo CSV
    emails_enviados = []
    emails_pulados = []
    total_emails = 0
    
    try:
        # Read CSV with encoding fallback
        emails = None
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
        
        for encoding in encodings_to_try:
            try:
                with open(csv_file, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    emails = list(reader)
                    total_emails = len(emails)
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if emails is None:
            safe_print(f"❌ Erro: Não foi possível ler o arquivo CSV com nenhuma codificação")
            return
            
        if total_emails == 0:
            safe_print("❌ Nenhum email encontrado no arquivo!")
            return
            
        safe_print(f"📊 Total de emails no arquivo: {total_emails}")
        
        # Primeira passagem: verificar quantos emails já foram enviados
        emails_to_send = []
        for row in emails:
            empresa = row.get('Company', 'Empresa')
            destinatario = row.get('Email', '')
            
            if not destinatario or '@' not in destinatario:
                continue
            
            already_sent, last_send = is_email_already_sent(destinatario, language)
            if not already_sent:
                emails_to_send.append(row)
            else:
                emails_pulados.append({
                    'email': destinatario,
                    'company': empresa,
                    'last_send': last_send
                })
        
        emails_to_send_count = len(emails_to_send)
        emails_skipped_count = len(emails_pulados)
        
        safe_print(f"✅ Emails novos para enviar: {emails_to_send_count}")
        safe_print(f"⏭️ Emails já enviados (pulados): {emails_skipped_count}")
        
        if emails_skipped_count > 0:
            safe_print("\n📋 Emails que serão pulados:")
            for skip_info in emails_pulados[:5]:  # Mostrar apenas os primeiros 5
                last_date = skip_info['last_send'].get('date', 'data desconhecida')
                safe_print(f"   ⏭️ {skip_info['company']} ({skip_info['email']}) - enviado em {last_date}")
            if emails_skipped_count > 5:
                safe_print(f"   ... e mais {emails_skipped_count - 5} emails")
            safe_print("")
        
        if emails_to_send_count == 0:
            safe_print("🎉 Todos os emails já foram enviados anteriormente!")
            return emails_enviados
        
        # Segunda passagem: enviar emails novos
        successfully_sent_emails = []  # Track emails that were actually sent
        
        for i, row in enumerate(emails_to_send, 1):
            empresa = row.get('Company', 'Empresa')
            destinatario = row.get('Email', '')
                
            safe_print(f"\n[{i}/{emails_to_send_count}] Enviando para: {empresa} ({destinatario})")
            
            # Obter template do email
            subject, corpo_html, corpo_texto = get_email_template(empresa, language)
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg["Subject"] = subject
            msg["From"] = EMAIL_REMETENTE
            msg["To"] = destinatario
            
            # Adicionar versões HTML e texto
            part1 = MIMEText(corpo_texto, 'plain')
            part2 = MIMEText(corpo_html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar email
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_REMETENTE, SENHA_APP)
                    server.send_message(msg)
                    safe_print(f"✅ Email enviado com sucesso para {empresa}")
                    emails_enviados.append(destinatario)
                    successfully_sent_emails.append(destinatario)
                    
                    # Adicionar ao log de emails enviados
                    add_sent_email(destinatario, empresa, language)
                    
            except Exception as e:
                safe_print(f"❌ Erro ao enviar para {empresa}: {e}")
            
            # Check for interruption signal (for future use)
            # This can be expanded to check for stop signals
            
            # Aguardar entre emails (40-90 segundos)
            if i < emails_to_send_count:
                tempo_espera = random.uniform(40, 90)
                safe_print(f"⏳ Aguardando {int(tempo_espera)} segundos...")
                time.sleep(tempo_espera)
        
        # Relatório final
        safe_print(f"\n🎉 CONCLUÍDO!")
        safe_print(f"📊 Emails enviados: {len(emails_enviados)}/{emails_to_send_count} (novos)")
        safe_print(f"⏭️ Emails pulados (já enviados): {emails_skipped_count}")
        safe_print(f"📁 Total no arquivo: {total_emails}")
        safe_print(f"📧 Idioma: {language.upper()}")
        
        # Update CSV file if requested and emails were sent
        if update_csv_on_completion and successfully_sent_emails:
            safe_print(f"\n💾 Atualizando arquivo CSV...")
            update_result = remove_sent_emails_from_csv(csv_file, successfully_sent_emails)
            if update_result:
                safe_print(f"🧹 Arquivo limpo: {update_result['removed_count']} emails enviados removidos")
                safe_print(f"📝 Restam: {update_result['remaining_count']} emails para futuras campanhas")
        
        # Atualizar estatísticas finais
        final_stats = get_sent_emails_stats()
        safe_print(f"📈 Total geral no log: {final_stats['total_unique_emails']} emails únicos")
        
        return {
            'emails_enviados': emails_enviados,
            'successfully_sent': successfully_sent_emails,
            'emails_skipped_count': emails_skipped_count,
            'total_emails': total_emails
        }
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}", flush=True)
        return []

def clean_csv_file(csv_file):
    """
    Clean CSV file by removing emails that were already sent (based on log)
    This is useful for resuming campaigns
    """
    try:
        safe_print(f"🧹 Limpando arquivo: {csv_file}")
        
        # Read the original CSV with encoding fallback
        all_rows = None
        fieldnames = None
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
        
        for encoding in encodings_to_try:
            try:
                with open(csv_file, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    all_rows = list(reader)
                    fieldnames = reader.fieldnames
                    break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if all_rows is None:
            safe_print(f"❌ Erro: Não foi possível ler o arquivo CSV com nenhuma codificação")
            return {'removed_count': 0, 'remaining_count': 0}
        
        if not all_rows:
            safe_print("📝 Arquivo CSV está vazio")
            return {'removed_count': 0, 'remaining_count': 0}
        
        # Filter out emails that were already sent
        remaining_rows = []
        removed_count = 0
        
        for row in all_rows:
            email = row.get('Email', '')
            company = row.get('Company', 'Unknown')
            
            if email and '@' in email:
                # Check if email was already sent (any language)
                already_sent, _ = is_email_already_sent(email)
                if already_sent:
                    removed_count += 1
                    safe_print(f"🔄 Removendo (já enviado): {company} ({email})")
                else:
                    remaining_rows.append(row)
            else:
                # Keep invalid emails for manual review
                remaining_rows.append(row)
        
        # Write back the filtered CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as file:
            if remaining_rows:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(remaining_rows)
            else:
                # Create empty CSV with headers
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
        
        safe_print(f"✅ Limpeza concluída: {removed_count} emails removidos, {len(remaining_rows)} restantes")
        
        return {
            'removed_count': removed_count,
            'remaining_count': len(remaining_rows),
            'original_count': len(all_rows)
        }
        
    except Exception as e:
        safe_print(f"❌ Erro ao limpar arquivo CSV: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    # Check if this is a special command
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            # Show statistics
            stats = get_sent_emails_stats()
            print(f"\n📊 Estatísticas dos Emails Enviados:")
            print(f"   🎯 Emails únicos: {stats['total_unique_emails']}")
            print(f"   📨 Total de envios: {stats['total_sends']}")
            print(f"   🌍 Por idioma:")
            for lang, count in stats['by_language'].items():
                print(f"      - {lang.upper()}: {count}")
            exit(0)
        
        elif sys.argv[1] == "--clear":
            # Clear the sent emails log
            confirm = input("⚠️ Tem certeza que deseja limpar o log de emails enviados? (sim/não): ")
            if confirm.lower() in ['sim', 's', 'yes', 'y']:
                if os.path.exists(SENT_EMAILS_LOG):
                    os.remove(SENT_EMAILS_LOG)
                    print("✅ Log de emails enviados foi limpo!")
                else:
                    print("ℹ️ Log já estava vazio.")
            else:
                print("❌ Operação cancelada.")
            exit(0)
        
        elif sys.argv[1] == "--clean":
            # Clean CSV file by removing already sent emails
            if len(sys.argv) > 2:
                csv_file = sys.argv[2]
                if os.path.exists(csv_file):
                    result = clean_csv_file(csv_file)
                    if result:
                        safe_print(f"✅ Limpeza concluída!")
                        safe_print(f"   📊 Original: {result['original_count']} emails")
                        safe_print(f"   🗑️ Removidos: {result['removed_count']} emails")
                        safe_print(f"   📝 Restantes: {result['remaining_count']} emails")
                else:
                    safe_print(f"❌ Arquivo não encontrado: {csv_file}")
            else:
                safe_print("❌ Por favor, forneça o arquivo CSV para limpar.")
                safe_print("   Uso: python email_sender.py --clean arquivo.csv")
            exit(0)
        
        elif sys.argv[1] == "--check":
            # Check if a specific email was sent
            if len(sys.argv) > 2:
                email = sys.argv[2]
                sent, last_info = is_email_already_sent(email)
                if sent:
                    print(f"✅ Email {email} já foi enviado:")
                    print(f"   📅 Data: {last_info.get('date', 'desconhecida')}")
                    print(f"   🏢 Empresa: {last_info.get('company', 'desconhecida')}")
                    print(f"   🌍 Idioma: {last_info.get('language', 'desconhecido')}")
                else:
                    print(f"❌ Email {email} ainda não foi enviado.")
            else:
                print("❌ Por favor, forneça um email para verificar.")
                print("   Uso: python email_sender.py --check email@exemplo.com")
            exit(0)
    
    # Exemplo de uso normal
    safe_print("\n🔧 Utilitário de Email - Opções:")
    safe_print("  python email_sender.py --stats    (mostrar estatísticas)")
    safe_print("  python email_sender.py --clear    (limpar log de enviados)")
    safe_print("  python email_sender.py --clean arquivo.csv  (remover emails já enviados do CSV)")
    safe_print("  python email_sender.py --check email@exemplo.com  (verificar email)")
    safe_print("\n📧 Modo normal - envio de emails:")
    
    csv_file = input("Arquivo CSV: ")
    language = input("Idioma (pt/en/de): ") or 'pt'
    
    send_emails_from_csv(csv_file, language)
