# Cortez Voz — distribuição 0.1.0

Aplicativo local de voz mantido pela Empire-Business, derivado de VoiceStudio.
O instalador do Cortez seleciona uma revisão exata deste repositório e verifica
o SHA-256 do pacote. O aplicativo abre no navegador local; não depende da
instalação do aplicativo Electron original.

## Instalação

Python 3.11 ou 3.12 já deve estar disponível. O instalador baixa uv e Bun nas
versões e hashes de `tools.lock.json`, prepara as dependências de `uv.lock` e
`bun.lock` em ambiente exclusivo e compila a interface. Não usa sudo, não remove
quarentena, não modifica assinaturas e não altera o Python global.

Para desenvolvimento, `python cortez/install.py` mostra a prévia e `--apply`
instala. A operação pode baixar vários GB. Ela não inicia o backend, não cria
o banco do aplicativo e não baixa modelos. Dependências Python sem wheel podem
executar seu build declarado; o processo recebe ambiente sem as credenciais
do shell, mas isso não é uma sandbox contra código malicioso.

Matriz inicial: macOS Apple Silicon, Windows x64, Linux x64 com glibc.
Mac Intel, Windows ARM e Linux ARM ainda não são suportados por este instalador.
Planejamento por plataforma não equivale a teste real nessas máquinas.

## Primeiro início e dados

O início é uma ação separada: `python cortez/install.py --start --data-dir CAMINHO
--initialize-data`. Essa autorização explícita se refere ao banco local naquela
pasta: o backend cria o banco SQLite e aplica suas migrations. Não usar uma
pasta de banco de outra aplicação. O instalador não executa esse passo.

A interface fica em `http://127.0.0.1:3930`. Vozes, projetos e cache de modelos
ficam na pasta de dados selecionada, fora das versões de código. Atualizar o
Cortez não deve substituir esses dados. Não há atualização automática do app.

Esta primeira distribuição libera os engines locais OmniVoice, MLX Audio
(Apple Silicon) e KittenTTS. Instalações de engines extras e a galeria remota
do projeto original ficam desativadas. Os modelos são preparados por escolha
explícita e têm licenças próprias: em especial, não presumir que os pesos
padrão OmniVoice permitem uso comercial. Ver `LICENSE-NOTICE.md`.
Os modelos ainda não possuem um catálogo de revisões homologadas pela Empire;
o pin de código não é uma promessa de que todos os pesos são imutáveis.

## Licença, segurança e manutenção

Código e alterações distribuídos sob AGPL-3.0-only; código original e atribuições
preservados em `LICENSE`, `LICENSE-NOTICE.md` e `cortez/UPSTREAM.json`.
Fonte completa: https://github.com/Empire-Business/cortez-voz .
Veja [segurança, privacidade e IA](SECURITY.md). Os documentos históricos do
upstream descrevem também recursos não habilitados nesta edição; este guia
define o caminho de instalação suportado pela Empire.
