how to run:

Build docker 

```shell
docker build -t llm_recnik -f Dockerfile .
```

Run docker 

```shell
docker run --rm -e OPENAI_API_KEY=<put your key here> -p 8924:8924 llm_recnik
```