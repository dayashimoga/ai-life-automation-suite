.PHONY: test-all lint-all run-all clean

test-all:
	@echo "Running tests for memory-journal-app..."
	@bash scripts/test_memory-journal-app.sh
	@echo "Running tests for doomscroll-breaker-app..."
	@bash scripts/test_doomscroll-breaker-app.sh
	@echo "Running tests for visual-intelligence-app..."
	@bash scripts/test_visual-intelligence-app.sh

lint-all:
	@echo "Running linters for all apps..."
	@bash scripts/lint_all.sh

run-all:
	docker compose -f docker/docker-compose.yml up

clean:
	@bash scripts/clean_envs.sh
