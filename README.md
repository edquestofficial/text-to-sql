# text-to-sql
<ul>
    <li>1: Take a clone from github</li>
    <li>2: go inside main directory (text-to-sql)</li>
    <li>3: run below command: </li>
</ul>

```bash 
pipenv shell
pipenv install
pipenv run python main.py
```

Important pipenv related commands:
```bash
Install: pip install pipenv
check installed version: pipenv --version
install all defined dependencies in pipfile: pipenv install
install specific package/dependencies: pipenv install package_name
Create virtual enviorment: pipenv shell
```

docker commands:
1: docker build -t text-to-sql .
Run Docker container
2.1: docker run -it --network=host -p 7861:7860 text-to-sql
Pass openAI key in docker run command
2.2: docker run -it --network=host -p 7860:7860 -e OPENAI_API_KEY=<your-openai-api-key> text-to-sql
2.2: docker run -it --network=host -p 7860:7860 -e text-to-sql
List of running containers:
docker ps -a
Go inside the container
 docker exec -it 50ca7c177bdd /bin/bash
open any file:
    cat filename
Stop docker container:
    docker stop container_id_or_name
    docker stop $(docker ps -q)
Remove stopper container
    docker rm container_id_or_name
    docker rm $(docker ps -a -q)
Delete Docker Images
    docker image rm image_id_or_name
    docker rmi image_id_or_name
    docker image prune
    docker system prune
