// =====================================
// ROBÔ ATENDIMENTO MTECH - VERSÃO HUMANIZADA
// COM LIMITE DE TESTES E PREVENÇÃO DE CONFLITOS
// MENU SEQUENCIAL 1-100
// QR CODE CORRIGIDO PARA ORACLE CLOUD
// =====================================

const { Client, LocalAuth } = require("whatsapp-web.js");
const https = require("https");
const fs = require("fs");
const path = require("path");
const { toFile, toDataURL } = require('qrcode');

// =====================================
// ARQUIVO PARA ARMAZENAR TESTES REALIZADOS
// =====================================
const dadosPath = path.join(__dirname, "testes_realizados.json");
let testesRealizados = {};

// =====================================
// ARQUIVO PARA ARMAZENAR NÚMEROS BLOQUEADOS POR LIGAÇÕES
// =====================================
const bloqueadosPath = path.join(__dirname, "bloqueados_ligacoes.json");
let numerosBloqueadosLigacoes = {};

// =====================================
// NÚMEROS IGNORADOS
// =====================================
const numerosIgnorados = [
    "553899085898@c.us",
    "553899085898",
    "55 38 9908-5898",
    "553899085898",
    "5514982325661@c.us",
    "5514982325661",
    "55 14 98232-5661",
    "5514982325661"
];

function isNumeroIgnorado(numero) {
    if (!numero) return false;
    const numeroLimpo = numero.replace(/[^0-9]/g, '');
    return numerosIgnorados.some(ignorado => {
        const ignoradoLimpo = ignorado.replace(/[^0-9]/g, '');
        return numeroLimpo === ignoradoLimpo || numero === ignorado;
    });
}

// =====================================
// ESTADO DA CONVERSA - QUAL SUBMENU O USUÁRIO ESTÁ
// =====================================
let estadoConversa = new Map();

if (fs.existsSync(bloqueadosPath)) {
  try {
    numerosBloqueadosLigacoes = JSON.parse(fs.readFileSync(bloqueadosPath, "utf8"));
  } catch (e) {
    numerosBloqueadosLigacoes = {};
  }
}

function salvarNumeroBloqueado(numero) {
  numerosBloqueadosLigacoes[numero] = {
    bloqueado_em: new Date().toISOString(),
    motivo: "Ligações repetidas não autorizadas"
  };
  fs.writeFileSync(bloqueadosPath, JSON.stringify(numerosBloqueadosLigacoes, null, 2));
  console.log(`🚫 Número ${numero} bloqueado por ligações repetidas!`);
}

function verificarNumeroBloqueado(numero) {
  return !!numerosBloqueadosLigacoes[numero];
}

if (fs.existsSync(dadosPath)) {
  try {
    testesRealizados = JSON.parse(fs.readFileSync(dadosPath, "utf8"));
  } catch (e) {
    testesRealizados = {};
  }
}

function salvarTesteRealizado(numero, tipoTeste) {
  if (!testesRealizados[numero]) testesRealizados[numero] = [];
  testesRealizados[numero].push({
    tipo: tipoTeste,
    data: new Date().toISOString(),
  });
  fs.writeFileSync(dadosPath, JSON.stringify(testesRealizados, null, 2));
  console.log(`💾 Teste ${tipoTeste} salvo para ${numero}`);
}

function verificarTesteRealizado(numero, tipoTeste) {
  if (!testesRealizados[numero]) return false;
  return testesRealizados[numero].some(teste => teste.tipo === tipoTeste);
}

// =====================================
// SISTEMA DE PAUSA DE 30 MINUTOS (OPÇÃO 6)
// =====================================
let conversasPausadas = new Map();

function pausarConversa(numero, minutos = 30) {
  const fimPausa = Date.now() + (minutos * 60 * 1000);
  conversasPausadas.set(numero, fimPausa);
  console.log(`⏸️ Conversa com ${numero} pausada por ${minutos} minutos.`);
}

function verificarConversaPausada(numero) {
  if (!conversasPausadas.has(numero)) return false;
  const fimPausa = conversasPausadas.get(numero);
  if (Date.now() > fimPausa) {
    conversasPausadas.delete(numero);
    return false;
  }
  return true;
}

// =====================================
// CONTADOR DE LIGAÇÕES PARA BLOQUEIO
// =====================================
let contadorLigacoes = new Map();

function registrarLigacao(numero) {
  const agora = Date.now();
  const dados = contadorLigacoes.get(numero) || { contador: 0, primeiroAvisoEnviado: false, ultimaLigacao: 0 };
  
  if (agora - dados.ultimaLigacao > 5 * 60 * 1000) {
    dados.contador = 0;
    dados.primeiroAvisoEnviado = false;
  }
  
  dados.contador++;
  dados.ultimaLigacao = agora;
  contadorLigacoes.set(numero, dados);
  return dados.contador;
}

// =====================================
// CONFIGURAÇÃO DO CLIENTE - CORRIGIDA PARA RENDER/LINUX
// =====================================
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./session" }),
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox", 
      "--disable-setuid-sandbox", 
      "--disable-dev-shm-usage", 
      "--disable-gpu",
      "--disable-accelerated-2d-canvas",
      "--no-first-run",
      "--no-zygote",
      "--single-process",
      "--disable-default-apps"
    ],
  },
});

// =====================================
// QR CODE CORRIGIDO PARA ORACLE CLOUD
// =====================================
let qrServer = null;

