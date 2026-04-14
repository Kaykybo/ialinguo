// URL base da API
const API_URL = 'http://localhost:5000/api';

// Estado da aplicação
let token = localStorage.getItem('token');
let conversaAtualId = null;
let recognition = null;
let isListening = false;

const apiRequest = async (path, options = {}) => {
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw data;
    }

    return data;
};

const setLoading = (button, loading) => {
    if (!button) return;

    const isSendButton = button.classList.contains('btn-send');
    if (loading) {
        button.dataset.originalText = button.dataset.originalText || button.innerHTML;
        if (!isSendButton) {
            button.innerHTML = 'Carregando...';
        }
        button.disabled = true;
        button.classList.add('btn-loading');
    } else {
        if (!isSendButton) {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
        button.disabled = false;
        button.classList.remove('btn-loading');
    }
};

const showToast = (message, type = 'error') => {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4500);
};

const speakText = (text) => {
    if (!('speechSynthesis' in window) || !text) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';

    // Try to find an American English voice
    const voices = window.speechSynthesis.getVoices();
    const americanVoice = voices.find(voice =>
        voice.lang.startsWith('en-US') &&
        (voice.name.toLowerCase().includes('female') ||
         voice.name.toLowerCase().includes('male') ||
         voice.name.toLowerCase().includes('samantha') ||
         voice.name.toLowerCase().includes('alex'))
    );

    if (americanVoice) {
        utterance.voice = americanVoice;
    }

    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.1; // Slightly higher pitch for more natural sound
    utterance.volume = 1.0;

    window.speechSynthesis.speak(utterance);
};

// Ensure voices are loaded before trying to use them
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        // Voices are now available
    };
}

const initVoiceRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true; // Allow interim results for better UX
    recognition.maxAlternatives = 1;
    recognition.continuous = true; // Keep listening until manually stopped

    recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const input = document.getElementById('mensagem-input');
        if (input) {
            if (finalTranscript) {
                // Append final results
                const currentText = input.value.trim();
                input.value = currentText ? `${currentText} ${finalTranscript.trim()}` : finalTranscript.trim();
                // Don't show toast for each recognition, just accumulate
            }
            // Interim results could be shown differently if needed
        }
    };

    recognition.onerror = (event) => {
        const errorMessage = event.error === 'not-allowed'
            ? 'Permissão para microfone negada'
            : `Erro de voz: ${event.error}`;
        showToast(errorMessage, 'error');
        stopListening();
    };

    recognition.onend = () => {
        // Don't automatically stop - only stop when user clicks
        // This prevents automatic stopping after silence
    };
};

const updateMicButton = () => {
    const button = document.getElementById('mic-button');
    if (!button) return;
    button.classList.toggle('listening', isListening);
};

const startListening = () => {
    if (!recognition) {
        showToast('Reconhecimento de voz não suportado neste navegador.', 'error');
        return;
    }
    try {
        recognition.start();
        isListening = true;
        updateMicButton();
        showToast('🎤 Gravando... Clique novamente para enviar!', 'info');
    } catch (error) {
        showToast('Não foi possível ativar o microfone.', 'error');
    }
};

const stopListening = () => {
    if (!recognition) return;
    try {
        recognition.stop();
    } catch (error) {
        // Ignore errors when stopping
    }
    isListening = false;
    updateMicButton();
};

const toggleListening = () => {
    if (isListening) {
        stopListening();
        // Auto-send the message when stopping recording
        const input = document.getElementById('mensagem-input');
        if (input && input.value.trim()) {
            enviarMensagem();
        } else {
            showToast('Nenhuma mensagem para enviar.', 'warning');
        }
    } else {
        startListening();
    }
};

const openModal = (contentHtml, title = 'Detalhes da conversa') => {
    const overlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');

    if (!overlay || !modalBody || !modalTitle) return;

    modalTitle.textContent = title;
    modalBody.innerHTML = contentHtml;
    overlay.classList.remove('hidden');
};

const closeModal = () => {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.add('hidden');
};

const formatTime = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// ========== FUNÇÕES DE AUTENTICAÇÃO ==========

function showTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.form').forEach(form => form.classList.remove('active'));
    
    if (tab === 'login') {
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('login-form').classList.add('active');
    } else {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('cadastro-form').classList.add('active');
    }
}

