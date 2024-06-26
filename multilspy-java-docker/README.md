# LSP Server

Self-built Docker image that generically clones a repo and allows LSP interaction

## Demo
Build with
`docker build -t multilspy-java-docker .`

Clone a repo with

git clone https://github.com/wireapp/lithium.git lithium && cd lithium && \
git fetch --depth 2 origin 10d7545c5771b03dd9f6122bd5973a759eb2cd03 && \
git checkout 10d7545c5771b03dd9f6122bd5973a759eb2cd03

Run with
`docker run -v "$(pwd)/lithium:/mnt/repo" -v "$(pwd)/data:/mnt/data" -v "$(pwd)/edit:/mnt/input" multilspy-java-docker -e yes -f src/main/java/com/wire/lithium/models/NewBotResponseModel.java`