async function mostrarQRCode(qr) {
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║              📲 ESCANEIE O QR CODE ABAIXO                    ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");
    
    try {
        // Método 1: Gerar QR no terminal (simples)
        const { default: generate } = await import('qrcode');
        const qrTerminal = await generate(qr, { type: 'terminal', small: true });
        console.log(qrTerminal);
        
        // Método 2: Salvar como imagem PNG
        await toFile('qrcode.png', qr, { 
            width: 400,
            margin: 2,
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            }
        });
        console.log("\n✅ QR Code SALVO como 'qrcode.png'");
        
        // Método 3: Criar HTML para visualização no navegador
        const qrBase64 = await toDataURL(qr);
        const htmlContent = `<!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QR Code - MTECH Atendimento</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 30px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                    animation: fadeIn 0.5s ease-in;
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                    font-size: 28px;
                }
                .subtitle {
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 16px;
                }
                .qr-container {
                    background: white;
                    padding: 20px;
                    border-radius: 20px;
                    display: inline-block;
                    margin: 20px 0;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }
                img {
                    width: 280px;
                    height: 280px;
                    display: block;
                }
                .status {
                    background: #e8f5e9;
                    color: #2e7d32;
                    padding: 15px;
                    border-radius: 15px;
                    margin-top: 20px;
                    font-weight: bold;
                }
                .steps {
                    text-align: left;
                    margin-top: 25px;
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 15px;
                }
                .steps h3 {
                    color: #333;
                    margin-bottom: 10px;
                }
                .steps ol {
                    margin-left: 20px;
                    color: #555;
                }
                .steps li {
                    margin: 10px 0;
                }
                .footer {
                    margin-top: 20px;
                    color: #999;
                    font-size: 12px;
                }
                .ip-info {
                    background: #e3f2fd;
                    padding: 10px;
                    border-radius: 10px;
                    margin-top: 15px;
                    font-family: monospace;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📱 MTECH ATENDIMENTO</h1>
                <div class="subtitle">WhatsApp Business - Robô Automático</div>
                
                <div class="qr-container">
                    <img src="${qrBase64}" alt="QR Code">
                </div>
                
                <div class="status">
                    ✅ AGUARDANDO CONEXÃO<br>
                    Escaneie o QR Code com o WhatsApp
                </div>
                
                <div class="steps">
                    <h3>📌 COMO CONECTAR:</h3>
                    <ol>
                        <li>Abra o WhatsApp no seu celular</li>
                        <li>Toque nos 3 pontos (⋮) > WhatsApp Web</li>
                        <li>Escaneie o QR Code acima</li>
                        <li>Aguardar confirmação de conexão</li>
                    </ol>
                </div>
                
                <div class="ip-info" id="ipInfo">
                    🔄 Carregando informações de rede...
                </div>
                
                <div class="footer">
                    🔒 Conexão segura e criptografada<br>
                    ⏱️ QR Code expira em 60 segundos
                </div>
            </div>
            
            <script>
                // Tenta obter o IP da máquina
                fetch('https://api.ipify.org?format=json')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('ipInfo').innerHTML = '🌐 IP Público: ' + data.ip + '<br>📱 Acesse este QR Code por qualquer dispositivo na mesma rede';
                    })
                    .catch(() => {
                        document.getElementById('ipInfo').innerHTML = '📱 Escaneie o QR Code diretamente pelo WhatsApp';
                    });
            </script>
        </body>
        </html>`;
        
        fs.writeFileSync('qrcode.html', htmlContent);
        console.log("✅ QR Code HTML salvo como 'qrcode.html'");
        
        // Método 4: Iniciar servidor HTTP para servir o QR
        if (!qrServer) {
            const http = require('http');
            const port = 8080;
            
            qrServer = http.createServer((req, res) => {
                if (req.url === '/' || req.url === '/qrcode') {
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end(htmlContent);
                } else if (req.url === '/qrcode.png') {
                    res.writeHead(200, { 'Content-Type': 'image/png' });
                    res.end(fs.readFileSync('qrcode.png'));
                } else if (req.url === '/status') {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'online', timestamp: Date.now() }));
                } else {
                    res.writeHead(404);
                    res.end();
                }
            });
            
            qrServer.listen(port, '0.0.0.0', () => {
                console.log("\n╔══════════════════════════════════════════════════════════════╗");
                console.log("║              🌐 SERVIDOR QR CODE INICIADO!                    ║");
                console.log("╚══════════════════════════════════════════════════════════════╝");
                console.log(`\n📱 ACESSE NO NAVEGADOR:`);
                console.log(`   → http://localhost:${port}`);
                console.log(`   → http://127.0.0.1:${port}`);
                
                // Tenta pegar IP da máquina
                const { networkInterfaces } = require('os');
                const nets = networkInterfaces();
                for (const name of Object.keys(nets)) {
                    for (const net of nets[name]) {
                        if (net.family === 'IPv4' && !net.internal) {
                            console.log(`   → http://${net.address}:${port}`);
                        }
                    }
                }
                console.log("\n💡 DICA: Se estiver no Cloud, use o IP público ou configure túnel SSH");
                console.log("════════════════════════════════════════════════════════════════\n");
            });
        }
        
        // Salvar QR como texto (fallback)
        fs.writeFileSync('qr_code.txt', qr);
        console.log("✅ QR Code salvo como 'qr_code.txt' (texto puro)");
        
    } catch (err) {
        console.error("❌ Erro ao gerar QR Code:", err.message);
        console.log("\n📝 QR CODE EM TEXTO (copie e cole para decodificar):");
        console.log(qr);
        console.log("\n🔗 Ou use: https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + encodeURIComponent(qr));
    }
    
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║  💡 FORMAS DE ESCANEAR O QR CODE:                            ║");
    console.log("║  1️⃣ Abra o arquivo 'qrcode.html' no navegador               ║");
    console.log("║  2️⃣ Acesse http://localhost:8080 no navegador               ║");
    console.log("║  3️⃣ Baixe a imagem 'qrcode.png' e escaneie                  ║");
    console.log("║  4️⃣ Use um decodificador online com o 'qr_code.txt'        ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");
}

// =====================================
// LINKS DA API (IPTV)
// =====================================
const linksAPI = {
  teste1hr1: "https://starpainel.site/api/chatbot/dqLkwzKLAE/rlKWO3lWzo",
  teste1hr2: "https://starpainel.site/api/chatbot/dqLkwzKLAE/bOxLApQ1Z7",
  teste1hrFutebol: "https://starpainel.site/api/chatbot/dqLkwzKLAE/rdqLk4pDAE",
  teste2hrs: "https://starpainel.site/api/chatbot/dqLkwzKLAE/VpKDa4JLRA",
  teste4hrs: "https://starpainel.site/api/chatbot/dqLkwzKLAE/7loL7VM1XM",
  teste6hrIbo: "https://starpainel.site/api/chatbot/dqLkwzKLAE/o231qyz14q",
  teste12hrSemAdultos: "https://starpainel.site/api/chatbot/dqLkwzKLAE/EMeWe0pDnN",
  teste12hrSamsung: "https://starpainel.site/api/chatbot/dqLkwzKLAE/rlKWO33Wzo",
  teste12hrLg: "https://starpainel.site/api/chatbot/dqLkwzKLAE/lze15A15KB",
  teste12hrAndroid: "https://starpainel.site/api/chatbot/dqLkwzKLAE/nVrW8oDKaN",
  teste12hrIphone: "https://starpainel.site/api/chatbot/dqLkwzKLAE/Yxl1jB1Mjm",
  teste12hrTvBox: "https://starpainel.site/api/chatbot/dqLkwzKLAE/b8K1x6DvGN",
  testePcNotebook: "https://starpainel.site/api/chatbot/dqLkwzKLAE/boQ1Ye1ONY",
  testeRoku: "https://starpainel.site/api/chatbot/dqLkwzKLAE/kg5164DjlQ",
  testeFireStick: "https://starpainel.site/api/chatbot/dqLkwzKLAE/64vLbNLgGn",
};

// =====================================
// VARIÁVEIS DE CONTROLE
// =====================================
let aguardandoProblemaIPTV = new Set();
let aguardandoProblemaInternet = new Set();
let aguardandoRecarga = new Map();
let ultimaInteracao = new Map();

// =====================================
// EVENTOS DO CLIENTE
// =====================================
client.on("qr", async (qr) => {
    console.log("\n🔄 GERANDO QR CODE PARA CONEXÃO...\n");
    await mostrarQRCode(qr);
});

client.on("ready", () => {
  console.log("\n╔══════════════════════════════════════════════════════════════╗");
  console.log("║         ✅ ATENDIMENTO MTECH - Robô conectado!                ║");
  console.log("╚══════════════════════════════════════════════════════════════╝");
  console.log("🤖 Modo humanizado ativado!");
  console.log("📋 Menu sequencial 1-100 ativado!");
  console.log("🔄 Sistema de estado de conversa ativado!");
  console.log("🚫 Bloqueio de ligações ativado!");
  console.log("📱 QR Code server rodando em http://localhost:8080\n");
});

client.on("disconnected", (reason) => {
  console.log("⚠️ Desconectado:", reason);
  if (reason === "NAVIGATION") {
    console.log("🔄 QR Code expirado, novo QR será gerado...");
  }
});

client.on("auth_failure", (msg) => {
    console.error("❌ Falha na autenticação:", msg);
    console.log("🔄 Reinicie o robô para gerar novo QR Code");
});

client.initialize();

// =====================================
// FUNÇÕES UTILITÁRIAS
// =====================================
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

const humanDelay = async () => {
  const tempo = Math.floor(Math.random() * (3000 - 1000 + 1) + 1000);
  await delay(tempo);
};

const simulateTyping = async (chat) => {
  await chat.sendStateTyping();
  await delay(Math.floor(Math.random() * (3000 - 1500 + 1) + 1500));
};

const simulateSeen = async (chat) => {
  await chat.sendSeen();
  await delay(500);
};

function isFlood(numero) {
  const agora = Date.now();
  const ultima = ultimaInteracao.get(numero) || 0;
  if (agora - ultima < 2000) return true;
  ultimaInteracao.set(numero, agora);
  return false;
}

function getSaudacao() {
  const hora = new Date().getHours();
  if (hora >= 5 && hora < 12) return "🌞 Bom dia";
  if (hora >= 12 && hora < 18) return "🌤️ Boa tarde";
  return "🌙 Boa noite";
}

function getSaudacaoProprietario() {
  const hora = new Date().getHours();
  if (hora >= 5 && hora < 12) return "Bom dia";
  if (hora >= 12 && hora < 18) return "Boa tarde";
  return "Boa noite";
}

async function getNomeContato(msg) {
  try {
    const contato = await msg.getContact();
    const nome = contato.pushname || contato.name || contato.number || "Cliente";
    return nome.split(" ")[0];
  } catch (error) {
    return "Cliente";
  }
}

const respostasBoasVindas = [
  "Que bom falar com você! 😊",
  "Fico feliz em atendê-lo(a)! ✨",
  "Estou aqui para ajudar! 💪",
  "Como posso te ajudar hoje? 🎯"
];