async function cadastrar() {
    const nome = document.getElementById('cadastro-nome').value;
    const email = document.getElementById('cadastro-email').value;
    const senha = document.getElementById('cadastro-senha').value;
    
    const errorEl = document.getElementById('cadastro-error');
    const successEl = document.getElementById('cadastro-success');
    const button = document.querySelector('#cadastro-form .btn-main');
    
    errorEl.textContent = '';
    successEl.textContent = '';
    setLoading(button, true);

    try {
        await apiRequest('/auth/cadastrar', {
            method: 'POST',
            body: JSON.stringify({ nome, email, senha })
        });

        successEl.textContent = 'Cadastro realizado! Faça login.';
        showToast('Cadastro realizado! Faça login.', 'success');
        document.getElementById('cadastro-nome').value = '';
        document.getElementById('cadastro-email').value = '';
        document.getElementById('cadastro-senha').value = '';
        showTab('login');
    } catch (error) {
        const message = error?.erro || 'Erro ao cadastrar';
        errorEl.textContent = message;
        showToast(message, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function login() {
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-senha').value;
    
    const errorEl = document.getElementById('login-error');
    const button = document.querySelector('#login-form .btn-main');
    errorEl.textContent = '';
    setLoading(button, true);

    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha })
        });

        token = data.access_token;
        localStorage.setItem('token', token);
        
        document.getElementById('auth-area').style.display = 'none';
        document.getElementById('main-area').style.display = 'block';
        
        carregarPerfil();
        carregarContextos();
        carregarHistorico();
    } catch (error) {
        const message = error?.erro || 'Erro ao fazer login';
        errorEl.textContent = message;
        showToast(message, 'error');
    } finally {
        setLoading(button, false);
    }
}

function logout() {
    token = null;
    localStorage.removeItem('token');
    document.getElementById('auth-area').style.display = 'block';
    document.getElementById('main-area').style.display = 'none';
    conversaAtualId = null;
}

// ========== FUNÇÕES DA API ==========

async function carregarPerfil() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('perfil-nome').textContent = data.nome;
            document.getElementById('perfil-email').textContent = data.email;
            document.getElementById('perfil-nivel').textContent = data.nivel || 'iniciante';
            const avatar = document.getElementById('avatar-inicial');
            if (avatar) avatar.textContent = data.nome.charAt(0).toUpperCase();
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
    }
}

