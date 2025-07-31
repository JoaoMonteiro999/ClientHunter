import streamlit as st
import pandas as pd
import os
import subprocess
import sys
import time
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="ClientHunter CLEAN",
    page_icon="🔍",
    layout="wide"
)

# CSS simples
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .step-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    /* Real-time output styling */
    .output-container {
        background: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #333;
    }
    
    /* Remove extra white space */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Remove default streamlit spacing */
    .stMarkdown {
        margin-bottom: 0 !important;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 ClientHunter CLEAN</h1>
    <p>Simple Email Collection & Outreach Tool</p>
</div>
""", unsafe_allow_html=True)

# Função para executar busca de emails
def run_email_search(query, max_urls):
    """Executa busca de emails usando o script email_finder.py com output em tempo real"""
    try:
        # Use the full path to ensure we're running the correct script
        script_path = Path(__file__).parent / "email_finder.py"
        cmd = [sys.executable, str(script_path)]
        
        # Set environment variables for encoding protection
        env = os.environ.copy()
        env.update({
            'PYTHONIOENCODING': 'utf-8:replace',
            'PYTHONUTF8': '1',
            'PYTHONLEGACYWINDOWSSTDIO': '0',
            'PYTHONLEGACYWINDOWSIOENCODING': '0'
        })
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=Path(__file__).parent,  # Set working directory
            env=env,  # Use our encoding-protected environment
            encoding='utf-8',
            errors='replace'
        )
        
        # Enviar inputs
        inputs = f"{query}\n{max_urls}\n"
        process.stdin.write(inputs)
        process.stdin.close()
        
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_lines.append(output.strip())
                yield output.strip()
        
        return_code = process.poll()
        if return_code != 0:
            stderr_output = process.stderr.read()
            yield f"❌ Error: {stderr_output}"
        else:
            yield "✅ Email search completed successfully!"
            
    except Exception as e:
        yield f"❌ Exception: {str(e)}"

# Função para limpar arquivo CSV
def clean_csv_file_app(csv_file):
    """Clean CSV file by removing already sent emails"""
    try:
        script_path = Path(__file__).parent / "email_sender.py"
        cmd = [sys.executable, str(script_path), "--clean", csv_file]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
            cwd=Path(__file__).parent
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # Parse the output for statistics
            lines = stdout.strip().split('\n')
            for line in lines:
                yield line
        else:
            yield f"❌ Error: {stderr}"
            
    except Exception as e:
        yield f"❌ Exception: {str(e)}"

# Função para carregar resultados CSV
def load_results():
    """Carrega arquivos CSV da pasta results"""
    # Use absolute path relative to the current script
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        return []
    
    csv_files = []
    for csv_file in results_dir.glob("*.csv"):
        csv_files.append({
            'name': csv_file.name,
            'path': str(csv_file),
            'modified': csv_file.stat().st_mtime
        })
    
    return sorted(csv_files, key=lambda x: x['modified'], reverse=True)

# Função para enviar emails
def send_email_campaign(csv_file, language, track_sent_emails=False):
    """Envia campanha de emails com output em tempo real"""
    try:
        # Use the full path to ensure we're running the correct script
        script_path = Path(__file__).parent / "email_sender.py"
        cmd = [sys.executable, str(script_path)]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # Unbuffered for real-time output
            universal_newlines=True,
            cwd=Path(__file__).parent,  # Set working directory
            env=dict(os.environ, PYTHONUNBUFFERED="1")  # Force Python to be unbuffered
        )
        
        # Enviar inputs
        inputs = f"{csv_file}\n{language}\n"
        process.stdin.write(inputs)
        process.stdin.flush()
        process.stdin.close()
        
        # Read output line by line in real-time
        output_lines = []
        sent_emails_count = 0
        
        while True:
            # Check if user wants to stop the campaign
            if st.session_state.get('campaign_stopped', False):
                process.terminate()
                yield "🛑 Campaign stopped by user"
                break
                
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                clean_output = output.strip()
                if clean_output:  # Only yield non-empty lines
                    output_lines.append(clean_output)
                    
                    # Track sent emails if requested
                    if track_sent_emails and "✅ Email enviado com sucesso" in clean_output:
                        sent_emails_count += 1
                        if 'sent_emails_this_session' not in st.session_state:
                            st.session_state.sent_emails_this_session = []
                    
                    yield clean_output
        
        # Check for any remaining output
        remaining_output = process.stdout.read()
        if remaining_output:
            for line in remaining_output.strip().split('\n'):
                if line.strip():
                    yield line.strip()
        
        return_code = process.poll()
        
        if return_code != 0 and not st.session_state.get('campaign_stopped', False):
            stderr_output = process.stderr.read()
            if stderr_output:
                yield f"❌ Error: {stderr_output.strip()}"
        else:
            if not any("🎉 CONCLUÍDO!" in line for line in output_lines) and not st.session_state.get('campaign_stopped', False):
                yield "✅ Email campaign completed successfully!"
            
    except Exception as e:
        yield f"❌ Exception: {str(e)}"

# Interface principal
st.header("🎯 Complete Email Collection & Outreach")

# Step 1: Search for Emails
with st.container():
    st.subheader("Step 1: 🔍 Search for Emails")

col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Search Query:",
        placeholder="e.g., dental clinic London, restaurant Portugal, zahnarzt Berlin",
        help="Enter your search terms. Be specific for better results."
    )

with col2:
    max_urls = st.number_input(
        "Max URLs:",
        min_value=10,
        max_value=1000,
        value=50,
        step=10,
        help="Number of URLs to search"
    )

if st.button("🚀 Start Email Search", type="primary", use_container_width=True):
    if search_query:
        with st.status("🔍 Searching for emails...", expanded=True) as status:
            st.write(f"🎯 Query: {search_query}")
            st.write(f"📊 Max URLs: {max_urls}")
            st.write("⏳ This may take a few minutes...")
            
            # Container para output em tempo real
            output_container = st.empty()
            output_lines = []
            
            # Executar busca e mostrar output em tempo real
            success = True
            try:
                for output_line in run_email_search(search_query, max_urls):
                    output_lines.append(output_line)
                    # Mostrar apenas as últimas 15 linhas para não sobrecarregar a interface
                    recent_lines = output_lines[-15:]
                    
                    # Adicionar header informativo no topo
                    display_text = "🔍 Real-time Email Search Progress:\n" + "="*50 + "\n"
                    display_text += '\n'.join(recent_lines)
                    
                    output_container.code(display_text)
                    time.sleep(0.1)  # Para permitir atualização da UI
                    
                    if "❌" in output_line:
                        success = False
                        
            except Exception as e:
                success = False
                output_lines.append(f"❌ Exception: {str(e)}")
                display_text = "🔍 Real-time Email Search Progress:\n" + "="*50 + "\n"
                display_text += '\n'.join(output_lines[-15:])
                output_container.code(display_text)
            
            # Mostrar output final completo após conclusão
            if output_lines:
                st.subheader("📋 Complete Search Log")
                with st.expander("View Full Output", expanded=False):
                    full_output = '\n'.join(output_lines)
                    st.code(full_output)
            
            if success:
                status.update(label="✅ Search completed!", state="complete")
                st.success("🎉 Email search completed successfully!")
                # Removido st.rerun() para manter o output visível
            else:
                status.update(label="❌ Search failed", state="error")
                st.error("❌ Search failed. Check the output above for details.")
    else:
        st.warning("Please enter a search query!")

# Step 2: View Results
with st.container():
    st.subheader("Step 2: 📊 View Results")

# Carregar resultados
results = load_results()

if results:
    # Mostrar arquivo mais recente
    latest_file = results[0]
    st.success(f"📁 Latest result: **{latest_file['name']}**")
    
    # Selectbox para escolher arquivo
    if len(results) > 1:
        selected_file_name = st.selectbox(
            "Choose result file:",
            options=[f['name'] for f in results],
            index=0
        )
        selected_file = next(f for f in results if f['name'] == selected_file_name)
    else:
        selected_file = latest_file
    
    # Carregar e mostrar dados
    try:
        df = pd.read_csv(selected_file['path'])
        
        if not df.empty:
            st.info(f"✅ Found **{len(df)} emails** from **{df['Company'].nunique()} companies**")
            
            # Mostrar preview
            with st.expander("📋 Preview Results", expanded=False):
                st.dataframe(df, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📧 Total Emails", len(df))
            with col2:
                st.metric("🏢 Companies", df['Company'].nunique())
            with col3:
                st.metric("🌐 Domains", df['Email'].apply(lambda x: x.split('@')[1]).nunique())
            
            # CSV Management Section
            st.subheader("🛠️ CSV File Management")
            
            col_mgmt1, col_mgmt2 = st.columns(2)
            
            with col_mgmt1:
                if st.button("🧹 Clean CSV File", help="Remove emails that were already sent", use_container_width=True):
                    with st.status("🧹 Cleaning CSV file...", expanded=True) as clean_status:
                        st.write(f"📁 File: {selected_file['name']}")
                        st.write("🔍 Checking sent emails and removing duplicates...")
                        
                        output_container = st.empty()
                        output_lines = []
                        
                        try:
                            for output_line in clean_csv_file_app(selected_file['path']):
                                output_lines.append(output_line)
                                
                                # Show output
                                display_text = "🧹 CSV Cleaning Progress:\n" + "="*40 + "\n"
                                display_text += '\n'.join(output_lines[-10:])
                                output_container.code(display_text)
                                
                            clean_status.update(label="✅ CSV cleaned!", state="complete")
                            st.success("🎉 CSV file cleaned successfully! Refresh to see updated statistics.")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            clean_status.update(label="❌ Cleaning failed", state="error")
                            st.error(f"❌ Error cleaning CSV: {e}")
            
            with col_mgmt2:
                # Download button for the CSV file
                try:
                    with open(selected_file['path'], 'rb') as file:
                        csv_data = file.read()
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=selected_file['name'],
                        mime="text/csv",
                        use_container_width=True,
                        help="Download the current CSV file"
                    )
                except:
                    st.error("❌ Error reading CSV file")
        else:
            st.warning("No emails found in the selected file.")
            
    except Exception as e:
        st.error(f"Error loading file: {e}")
        
else:
    st.info("No search results found. Run a search first!")

# Step 3: Send Emails
with st.container():
    st.subheader("Step 3: 📤 Send Email Campaign")

if results:
    # Show sent emails statistics
    try:
        # Import the functions to get sent email stats
        import sys
        sys.path.append(str(Path(__file__).parent))
        from email_sender import get_sent_emails_stats, SENT_EMAILS_LOG
        
        if os.path.exists(Path(__file__).parent / SENT_EMAILS_LOG):
            stats = get_sent_emails_stats()
            
            with st.expander("📊 Sent Emails History", expanded=False):
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.metric("🎯 Unique Recipients", stats['total_unique_emails'])
                
                with col_stat2:
                    st.metric("📨 Total Emails Sent", stats['total_sends'])
                
                with col_stat3:
                    languages = stats['by_language']
                    main_lang = max(languages.items(), key=lambda x: x[1]) if languages else ('none', 0)
                    st.metric("🌍 Main Language", f"{main_lang[0].upper()} ({main_lang[1]})")
                
                if stats['by_language']:
                    st.write("**Emails sent by language:**")
                    for lang, count in stats['by_language'].items():
                        lang_names = {'pt': '🇵🇹 Portuguese', 'en': '🇬🇧 English', 'de': '🇩🇪 German'}
                        lang_display = lang_names.get(lang, f"🌐 {lang.upper()}")
                        st.write(f"- {lang_display}: {count} emails")
                
                st.info("💡 **Duplicate Prevention Active:** Emails already sent will be automatically skipped in future campaigns.")
                
                # Add management buttons
                col_mgmt1, col_mgmt2 = st.columns(2)
                
                with col_mgmt1:
                    if st.button("🔄 Refresh Stats", help="Reload sent emails statistics"):
                        st.rerun()
                
                with col_mgmt2:
                    if st.button("⚠️ Clear History", help="Clear all sent emails history - USE WITH CAUTION!", type="secondary"):
                        # Show confirmation
                        if 'confirm_clear_history' not in st.session_state:
                            st.session_state.confirm_clear_history = False
                        
                        if not st.session_state.confirm_clear_history:
                            st.session_state.confirm_clear_history = True
                            st.warning("⚠️ **Are you sure?** This will clear ALL sent email history and allow re-sending to previous recipients!")
                            st.rerun()
                
                # Handle history clearing confirmation
                if st.session_state.get('confirm_clear_history', False):
                    st.error("⚠️ **CONFIRM:** Clear all sent email history?")
                    col_confirm_clear1, col_confirm_clear2 = st.columns(2)
                    
                    with col_confirm_clear1:
                        if st.button("❌ Cancel Clear", use_container_width=True):
                            st.session_state.confirm_clear_history = False
                            st.rerun()
                    
                    with col_confirm_clear2:
                        if st.button("✅ Yes, Clear All", type="primary", use_container_width=True):
                            try:
                                log_path = Path(__file__).parent / SENT_EMAILS_LOG
                                if log_path.exists():
                                    log_path.unlink()
                                    st.success("✅ Sent email history cleared successfully!")
                                else:
                                    st.info("ℹ️ No history file found - already clear.")
                                st.session_state.confirm_clear_history = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error clearing history: {e}")
        
    except ImportError:
        pass  # If import fails, just skip the stats display
    # Test Email Section
    with st.expander("🧪 Test Email (Send Single Email)", expanded=False):
        st.info("📧 **Test Mode:** Send a single email to verify template and delivery")
        
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            test_email = st.text_input(
                "Test Email Address:",
                placeholder="test@example.com",
                help="Enter your email to receive a test email"
            )
            
            test_company = st.text_input(
                "Test Company Name:",
                placeholder="Test Company",
                value="Test Company",
                help="Company name to use in the email template"
            )
        
        with col_test2:
            test_language = st.selectbox(
                "Test Email Language:",
                options=['pt', 'en', 'de'],
                format_func=lambda x: {'pt': '🇵🇹 Portuguese', 'en': '🇬🇧 English', 'de': '🇩🇪 German'}[x],
                help="Choose language for the test email"
            )
            
            # Preview do template
            if st.button("👀 Preview Template", use_container_width=True):
                from email_template import get_email_template
                subject, html_content, text_content = get_email_template(test_company or "Test Company", test_language)
                
                st.subheader("📧 Email Preview")
                st.write(f"**Subject:** {subject}")
                
                with st.expander("View HTML Content", expanded=False):
                    st.code(html_content, language='html')
                
                with st.expander("View Text Content", expanded=False):
                    st.text(text_content)
        
        if st.button("📧 Send Test Email", type="secondary", use_container_width=True):
            if test_email and test_company:
                with st.status("📧 Sending test email...", expanded=True) as test_status:
                    st.write(f"📧 To: {test_email}")
                    st.write(f"🏢 Company: {test_company}")
                    
                    language_names = {'pt': '🇵🇹 Portuguese', 'en': '🇬🇧 English', 'de': '🇩🇪 German'}
                    st.write(f"🌍 Language: {language_names[test_language]}")
                    
                    # Criar arquivo temporário para teste
                    import tempfile
                    import csv
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_file:
                        writer = csv.DictWriter(temp_file, fieldnames=['Company', 'Email', 'URL'])
                        writer.writeheader()
                        writer.writerow({
                            'Company': test_company,
                            'Email': test_email,
                            'URL': 'https://test-website.com'
                        })
                        temp_file_path = temp_file.name
                    
                    # Container para output em tempo real
                    test_output_container = st.empty()
                    test_output_lines = []
                    
                    # Executar envio de teste
                    test_success = True
                    try:
                        for output_line in send_email_campaign(temp_file_path, test_language):
                            test_output_lines.append(output_line)
                            # Mostrar output em tempo real
                            recent_lines = test_output_lines[-8:]
                            
                            display_text = "📧 Test Email Progress:\n" + "="*30 + "\n"
                            display_text += '\n'.join(recent_lines)
                            
                            test_output_container.code(display_text)
                            time.sleep(0.1)
                            
                            if "❌" in output_line:
                                test_success = False
                                
                    except Exception as e:
                        test_success = False
                        test_output_lines.append(f"❌ Exception: {str(e)}")
                        display_text = "📧 Test Email Progress:\n" + "="*30 + "\n"
                        display_text += '\n'.join(test_output_lines[-8:])
                        test_output_container.code(display_text)
                    
                    # Limpar arquivo temporário
                    import os
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                    
                    if test_success:
                        test_status.update(label="✅ Test email sent!", state="complete")
                        st.success("🎉 **Test email sent successfully!** Check your inbox.")
                    else:
                        test_status.update(label="❌ Test email failed", state="error")
                        st.error("❌ Test email failed. Check the output above for details.")
            else:
                st.warning("Please enter both email address and company name!")
    
    st.divider()
    
    # Seleção de idioma
    language_options = {
        'pt': '🇵🇹 Portuguese',
        'en': '🇬🇧 English', 
        'de': '🇩🇪 German'
    }
    
    selected_language = st.selectbox(
        "Choose email language:",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=0
    )
    
    st.info(f"📧 **Email Language:** {language_options[selected_language]}")
    
    # Configurações de envio
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Email Settings")
        st.code("""📨 From: vyqo.eu@gmail.com
⏱️ Delay: 40-90 seconds between emails
📊 Automatic progress tracking
🔄 Professional HTML templates""")
    
    with col2:
        st.subheader("⚠️ Important Notes")
        st.warning("""**Before sending:**
- ✅ Check email language selection
- ✅ Ensure stable internet connection
- ✅ Review email template
- 🔄 Duplicate emails are automatically prevented
- ⚠️ Cannot stop once started""")
        
        st.info("""**Smart Features:**
- 🛡️ **Duplicate Prevention:** Previously sent emails are automatically skipped
- 📊 **Progress Tracking:** Real-time progress with detailed logs
- 🔍 **Email Validation:** Invalid emails are filtered out
- 📈 **Statistics:** Track sent emails history and stats""")
    
    # Arquivo para envio
    if results:
        csv_file = selected_file['path']
        
        # Contar emails
        try:
            df = pd.read_csv(csv_file)
            num_emails = len(df)
        except:
            num_emails = 0
        
        # Initialize session state for campaign confirmation
        if 'show_confirmation' not in st.session_state:
            st.session_state.show_confirmation = False
        if 'campaign_running' not in st.session_state:
            st.session_state.campaign_running = False
        if 'campaign_stopped' not in st.session_state:
            st.session_state.campaign_stopped = False
        if 'sent_emails_this_session' not in st.session_state:
            st.session_state.sent_emails_this_session = []
        
        # Botão de envio
        if st.button(
            f"🚀 Send Email Campaign ({num_emails} emails)",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.campaign_running
        ):
            st.session_state.show_confirmation = True
            st.rerun()
        
        # Show confirmation dialog if needed
        if st.session_state.show_confirmation and not st.session_state.campaign_running:
            # Confirmação
            st.warning("⚠️ **Final Confirmation Required**")
            st.write(f"You are about to send **{num_emails} emails** in **{language_options[selected_language]}**.")
            
            col_confirm1, col_confirm2 = st.columns(2)
            
            with col_confirm1:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_confirmation = False
                    st.success("✅ Campaign cancelled")
                    st.rerun()
            
            with col_confirm2:
                if st.button("✅ Send Now", type="primary", use_container_width=True):
                    st.session_state.show_confirmation = False
                    st.session_state.campaign_running = True
                    st.rerun()
        
        # Execute campaign if confirmed
        if st.session_state.campaign_running:
            
            with st.status("📤 Sending emails...", expanded=True) as status:
                st.write(f"📧 Language: {language_options[selected_language]}")
                st.write(f"📊 Total emails: {num_emails}")
                st.write("⏳ Starting campaign...")
                
                # Add stop button with confirmation
                col_stop1, col_stop2 = st.columns([2, 1])
                
                with col_stop1:
                    st.info("🛑 **Stop Options:** You can stop the campaign and optionally clean sent emails from the CSV file")
                
                with col_stop2:
                    if st.button("🛑 Stop Campaign", type="secondary", use_container_width=True):
                        st.session_state.campaign_stopped = True
                        st.session_state.campaign_running = False
                        st.warning("🛑 Campaign will stop after current email...")
                        st.rerun()
                
                # Container para output em tempo real
                output_container = st.empty()
                progress_bar = st.progress(0)
                output_lines = []
                
                # Executar envio e mostrar output em tempo real
                success = True
                email_count = 0
                
                try:
                    st.write("🔄 **Starting email campaign...**")
                    
                    for output_line in send_email_campaign(csv_file, selected_language, track_sent_emails=True):
                        output_lines.append(output_line)
                        
                        # Count successful emails for progress
                        if "✅ Email enviado com sucesso" in output_line:
                            email_count += 1
                            progress = min(email_count / num_emails, 1.0)
                            progress_bar.progress(progress)
                        
                        # Check if campaign was stopped
                        if st.session_state.get('campaign_stopped', False):
                            break
                        
                        # Show the latest output immediately
                        recent_lines = output_lines[-8:]  # Show last 8 lines
                        
                        # Create display text
                        display_text = f"📊 Progress: {email_count}/{num_emails} emails sent\n"
                        display_text += "="*50 + "\n"
                        display_text += '\n'.join(recent_lines)
                        
                        # Force immediate update
                        output_container.code(display_text, language="text")
                        
                        # Small delay to ensure UI updates
                        time.sleep(0.05)
                        
                        if "❌" in output_line and "Erro ao processar" in output_line:
                            success = False
                            break
                            
                except Exception as e:
                    success = False
                    error_msg = f"❌ Exception: {str(e)}"
                    output_lines.append(error_msg)
                    
                    display_text = f"📊 Progress: {email_count}/{num_emails} emails sent\n"
                    display_text += "="*50 + "\n"
                    display_text += '\n'.join(output_lines[-8:])
                    output_container.code(display_text, language="text")
                    
                    st.error(f"Campaign failed: {str(e)}")
                
                # Reset campaign state after completion
                st.session_state.campaign_running = False
                campaign_was_stopped = st.session_state.get('campaign_stopped', False)
                
                # Handle campaign completion or stopping
                if campaign_was_stopped:
                    st.session_state.campaign_stopped = False  # Reset stop flag
                    status.update(label="🛑 Campaign stopped", state="error")
                    st.warning(f"🛑 **Campaign stopped!** {email_count} emails were sent.")
                    
                    # Option to clean CSV file
                    if email_count > 0:
                        st.subheader("🧹 Clean CSV File")
                        st.info(f"� **Option:** Remove the {email_count} successfully sent emails from the CSV file so you can resume the campaign later with only the remaining recipients.")
                        
                        col_clean1, col_clean2 = st.columns(2)
                        
                        with col_clean1:
                            if st.button("🧹 Yes, Clean CSV File", type="primary", use_container_width=True):
                                with st.status("🧹 Cleaning CSV file...", expanded=True) as clean_status:
                                    st.write("🔄 Removing sent emails from CSV file...")
                                    
                                    try:
                                        for clean_output in clean_csv_file_app(csv_file):
                                            st.write(clean_output)
                                        
                                        clean_status.update(label="✅ CSV cleaned!", state="complete")
                                        st.success("🎉 **CSV file cleaned!** You can now resume the campaign with only the remaining emails.")
                                        st.info("💡 **Tip:** Refresh the page to see the updated email count in Step 2.")
                                        
                                    except Exception as e:
                                        clean_status.update(label="❌ Cleaning failed", state="error")
                                        st.error(f"❌ Error cleaning CSV: {e}")
                        
                        with col_clean2:
                            if st.button("❌ Keep CSV Unchanged", use_container_width=True):
                                st.info("📝 CSV file kept unchanged. You can clean it later using the 'Clean CSV File' button in Step 2.")
                else:
                    # Campaign completed normally
                    if success:
                        status.update(label="✅ Campaign completed!", state="complete")
                        st.success("🎉 **Email campaign completed successfully!**")
                    else:
                        status.update(label="❌ Campaign failed", state="error")
                        st.error("❌ Campaign failed. Check the output above for details.")
                
                # Mostrar output final completo após conclusão
                if output_lines:
                    st.subheader("📋 Complete Campaign Log")
                    with st.expander("View Full Campaign Output", expanded=False):
                        full_output = '\n'.join(output_lines)
                        st.code(full_output, language="text")
else:
    st.info("No email results available. Run a search first!")

# Footer
st.markdown(
    "<div style='text-align: center; color: #666; margin-top: 2rem;'>🔍 ClientHunter CLEAN - Simple Email Collection & Outreach</div>",
    unsafe_allow_html=True
)
