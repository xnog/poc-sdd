.PHONY: run install build start lint typecheck clean

install:
	pnpm install

run: install
	pnpm dev

build: install
	pnpm build

start: build
	pnpm start

lint: install
	pnpm lint

typecheck: install
	pnpm typecheck

clean:
	rm -rf node_modules .next
