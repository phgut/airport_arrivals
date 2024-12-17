FROM ubuntu:jammy

# Set working directory
WORKDIR /opt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3.10-venv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and env files
COPY builder/requirements /opt/

# Install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install -r /opt/requirements

RUN mkdir -p /opt/logs || touch /opt/logs/app.log

COPY . /opt/source
COPY builder/.env builder/.env.template /opt/
# Copy entrypoint script
COPY builder/entrypoint.sh /opt/
RUN chmod +x /opt/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/opt/entrypoint.sh"]