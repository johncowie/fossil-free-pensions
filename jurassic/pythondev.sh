docker build -t jurassic-dev .
docker run -it -v $PWD/:/jurassic jurassic-dev bash