async function carregarContextos() {
    try {
        const response = await fetch(`${API_URL}/conversas/contextos`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('contexto-select');
            select.innerHTML = '<option value="">Selecione um contexto...</option>';
            
            data.contextos.forEach(ctx => {
                const option = document.createElement('option');
                option.value = ctx.id;
                option.textContent = ctx.nome;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar contextos:', error);
    }
}

async function iniciarConversa() {
    const select = document.getElementById('contexto-select');
    const contexto = select.value;
    
    if (!contexto) {
        alert('Selecione um contexto!');
        return;
    }
    
    const button = document.querySelector('.contextos-card .btn-main');
    setLoading(button, true);

    try {
        const data = await apiRequest('/conversas/iniciar', {
            method: 'POST',
            body: JSON.stringify({ contexto })
        });

        conversaAtualId = data.conversa_id;
        document.getElementById('conversa-area').style.display = 'flex';
        document.getElementById('feedback-area').style.display = 'none';
        document.getElementById('empty-conversa').style.display = 'none';
        document.getElementById('contexto-atual').textContent = contexto;
        
        document.getElementById('mensagens-container').innerHTML = '';
        adicionarMensagem('ia', data.mensagem_inicial, 'ia');
    } catch (error) {
        const message = error?.erro || 'Erro ao iniciar conversa';
        showToast(message, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function enviarMensagem() {
    if (!conversaAtualId) {
        showToast('Inicie uma conversa primeiro!', 'error');
        return;
    }
    
    const input = document.getElementById('mensagem-input');
    const mensagem = input.value.trim();
    const button = document.querySelector('.btn-send');
    
    if (!mensagem) return;
    
    input.value = '';
    adicionarMensagem('aluno', mensagem, 'aluno');
    setLoading(button, true);
    
    try {
        const data = await apiRequest(`/conversas/${conversaAtualId}/enviar`, {
            method: 'POST',
            body: JSON.stringify({ mensagem, tipo: 'texto' })
        });
        
        adicionarMensagem('ia', data.resposta, 'ia');
    } catch (error) {
        const message = error?.erro || 'Erro ao enviar mensagem';
        showToast(message, 'error');
        adicionarMensagem('ia', message, 'ia');
    } finally {
        setLoading(button, false);
    }
}

function adicionarMensagem(remetente, texto, tipo = 'texto') {
    const container = document.getElementById('mensagens-container');
    const msgDiv = document.createElement('div');
    const timestamp = formatTime();

    msgDiv.className = `mensagem ${remetente}`;
    msgDiv.innerHTML = `
        <div>${texto}</div>
        <small>${timestamp}</small>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    if (remetente === 'ia') {
        speakText(texto);
    }
}

window.addEventListener('DOMContentLoaded', initVoiceRecognition);

async function finalizarConversa() {
    if (!conversaAtualId) return;
    const button = document.querySelector('.btn-finalizar');
    setLoading(button, true);

    try {
        const data = await apiRequest(`/conversas/${conversaAtualId}/finalizar`, {
            method: 'POST'
        });

        document.getElementById('feedback-area').style.display = 'block';
        document.getElementById('feedback-positivos').textContent = data.feedback.pontos_positivos;
        document.getElementById('feedback-melhoria').textContent = data.feedback.pontos_melhoria;
        document.getElementById('feedback-nota').textContent = data.feedback.nota_fluencia;
        
        document.getElementById('conversa-area').style.display = 'none';
        document.getElementById('empty-conversa').style.display = 'none';
        
        carregarHistorico();
        conversaAtualId = null;
        showToast('Conversa finalizada com sucesso', 'success');
    } catch (error) {
        const message = error?.erro || 'Erro ao finalizar conversa';
        showToast(message, 'error');
    } finally {
        setLoading(button, false);
    }
}

async function carregarHistorico() {
    try {
        const data = await apiRequest('/historico/conversas');
        const container = document.getElementById('historico-container');
        const summary = document.getElementById('historico-summary');

        container.innerHTML = '';
        summary.innerHTML = '';

        const total = data.historico.length;

        if (total === 0) {
            container.innerHTML = '<p class="empty-state">Nenhuma conversa finalizada ainda.</p>';
            return;
        }

        summary.innerHTML = `
            <div class="historico-meta">
                <div>
                    <strong>${total}</strong>
                    <span>conversas finalizadas</span>
                </div>
            </div>
        `;

        data.historico.forEach(conv => {
            const div = document.createElement('div');
            div.className = 'historico-item';
            div.onclick = () => verDetalhesConversa(conv.conversa_id);

            const dataInicio = new Date(conv.data_inicio).toLocaleString();
            const statusLabel = 'Finalizada';
            const score = conv.feedback?.nota_fluencia || '–';

            div.innerHTML = `
                <div class="historico-item-main">
                    <div class="historico-item-title">
                        <strong>${conv.contexto}</strong>
                        <span class="historico-status finalizada">${statusLabel}</span>
                    </div>
                    <div class="historico-item-meta">
                        <span>${dataInicio}</span>
                        <span class="historico-badge">Nota ${score}/10</span>
                    </div>
                </div>
                <div class="historico-item-actions">
                    <button type="button" class="btn-sm">Ver</button>
                </div>
            `;

            container.appendChild(div);
        });
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        showToast('Erro ao carregar histórico', 'error');
    }
}

async function verDetalhesConversa(conversaId) {
    try {
        const data = await apiRequest(`/historico/conversas/${conversaId}`);

        const mensagensHtml = data.mensagens.map(m => {
            const isAluno = m.remetente === 'aluno';
            const label = isAluno ? 'Você' : 'IA';
            const classe = isAluno ? 'mensagem-aluno' : 'mensagem-ia';
            const timestamp = new Date(m.timestamp).toLocaleString();
            return `
                <div class="mensagem ${classe}">
                    <div class="mensagem-header">
                        <strong>${label}</strong>
                        <small>${timestamp}</small>
                    </div>
                    <div class="mensagem-texto">${m.texto}</div>
                </div>
            `;
        }).join('');

        const feedback = data.feedback || {};
        const dataFim = data.conversa.data_fim ? new Date(data.conversa.data_fim).toLocaleString() : 'Em andamento';
        const content = `
            <div class="conversa-detalhes">
                <div class="conversa-info">
                    <h3>Informações da Conversa</h3>
                    <p><strong>Contexto:</strong> ${data.conversa.contexto}</p>
                    <p><strong>Início:</strong> ${new Date(data.conversa.data_inicio).toLocaleString()}</p>
                    <p><strong>Fim:</strong> ${dataFim}</p>
                    <p><strong>Status:</strong> ${data.conversa.status}</p>
                </div>
                <hr>
                <div class="mensagens-container">
                    <h3>Mensagens</h3>
                    ${mensagensHtml}
                </div>
                <hr>
                <div class="feedback-container">
                    <h3>Feedback</h3>
                    <p><strong>Pontos positivos:</strong> ${feedback.pontos_positivos || 'N/A'}</p>
                    <p><strong>A melhorar:</strong> ${feedback.pontos_melhoria || 'N/A'}</p>
                    <p><strong>Nota de Fluência:</strong> ${feedback.nota_fluencia || 'N/A'}/10</p>
                </div>
            </div>
        `;

        openModal(content, `Detalhes da Conversa: ${data.conversa.contexto}`);
    } catch (error) {
        const message = error?.erro || 'Erro ao carregar detalhes';
        showToast(message, 'error');
    }
}

// ========== VERIFICAR SE JÁ ESTÁ LOGADO ==========

if (token) {
    fetch(`${API_URL}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('auth-area').style.display = 'none';
            document.getElementById('main-area').style.display = 'block';
            carregarPerfil();
            carregarContextos();
            carregarHistorico();
        } else {
            localStorage.removeItem('token');
        }
    })
    .catch(() => {
        localStorage.removeItem('token');
    });
}
