FROM maven:3-eclipse-temurin-17

WORKDIR /app


# Install Python and required packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Optionally, run Maven tests
# RUN mvn dependency:go-offline
# RUN mvn clean test -B

# Set up the Python environment and install dependencies
COPY setup.py .
COPY download.py .
RUN mkdir -p /tmp/repo
RUN python3 --version
RUN python3 -m venv .env && \
    . .env/bin/activate && \
    pip install -q --no-cache-dir requests https://github.com/LukvonStrom/multilspy-java/archive/main.zip && \
    python download.py




COPY *.py /app/

COPY setup.sh .

VOLUME [ "/mnt/data", "/mnt/input", "/mnt/repo" ]

ENV INITIAL_DATA_PATH="/mnt/data/initial.json"
ENV EDIT_DATA_PATH="/mnt/data/edit.json"

ENV BASE_OPERATION_DIR="/mnt/repo"

ENV LOGLEVEL="DEBUG"

COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# Set the default command
ENTRYPOINT ["/app/init.sh"]