# os-pysnake
Desenvolvimento do jogo da cobrinha usando a arquitetura cliente-servidor com sockets.

### Autores
1. Ícaro Azevedo (icazevedo10@gmail.com)
2. Maria Rayane Alves (mrayalves05@gmail.com)
2. Pedro Cardoso (carvalho.pedro.cardoso@gmail.com)

### Tecnologias
1. Python

### Informações gerais
A proposta dessa atividade é criar uma estrutura cliente-servidor e aplicar no jogo Pysnake. 

### Desenvolvimento da solução
Para estruturação do jogo foi decidido a criação do servidor isolado que irá gerenciar a comunicação  entre os dois clientes, sendo responsável pela aplicação das regras do jogo e armazenar o cenário.  Nessa formatação o servidor recebe a comunicação dos dois clientes pelo sistema de mensagem e realiza a sincronização de ambas as telas. Ao receber a mensagem o servidor executa essas ações nos objetos de armazenamento criados ( exemplo no caso de movimentação da cobra de id 1, será replicada no objeto interno que espelha essa cobra) dependendo da ação recebida o sistema verifica se causa alguma reação na tela e comunica aos demais clientes.

### Executando a soluçao
Para executar o projeto, primeiramente clone esse repositório em sua máquina.

Importe o pygame usando o comando `pip3 install pygame`. Em seguida, abra três abas de terminal. Na primeira, execute o comando para startar o servidor (`python3 servidor.py`). Depois, execute na segunda aba o primeiro cliente (`python3 snake.py`); e na terceira aba, o segundo cliente (`python3 snake2.py`). Pronto! Agora você pode interagir com os dois cliente e se divertir.

### Para deixar claro
As lógicas de comer a fruta e matar a cobra, não estão funcionando.
