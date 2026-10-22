# Segurança, privacidade e IA

Esta é uma distribuição inicial de código aberto, sem certificação de segurança.
O instalador valida revisão, tamanho e hash dos downloads, rejeita links e caminhos
perigosos em arquivos compactados e não acompanha a branch do autor original.
Atualizações de código precisam de revisão e publicação da Empire-Business.

A interface distribuída é web local e o backend escuta apenas em 127.0.0.1:3930.
Não publique essa porta na internet. As proteções originais de origem/autenticação
permanecem; o nome da distribuição não é uma prova criptográfica de identidade.

A instalação acessa GitHub, os registros de pacotes e os índices PyTorch declarados
no lock. Modelos escolhidos pelo usuário podem acessar Hugging Face e outros
fornecedores documentados. As dependências e os modelos mantêm suas licenças.
Não há uma auditoria completa de todos esses fornecedores. O aplicativo original
inclui recursos online opcionais; esta edição não transforma todo o código herdado
em uma sandbox offline. Não configurar serviços remotos sem consentimento.

Dados e mídias ficam no diretório local escolhido. O setup não lê chaves do Cortez.
Dependências são preparadas com um ambiente de processo reduzido; builds de pacotes
continuam sendo execução de código. Não há envio de telemetria habilitado pela Empire.

Vozes sintéticas e clones exigem direito de uso das gravações e da voz. A licença
do aplicativo não concede direitos sobre modelos, vozes ou conteúdos produzidos.
Qualidade, pronúncia e alinhamento precisam de revisão humana.

Reportar problemas ao mantenedor pelo repositório da Empire, sem anexar chaves,
voz privada ou bancos de projetos. Builds e funcionamento real por plataforma
devem ser registrados em cada release; uma verificação estática não os substitui.
