FROM postgres:16

# Install required packages for progress monitoring and PostgreSQL client
RUN apt-get update && apt-get install -y \
    bash \
    pv \
    curl \
    gzip \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the import script and make it executable
COPY import_all.sh /usr/local/bin/import_all.sh
RUN sed -i 's/\r$//' /usr/local/bin/import_all.sh
RUN chmod +x /usr/local/bin/import_all.sh

# Set the entrypoint to our script
ENTRYPOINT ["/bin/bash", "/usr/local/bin/import_all.sh"]