const respostasAgradecimento = [
  "Por nada! 😊 Estou aqui sempre que precisar.",
  "Disponha! ✨ Conte comigo.",
  "Imagina! 🚀 Qualquer coisa é só chamar.",
  "Tamo junto! 🤝"
];

const respostasDespedida = [
  "Até mais! 👋 Volte sempre que precisar.",
  "Tchau tchau! ✨ Tenha um ótimo dia.",
  "Falou! 😊 Se precisar, estou por aqui.",
  "Até logo! 🚀"
];

const respostasNaoEntendi = [
  "Hmm, não entendi direito... 🤔",
  "Desculpa, pode repetir? 😅",
  "Não consegui captar sua mensagem... Pode digitar de novo?",
  "Ops! Não reconheci esse comando. 😊"
];

function getRespostaAleatoria(respostas) {
  return respostas[Math.floor(Math.random() * respostas.length)];
}

async function enviarParaProprietario(nomeCliente, numeroCliente) {
  const numeroProprietario = "5583988387164@c.us";
  const saudacao = getSaudacaoProprietario();
  const horario = new Date().toLocaleString('pt-BR');
  
  const mensagem = `${saudacao}, Chefe! 👨‍💼\n\n` +
    `📌 *${nomeCliente}* está solicitando suporte!\n\n` +
    `📱 *Número:* ${numeroCliente}\n` +
    `⏰ *Horário:* ${horario}\n\n` +
    `🔔 *Responda diretamente por aqui para atendê-lo(a).*`;
  
  try {
    await client.sendMessage(numeroProprietario, mensagem);
    console.log(`📨 Mensagem enviada ao proprietário sobre ${nomeCliente}`);
    return true;
  } catch (error) {
    console.error("❌ Erro ao enviar mensagem:", error);
    return false;
  }
}

function chamarAPI(url) {
  return new Promise((resolve) => {
    const urlObj = new URL(url);
    
    const dadosEnvio = {
      mac_address: `00:${Math.floor(Math.random()*256).toString(16).padStart(2,'0')}:${Math.floor(Math.random()*256).toString(16).padStart(2,'0')}:${Math.floor(Math.random()*256).toString(16).padStart(2,'0')}:${Math.floor(Math.random()*256).toString(16).padStart(2,'0')}:${Math.floor(Math.random()*256).toString(16).padStart(2,'0')}`,
      device_id: `DEV_${Date.now()}`,
      timestamp: Date.now()
    };
    
    const postData = JSON.stringify(dadosEnvio);
    
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
        'User-Agent': 'MtechBot/1.0'
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json);
        } catch (e) {
          resolve({ error: true, raw: data });
        }
      });
    });
    
    req.on('error', (error) => {
      resolve({ error: true, message: error.message });
    });
    
    req.write(postData);
    req.end();
  });
}

