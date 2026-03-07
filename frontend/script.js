// URL base da API
const API_URL = 'http://localhost:5000/api';

// Estado da aplicação
let token = localStorage.getItem('token');
let conversaAtualId = null;

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
    
    errorEl.textContent = '';
    successEl.textContent = '';
    
    try {
        const response = await fetch(`${API_URL}/auth/cadastrar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome, email, senha })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            successEl.textContent = 'Cadastro realizado! Faça login.';
            document.getElementById('cadastro-nome').value = '';
            document.getElementById('cadastro-email').value = '';
            document.getElementById('cadastro-senha').value = '';
            showTab('login');
        } else {
            errorEl.textContent = data.erro || 'Erro ao cadastrar';
        }
    } catch (error) {
        errorEl.textContent = 'Erro de conexão';
    }
}

async function login() {
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-senha').value;
    
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = '';
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, senha })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            
            document.getElementById('auth-area').style.display = 'none';
            document.getElementById('main-area').style.display = 'block';
            
            carregarPerfil();
            carregarContextos();
            carregarHistorico();
        } else {
            errorEl.textContent = data.erro || 'Erro ao fazer login';
        }
    } catch (error) {
        errorEl.textContent = 'Erro de conexão';
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
    
    try {
        const response = await fetch(`${API_URL}/conversas/iniciar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ contexto })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            conversaAtualId = data.conversa_id;
            document.getElementById('conversa-area').style.display = 'flex';
            document.getElementById('feedback-area').style.display = 'none';
            document.getElementById('empty-conversa').style.display = 'none';
            document.getElementById('contexto-atual').textContent = contexto;
            
            document.getElementById('mensagens-container').innerHTML = '';
            adicionarMensagem('ia', data.mensagem_inicial);
        } else {
            alert(data.erro || 'Erro ao iniciar conversa');
        }
    } catch (error) {
        console.error('Erro ao iniciar conversa:', error);
    }
}

async function enviarMensagem() {
    if (!conversaAtualId) {
        alert('Inicie uma conversa primeiro!');
        return;
    }
    
    const input = document.getElementById('mensagem-input');
    const mensagem = input.value.trim();
    
    if (!mensagem) return;
    
    input.value = '';
    adicionarMensagem('aluno', mensagem);
    
    try {
        const response = await fetch(`${API_URL}/conversas/${conversaAtualId}/enviar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mensagem, tipo: 'texto' })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            adicionarMensagem('ia', data.resposta);
        } else {
            adicionarMensagem('ia', 'Erro ao obter resposta');
        }
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        adicionarMensagem('ia', 'Erro de conexão');
    }
}

function adicionarMensagem(remetente, texto) {
    const container = document.getElementById('mensagens-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `mensagem ${remetente}`;
    msgDiv.textContent = texto;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

async function finalizarConversa() {
    if (!conversaAtualId) return;
    
    try {
        const response = await fetch(`${API_URL}/conversas/${conversaAtualId}/finalizar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('feedback-area').style.display = 'block';
            document.getElementById('feedback-positivos').textContent = data.feedback.pontos_positivos;
            document.getElementById('feedback-melhoria').textContent = data.feedback.pontos_melhoria;
            document.getElementById('feedback-nota').textContent = data.feedback.nota_fluencia;
            
            document.getElementById('conversa-area').style.display = 'none';
            document.getElementById('empty-conversa').style.display = 'none';
            
            carregarHistorico();
            conversaAtualId = null;
        }
    } catch (error) {
        console.error('Erro ao finalizar conversa:', error);
    }
}

async function carregarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico/conversas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const container = document.getElementById('historico-container');
            container.innerHTML = '';
            
            if (data.historico.length === 0) {
                container.innerHTML = '<p>Nenhuma conversa ainda.</p>';
                return;
            }
            
            data.historico.forEach(conv => {
                const div = document.createElement('div');
                div.className = 'historico-item';
                div.onclick = () => verDetalhesConversa(conv.conversa_id);
                
                const dataInicio = new Date(conv.data_inicio).toLocaleString();
                
                div.innerHTML = `
                    <strong>${conv.contexto}</strong><br>
                    <small>${dataInicio}</small><br>
                    <small>Nota: ${conv.feedback?.nota_fluencia || 'N/A'}/10</small>
                `;
                
                container.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

async function verDetalhesConversa(conversaId) {
    try {
        const response = await fetch(`${API_URL}/historico/conversas/${conversaId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            let mensagens = '';
            data.mensagens.forEach(m => {
                mensagens += `${m.remetente === 'aluno' ? '👤' : '🤖'} ${m.texto}\n`;
            });
            
            alert(`CONVERSA: ${data.conversa.contexto}\n\n${mensagens}\n\nFEEDBACK:\nPositivos: ${data.feedback?.pontos_positivos}\nMelhorar: ${data.feedback?.pontos_melhoria}\nNota: ${data.feedback?.nota_fluencia}/10`);
        }
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
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
