FROM maven:3.9.7-eclipse-temurin-17

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
RUN python3 -m venv .env && \
    . .env/bin/activate && \
    pip install -q --no-cache-dir requests https://github.com/LukvonStrom/monitors4codegen/archive/main.zip && \
    python setup.py install




# Copy the test script
COPY lsp-test.py .

VOLUME [ "/data", "/input", "/repo" ]

ENV INITIAL_DATA_PATH "/data/initial.json"
ENV EDIT_DATA_PATH "/data/edit.json"

COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# Set the default command
ENTRYPOINT ["/app/init.sh"]