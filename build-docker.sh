# should be cross-compatible
docker rm -f cuso
docker build --rm --tag=cuso .
docker run -p4444:4444 --name=cuso cuso