app_name = ray-tests


build-test:
		@sudo podman build -t $(app_name) .. -f tests/Containerfile

build-test-no-cache:
		@sudo podman build -t $(app_name) .. --no-cache -f tests/Containerfile

run-test:
		@sudo podman run -it $(app_name)