async function enviarTesteIPTV(chat, link, descricao, nomeCliente, numeroUsuario) {
  if (verificarTesteRealizado(numeroUsuario, "IPTV")) {
    const mensagemBloqueio = `🔒 *Ops, ${nomeCliente}!* 🔒\n\n` +
      `Você já utilizou seu **teste gratuito de IPTV** anteriormente.\n\n` +
      `📌 *Nosso sistema permite apenas 1 teste por cliente.*\n\n` +
      `💎 *Adquira um plano pago para continuar usando:*\n` +
      `• 1 Mês - R$ 29,90\n` +
      `• 3 Meses - R$ 69,90\n` +
      `• 6 Meses - R$ 119,90\n` +
      `• 12 Meses - R$ 199,90\n\n` +
      `👨‍💼 *Digite 100 para falar com o proprietário.*\n\n` +
      `🌟 *Obrigado pela compreensão!*`;
    
    await simulateTyping(chat);
    await client.sendMessage(chat.id._serialized, mensagemBloqueio);
    return;
  }
  
  try {
    await client.sendMessage(chat.id._serialized, 
      `📺 *${descricao}*\n\n🔄 Gerando seu teste, ${nomeCliente}... Aguarde um pouquinho ⏳`);
    
    const resposta = await chamarAPI(link);
    
    if (resposta.username && resposta.password) {
      salvarTesteRealizado(numeroUsuario, "IPTV");
      
      const mensagem = `✅ *TESTE ATIVADO COM SUCESSO!* ✅\n\n` +
        `Olá ${nomeCliente}, seu teste foi gerado com sucesso!\n\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `📺 *DADOS DO TESTE*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `👤 Usuário: ${resposta.username}\n` +
        `🔑 Senha: ${resposta.password}\n` +
        `🔐 Senha Adultos: 0000\n` +
        `⏱️ Expira em: ${resposta.expiresAtFormatted || "N/A"}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
        `📌 *Como instalar na sua TV:*\n\n` +
        `1️⃣ Baixe ASSIST+ ou LAZER PLAY\n` +
        `2️⃣ Código: starplay\n` +
        `3️⃣ Cole Usuário e Senha\n` +
        `4️⃣ Clique em OK e aguarde\n\n` +
        `🔒 *Este é seu ÚNICO teste gratuito!*\n` +
        `💎 *Para mais tempo, digite 100 e fale com o proprietário.*\n\n` +
        `🎯 *Aproveite!*`;
      
      await simulateTyping(chat);
      await client.sendMessage(chat.id._serialized, mensagem);
    }
  } catch (error) {
    console.error("❌ Erro:", error);
    await client.sendMessage(chat.id._serialized, 
      `❌ *Erro ao gerar teste*\n\nDesculpe, ${nomeCliente}. Tivemos um problema técnico.\n\n🔗 Tente manualmente: ${link}`);
  }
}

async function enviarTesteInternet(chat, nomeCliente, numeroUsuario) {
  if (verificarTesteRealizado(numeroUsuario, "INTERNET")) {
    const mensagemBloqueio = `🔒 *Ops, ${nomeCliente}!* 🔒\n\n` +
      `Você já utilizou seu **teste gratuito de Internet Ilimitada** anteriormente.\n\n` +
      `📌 *Nosso sistema permite apenas 1 teste por cliente.*\n\n` +
      `💎 *Adquira um plano pago para continuar usando:*\n` +
      `• 1 Mês - R$ 49,90\n` +
      `• 3 Meses - R$ 129,90\n` +
      `• 6 Meses - R$ 199,90\n` +
      `• 12 Meses - R$ 349,90\n\n` +
      `👨‍💼 *Digite 100 para falar com o proprietário.*\n\n` +
      `🌟 *Obrigado pela compreensão!*`;
    
    await simulateTyping(chat);
    await client.sendMessage(chat.id._serialized, mensagemBloqueio);
    return;
  }
  
  const link = "https://servex.ws/test/a3bf7a43-f70a-43ec-9a68-c72427bbd193";
  
  const mensagemInternet = `🌐 *INTERNET ILIMITADA*\n\n` +
    `✅ *Teste gratuito disponível, ${nomeCliente}!* ✅\n\n` +
    `🔗 *Acesse o link abaixo e clique em "Gerar Teste Grátis":*\n\n` +
    `${link}\n\n` +
    `📌 *Instruções:*\n` +
    `1️⃣ Clique no link acima\n` +
    `2️⃣ Clique em "Gerar Teste Grátis"\n` +
    `3️⃣ Seu teste será gerado automaticamente\n\n` +
    `🔒 *ATENÇÃO: Você tem direito a APENAS 1 teste gratuito!*\n\n` +
    `💎 *Após o teste, adquira seu plano (opção 100)*\n\n` +
    `🔧 *Precisa de ajuda?* Digite 5 para suporte.`;
  
  salvarTesteRealizado(numeroUsuario, "INTERNET");
  
  await simulateTyping(chat);
  await client.sendMessage(chat.id._serialized, mensagemInternet);
}

async function enviarInfoApps(chat, nomeCliente) {
  const mensagemApps = `📱 *APLICATIVOS IPTV - STARPLAY* 📱

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 *APLICATIVO NA PLAY STORE*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✴️ *RP725* ✴️
Código: 26236258
🔗 https://play.google.com/store/apps/details?id=rp.rp725&pcampaignid=web_share

✴️ *FUNPLAY* ✴️
🔗 https://play.google.com/store/apps/details?id=com.funplusplay.app&pcampaignid=web_share

✴️ *VUSER* ✴️
🔗 https://play.google.com/store/apps/details?id=app.vuser.mmx

✴️ *BOX PLAYER OFFICIAL* ✴️
🔗 https://play.google.com/store/apps/details?id=rp.boxplayerofficial&hl=pt_BR

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🫱🏻‍🫲🏾 *APLICATIVOS PARCEIROS E PAGOS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔖 *APLICATIVOS PARCEIROS:* 
São aplicativos que são pagos no mercado de IPTV, porém a STARPLAY tem parceria e sai totalmente gratuito para vocês.

🔖 *APLICATIVOS PAGOS:* 
São aplicativos que liberam alguns dias de teste gratuito (3, 7, 14 dias em média). Para continuar a utilização do serviço após o período de teste, é necessário fazer a ativação da Licença anual/mensal diretamente pelo site oficial.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *APPS PARCEIROS GRATÍS NAS SMART TV 2021 a 2026*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 *Samsung:* Blessed Player, Lazer Play, Fun Play, Focox play, Assist+ ou Galax Play, Playsim, Xcloudtv e Maxplayer
📺 *LG:* Blessed Player, Lazer Play, Fun Play, Assist+, Playsim, Xcloudtv, Maxplayer, Box Play e Magic Play
📺 *Roku:* Blessed Player, Lazer Play, Fun Play, Assist+, Playsim, Xcloudtv, Maxplayer, Box Play e Magic Play
📺 *Android TV:* Blessed Player, Fun Play, Max player

⚠️ *OBS:* Tem informações detalhada dos apps na tela de inicio em TESTES RÁPIDO.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *APPS PAGOS MAIS USADOS NAS SMART TV*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 *Samsung e LG:*
IBO PLAYER | VU PLAYER PRO | SMART ONE | CR7 PLAYER | BOB PLAYER | QUICK PLAYER | HOT PLAYER

📺 *Android TV e TCL Android:*
Os mesmos das smart TV Samsung e LG + IBO PLAYER PRO | HOT PLAYER

📺 *Roku:*
IBO PLAYER PRO | CR7 PLAYER | QUICK PLAYER | RIVOLUT PLAYER | VU PLAYER PRO | IPTV PLAYER.IO | HOT PLAYER

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛍️ *LOJAS NTDOWN E DOWNLOADER*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 *NTdown - Play Store:*
🔗 https://play.google.com/store/apps/details?id=link.ntdev.ntdw

*Códigos NTdown:*

STAR XC ORIGINAL: 18932
STAR LT: 49442
STAR IBO MAC: 86171
STAR IBO DNS: 88744
STAR ONE: 65865
STAR V3: 16813
STAR TIVIMATE: 28471
STAR FLIX: 73497
STAR LEGACY: 49629
POTTER PLUS: 464384
ASSIST+: 77646
PLAYSIM: 72853
LAZER PLAY: 56281
FUNPLAY: 36398

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 *DOWNLOADER*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 https://play.google.com/store/apps/details?id=com.esaba.downloader&pcampaignid=web_share

*Códigos Downloader:*

STAR XC ORIGINAL: 473533
STAR LT: 328123
STAR IBO MAC: 198905 (site: https://staribo.top/login)
STAR IBO DNS: 337692
STAR ONE: 335992
STAR V3: 380557
STAR TIVIMATE: 5682045
STAR FLIX: 3865578
STAR LEGACY: 2769656
UNITV: 4925375
ASSIST+: 3091788
PLAYSIM: 7275096
LAZER PLAY: 9101816
FUNPLAY: 257286

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Digite 0 para voltar ao Menu Principal*
1️⃣0️⃣0️⃣ *Para falar com o Proprietário*`;

  await simulateTyping(chat);
  await client.sendMessage(chat.id._serialized, mensagemApps);
}

async function suporteIPTV(chat, problema, nomeCliente) {
  await simulateTyping(chat);
  
  const resposta = `🔧 *Suporte IPTV - ${nomeCliente}* 🔧\n\n` +
    `Anotamos seu problema: "${problema}"\n\n` +
    `✅ *Um atendente especializado irá te ajudar em breve.*\n\n` +
    `📞 *Se for urgente, digite 100 para falar com o proprietário agora.*`;
  
  await client.sendMessage(chat.id._serialized, resposta);
}

async function suporteInternet(chat, problema, nomeCliente) {
  await simulateTyping(chat);
  
  const resposta = `🔧 *Suporte Internet - ${nomeCliente}* 🔧\n\n` +
    `Anotamos sua dificuldade: "${problema}"\n\n` +
    `✅ *Um especialista irá te ajudar em breve.*\n\n` +
    `📞 *Urgente?* Digite 100 para falar com o proprietário.`;
  
  await client.sendMessage(chat.id._serialized, resposta);
}

// =====================================
// CONFIGURAÇÕES DE RECARGAS
// =====================================
// Mapeamento de valores: o que o cliente paga e quanto recebe em créditos
const recargasConfig = {
    "VIVO": {
        "10": { paga: 13.00, recebe: 15.00 },
        "20": { paga: 15.00, recebe: 20.00 },
        "30": { paga: 19.00, recebe: 25.00 },
        "50": { paga: 20.00, recebe: 30.00 },
        "100": { paga: 0.00, recebe: 0.00 }
    },
    "TIM": {
        "10": { paga: 0.00, recebe: 0.00 },
        "20": { paga: 0.00, recebe: 0.00 },
        "30": { paga: 0.00, recebe: 0.00 },
        "50": { paga: 0.00, recebe: 0.00 },
        "100": { paga: 0.00, recebe: 0.00 }
    },
    "CLARO": {
        "10": { paga: 15.00, recebe: 10.00 },
        "20": { paga: 16.00, recebe: 20.00 },
        "30": { paga: 20.00, recebe: 30.00 },
        "50": { paga: 21.00, recebe: 50.00 },
        "100": { paga: 0.00, recebe: 0.00 }
    }
};

// =====================================
// FUNÇÃO PARA RECARGAS DE CHIP
// =====================================
async function enviarMensagemRecarga(chat, operadora, valor, nomeCliente) {
  const config = recargasConfig[operadora]?.[valor] || { paga: parseFloat(valor), recebe: parseFloat(valor) };
  const valorPaga = config.paga.toFixed(2).replace('.', ',');
  const valorRecebe = config.recebe.toFixed(2).replace('.', ',');
  
  const mensagem = `📱 *RECARGA ${operadora}* 📱

Olá ${nomeCliente}! ✅

✅ *Recarga ${operadora}*
💰 *Você paga:* R$ ${valorPaga}
📱 *Recebe:* R$ ${valorRecebe} em créditos

🔗 *Link para pagamento:*
https://payment.mtech.com.br/recarga?op=${operadora.toLowerCase()}&value=${valor}

📌 *Instruções:*
1️⃣ Clique no link acima
2️⃣ Escolha a forma de pagamento (PIX, Cartão, Boleto)
3️⃣ Após o pagamento, a recarga é feita em até 5 minutos
4️⃣ Você receberá a confirmação no seu WhatsApp

💡 *Dúvidas?* Digite 0 para voltar ou 100 para falar com o proprietário

🎯 *Obrigado pela preferência!*`;

  await simulateTyping(chat);
  await client.sendMessage(chat.id._serialized, mensagem);
}

// =====================================
// FUNÇÃO PARA BLOQUEAR LIGAÇÕES
// =====================================
async function handleCall(call) {
  try {
    const numeroUsuario = call.from.split("@")[0];
    console.log(`📞 Ligação recebida de ${numeroUsuario} - REJEITANDO...`);
    await call.reject();
    
    if (verificarNumeroBloqueado(numeroUsuario)) return;
    
    const contagem = registrarLigacao(numeroUsuario);
    const dados = contadorLigacoes.get(numeroUsuario);
    
    if (contagem === 1 && !dados.primeiroAvisoEnviado) {
      dados.primeiroAvisoEnviado = true;
      const aviso = `🔊 *ATENÇÃO!* 🔊\n\n` +
        `📵 *Ligações NÃO são permitidas!*\n\n` +
        `✅ *Utilize apenas MENSAGENS DE TEXTO* para ser atendido.\n\n` +
        `📱 *Digite "menu" para ver todas as opções.*\n\n` +
        `🔒 *Se continuar ligando, seu número será BLOQUEADO.*`;
      await client.sendMessage(call.from, aviso);
    } else if (contagem === 2) {
      const avisoFinal = `🔴 *ÚLTIMO AVISO!* 🔴\n\n` +
        `❌ *Esta é sua SEGUNDA ligação não autorizada!*\n\n` +
        `⚠️ *PRÓXIMA LIGAÇÃO = BLOQUEIO PERMANENTE!*`;
      await client.sendMessage(call.from, avisoFinal);
    } else if (contagem >= 3) {
      salvarNumeroBloqueado(numeroUsuario);
      const msgBloqueio = `🚫 *NÚMERO BLOQUEADO PERMANENTEMENTE!* 🚫\n\n` +
        `❌ *Você realizou ${contagem} ligações não autorizadas.*\n\n` +
        `📵 *Este canal é APENAS para MENSAGENS DE TEXTO!*`;
      await client.sendMessage(call.from, msgBloqueio);
    }
  } catch (error) {
    console.error("❌ Erro ao processar ligação:", error);
  }
}

client.on("call", async (call) => {
  try {
    await call.reject();
    await handleCall(call);
  } catch (error) {
    console.error("❌ Erro ao rejeitar ligação:", error);
  }
});

// =====================================
// MENUS
// =====================================

const menuPrincipal = `*📱 MENU PRINCIPAL - MTECH* 📱

*${getSaudacao()}! Digite o número da opção:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ → 📺 TESTES IPTV
2️⃣ → 🌐 TESTE INTERNET ILIMITADA
3️⃣ → 📱 RECARGAS DE CHIP
4️⃣ → 🔧 SUPORTE IPTV
5️⃣ → 🔧 SUPORTE INTERNET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣0️⃣ → 📋 CONSULTAS
2️⃣0️⃣ → 👤 MINHA CONTA
3️⃣0️⃣ → 🎁 INDICAR AMIGOS
4️⃣0️⃣ → ❓ AJUDA
5️⃣0️⃣ → ⚖️ TERMOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6️⃣ → ⏸️ PAUSAR ATENDIMENTO (30min)
1️⃣0️⃣0️⃣ → 👨‍💼 FALAR COM PROPRIETÁRIO

📌 *Digite o número da opção desejada*`;

const menuIPTV = `📺 *MENU IPTV - STAR PLAY* 📺

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 *TESTES RÁPIDOS (1-6)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ → 1 Hora (Completo)
2️⃣ → 1 Hora (User/Senha)
3️⃣ → 1 Hora (Futebol/Lutas)
4️⃣ → 2 Horas
5️⃣ → 4 Horas
6️⃣ → 6 Horas (IBO MAC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟣 *TESTES 12 HORAS (7-15)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣ → 12H Sem Adultos
8️⃣ → 12H Smart Samsung
9️⃣ → 12H Smart LG
1️⃣0️⃣ → 12H Android Celular
1️⃣1️⃣ → 12H iPhone (iOS)
1️⃣2️⃣ → 12H TV Box
1️⃣3️⃣ → 12H PC/Notebook
1️⃣4️⃣ → 12H Roku TV
1️⃣5️⃣ → 12H Fire Stick

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ *CONFIGURAÇÕES (16-20)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣6️⃣ → APP ASSIST+ (Download)
1️⃣7️⃣ → APP LAZER PLAY (Download)
1️⃣8️⃣ → COMO INSTALAR
1️⃣9️⃣ → DICAS E SOLUÇÕES
2️⃣0️⃣ → CONFIGURAÇÕES AVANÇADAS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 *Você tem direito a apenas 1 teste gratuito*
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

const menuInternet = `🌐 *MENU INTERNET ILIMITADA* 🌐

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📶 *TESTES E PLANOS (21-25)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣1️⃣ → Teste Grátis Internet
2️⃣2️⃣ → Plano 1 Mês (R$ 20,00)
2️⃣3️⃣ → Plano 3 Meses (R$ 60,00)
2️⃣4️⃣ → Plano 6 Meses (R$ 120,00)
2️⃣5️⃣ → Plano 12 Meses (R$ 240,00)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 *CONFIGURAÇÕES (26-30)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣6️⃣ → Configurar no Android
2️⃣7️⃣ → Configurar no iPhone
2️⃣8️⃣ → Configurar no PC
2️⃣9️⃣ → Configurar no Roteador
3️⃣0️⃣ → Dicas para melhor velocidade

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *SOLUÇÃO DE PROBLEMAS (31-35)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣1️⃣ → Internet lenta
3️⃣2️⃣ → Conexão caindo
3️⃣3️⃣ → Não consigo conectar
3️⃣4️⃣ → VPN/Proxy não funciona
3️⃣5️⃣ → Erro de autenticação

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

const menuRecargas = `📱 *MENU RECARGAS DE CHIP* 📱

*${getSaudacao()}! Escolha a OPERADORA:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 *OPERADORAS DISPONÍVEIS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣6️⃣ → 📱 VIVO
3️⃣7️⃣ → 📱 TIM
3️⃣8️⃣ → 📱 CLARO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *APÓS ESCOLHER A OPERADORA, SELECIONE O VALOR:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣1️⃣ → R$ 10,00
4️⃣2️⃣ → R$ 20,00
4️⃣3️⃣ → R$ 30,00
4️⃣4️⃣ → R$ 50,00
4️⃣5️⃣ → R$ 100,00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *SERVIÇOS ADICIONAIS (46-50)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣6️⃣ → Recarga de Jogos (PicPay)
4️⃣7️⃣ → Recarga Netflix/Spotify
4️⃣8️⃣ → Histórico de Recargas
4️⃣9️⃣ → Saldo de Bônus
5️⃣0️⃣ → Criar Conta no Site

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário

📌 *Digite primeiro a OPERADORA (36-38) e depois o VALOR (41-45)*`;

const menuConsultas = `📋 *MENU CONSULTAS* 📋

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *INFORMAÇÕES (51-55)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣1️⃣ → Planos IPTV Completos
5️⃣2️⃣ → Planos Internet Ilimitada
5️⃣3️⃣ → Combos Promocionais
5️⃣4️⃣ → Pagamentos Aceitos
5️⃣5️⃣ → Prazo de Entrega

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 *PROMOÇÕES (56-60)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣6️⃣ → Promoção Black Friday
5️⃣7️⃣ → Desconto no PIX
5️⃣8️⃣ → Indicação Premiada
5️⃣9️⃣ → Cliente VIP
6️⃣0️⃣ → Sorteios Mensais

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

const menuAjuda = `❓ *MENU AJUDA E SUPORTE* ❓

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆘 *FAQ (61-70)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6️⃣1️⃣ → Como funciona o teste?
6️⃣2️⃣ → Como instalar na TV?
6️⃣3️⃣ → Como instalar no Celular?
6️⃣4️⃣ → Como instalar no PC?
6️⃣5️⃣ → APP não abre, e agora?
6️⃣6️⃣ → Canais travando?
6️⃣7️⃣ → Senha não funciona?
6️⃣8️⃣ → Como renovar o plano?
6️⃣9️⃣ → Perdi meus dados!
7️⃣0️⃣ → Como cancelar?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 *CONTATO (71-75)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣1️⃣ → WhatsApp Suporte
7️⃣2️⃣ → Telefone Comercial
7️⃣3️⃣ → E-mail Contato
7️⃣4️⃣ → Horário de Atendimento
7️⃣5️⃣ → Reclamações/Sugestões

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

const menuConfiguracoes = `⚙️ *MENU CONFIGURAÇÕES* ⚙️

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 *AJUSTES TÉCNICOS (76-85)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣6️⃣ → Configurar DNS (Google)
7️⃣7️⃣ → Configurar DNS (Cloudflare)
7️⃣8️⃣ → Limpar Cache do APP
7️⃣9️⃣ → Atualizar APP Manual
8️⃣0️⃣ → Forçar Parada APP
8️⃣1️⃣ → Teste de Velocidade
8️⃣2️⃣ → Configurar VPN
8️⃣3️⃣ → Proxy Configuração
8️⃣4️⃣ → Firewall Liberação
8️⃣5️⃣ → Logs de Erro

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *APPS COMPATÍVEIS (86-90)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8️⃣6️⃣ → ASSIST+ Configuração
8️⃣7️⃣ → LAZER PLAY Configuração
8️⃣8️⃣ → IPTV Smarters Config
8️⃣9️⃣ → TiviMate Config
9️⃣0️⃣ → OTT Navigator Config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

const menuTermos = `📜 *MENU TERMOS E POLÍTICAS* 📜

*DIGITE O NÚMERO DA OPÇÃO:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ *DOCUMENTOS (91-99)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9️⃣1️⃣ → Termos de Uso
9️⃣2️⃣ → Política de Privacidade
9️⃣3️⃣ → Garantia e Reembolso
9️⃣4️⃣ → Política de Cancelamento
9️⃣5️⃣ → Uso Aceitável
9️⃣6️⃣ → Direitos do Consumidor
9️⃣7️⃣ → Segurança de Dados
9️⃣8️⃣ → Cookies e Rastreamento
9️⃣9️⃣ → Atualizações do Serviço

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0️⃣ → Voltar ao Menu Principal
1️⃣0️⃣0️⃣ → Falar com Proprietário`;

// =====================================
// MAPEAMENTO DOS TESTES IPTV (1 A 15)
// =====================================
const getTestePorNumero = (num) => {
  const testes = {
    1: { link: linksAPI.teste1hr1, desc: "🔴 TESTE 1 HORA (Completo)" },
    2: { link: linksAPI.teste1hr2, desc: "🔴 TESTE 1 HORA (User/Senha)" },
    3: { link: linksAPI.teste1hrFutebol, desc: "⚽ TESTE 1 HORA FUTEBOL" },
    4: { link: linksAPI.teste2hrs, desc: "🟠 TESTE 2 HORAS" },
    5: { link: linksAPI.teste4hrs, desc: "🟢 TESTE 4 HORAS" },
    6: { link: linksAPI.teste6hrIbo, desc: "🔵 TESTE 6 HORAS" },
    7: { link: linksAPI.teste12hrSemAdultos, desc: "🟣 12H SEM ADULTOS" },
    8: { link: linksAPI.teste12hrSamsung, desc: "📺 12H SAMSUNG" },
    9: { link: linksAPI.teste12hrLg, desc: "📺 12H LG" },
    10: { link: linksAPI.teste12hrAndroid, desc: "📱 12H ANDROID" },
    11: { link: linksAPI.teste12hrIphone, desc: "📱 12H IPHONE" },
    12: { link: linksAPI.teste12hrTvBox, desc: "📦 12H TV BOX" },
    13: { link: linksAPI.testePcNotebook, desc: "💻 12H PC" },
    14: { link: linksAPI.testeRoku, desc: "🎮 12H ROKU" },
    15: { link: linksAPI.testeFireStick, desc: "🔥 12H FIRE STICK" },
  };
  return testes[num];
};

// =====================================
// FUNÇÃO PARA RESETAR O ESTADO DA CONVERSA
// =====================================
function resetarEstadoConversa(numero) {
  estadoConversa.set(numero, { menu: "principal" });
  console.log(`🔄 Estado resetado para ${numero} - Menu principal`);
}

// =====================================
// PROCESSAMENTO DE MENSAGENS
// =====================================
client.on("message", async (msg) => {
  try {
    if (msg.from && msg.from.endsWith("@g.us")) return;
    if (msg.author && msg.author.endsWith("@broadcast")) return;
    
    if (isNumeroIgnorado(msg.from) || isNumeroIgnorado(msg.author)) {
      console.log(`🚫 Mensagem ignorada de número bloqueado: ${msg.from}`);
      return;
    }
    
    const chat = await msg.getChat();
    if (chat.isGroup || chat.isBroadcast) return;
    
    const numeroUsuario = msg.from.split("@")[0];
    const nomeCliente = await getNomeContato(msg);
    const saudacao = getSaudacao();
    
    let texto = msg.body ? msg.body.trim() : "";
    
    console.log(`📨 Mensagem de ${nomeCliente} (${numeroUsuario}): "${texto}" | Estado: ${estadoConversa.get(numeroUsuario)?.menu || "none"}`);
    
    if (verificarConversaPausada(numeroUsuario)) return;
    if (verificarNumeroBloqueado(numeroUsuario)) return;
    if (isFlood(numeroUsuario)) return;
    
    await simulateSeen(chat);
    await humanDelay();
    
    const aguardandoIPTV = aguardandoProblemaIPTV.has(numeroUsuario);
    const aguardandoInternet = aguardandoProblemaInternet.has(numeroUsuario);
    
    if (!estadoConversa.has(numeroUsuario)) {
      estadoConversa.set(numeroUsuario, { menu: "principal" });
    }
    
    const estadoAtual = estadoConversa.get(numeroUsuario);
    
    // =====================================
    // SUPORTE (prioridade máxima)
    // =====================================
    if (aguardandoIPTV && !texto.startsWith("/") && !/^[0-9]+$/.test(texto)) {
      await suporteIPTV(chat, texto, nomeCliente);
      aguardandoProblemaIPTV.delete(numeroUsuario);
      return;
    }
    
    if (aguardandoInternet && !texto.startsWith("/") && !/^[0-9]+$/.test(texto)) {
      await suporteInternet(chat, texto, nomeCliente);
      aguardandoProblemaInternet.delete(numeroUsuario);
      return;
    }
    
    // =====================================
    // COMANDOS GLOBAIS
    // =====================================
    if (texto === "0") {
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    if (texto === "/menu" || texto === "menu" || texto === "/start") {
      resetarEstadoConversa(numeroUsuario);
      aguardandoProblemaIPTV.delete(numeroUsuario);
      aguardandoProblemaInternet.delete(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `${saudacao}, ${nomeCliente}! 👋`);
      await humanDelay();
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `Que bom falar com você! 😊`);
      await humanDelay();
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    // =====================================
    // SAUDAÇÃO
    // =====================================
    if (/^(oi|olá|ola|bom dia|boa tarde|boa noite|eae|opa|oie)$/i.test(texto) && estadoAtual.menu === "principal") {
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `${saudacao}, ${nomeCliente}! 👋`);
      await humanDelay();
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `Que bom falar com você! 😊`);
      await humanDelay();
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    // =====================================
    // DESPEDIDAS
    // =====================================
    if (/^(tchau|bye|até mais|falou|flw|xau|sair)$/i.test(texto)) {
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, getRespostaAleatoria(respostasDespedida));
      return;
    }
    
    // =====================================
    // AGRADECIMENTOS
    // =====================================
    if (/(obrigado|valeu|brigado|thanks|obg|vlw|agradeço)/i.test(texto)) {
      await simulateTyping(chat);
      await client.sendMessage(msg.from, getRespostaAleatoria(respostasAgradecimento));
      return;
    }
    
    // =====================================
    // PROCESSAMENTO NUMÉRICO POR ESTADO
    // =====================================
    const opcao = parseInt(texto);
    
    if (isNaN(opcao)) {
      if (texto.length > 0 && !texto.startsWith("/")) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `${getRespostaAleatoria(respostasNaoEntendi)}\n\n📌 *Digite "menu" para ver as opções.*`);
      }
      return;
    }
    
    // =====================================
    // OPÇÃO 6 - PAUSAR
    // =====================================
    if (opcao === 6) {
      pausarConversa(numeroUsuario, 30);
      console.log(`⏸️ Cliente ${numeroUsuario} ativou pausa de 30 minutos`);
      return;
    }
    
    // =====================================
    // OPÇÃO 100 - PROPRIETÁRIO
    // =====================================
    if (opcao === 100) {
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `👨‍💼 *FALAR COM PROPRIETÁRIO*\n\nOlá ${nomeCliente}, seu pedido foi encaminhado!\n⏱️ *O proprietário irá entrar em contato em breve.*`);
      await enviarParaProprietario(nomeCliente, numeroUsuario);
      return;
    }
    
    // =====================================
    // PROCESSAMENTO POR ESTADO ATUAL
    // =====================================
    
    // ESTADO: MENU IPTV (opções 1-20)
    if (estadoAtual.menu === "iptv") {
      const testeInfo = getTestePorNumero(opcao);
      if (testeInfo && opcao >= 1 && opcao <= 15) {
        await enviarTesteIPTV(chat, testeInfo.link, testeInfo.desc, nomeCliente, numeroUsuario);
        return;
      }
      
      if (opcao >= 16 && opcao <= 20) {
        await simulateTyping(chat);
        const configs = {
          16: `📲 *APP ASSIST+*\n\n🔗 Download: https://bit.ly/assist-plus\n📌 Código: starplay`,
          17: `📲 *APP LAZER PLAY*\n\n🔗 Download: https://bit.ly/lazer-play\n📌 Código: starplay`,
          18: `📺 *COMO INSTALAR*\n\n1️⃣ Baixe o app\n2️⃣ Instale na sua TV/Celular\n3️⃣ Abra e digite: starplay\n4️⃣ Cole usuário e senha`,
          19: `💡 *DICAS*\n\n• Limpe o cache\n• Reinicie o dispositivo\n• Configure DNS 8.8.8.8`,
          20: `⚙️ *CONFIGURAÇÕES AVANÇADAS*\n\n• Servidor: http://starplay.tv\n• Porta: 8080`
        };
        await client.sendMessage(msg.from, configs[opcao]);
        return;
      }
      
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `📺 *Opção inválida no Menu IPTV*\n\nDigite 1-20 ou 0 para voltar.\n\n${menuIPTV}`);
      return;
    }
    
    // ESTADO: MENU INTERNET (opções 21-35)
    if (estadoAtual.menu === "internet") {
      if (opcao === 21) {
        await enviarTesteInternet(chat, nomeCliente, numeroUsuario);
        return;
      }
      if (opcao >= 22 && opcao <= 25) {
        await simulateTyping(chat);
        const planos = {
          22: "1 Mês - R$ 49,90", 23: "3 Meses - R$ 129,90",
          24: "6 Meses - R$ 199,90", 25: "12 Meses - R$ 349,90"
        };
        await client.sendMessage(msg.from, `💎 *PLANO ${planos[opcao]}*\n\n✅ Para adquirir, digite 100.`);
        return;
      }
      if (opcao >= 26 && opcao <= 35) {
        await simulateTyping(chat);
        const configs = {
          26: "📱 *ANDROID*\nBaixe HTTP Injector e importe o arquivo",
          27: "📱 *IPHONE*\nBaixe OpenVPN e importe o arquivo",
          28: "💻 *PC*\nBaixe OpenVPN e configure",
          29: "📡 *ROTEADOR*\nAcesse 192.168.0.1 e configure a VPN",
          30: "⚡ *DICAS*\nUse cabo de rede e evite muitas conexões",
          31: "🐢 *LENTA*\nReinicie o modem e troque o DNS",
          32: "🔌 *CAINDO*\nVerifique cabos e reinicie",
          33: "❌ *NÃO CONECTA*\nVerifique usuário/senha",
          34: "🔒 *VPN NÃO FUNCIONA*\nDesative o firewall",
          35: "⚠️ *ERRO*\nTeste pode ter expirado"
        };
        await client.sendMessage(msg.from, configs[opcao] || "🔧 Configuração em breve");
        return;
      }
      
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `🌐 *Opção inválida no Menu Internet*\n\nDigite 21-35 ou 0 para voltar.\n\n${menuInternet}`);
      return;
    }
    
    // ESTADO: MENU RECARGAS (opções 36-50)
    if (estadoAtual.menu === "recargas") {
      // Operadoras (36-38 apenas VIVO, TIM, CLARO)
      const operadorasMap = {
        36: "VIVO", 37: "TIM", 38: "CLARO"
      };
      
      // Valores (41-45)
      const valoresMap = {
        41: "10", 42: "20", 43: "30", 44: "50", 45: "100"
      };
      
      // Se escolheu uma operadora
      if (opcao >= 36 && opcao <= 38) {
        const operadora = operadorasMap[opcao];
        estadoConversa.set(numeroUsuario, { menu: "recargas", operadora_selecionada: operadora });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `📱 *${operadora} selecionada!* ✅\n\nAgora digite o VALOR da recarga:\n\n4️⃣1️⃣ → R$ 10,00\n4️⃣2️⃣ → R$ 20,00\n4️⃣3️⃣ → R$ 30,00\n4️⃣4️⃣ → R$ 50,00\n4️⃣5️⃣ → R$ 100,00\n\n0️⃣ → Voltar ao Menu Recargas`);
        return;
      }
      
      // Se escolheu um valor e já tem operadora selecionada
      if (opcao >= 41 && opcao <= 45 && estadoAtual.operadora_selecionada) {
        const operadora = estadoAtual.operadora_selecionada;
        const valor = valoresMap[opcao];
        await enviarMensagemRecarga(chat, operadora, valor, nomeCliente);
        return;
      }
      
      // Serviços adicionais
      if (opcao === 46) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `🎮 *RECARGA DE JOGOS (PicPay)*\n\n🔗 https://picpay.com/recarga-jogos\n\n💰 Valores: R$ 10,00 | R$ 20,00 | R$ 50,00`);
        return;
      }
      if (opcao === 47) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `🎬 *RECARGA NETFLIX/SPOTIFY*\n\n🔗 https://mtech.com.br/streaming\n\n📺 Netflix: R$ 39,90/mês\n🎵 Spotify: R$ 19,90/mês`);
        return;
      }
      if (opcao === 48) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `📋 *HISTÓRICO DE RECARGAS*\n\n🔗 https://mtech.com.br/historico/${numeroUsuario}\n\n📌 Digite 100 se precisar de ajuda.`);
        return;
      }
      if (opcao === 49) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `💰 *SALDO DE BÔNUS*\n\nSeu saldo atual: R$ 0,00\n\n🎁 Indique amigos e ganhe 10% de bônus!`);
        return;
      }
      if (opcao === 50) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `📝 *CRIAR CONTA*\n\n🔗 https://mtech.com.br/register?ref=${numeroUsuario}\n\n✅ Crie sua conta e ganhe R$ 5,00 de bônus!`);
        return;
      }
      
      // Se não escolheu operadora ainda
      await simulateTyping(chat);
      await client.sendMessage(msg.from, `📱 *ESCOLHA PRIMEIRO A OPERADORA!*\n\nDigite:\n3️⃣6️⃣ → VIVO\n3️⃣7️⃣ → TIM\n3️⃣8️⃣ → CLARO\n\n0️⃣ → Voltar ao Menu Principal`);
      return;
    }
    
    // =====================================
    // MENU PRINCIPAL
    // =====================================
    if (estadoAtual.menu === "principal") {
      
      if (opcao === 1) {
        estadoConversa.set(numeroUsuario, { menu: "iptv" });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `📺 *TESTES IPTV*\n\n🔒 *Você tem direito a APENAS 1 teste gratuito!*\n\n${menuIPTV}`);
        return;
      }
      
      if (opcao === 2) {
        const linkInternet = "https://servex.ws/test/a3bf7a43-f70a-43ec-9a68-c72427bbd193";
        
        const mensagemInternet = `🌐 *INTERNET ILIMITADA - STARPLAY* 🌐

✅ *TESTE GRATUITO DISPONÍVEL, ${nomeCliente}!* ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 *ACESSE O LINK ABAIXO:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${linkInternet}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *INSTRUÇÕES:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Clique no link acima
2️⃣ Clique em "GERAR TESTE GRÁTIS"
3️⃣ Seu teste será gerado automaticamente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 *ATENÇÃO: Você tem direito a APENAS 1 teste gratuito!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 *Após o teste, adquira seu plano (opção 100)*
🔧 *Precisa de ajuda?* Digite 5 para suporte.`;

        await simulateTyping(chat);
        await client.sendMessage(msg.from, mensagemInternet);
        await humanDelay();
        await enviarInfoApps(chat, nomeCliente);
        return;
      }
      
      if (opcao === 3) {
        estadoConversa.set(numeroUsuario, { menu: "recargas" });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, menuRecargas);
        return;
      }
      
      if (opcao === 4) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `🔧 *SUPORTE IPTV*\n\nDescreva seu problema:`);
        aguardandoProblemaIPTV.add(numeroUsuario);
        return;
      }
      
      if (opcao === 5) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `🔧 *SUPORTE INTERNET*\n\nDescreva sua dificuldade:`);
        aguardandoProblemaInternet.add(numeroUsuario);
        return;
      }
      
      if (opcao === 10) {
        estadoConversa.set(numeroUsuario, { menu: "consultas" });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, menuConsultas);
        return;
      }
      
      if (opcao === 20) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `👤 *MINHA CONTA*\n\n🔗 https://creditodecelular.com/account`);
        return;
      }
      
      if (opcao === 30) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `🎁 *INDICAR AMIGOS*\n\n🔗 https://mtech.com.br/indicar/MTECH${numeroUsuario}\n💎 Ganhe 10% de bônus!`);
        return;
      }
      
      if (opcao === 40) {
        estadoConversa.set(numeroUsuario, { menu: "ajuda" });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, menuAjuda);
        return;
      }
      
      if (opcao === 50) {
        estadoConversa.set(numeroUsuario, { menu: "termos" });
        await simulateTyping(chat);
        await client.sendMessage(msg.from, menuTermos);
        return;
      }
      
      if (opcao !== 0 && opcao !== 6 && opcao !== 100) {
        await simulateTyping(chat);
        await client.sendMessage(msg.from, `${getRespostaAleatoria(respostasNaoEntendi)}\n\n📌 *Digite o número da opção desejada.*\n\n${menuPrincipal}`);
      }
    }
    
    // =====================================
    // SUBMENU CONSULTAS (51-60)
    // =====================================
    if (estadoAtual.menu === "consultas") {
      if (opcao >= 51 && opcao <= 60) {
        await simulateTyping(chat);
        const consultas = {
          51: "📺 *IPTV:* 1M=R$29,90 | 3M=R$69,90 | 6M=R$119,90 | 12M=R$199,90",
          52: "🌐 *INTERNET:* 1M=R$49,90 | 3M=R$129,90 | 6M=R$199,90 | 12M=R$349,90",
          53: "🎁 *COMBOS:* IPTV+Internet R$69,90/mês | IPTV+Recargas R$59,90",
          54: "💳 *PAGAMENTOS:* PIX (10% off), Cartão, Boleto, PicPay",
          55: "⏱️ *PRAZO:* Testes imediato | Planos 5min | Recargas 2min",
          56: "🛍️ *BLACK FRIDAY:* 50% OFF em todos os planos!",
          57: "💸 *DESCONTO PIX:* 10% de desconto pagando via PIX!",
          58: "🤝 *INDICAÇÃO:* Ganhe 10% de bônus indicando amigos!",
          59: "👑 *CLIENTE VIP:* Benefícios exclusivos para clientes fiéis",
          60: "🎲 *SORTEIOS:* Participe fazendo uma recarga!"
        };
        await client.sendMessage(msg.from, consultas[opcao]);
        return;
      }
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    // =====================================
    // SUBMENU AJUDA (61-75)
    // =====================================
    if (estadoAtual.menu === "ajuda") {
      if (opcao >= 61 && opcao <= 75) {
        await simulateTyping(chat);
        const ajudas = {
          61: "❓ *TESTE:* 1 teste IPTV e 1 Internet | Duração 1h-12h",
          62: "📺 *TV:* Baixe ASSIST+ ou LAZER PLAY | Código: starplay",
          63: "📱 *CELULAR:* Android: IPTV Smarters | iOS: ASSIST+",
          64: "💻 *PC:* Use BlueStacks + app ASSIST+",
          65: "⚠️ *APP NÃO ABRE:* Limpe cache e reinicie",
          66: "🐢 *TRAVANDO:* Configure DNS 8.8.8.8",
          67: "🔑 *SENHA:* Teste pode ter expirado",
          68: "🔄 *RENOVAR:* Digite 100 e fale com proprietário",
          69: "🔍 *PERDI DADOS:* Verifique histórico ou solicite novo teste",
          70: "🚫 *CANCELAR:* Digite 100 e informe o motivo",
          71: "📱 *WHATSAPP:* (83) 98838-7164",
          72: "📞 *TELEFONE:* (83) 98838-7164 (mensagens)",
          73: "✉️ *E-MAIL:* suporte@mtech.com.br",
          74: "🕐 *HORÁRIO:* Seg-Sex 8h-22h | Sáb 9h-18h | Dom 10h-16h",
          75: "💬 *RECLAMAÇÕES:* Digite 100 e envie sua mensagem"
        };
        await client.sendMessage(msg.from, ajudas[opcao]);
        return;
      }
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    // =====================================
    // SUBMENU CONFIGURAÇÕES (76-90)
    // =====================================
    if (estadoAtual.menu === "configuracoes") {
      if (opcao >= 76 && opcao <= 90) {
        await simulateTyping(chat);
        const configs = {
          76: "🔧 *DNS GOOGLE:* 8.8.8.8 / 8.8.4.4",
          77: "🔧 *DNS CLOUDFLARE:* 1.1.1.1 / 1.0.0.1",
          78: "🗑️ *LIMPAR CACHE:* Configurações > Apps > APP > Limpar cache",
          79: "🔄 *ATUALIZAR:* Desinstale e instale a nova versão",
          80: "⏹️ *FORÇAR PARADA:* Configurações > Apps > APP > Forçar parada",
          81: "📊 *TESTE VELOCIDADE:* fast.com ou speedtest.net",
          82: "🔒 *VPN:* Baixe um app VPN e conecte ao servidor",
          83: "🌐 *PROXY:* Host proxy.mtech.com | Porta 8080",
          84: "🛡️ *FIREWALL:* Libere portas 80, 443, 8080",
          85: "📋 *LOGS:* Envie versão do app e descrição do erro",
          86: "📲 *ASSIST+:* Código starplay | Cole usuário e senha",
          87: "📲 *LAZER PLAY:* Código starplay | Configure login",
          88: "📲 *IPTV SMARTERS:* URL: http://starplay.tv",
          89: "📲 *TIVIMATE:* XC API | URL: http://starplay.tv",
          90: "📲 *OTT NAVIGATOR:* Xtream API | Preencha os dados"
        };
        await client.sendMessage(msg.from, configs[opcao]);
        return;
      }
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
    // =====================================
    // SUBMENU TERMOS (91-99)
    // =====================================
    if (estadoAtual.menu === "termos") {
      if (opcao >= 91 && opcao <= 99) {
        await simulateTyping(chat);
        const termos = {
          91: "📜 *TERMOS DE USO:* Serviço pessoal e intransferível",
          92: "🔒 *PRIVACIDADE:* Seus dados são protegidos",
          93: "💰 *GARANTIA:* 7 dias de garantia | Reembolso integral",
          94: "🚫 *CANCELAMENTO:* A qualquer momento | Sem multa",
          95: "⚖️ *USO ACEITÁVEL:* Apenas uso pessoal",
          96: "👤 *DIREITOS:* Arrependimento em 7 dias | Garantia",
          97: "🛡️ *SEGURANÇA:* Criptografia ponta a ponta | LGPD",
          98: "🍪 *COOKIES:* Para melhorar experiência",
          99: "🔄 *ATUALIZAÇÕES:* Serviço pode ser atualizado"
        };
        await client.sendMessage(msg.from, termos[opcao]);
        return;
      }
      resetarEstadoConversa(numeroUsuario);
      await simulateTyping(chat);
      await client.sendMessage(msg.from, menuPrincipal);
      return;
    }
    
  } catch (error) {
    console.error("❌ Erro:", error);
    try {
      await client.sendMessage(msg.from, 
        `⚠️ *Erro técnico*\n\nDesculpe, ocorreu um erro.\n🔄 *Digite /menu para reiniciar.*`);
    } catch(e) {}
  }
});

console.log("╔══════════════════════════════════════════════════════════════╗");
console.log("║         🚀 ATENDIMENTO MTECH - Robô iniciado!                 ║");
console.log("╠══════════════════════════════════════════════════════════════╣");
console.log("║ ✅ CORREÇÃO: Interferência entre menus resolvida!            ║");
console.log("║ ✅ QR CODE CORRIGIDO para Oracle Cloud!                       ║");
console.log("║ 📱 Sistema de estado de conversa ativado!                    ║");
console.log("║ 🚫 BLOQUEIO de ligações ativado!                             ║");
console.log("║ 📱 QR Code servidor em http://localhost:8080                 ║");
console.log("╚══════════════════════════════════════════════════════════════╝");
