# XML-RPC com containers usando Podman

Exemplo simples de comunicação XML-RPC entre um container servidor e um ou mais containers clientes.

Baseei toda a demonstração na própria documentação Python do
módulo XML-RPC. Como uso podman, se você usa docker, substitua
o comando podman por docker (os argumentos e flags são
compatíveis).

## Subir a demonstração

```bash
podman compose up --build
```

O serviço `server` fica disponível dentro da rede do Compose pelo hostname `server`.
Por isso o cliente usa:

```text
http://server:8000/RPC2
```

## Subir vários clientes

```bash
podman compose up --build --scale client=3
```

Cada cliente executa as chamadas XML-RPC e encerra. O servidor continua em execução.

## Acompanhar as interações

Os logs aparecem diretamente no terminal do Compose. O cliente mostra cada chamada enviada:

```text
client:<container> -> add(2, 3)
client:<container> <- add = 5
```

O servidor mostra de qual container/IP recebeu a chamada e qual resposta retornou:

```text
server <- 10.89.2.3:12345 add(2, 3)
server -> 10.89.2.3:12345 add = 5
```

## Testar o servidor pelo host

Como a porta `8000` está publicada, também é possível executar o cliente fora do Compose:

```bash
python client/main.py
```

Uso isso para demonstrar o "cliente impaciente" no script
teste_retry.py

Nesse caso o cliente usa o valor padrão:

```text
http://localhost:8000/RPC2
```

## Encerrar os containers

```bash
podman compose down
```

## Demonstrações

### Demonstrando falha no servidor

Podemos derrubar o servidor e ver o comportamento dos clientes.

```bash
podman compose up --build
podman compose stop server
podman compose run client
```

### Demonstrando chamada síncrona bloqueante

Se registrarmos no servidor uma função como essa, e fizeremos os clientes a chamarem, veremos que o primeiro cliente faz todos os outros ficarem em espera.

```python
import time

def slow_add(x, y):
    time.sleep(10)
    return x + y

server.register_function(slow_add, "slow_add")
```

### Estamos lidando com chamadas duplicadas?

Se adicionarmos esse trecho no servidor e registrarmos, e algum cliente fizer retry de chamada, não estamos lidando com isso ainda.

```python
import time

counter = 0

def increment():
    global counter
    counter += 1
    log(f"Contador mudou para {counter}")
    time.sleep(5)
    return counter

server.register_function(increment, "increment")

```

## Liberando espaço no seu disco

Liste os containers criados e qualquer outro. Você pode remover
todos também, mas cuidado, pois isso fará com que, se você
usa docker no dia a dia, numa próxima execução de outro projeto
você precise recriar os containers deles. Depois de remover
um container específico (sem a flag a) ou todos, você pode
remover as imagens de containers baixadas.

```bash
podman container ls -a
porman container rm -a
podman images
podman image rm -a
```

Com o comando de listar as imagens, perceba quanto espaço de
armazenamento é utilizado.
