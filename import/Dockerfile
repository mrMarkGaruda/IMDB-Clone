FROM postgres:16

# Install required packages for progress monitoring
RUN apt-get update && apt-get install -y \
    pv \
    curl \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Copy the import script
COPY import_all.sh /usr/local/bin/import_all.sh
RUN chmod +x /usr/local/bin/import_all.sh

# Set working directory
WORKDIR /import

# Default command
CMD ["/usr/local/bin/import_all.sh"]
