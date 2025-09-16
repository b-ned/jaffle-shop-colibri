.PHONY: all seed build docs run

# Default target (can be overridden: make run TARGET=dev)
TARGET ?= dev

# Default pipeline
all: run

# Run dbt seed
seed:
	dbt seed --full-refresh --vars '{"load_source_data": true}' --target $(TARGET)

fixture:
	dbt run-operation create_customers_hardcoded --target $(TARGET)

# Run dbt build
build:
	dbt build --target $(TARGET)

# Generate docs
docs:
	dbt docs generate --target $(TARGET)

# Full pipeline
run: seed build docs
run_from_build: build docs